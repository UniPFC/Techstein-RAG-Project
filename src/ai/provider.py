"""
LLM and Embedding providers with support for multiple backends.
Adapted for multi-tenant RAG chat system.
Supports: Ollama, OpenAI, Gemini, local HuggingFace models.
"""

import torch
from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
from openai import OpenAI
from config.logger import logger
from config.settings import settings


URLS = {
    "ollama": "http://localhost:11434/v1",
    "gemini": "https://generativelanguage.googleapis.com/v1beta/openai/",
    "openai": "https://api.openai.com/v1"
}


def resolve_api_key(provider_alias: str, explicit_key: Optional[str]) -> str:
    """Determines the correct credential for the selected provider."""
    if explicit_key:
        return explicit_key

    alias = provider_alias.lower()
    match alias:
        case "ollama":
            return getattr(settings, "OLLAMA_API_KEY", alias)
        case "gemini":
            return getattr(settings, "GEMINI_API_KEY", "")
        case "openai":
            return getattr(settings, "OPENAI_API_KEY", "")
        case _:
            raise ValueError(f"Invalid provider alias: {provider_alias}")


class LLMProvider(ABC):
    """Base class for LLM providers."""
    
    @abstractmethod
    def generate(self, messages: List[Dict[str, str]], **kwargs) -> str:
        """Generate text from messages."""
        pass


class Provider(LLMProvider):
    """
    OpenAI-compatible LLM provider.
    Supports Ollama, OpenAI, Gemini, and other OpenAI-compatible APIs.
    """

    def __init__(
        self, 
        model_name: str, 
        provider_alias: str = "openai",  
        api_key: Optional[str] = None, 
        base_url: Optional[str] = None
    ):
        """
        Initialize remote LLM provider.
        
        Args:
            model_name: Model identifier
            provider_alias: Provider name (ollama, openai, gemini)
            api_key: API key (auto-resolved if None)
            base_url: Custom base URL (overrides provider_alias)
        """
        normalized_alias = provider_alias.lower()
        self.target_url = base_url if base_url else URLS.get(normalized_alias, URLS["openai"])
        self.api_key = resolve_api_key(normalized_alias, api_key)
        self.client = OpenAI(api_key=self.api_key, base_url=self.target_url)
        self.model_name = model_name
        logger.info(f"Provider configured: model={model_name}, alias={provider_alias}, endpoint={self.target_url}")

    def generate(self, messages: List[Dict[str, str]], **kwargs) -> str:
        """
        Generate text completion.
        
        Args:
            messages: Chat messages
            **kwargs: max_new_tokens, temperature, top_p, etc.
            
        Returns:
            Generated text
        """
        max_tokens = kwargs.pop("max_new_tokens", 1024)
        temperature = kwargs.pop("temperature", 0.7) 
        top_p = kwargs.pop("top_p", 1.0)

        try:
            logger.debug(f"Generating: model={self.model_name}, max_tokens={max_tokens}, temp={temperature}")
            response = self.client.chat.completions.create(
                model=self.model_name,
                messages=messages,
                max_tokens=max_tokens,
                temperature=temperature,
                top_p=top_p,
                stream=False,
            )
            return response.choices[0].message.content
        except Exception as e:
            logger.error(f"Provider error ({self.target_url}): {e}")
            raise

    def generate_structured(
        self, 
        messages: List[Dict[str, str]], 
        response_format: Any, 
        **kwargs
    ) -> Any:
        """
        Generate structured output following a Pydantic schema.
        
        Args:
            messages: Chat messages
            response_format: Pydantic model class
            **kwargs: Generation parameters
            
        Returns:
            Parsed Pydantic object or raw content
        """
        max_tokens = kwargs.pop("max_new_tokens", 8192)
        temperature = kwargs.pop("temperature", 0.0)
        top_p = kwargs.pop("top_p", 1.0)

        try:
            logger.debug(f"Structured generation: model={self.model_name}, format={response_format.__name__}")
            
            completion = self.client.beta.chat.completions.parse(
                model=self.model_name,
                messages=messages,
                max_tokens=max_tokens,
                temperature=temperature,
                top_p=top_p,
                response_format=response_format,
                **kwargs,
            )

            message = completion.choices[0].message
            parsed = getattr(message, "parsed", None)
            if parsed is not None:
                logger.debug("Structured generation completed (parsed object)")
                return parsed

            logger.debug("Structured generation completed (raw content)")
            return message.content
        except Exception as e:
            logger.error(f"Structured provider error ({self.target_url}): {e}")
            raise

    def generate_stream(self, messages: List[Dict[str, str]], **kwargs):
        """
        Generate text with streaming.
        
        Args:
            messages: Chat messages
            **kwargs: Generation parameters
            
        Yields:
            Text chunks as they arrive
        """
        max_tokens = kwargs.pop("max_new_tokens", 1024)
        temperature = kwargs.pop("temperature", 0.7)
        top_p = kwargs.pop("top_p", 1.0)

        try:
            logger.debug(f"Streaming generation: model={self.model_name}")
            stream = self.client.chat.completions.create(
                model=self.model_name,
                messages=messages,
                max_tokens=max_tokens,
                temperature=temperature,
                top_p=top_p,
                stream=True,
            )
            
            for chunk in stream:
                if chunk.choices[0].delta.content:
                    yield chunk.choices[0].delta.content
                    
        except Exception as e:
            logger.error(f"Streaming error ({self.target_url}): {e}")
            raise


