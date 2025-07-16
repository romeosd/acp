"""
Watsonx.ai client for IBM ACP Agent.
"""

import json
import logging
from typing import Optional, Dict, Any
import httpx
from .models import WatsonxRequest, WatsonxResponse, WatsonxError
from ..config import config_manager


logger = logging.getLogger(__name__)


class WatsonxClient:
    """Client for interacting with IBM Watsonx.ai API."""
    
    def __init__(self, api_key: Optional[str] = None, project_id: Optional[str] = None):
        """Initialize Watsonx client."""
        config = config_manager.get_config()
        self.api_key = api_key or config.watsonx.api_key
        self.project_id = project_id or config.watsonx.project_id
        self.endpoint = config.watsonx.endpoint
        self.model = config.watsonx.model
        self.max_tokens = config.watsonx.max_tokens
        self.temperature = config.watsonx.temperature
        
        if not self.api_key:
            raise ValueError("Watsonx API key is required")
        if not self.project_id:
            raise ValueError("Watsonx project ID is required")
        
        self.base_url = f"{self.endpoint}/ml/v1/text/generation"
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "Accept": "application/json"
        }
    
    async def generate_text(self, request: WatsonxRequest) -> WatsonxResponse:
        """Generate text using Watsonx.ai API."""
        try:
            # Prepare request payload
            payload = {
                "model_id": request.model or self.model,
                "input": request.prompt,
                "parameters": {
                    "max_new_tokens": request.max_tokens or self.max_tokens,
                    "temperature": request.temperature or self.temperature,
                    "top_p": request.top_p or 1.0,
                    "stream": request.stream or False
                }
            }
            
            if request.stop_sequences:
                payload["parameters"]["stop_sequences"] = request.stop_sequences
            
            # Add project ID
            params = {"version": "2024-01-01"}
            
            logger.info(f"Sending request to Watsonx.ai: {self.base_url}")
            
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    self.base_url,
                    headers=self.headers,
                    params=params,
                    json=payload
                )
                
                if response.status_code == 200:
                    data = response.json()
                    return self._parse_response(data, request.model or self.model)
                else:
                    error_data = response.json() if response.content else {}
                    raise WatsonxError(
                        error=f"Watsonx.ai API error: {response.status_code}",
                        code=str(response.status_code),
                        details=error_data
                    )
        
        except httpx.RequestError as e:
            logger.error(f"Request error: {e}")
            raise WatsonxError(error=f"Network error: {str(e)}")
        except Exception as e:
            logger.error(f"Unexpected error: {e}")
            raise WatsonxError(error=f"Unexpected error: {str(e)}")
    
    def _parse_response(self, data: Dict[str, Any], model: str) -> WatsonxResponse:
        """Parse Watsonx.ai API response."""
        try:
            results = data.get("results", [])
            if not results:
                raise WatsonxError(error="No results in response")
            
            result = results[0]
            generated_text = result.get("generated_text", "")
            
            # Extract usage information if available
            usage = None
            if "usage" in data:
                usage = {
                    "prompt_tokens": data["usage"].get("prompt_tokens", 0),
                    "completion_tokens": data["usage"].get("completion_tokens", 0),
                    "total_tokens": data["usage"].get("total_tokens", 0)
                }
            
            return WatsonxResponse(
                text=generated_text,
                model=model,
                usage=usage,
                finish_reason=result.get("finish_reason"),
                metadata={"raw_response": data}
            )
        
        except Exception as e:
            logger.error(f"Error parsing response: {e}")
            raise WatsonxError(error=f"Error parsing response: {str(e)}")
    
    async def summarize_text(self, text: str, max_length: int = 500) -> str:
        """Summarize text using Watsonx.ai."""
        prompt = f"""Please provide a concise summary of the following text in approximately {max_length} characters:

{text}

Summary:"""
        
        request = WatsonxRequest(
            prompt=prompt,
            max_tokens=max_length // 4,  # Rough estimate
            temperature=0.3  # Lower temperature for more focused summaries
        )
        
        response = await self.generate_text(request)
        return response.text
    
    async def answer_question(self, context: str, question: str) -> str:
        """Answer a question based on the given context."""
        prompt = f"""Based on the following context, please answer the question:

Context:
{context}

Question: {question}

Answer:"""
        
        request = WatsonxRequest(
            prompt=prompt,
            max_tokens=1000,
            temperature=0.5
        )
        
        response = await self.generate_text(request)
        return response.text
    
    async def extract_key_points(self, text: str) -> str:
        """Extract key points from text."""
        prompt = f"""Please extract the key points from the following text:

{text}

Key Points:
1."""
        
        request = WatsonxRequest(
            prompt=prompt,
            max_tokens=800,
            temperature=0.4
        )
        
        response = await self.generate_text(request)
        return response.text 