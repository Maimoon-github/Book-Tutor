from typing import Any, List, Mapping, Optional, Dict
from langchain.llms.base import LLM
from langchain.callbacks.manager import CallbackManagerForLLMRun
import requests
import json
import os

class OllamaLLM(LLM):
    """
    LangChain integration for Ollama local models.
    
    This class provides an interface to use local Ollama models
    with the LangChain framework.
    """
    
    # Model configuration
    model_name: str = "deepseek-r1:1.5b"
    base_url: str = "http://localhost:11434"
    temperature: float = 0.7
    top_p: float = 0.9
    max_tokens: int = 2048
    
    @property
    def _llm_type(self) -> str:
        """Return the type of LLM."""
        return "ollama"

    @property
    def _identifying_params(self) -> Mapping[str, Any]:
        """Get the identifying parameters."""
        return {
            "model_name": self.model_name,
            "temperature": self.temperature,
            "top_p": self.top_p,
            "max_tokens": self.max_tokens,
        }
        
    def _call(
        self, 
        prompt: str, 
        stop: Optional[List[str]] = None,
        run_manager: Optional[CallbackManagerForLLMRun] = None,
        **kwargs: Any,
    ) -> str:
        """
        Call the Ollama API to generate text.
        
        Args:
            prompt: The prompt to send to the model
            stop: Optional list of stop sequences
            run_manager: Optional callback manager
            
        Returns:
            The generated text
        """
        headers = {"Content-Type": "application/json"}
        
        # Prepare the request body
        data = {
            "model": self.model_name,
            "prompt": prompt,
            "stream": False,
            "options": {
                "temperature": self.temperature,
                "top_p": self.top_p,
                "num_predict": self.max_tokens,
            }
        }
        
        # Add stop sequences if provided
        if stop:
            data["options"]["stop"] = stop
            
        # Additional parameters from kwargs
        if "system_prompt" in kwargs:
            data["system"] = kwargs["system_prompt"]
            
        # Make the API call to the local Ollama server
        try:
            response = requests.post(
                f"{self.base_url}/api/generate",
                headers=headers,
                data=json.dumps(data),
                timeout=120
            )
            
            response.raise_for_status()
            response_data = response.json()
            
            # Extract the generated text
            return response_data.get("response", "")
            
        except requests.exceptions.RequestException as e:
            raise ValueError(f"Error calling Ollama API: {e}")
    
    @classmethod
    def from_env(cls) -> "OllamaLLM":
        """
        Create an OllamaLLM instance from environment variables.
        
        Returns:
            An initialized OllamaLLM instance
        """
        return cls(
            model_name=os.environ.get("OLLAMA_MODEL", "deepseek-r1:1.5b"),
            base_url=os.environ.get("OLLAMA_BASE_URL", "http://localhost:11434"),
            temperature=float(os.environ.get("TEMPERATURE", "0.7")),
            top_p=float(os.environ.get("TOP_P", "0.9")),
            max_tokens=int(os.environ.get("MAX_TOKENS", "2048")),
        )