class HFProvider(LLMProvider):
    """Local HuggingFace model provider."""

    def __init__(self, model, tokenizer):
        """
        Initialize with loaded model and tokenizer.
        
        Args:
            model: HuggingFace model
            tokenizer: HuggingFace tokenizer
        """
        self.model = model
        self.model.eval()
        self.tokenizer = tokenizer
        if getattr(self.model, "generation_config", None):
            self.model.generation_config.temperature = None
        logger.info("HFProvider ready")

    def generate(self, messages: List[Dict[str, str]], **kwargs) -> str:
        """
        Generate text using local model.
        
        Args:
            messages: Chat messages
            **kwargs: Generation parameters
            
        Returns:
            Generated text
        """
        gen_params = {
            "max_new_tokens": 1024,
            "top_p": 1.0,
            "do_sample": False,
            "repetition_penalty": 1.0
        }
        
        ignored_temp = kwargs.pop("temperature", None)
        if ignored_temp is not None:
            logger.debug("Temperature ignored for HFProvider")

        gen_params.update(kwargs)

        try:
            input_ids = self.tokenizer.apply_chat_template(
                messages, 
                tokenize=True, 
                add_generation_prompt=True, 
                return_tensors="pt"
            ).to(self.model.device)
            
            attention_mask = (input_ids != self.tokenizer.pad_token_id).long()
        except Exception as e:
            logger.error(f"Chat template error: {e}")
            raise

        with torch.no_grad():
            outputs = self.model.generate(
                input_ids, 
                attention_mask=attention_mask,
                **gen_params,
                pad_token_id=self.tokenizer.pad_token_id
            )

        generated_ids = outputs[0][input_ids.shape[1]:]
        response = self.tokenizer.decode(generated_ids, skip_special_tokens=True)
        logger.debug("HFProvider generation completed")
        return response


class EmbeddingProvider(ABC):
    """Base class for embedding providers."""
    
    @abstractmethod
    def embed(self, inputs: List[str], **kwargs) -> List[List[float]]:
        """Generate embeddings for texts."""
        pass


class HFEmbeddingProvider(EmbeddingProvider):
    """Local HuggingFace embedding provider."""

    def __init__(self, model, tokenizer):
        """
        Initialize with loaded model and tokenizer.
        
        Args:
            model: HuggingFace model
            tokenizer: HuggingFace tokenizer
        """
        self.model = model
        self.model.eval()
        self.tokenizer = tokenizer
        logger.info("HFEmbeddingProvider ready")

    def embed(self, inputs: List[str], **kwargs) -> List[List[float]]:
        """
        Generate embeddings using local model.
        
        Args:
            inputs: List of texts
            **kwargs: max_length, etc.
            
        Returns:
            List of embedding vectors
        """
        max_length = kwargs.get("max_length", 512)
        
        try:
            encoded = self.tokenizer(
                inputs, 
                padding=True, 
                truncation=True, 
                max_length=max_length, 
                return_tensors='pt'
            ).to(self.model.device)
            
            with torch.no_grad():
                output = self.model(**encoded)

            embeddings = self._mean_pooling(output, encoded['attention_mask'])
            embeddings = torch.nn.functional.normalize(embeddings, p=2, dim=1)
            
            return embeddings.tolist()

        except Exception as e:
            logger.error(f"Embedding error: {e}")
            raise

    def _mean_pooling(self, model_output, attention_mask):
        """Apply mean pooling with attention mask."""
        token_embeddings = model_output[0]
        input_mask_expanded = attention_mask.unsqueeze(-1).expand(token_embeddings.size()).float()
        return torch.sum(token_embeddings * input_mask_expanded, 1) / torch.clamp(
            input_mask_expanded.sum(1), min=1e-9
        )


