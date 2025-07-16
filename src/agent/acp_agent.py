"""
Main ACP Agent implementation for IBM ACP Agent.
"""

import asyncio
import time
import logging
import uuid
from typing import Dict, Any, Optional
from fastapi import FastAPI, HTTPException, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

from .models import ACPRequest, ACPResponse, AgentStatus, TaskType, ProcessingTask
from ..pdf_processor import PDFProcessor
from ..watsonx import WatsonxClient
from ..mcp import MCPServer
from ..config import config_manager


logger = logging.getLogger(__name__)


class ACPAgent:
    """Main ACP Agent implementation."""
    
    def __init__(self):
        """Initialize ACP Agent."""
        self.config = config_manager.get_config()
        self.app = FastAPI(title="IBM ACP Agent", version="1.0.0")
        self.pdf_processor = PDFProcessor()
        self.watsonx_client = WatsonxClient()
        self.mcp_server = MCPServer()
        
        # Agent state
        self.start_time = time.time()
        self.total_requests = 0
        self.successful_requests = 0
        self.failed_requests = 0
        self.active_tasks: Dict[str, ProcessingTask] = {}
        
        self._setup_routes()
        self._setup_middleware()
    
    def _setup_middleware(self):
        """Setup CORS middleware."""
        self.app.add_middleware(
            CORSMiddleware,
            allow_origins=self.config.security.allowed_origins,
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )
    
    def _setup_routes(self):
        """Setup API routes."""
        
        @self.app.post("/acp/process")
        async def process_document(request: ACPRequest):
            """Process a document using ACP protocol."""
            return await self._handle_acp_request(request)
        
        @self.app.post("/acp/upload")
        async def upload_and_process(
            file: UploadFile = File(...),
            task: str = "summarize",
            parameters: Optional[str] = None
        ):
            """Upload and process a PDF document."""
            return await self._handle_file_upload(file, task, parameters)
        
        @self.app.get("/acp/status")
        async def get_status():
            """Get agent status."""
            return self._get_status()
        
        @self.app.get("/acp/tasks/{task_id}")
        async def get_task_status(task_id: str):
            """Get task status."""
            if task_id not in self.active_tasks:
                raise HTTPException(status_code=404, detail="Task not found")
            return self.active_tasks[task_id]
        
        @self.app.get("/acp/health")
        async def health_check():
            """Health check endpoint."""
            return {"status": "healthy", "service": "acp-agent"}
    
    async def _handle_acp_request(self, request: ACPRequest) -> ACPResponse:
        """Handle ACP protocol request."""
        start_time = time.time()
        self.total_requests += 1
        
        try:
            logger.info(f"Processing ACP request: {request.request_id} - {request.task}")
            
            # Validate document path
            if not self.pdf_processor.validate_file(request.document_path):
                raise ValueError(f"Invalid or unsupported file: {request.document_path}")
            
            # Process PDF
            pdf_result = self.pdf_processor.process_document(request.document_path)
            if not pdf_result.success:
                raise ValueError(f"PDF processing failed: {pdf_result.error}")
            
            # Perform task using Watsonx.ai
            task_result = await self._perform_task(request.task, pdf_result, request.parameters)
            
            processing_time = time.time() - start_time
            self.successful_requests += 1
            
            logger.info(f"Successfully processed request {request.request_id} in {processing_time:.2f}s")
            
            return ACPResponse(
                request_id=request.request_id,
                success=True,
                result=task_result,
                processing_time=processing_time
            )
        
        except Exception as e:
            processing_time = time.time() - start_time
            self.failed_requests += 1
            
            logger.error(f"Error processing request {request.request_id}: {e}")
            
            return ACPResponse(
                request_id=request.request_id,
                success=False,
                error=str(e),
                processing_time=processing_time
            )
    
    async def _handle_file_upload(self, file: UploadFile, task: str, parameters: Optional[str]) -> Dict[str, Any]:
        """Handle file upload and processing."""
        import json
        import os
        
        # Validate file
        if not file.filename.lower().endswith('.pdf'):
            raise HTTPException(status_code=400, detail="Only PDF files are supported")
        
        # Save uploaded file
        temp_dir = self.config.pdf.temp_directory
        os.makedirs(temp_dir, exist_ok=True)
        file_path = os.path.join(temp_dir, file.filename)
        
        with open(file_path, "wb") as buffer:
            content = await file.read()
            buffer.write(content)
        
        # Parse parameters
        task_params = {}
        if parameters:
            try:
                task_params = json.loads(parameters)
            except json.JSONDecodeError:
                raise HTTPException(status_code=400, detail="Invalid parameters JSON")
        
        # Create ACP request
        request = ACPRequest(
            request_id=str(uuid.uuid4()),
            task=TaskType(task),
            document_path=file_path,
            parameters=task_params,
            source="file_upload"
        )
        
        # Process request
        response = await self._handle_acp_request(request)
        
        # Clean up temporary file
        try:
            os.remove(file_path)
        except:
            pass
        
        return response.dict()
    
    async def _perform_task(self, task: TaskType, pdf_result, parameters: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        """Perform the specified task using Watsonx.ai."""
        document = pdf_result.document
        chunks = pdf_result.chunks
        
        if task == TaskType.SUMMARIZE:
            # Combine chunks for summarization
            full_text = document.text_content
            max_length = parameters.get("max_length", 500) if parameters else 500
            
            summary = await self.watsonx_client.summarize_text(full_text, max_length)
            
            return {
                "summary": summary,
                "document_info": {
                    "file_name": document.file_name,
                    "page_count": document.page_count,
                    "file_size": document.file_size,
                    "original_length": len(full_text),
                    "summary_length": len(summary)
                }
            }
        
        elif task == TaskType.QUESTION_ANSWER:
            question = parameters.get("question") if parameters else "What is this document about?"
            
            # Use the full document as context
            answer = await self.watsonx_client.answer_question(document.text_content, question)
            
            return {
                "answer": answer,
                "question": question,
                "document_info": {
                    "file_name": document.file_name,
                    "page_count": document.page_count
                }
            }
        
        elif task == TaskType.EXTRACT:
            extraction_type = parameters.get("extraction_type", "key_points") if parameters else "key_points"
            
            if extraction_type == "key_points":
                key_points = await self.watsonx_client.extract_key_points(document.text_content)
                
                return {
                    "key_points": key_points,
                    "extraction_type": extraction_type,
                    "document_info": {
                        "file_name": document.file_name,
                        "page_count": document.page_count
                    }
                }
            else:
                raise ValueError(f"Unsupported extraction type: {extraction_type}")
        
        elif task == TaskType.ANALYZE:
            # Perform comprehensive analysis
            analysis_prompt = f"""Please provide a comprehensive analysis of the following document:

Document: {document.text_content}

Please include:
1. Main topics and themes
2. Key findings or conclusions
3. Document structure and organization
4. Any notable insights or observations

Analysis:"""
            
            from ..watsonx.models import WatsonxRequest
            request = WatsonxRequest(
                prompt=analysis_prompt,
                max_tokens=1500,
                temperature=0.3
            )
            
            response = await self.watsonx_client.generate_text(request)
            
            return {
                "analysis": response.text,
                "document_info": {
                    "file_name": document.file_name,
                    "page_count": document.page_count,
                    "file_size": document.file_size
                }
            }
        
        else:
            raise ValueError(f"Unsupported task type: {task}")
    
    def _get_status(self) -> AgentStatus:
        """Get current agent status."""
        uptime = time.time() - self.start_time
        
        return AgentStatus(
            status="running",
            uptime=uptime,
            total_requests=self.total_requests,
            successful_requests=self.successful_requests,
            failed_requests=self.failed_requests,
            watsonx_status="connected",  # TODO: Add actual health check
            mcp_status="running"  # TODO: Add actual health check
        )
    
    async def start(self):
        """Start the ACP agent."""
        config = uvicorn.Config(
            self.app,
            host=self.config.acp.host,
            port=self.config.acp.port,
            log_level="info"
        )
        server = uvicorn.Server(config)
        await server.serve()
    
    def run(self):
        """Run the ACP agent synchronously."""
        uvicorn.run(
            self.app,
            host=self.config.acp.host,
            port=self.config.acp.port,
            log_level="info"
        ) 