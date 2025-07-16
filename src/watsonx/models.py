"""
Watsonx.ai data models for IBM ACP Agent.
"""

from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field


class WatsonxRequest(BaseModel):
    """Request model for Watsonx.ai API calls."""
    
    prompt: str = Field(..., description="The input prompt for the model")
    model: Optional[str] = Field(None, description="Model to use for generation")
    max_tokens: Optional[int] = Field(2048, description="Maximum tokens to generate")
    temperature: Optional[float] = Field(0.7, description="Temperature for generation")
    top_p: Optional[float] = Field(1.0, description="Top-p sampling parameter")
    stop_sequences: Optional[List[str]] = Field(None, description="Stop sequences")
    stream: Optional[bool] = Field(False, description="Whether to stream the response")
    
    class Config:
        json_schema_extra = {
            "example": {
                "prompt": "Summarize the following document:",
                "model": "ibm-granite/granite-13b-chat-v2",
                "max_tokens": 500,
                "temperature": 0.7
            }
        }


class WatsonxResponse(BaseModel):
    """Response model for Watsonx.ai API calls."""
    
    text: str = Field(..., description="Generated text response")
    model: str = Field(..., description="Model used for generation")
    usage: Optional[Dict[str, int]] = Field(None, description="Token usage information")
    finish_reason: Optional[str] = Field(None, description="Reason for completion")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Additional metadata")
    
    class Config:
        json_schema_extra = {
            "example": {
                "text": "This is a summary of the document...",
                "model": "ibm-granite/granite-13b-chat-v2",
                "usage": {"prompt_tokens": 100, "completion_tokens": 200},
                "finish_reason": "stop"
            }
        }


class WatsonxError(BaseModel):
    """Error model for Watsonx.ai API errors."""
    
    error: str = Field(..., description="Error message")
    code: Optional[str] = Field(None, description="Error code")
    details: Optional[Dict[str, Any]] = Field(None, description="Additional error details")
    
    class Config:
        json_schema_extra = {
            "example": {
                "error": "Invalid API key",
                "code": "AUTH_ERROR",
                "details": {"api_key": "invalid"}
            }
        } 