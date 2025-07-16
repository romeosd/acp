"""
MCP (Model Context Protocol) data models for IBM ACP Agent.
"""

from typing import List, Optional, Dict, Any, Union
from pydantic import BaseModel, Field
from datetime import datetime


class MCPRequest(BaseModel):
    """MCP request model."""
    
    id: str = Field(..., description="Unique request identifier")
    method: str = Field(..., description="MCP method to call")
    params: Optional[Dict[str, Any]] = Field(None, description="Method parameters")
    timestamp: datetime = Field(default_factory=datetime.now, description="Request timestamp")
    
    class Config:
        json_schema_extra = {
            "example": {
                "id": "req_123",
                "method": "text/generate",
                "params": {
                    "prompt": "Summarize this document",
                    "max_tokens": 500
                }
            }
        }


class MCPResponse(BaseModel):
    """MCP response model."""
    
    id: str = Field(..., description="Request identifier")
    result: Optional[Dict[str, Any]] = Field(None, description="Response result")
    error: Optional[Dict[str, Any]] = Field(None, description="Error information")
    timestamp: datetime = Field(default_factory=datetime.now, description="Response timestamp")
    
    class Config:
        json_schema_extra = {
            "example": {
                "id": "req_123",
                "result": {
                    "text": "This is the generated text...",
                    "usage": {"prompt_tokens": 100, "completion_tokens": 200}
                }
            }
        }


class MCPError(BaseModel):
    """MCP error model."""
    
    code: int = Field(..., description="Error code")
    message: str = Field(..., description="Error message")
    data: Optional[Dict[str, Any]] = Field(None, description="Additional error data")
    
    class Config:
        json_schema_extra = {
            "example": {
                "code": 400,
                "message": "Invalid request parameters",
                "data": {"param": "prompt", "issue": "missing"}
            }
        }


class MCPNotification(BaseModel):
    """MCP notification model."""
    
    method: str = Field(..., description="Notification method")
    params: Optional[Dict[str, Any]] = Field(None, description="Notification parameters")
    timestamp: datetime = Field(default_factory=datetime.now, description="Notification timestamp")
    
    class Config:
        json_schema_extra = {
            "example": {
                "method": "text/generation/complete",
                "params": {"request_id": "req_123", "status": "completed"}
            }
        }


class MCPMessage(BaseModel):
    """Generic MCP message model."""
    
    type: str = Field(..., description="Message type (request, response, notification)")
    data: Union[MCPRequest, MCPResponse, MCPNotification] = Field(..., description="Message data")
    
    class Config:
        json_schema_extra = {
            "example": {
                "type": "request",
                "data": {
                    "id": "req_123",
                    "method": "text/generate",
                    "params": {"prompt": "Hello world"}
                }
            }
        } 