"""
ACP (Agent Communication Protocol) data models for IBM ACP Agent.
"""

from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
from datetime import datetime
from enum import Enum


class TaskType(str, Enum):
    """Supported task types."""
    SUMMARIZE = "summarize"
    QUESTION_ANSWER = "question_answer"
    EXTRACT = "extract"
    ANALYZE = "analyze"


class ACPRequest(BaseModel):
    """ACP request model."""
    
    request_id: str = Field(..., description="Unique request identifier")
    task: TaskType = Field(..., description="Task to perform")
    document_path: str = Field(..., description="Path to the document")
    parameters: Optional[Dict[str, Any]] = Field(None, description="Task-specific parameters")
    source: Optional[str] = Field(None, description="Request source (e.g., Microsoft Copilot)")
    timestamp: datetime = Field(default_factory=datetime.now, description="Request timestamp")
    
    class Config:
        json_schema_extra = {
            "example": {
                "request_id": "req_123",
                "task": "summarize",
                "document_path": "/path/to/document.pdf",
                "parameters": {"max_length": 500},
                "source": "Microsoft Copilot"
            }
        }


class ACPResponse(BaseModel):
    """ACP response model."""
    
    request_id: str = Field(..., description="Request identifier")
    success: bool = Field(..., description="Whether the request was successful")
    result: Optional[Dict[str, Any]] = Field(None, description="Task result")
    error: Optional[str] = Field(None, description="Error message if failed")
    processing_time: float = Field(..., description="Processing time in seconds")
    timestamp: datetime = Field(default_factory=datetime.now, description="Response timestamp")
    
    class Config:
        json_schema_extra = {
            "example": {
                "request_id": "req_123",
                "success": True,
                "result": {
                    "summary": "This is a summary of the document...",
                    "document_info": {
                        "file_name": "document.pdf",
                        "page_count": 10
                    }
                },
                "processing_time": 2.5
            }
        }


class AgentStatus(BaseModel):
    """Agent status model."""
    
    status: str = Field(..., description="Agent status")
    uptime: float = Field(..., description="Agent uptime in seconds")
    total_requests: int = Field(..., description="Total requests processed")
    successful_requests: int = Field(..., description="Successful requests")
    failed_requests: int = Field(..., description="Failed requests")
    watsonx_status: str = Field(..., description="Watsonx.ai connection status")
    mcp_status: str = Field(..., description="MCP server status")
    timestamp: datetime = Field(default_factory=datetime.now, description="Status timestamp")
    
    class Config:
        json_schema_extra = {
            "example": {
                "status": "running",
                "uptime": 3600.5,
                "total_requests": 100,
                "successful_requests": 95,
                "failed_requests": 5,
                "watsonx_status": "connected",
                "mcp_status": "running"
            }
        }


class ProcessingTask(BaseModel):
    """Processing task model."""
    
    task_id: str = Field(..., description="Task identifier")
    request: ACPRequest = Field(..., description="Original request")
    status: str = Field(..., description="Task status")
    progress: float = Field(0.0, description="Task progress (0-100)")
    result: Optional[Dict[str, Any]] = Field(None, description="Task result")
    error: Optional[str] = Field(None, description="Error message")
    created_at: datetime = Field(default_factory=datetime.now, description="Task creation time")
    completed_at: Optional[datetime] = Field(None, description="Task completion time")
    
    class Config:
        json_schema_extra = {
            "example": {
                "task_id": "task_123",
                "status": "completed",
                "progress": 100.0,
                "created_at": "2024-01-01T12:00:00Z",
                "completed_at": "2024-01-01T12:02:30Z"
            }
        } 