"""
PDF processing implementation for IBM ACP Agent.
"""

import os
import time
import logging
from typing import List, Optional, Dict, Any
import PyPDF2
import pdfplumber
from .models import PDFDocument, ProcessingResult, ProcessingTask
from ..config import config_manager


logger = logging.getLogger(__name__)


class PDFProcessor:
    """PDF document processor for IBM ACP Agent."""
    
    def __init__(self):
        """Initialize PDF processor."""
        self.config = config_manager.get_config().pdf
        self._ensure_temp_directory()
    
    def _ensure_temp_directory(self):
        """Ensure temporary directory exists."""
        os.makedirs(self.config.temp_directory, exist_ok=True)
    
    def process_document(self, file_path: str) -> ProcessingResult:
        """Process a PDF document and extract text content."""
        start_time = time.time()
        
        try:
            # Validate file
            if not os.path.exists(file_path):
                return ProcessingResult(
                    success=False,
                    error=f"File not found: {file_path}",
                    processing_time=time.time() - start_time
                )
            
            # Check file size
            file_size = os.path.getsize(file_path)
            if file_size > config_manager.get_config().acp.max_file_size:
                return ProcessingResult(
                    success=False,
                    error=f"File too large: {file_size} bytes",
                    processing_time=time.time() - start_time
                )
            
            # Extract text content
            text_content = self._extract_text(file_path)
            if not text_content.strip():
                return ProcessingResult(
                    success=False,
                    error="No text content found in PDF",
                    processing_time=time.time() - start_time
                )
            
            # Get metadata
            metadata = self._extract_metadata(file_path)
            
            # Create document object
            document = PDFDocument(
                file_path=file_path,
                file_name=os.path.basename(file_path),
                file_size=file_size,
                page_count=metadata.get("page_count", 0),
                text_content=text_content,
                metadata=metadata
            )
            
            # Create chunks for processing
            chunks = self._create_chunks(text_content)
            
            processing_time = time.time() - start_time
            
            logger.info(f"Successfully processed PDF: {file_path} ({processing_time:.2f}s)")
            
            return ProcessingResult(
                success=True,
                document=document,
                processing_time=processing_time,
                chunks=chunks
            )
        
        except Exception as e:
            logger.error(f"Error processing PDF {file_path}: {e}")
            return ProcessingResult(
                success=False,
                error=str(e),
                processing_time=time.time() - start_time
            )
    
    def _extract_text(self, file_path: str) -> str:
        """Extract text from PDF using multiple methods."""
        text_content = ""
        
        # Try pdfplumber first (better for complex layouts)
        try:
            with pdfplumber.open(file_path) as pdf:
                pages = []
                for page in pdf.pages[:self.config.max_pages]:  # Limit pages
                    page_text = page.extract_text()
                    if page_text:
                        pages.append(page_text)
                text_content = "\n".join(pages)
                
                if text_content.strip():
                    return text_content
        except Exception as e:
            logger.warning(f"pdfplumber failed for {file_path}: {e}")
        
        # Fallback to PyPDF2
        try:
            with open(file_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                pages = []
                for page_num in range(min(len(pdf_reader.pages), self.config.max_pages)):
                    page = pdf_reader.pages[page_num]
                    page_text = page.extract_text()
                    if page_text:
                        pages.append(page_text)
                text_content = "\n".join(pages)
        except Exception as e:
            logger.error(f"PyPDF2 failed for {file_path}: {e}")
            raise
        
        return text_content
    
    def _extract_metadata(self, file_path: str) -> Dict[str, Any]:
        """Extract metadata from PDF."""
        metadata = {}
        
        try:
            with open(file_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                
                metadata["page_count"] = len(pdf_reader.pages)
                
                if pdf_reader.metadata:
                    metadata.update({
                        "title": pdf_reader.metadata.get("/Title"),
                        "author": pdf_reader.metadata.get("/Author"),
                        "subject": pdf_reader.metadata.get("/Subject"),
                        "creator": pdf_reader.metadata.get("/Creator"),
                        "producer": pdf_reader.metadata.get("/Producer"),
                        "creation_date": pdf_reader.metadata.get("/CreationDate"),
                        "modification_date": pdf_reader.metadata.get("/ModDate")
                    })
        
        except Exception as e:
            logger.warning(f"Failed to extract metadata from {file_path}: {e}")
        
        return metadata
    
    def _create_chunks(self, text: str) -> List[str]:
        """Create text chunks for processing."""
        if not text:
            return []
        
        # Simple chunking by character count
        chunk_size = self.config.chunk_size
        chunks = []
        
        # Split by paragraphs first
        paragraphs = text.split('\n\n')
        
        current_chunk = ""
        for paragraph in paragraphs:
            if len(current_chunk) + len(paragraph) <= chunk_size:
                current_chunk += paragraph + "\n\n"
            else:
                if current_chunk:
                    chunks.append(current_chunk.strip())
                current_chunk = paragraph + "\n\n"
        
        # Add remaining chunk
        if current_chunk:
            chunks.append(current_chunk.strip())
        
        # If chunks are still too large, split by sentences
        final_chunks = []
        for chunk in chunks:
            if len(chunk) <= chunk_size:
                final_chunks.append(chunk)
            else:
                # Split by sentences
                sentences = chunk.split('. ')
                current_sentence_chunk = ""
                for sentence in sentences:
                    if len(current_sentence_chunk) + len(sentence) <= chunk_size:
                        current_sentence_chunk += sentence + ". "
                    else:
                        if current_sentence_chunk:
                            final_chunks.append(current_sentence_chunk.strip())
                        current_sentence_chunk = sentence + ". "
                
                if current_sentence_chunk:
                    final_chunks.append(current_sentence_chunk.strip())
        
        return final_chunks
    
    def validate_file(self, file_path: str) -> bool:
        """Validate if file is a supported PDF."""
        if not os.path.exists(file_path):
            return False
        
        # Check file extension
        if not file_path.lower().endswith('.pdf'):
            return False
        
        # Check file size
        file_size = os.path.getsize(file_path)
        if file_size > config_manager.get_config().acp.max_file_size:
            return False
        
        # Try to open with PyPDF2 to validate
        try:
            with open(file_path, 'rb') as file:
                PyPDF2.PdfReader(file)
            return True
        except Exception:
            return False 