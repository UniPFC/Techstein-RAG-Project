import os
from typing import List, Optional
from src.ai.provider.llm import Provider
from config.settings import settings
from config.logger import logger
from src.rag.models.query import RAGQuery, RAGQueries

class QueryEngine:
    """
    High-level engine for RAG query expansion.
    """
    def __init__(
        self,
        primary_provider: Optional[Provider] = None,
        fallback_provider: Optional[Provider] = None,
    ):
        self.primary_provider = primary_provider or Provider(
            model_name=settings.LLM_MODEL,
            provider_alias=settings.LLM_PROVIDER,
        )
        
        self.fallback_provider = fallback_provider or self.primary_provider
        
        self.templates_dir = os.path.join(settings.BASE_DIR, "src", "rag", "prompts", "query_expansion")
        self.system_template = self._load_prompt("query_exp_system_template")
        self.user_template = self._load_prompt("query_exp_user_template")

    def _load_prompt(self, prompt_name: str) -> str:
        """
        Load prompt template from markdown file.
        
        Args:
            prompt_name: Name of the prompt file (without .md extension)
            
        Returns:
            Prompt template as string
        """
        prompt_path = os.path.join(settings.BASE_DIR, "src", "rag", "prompts", f"{prompt_name}.md")
        try:
            with open(prompt_path, "r", encoding="utf-8") as f:
                return f.read().strip()
        except FileNotFoundError:
            logger.error(f"Prompt file not found: {prompt_path}")
            raise
        except Exception as e:
            logger.error(f"Failed to load prompt {prompt_name}: {e}")
            raise

    def expand_query(self, query_text: str) -> List[RAGQuery]:
        """
        Generates a set of expanded queries for a single user query.
        """
        count = max(1, settings.QUERY_EXPANSION_COUNT - 1)
        
        system_message = self.system_template.format(count=count)
        user_message = self.user_template.format(query_text=query_text, count=count)
        
        messages = [
            {"role": "system", "content": system_message},
            {"role": "user", "content": user_message}
        ]
        
        try:
            logger.info(f"Expanding query '{query_text}' using provider ({self.primary_provider.model_name}).")
            
            if hasattr(self.primary_provider, "generate_structured"):
                result = self.primary_provider.generate_structured(
                    messages=messages,
                    response_format=RAGQueries,
                    temperature=0.4
                )
                
                if isinstance(result, RAGQueries):
                    return self._normalize_response(query_text, result.queries)
            
            logger.warning("Primary provider returned unstructured response or failed. Attempting fallback/manual parse.")
             
        except Exception as e:
            logger.error(f"Primary expansion failed: {e}. Returning original query.")

        return [RAGQuery(text=query_text)]

    def _normalize_response(self, original_text: str, variations: List[RAGQuery]) -> List[RAGQuery]:
        """
        Normalizes and deduplicates expanded queries.
        """
        unique_queries = {original_text.strip().lower(): RAGQuery(text=original_text)}
        
        for q in variations:
            cleaned_text = q.text.strip()
            key = cleaned_text.lower()
            if key and key not in unique_queries:
                unique_queries[key] = q

        final_list = list(unique_queries.values())

        if len(final_list) > settings.QUERY_EXPANSION_COUNT:
            final_list = final_list[:settings.QUERY_EXPANSION_COUNT]
            
        return final_list
