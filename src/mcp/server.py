"""
MCP (Model Context Protocol) server implementation for IBM ACP Agent.
"""

import asyncio
import json
import logging
from typing import Dict, Any, Optional, Callable
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

from .models import MCPRequest, MCPResponse, MCPError, MCPNotification
from ..watsonx import WatsonxClient
from ..config import config_manager


logger = logging.getLogger(__name__)


class MCPServer:
    """MCP server for handling model context protocol requests."""
    
    def __init__(self):
        """Initialize MCP server."""
        self.config = config_manager.get_config().mcp
        self.app = FastAPI(title="IBM ACP MCP Server", version="1.0.0")
        self.watsonx_client = WatsonxClient()
        self._setup_routes()
        self._setup_middleware()
        self._setup_handlers()
    
    def _setup_middleware(self):
        """Setup CORS middleware."""
        self.app.add_middleware(
            CORSMiddleware,
            allow_origins=["*"],
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )
    
    def _setup_routes(self):
        """Setup API routes."""
        
        @self.app.post("/mcp/query")
        async def handle_mcp_query(request: MCPRequest):
            """Handle MCP query requests."""
            try:
                response = await self._process_request(request)
                return response
            except Exception as e:
                logger.error(f"Error processing MCP request: {e}")
                return MCPResponse(
                    id=request.id,
                    error=MCPError(
                        code=500,
                        message=str(e)
                    ).dict()
                )
        
        @self.app.get("/mcp/health")
        async def health_check():
            """Health check endpoint."""
            return {"status": "healthy", "service": "mcp-server"}
        
        @self.app.get("/mcp/capabilities")
        async def get_capabilities():
            """Get MCP server capabilities."""
            return {
                "methods": [
                    "text/generate",
                    "text/summarize",
                    "text/answer_question",
                    "text/extract_key_points"
                ],
                "models": ["ibm-granite/granite-13b-chat-v2"],
                "version": "1.0.0"
            }
    
    def _setup_handlers(self):
        """Setup MCP method handlers."""
        self.handlers = {
            "text/generate": self._handle_text_generate,
            "text/summarize": self._handle_text_summarize,
            "text/answer_question": self._handle_answer_question,
            "text/extract_key_points": self._handle_extract_key_points,
        }
    
    async def _process_request(self, request: MCPRequest) -> MCPResponse:
        """Process MCP request."""
        logger.info(f"Processing MCP request: {request.method}")
        
        if request.method not in self.handlers:
            return MCPResponse(
                id=request.id,
                error=MCPError(
                    code=400,
                    message=f"Unsupported method: {request.method}"
                ).dict()
            )
        
        try:
            handler = self.handlers[request.method]
            result = await handler(request.params or {})
            
            return MCPResponse(
                id=request.id,
                result=result
            )
        
        except Exception as e:
            logger.error(f"Error in method {request.method}: {e}")
            return MCPResponse(
                id=request.id,
                error=MCPError(
                    code=500,
                    message=str(e)
                ).dict()
            )
    
    async def _handle_text_generate(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle text generation requests."""
        from ..watsonx.models import WatsonxRequest
        
        prompt = params.get("prompt")
        if not prompt:
            raise ValueError("Prompt is required")
        
        request = WatsonxRequest(
            prompt=prompt,
            max_tokens=params.get("max_tokens", 2048),
            temperature=params.get("temperature", 0.7)
        )
        
        response = await self.watsonx_client.generate_text(request)
        
        return {
            "text": response.text,
            "model": response.model,
            "usage": response.usage,
            "finish_reason": response.finish_reason
        }
    
    async def _handle_text_summarize(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle text summarization requests."""
        text = params.get("text")
        if not text:
            raise ValueError("Text is required")
        
        max_length = params.get("max_length", 500)
        summary = await self.watsonx_client.summarize_text(text, max_length)
        
        return {
            "summary": summary,
            "original_length": len(text),
            "summary_length": len(summary)
        }
    
    async def _handle_answer_question(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle question answering requests."""
        context = params.get("context")
        question = params.get("question")
        
        if not context:
            raise ValueError("Context is required")
        if not question:
            raise ValueError("Question is required")
        
        answer = await self.watsonx_client.answer_question(context, question)
        
        return {
            "answer": answer,
            "question": question,
            "context_length": len(context)
        }
    
    async def _handle_extract_key_points(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle key points extraction requests."""
        text = params.get("text")
        if not text:
            raise ValueError("Text is required")
        
        key_points = await self.watsonx_client.extract_key_points(text)
        
        return {
            "key_points": key_points,
            "original_length": len(text)
        }
    
    async def start(self):
        """Start the MCP server."""
        config = uvicorn.Config(
            self.app,
            host=self.config.host,
            port=self.config.port,
            log_level="info"
        )
        server = uvicorn.Server(config)
        await server.serve()
    
    def run(self):
        """Run the MCP server synchronously."""
        uvicorn.run(
            self.app,
            host=self.config.host,
            port=self.config.port,
            log_level="info"
        ) 