class RemoteEmbeddingProvider(EmbeddingProvider):
    """Remote embedding provider (OpenAI-compatible)."""

    def __init__(
        self, 
        model_name: str, 
        provider_alias: str = "openai",  
        api_key: Optional[str] = None, 
        base_url: Optional[str] = None
    ):
        """
        Initialize remote embedding provider.
        
        Args:
            model_name: Model identifier
            provider_alias: Provider name
            api_key: API key
            base_url: Custom base URL
        """
        normalized_alias = provider_alias.lower()
        self.target_url = base_url if base_url else URLS.get(normalized_alias, URLS["openai"])
        self.api_key = resolve_api_key(normalized_alias, api_key)
        self.client = OpenAI(api_key=self.api_key, base_url=self.target_url)
        self.model_name = model_name
        logger.info(f"RemoteEmbeddingProvider: model={model_name}, endpoint={self.target_url}")

    def embed(self, inputs: List[str], **kwargs) -> List[List[float]]:
        """
        Generate embeddings via API.
        
        Args:
            inputs: List of texts
            **kwargs: Additional parameters
            
        Returns:
            List of embedding vectors
        """
        try:
            logger.debug(f"Remote embedding: model={self.model_name}, batch={len(inputs)}")
            response = self.client.embeddings.create(
                input=inputs,
                model=self.model_name,
                **kwargs
            )
            
            data = sorted(response.data, key=lambda x: x.index)
            embeddings = [item.embedding for item in data]
            
            logger.debug("Remote embedding completed")
            return embeddings

        except Exception as e:
            logger.error(f"Remote embedding error ({self.target_url}): {e}")
            raise


class RerankProvider(ABC):
    """Base class for reranking providers."""
    
    @abstractmethod
    def rerank(self, query: str, documents: List[str], **kwargs) -> List[float]:
        """Rerank documents by relevance to query."""
        pass


class HFRerankProvider(RerankProvider):
    """Local HuggingFace cross-encoder reranker."""

    def __init__(self, model, tokenizer):
        """
        Initialize with loaded model and tokenizer.
        
        Args:
            model: Cross-encoder model
            tokenizer: Tokenizer
        """
        self.model = model
        self.model.eval()
        self.tokenizer = tokenizer

        if self.tokenizer.pad_token is None:
            if self.tokenizer.eos_token is not None:
                self.tokenizer.pad_token = self.tokenizer.eos_token
            else:
                logger.warning("Rerank tokenizer has no pad_token")

        if getattr(self.model, "config", None) and getattr(self.model.config, "pad_token_id", None) is None:
            if self.tokenizer.pad_token_id is not None:
                self.model.config.pad_token_id = self.tokenizer.pad_token_id

        logger.info("HFRerankProvider ready")

    def rerank(self, query: str, documents: List[str], **kwargs) -> List[float]:
        """
        Rerank documents using cross-encoder.
        
        Args:
            query: Search query
            documents: List of documents
            **kwargs: max_length, batch_size
            
        Returns:
            List of relevance scores
        """
        if not documents:
            return []

        pairs = [[query, doc] for doc in documents]
        max_length = kwargs.get("max_length", 1024)
        batch_size = kwargs.get("batch_size", 8)
        all_scores = []

        try:
            for i in range(0, len(pairs), batch_size):
                batch_pairs = pairs[i : i + batch_size]
                
                inputs = self.tokenizer(
                    batch_pairs,
                    padding=True,
                    truncation=True,
                    max_length=max_length,
                    return_tensors="pt"
                ).to(self.model.device)

                with torch.no_grad():
                    outputs = self.model(**inputs)
                
                logits = outputs.logits
                if logits.dim() == 1:
                    scores = logits
                elif logits.shape[1] == 1:
                    scores = logits.squeeze(-1)
                else:
                    scores = logits[:, -1]

                all_scores.extend(scores.float().cpu().tolist())

            return all_scores

        except Exception as e:
            logger.error(f"Rerank error: {e}")
            raise
