"""
PDF processing data models for IBM ACP Agent.
"""

from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
from datetime import datetime


class PDFDocument(BaseModel):
    """PDF document model."""
    
    file_path: str = Field(..., description="Path to the PDF file")
    file_name: str = Field(..., description="Name of the PDF file")
    file_size: int = Field(..., description="Size of the file in bytes")
    page_count: int = Field(..., description="Number of pages in the PDF")
    text_content: str = Field(..., description="Extracted text content")
    metadata: Optional[Dict[str, Any]] = Field(None, description="PDF metadata")
    processed_at: datetime = Field(default_factory=datetime.now, description="Processing timestamp")
    
    class Config:
        json_schema_extra = {
            "example": {
                "file_path": "/path/to/document.pdf",
                "file_name": "document.pdf",
                "file_size": 1024000,
                "page_count": 10,
                "text_content": "This is the extracted text...",
                "metadata": {"title": "Sample Document", "author": "John Doe"}
            }
        }


class ProcessingResult(BaseModel):
    """Result of PDF processing operation."""
    
    success: bool = Field(..., description="Whether processing was successful")
    document: Optional[PDFDocument] = Field(None, description="Processed document")
    error: Optional[str] = Field(None, description="Error message if processing failed")
    processing_time: float = Field(..., description="Processing time in seconds")
    chunks: Optional[List[str]] = Field(None, description="Text chunks for processing")
    
    class Config:
        json_schema_extra = {
            "example": {
                "success": True,
                "processing_time": 2.5,
                "chunks": ["Chunk 1 text...", "Chunk 2 text..."]
            }
        }


class ProcessingTask(BaseModel):
    """Task for PDF processing."""
    
    task_type: str = Field(..., description="Type of processing task")
    document_path: str = Field(..., description="Path to the document")
    parameters: Optional[Dict[str, Any]] = Field(None, description="Task-specific parameters")
    
    class Config:
        json_schema_extra = {
            "example": {
                "task_type": "summarize",
                "document_path": "/path/to/document.pdf",
                "parameters": {"max_length": 500}
            }
        } 