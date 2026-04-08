"""
Chunk ingestion service for processing spreadsheets and storing in Qdrant.
Handles: Excel/CSV upload → parsing → embedding → Qdrant storage.
"""

import json
from typing import List, Dict, Any, Tuple
import pandas as pd
from uuid import UUID
from io import BytesIO
from config.logger import logger
from shared.qdrant.client import QdrantManager
from shared.database.models.knowledge_chunk import KnowledgeChunk
from src.ai.embedding import EmbeddingEngine


class ChunkIngestionService:
    """
    Service for ingesting question-answer chunks into Qdrant.
    """
    
    def __init__(self, embedding_engine: EmbeddingEngine, qdrant_manager: QdrantManager):
        """
        Initialize ingestion service.
        
        Args:
            embedding_engine: EmbeddingEngine for generating embeddings
            qdrant_manager: QdrantManager for vector storage
        """
        self.embedding_engine = embedding_engine
        self.qdrant_manager = qdrant_manager
        logger.info("ChunkIngestionService initialized")
    
    def parse_spreadsheet(
        self, 
        file_content: bytes, 
        filename: str,
        question_col: str = "question",
        answer_col: str = "answer"
    ) -> List[Dict[str, Any]]:
        """
        Parse spreadsheet file into chunks.
        
        Args:
            file_content: File bytes
            filename: Original filename
            question_col: Column name for questions
            answer_col: Column name for answers
            
        Returns:
            List of chunk dicts with question, answer, metadata
        """
        try:
            # Detect file type and read
            if filename.endswith('.csv'):
                for enc in ('utf-8', 'latin-1', 'cp1252'):
                    try:
                        # Auto-detect delimiter by reading first line
                        sample = file_content[:4096]
                        try:
                            first_line = sample.decode(enc).split('\n')[0]
                        except UnicodeDecodeError:
                            continue
                        if ';' in first_line and ',' not in first_line:
                            sep = ';'
                        elif '\t' in first_line and ',' not in first_line:
                            sep = '\t'
                        else:
                            sep = ','
                        df = pd.read_csv(BytesIO(file_content), encoding=enc, sep=sep)
                        break
                    except UnicodeDecodeError:
                        continue
                else:
                    raise ValueError(f"Não foi possível decodificar o arquivo {filename}. Tente salvar como UTF-8.")
            elif filename.endswith(('.xlsx', '.xls')):
                df = pd.read_excel(BytesIO(file_content))
            else:
                raise ValueError(f"Unsupported file format: {filename}")
            
            # Auto-detect columns if defaults not found
            question_col, answer_col = self._detect_columns(df, question_col, answer_col)
            
            # Validate columns
            if question_col not in df.columns or answer_col not in df.columns:
                available = ", ".join(df.columns.tolist())
                raise ValueError(
                    f"Não foi possível identificar as colunas de pergunta e resposta. "
                    f"Colunas disponíveis: {available}. "
                    f"Renomeie para 'question' e 'answer' ou use nomes similares."
                )
            
            # Parse chunks
            chunks = []
            for idx, row in df.iterrows():
                question = str(row[question_col]).strip()
                answer = str(row[answer_col]).strip()
                
                if question and answer and question != 'nan' and answer != 'nan':
                    chunks.append({
                        "question": question,
                        "answer": answer,
                        "metadata": {
                            "source_file": filename,
                            "row_number": int(idx) + 2  # +2 for header and 0-indexing
                        }
                    })
            
            logger.info(f"Parsed {len(chunks)} chunks from {filename}")
            return chunks
            
        except Exception as e:
            logger.error(f"Failed to parse spreadsheet {filename}: {e}")
            raise
    
    @staticmethod
    def _detect_columns(df: pd.DataFrame, question_col: str, answer_col: str) -> tuple:
        """
        Auto-detect question and answer columns if the specified ones don't exist.
        Tries common column name patterns (case-insensitive).
        """
        cols_lower = {c.lower().strip(): c for c in df.columns}
        
        # If exact columns exist, use them
        if question_col in df.columns and answer_col in df.columns:
            return question_col, answer_col
        
        # Common patterns for question columns
        q_patterns = ['question', 'pergunta', 'questão', 'questao', 'enunciado', 'prompt', 'input', 'q']
        # Common patterns for answer columns  
        a_patterns = ['answer', 'resposta', 'response', 'output', 'a', 'solução', 'solucao', 'gabarito']
        
        detected_q = None
        detected_a = None
        
        for pattern in q_patterns:
            if pattern in cols_lower:
                detected_q = cols_lower[pattern]
                break
        
        for pattern in a_patterns:
            if pattern in cols_lower:
                detected_a = cols_lower[pattern]
                break
        
        # Fallback: if file has exactly 2 columns, use first as question, second as answer
        if (detected_q is None or detected_a is None) and len(df.columns) == 2:
            detected_q = detected_q or df.columns[0]
            detected_a = detected_a or df.columns[1]
            logger.info(f"Auto-detected 2-column file: question='{detected_q}', answer='{detected_a}'")
        
        final_q = detected_q or question_col
        final_a = detected_a or answer_col
        
        if final_q != question_col or final_a != answer_col:
            logger.info(f"Auto-detected columns: question='{final_q}', answer='{final_a}'")
        
        return final_q, final_a

    def ingest_chunks(
        self,
        chat_type_id: UUID,
        chunks: List[Dict[str, Any]],
        db_session: Any,
        batch_size: int = 32,
        on_progress=None
    ) -> Tuple[List[str], int]:
        """
        Ingest chunks into Qdrant with embeddings.
        """
        if not chunks:
            logger.warning("No chunks to ingest")
            return [], 0
        
        try:
            # Prepare texts for embedding (question + answer concatenated)
            texts = [f"{chunk['question']}\n\n{chunk['answer']}" for chunk in chunks]
            
            # Generate embeddings in batches
            all_embeddings = []
            total_batches = (len(texts) - 1) // batch_size + 1
            for i in range(0, len(texts), batch_size):
                batch_texts = texts[i:i + batch_size]
                batch_embeddings = self.embedding_engine.embed(batch_texts)
                all_embeddings.extend(batch_embeddings)
                batch_num = i // batch_size + 1
                logger.debug(f"Generated embeddings for batch {batch_num}/{total_batches}")
                if on_progress:
                    on_progress(len(all_embeddings))
            
            # Insert into Qdrant
            point_ids = self.qdrant_manager.insert_chunks(
                chat_type_id=chat_type_id,
                chunks=chunks,
                embeddings=all_embeddings
            )
            
            for i, point_id in enumerate(point_ids):
                chunk_data = chunks[i]
                metadata = chunk_data.get("metadata", {})
                
                knowledge_chunk = KnowledgeChunk(
                    chat_type_id=chat_type_id,
                    qdrant_point_id=point_id,
                    source_file=metadata.get("source_file"),
                    row_number=metadata.get("row_number"),
                    chunk_metadata=json.dumps(metadata)
                )
                db_session.add(knowledge_chunk)
            
            db_session.commit()
            
            logger.info(f"Successfully ingested {len(point_ids)} chunks for chat_type_id={chat_type_id}")
            return point_ids, len(point_ids)
            
        except Exception as e:
            logger.error(f"Failed to ingest chunks for chat_type_id={chat_type_id}: {e}")
            raise
    
    def ingest_from_file(
        self,
        chat_type_id: UUID,
        file_content: bytes,
        filename: str,
        db_session: Any,
        question_col: str = "question",
        answer_col: str = "answer"
    ) -> Tuple[List[str], int]:
        """
        Complete ingestion pipeline: parse file → embed → store.
        
        Args:
            chat_type_id: ID of the ChatType
            file_content: File bytes
            filename: Original filename
            db_session: Database session
            question_col: Column name for questions
            answer_col: Column name for answers
            
        Returns:
            Tuple of (point_ids, total_ingested)
        """
        logger.info(f"Starting ingestion pipeline for chat_type_id={chat_type_id}, file={filename}")
        
        # Parse spreadsheet
        chunks = self.parse_spreadsheet(file_content, filename, question_col, answer_col)
        
        # Ingest chunks
        point_ids, total = self.ingest_chunks(chat_type_id, chunks, db_session)
        
        logger.info(f"Ingestion pipeline completed: {total} chunks ingested")
        return point_ids, total
