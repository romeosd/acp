#!/usr/bin/env python3
"""
Main entry point for IBM ACP Agent.

This script starts the ACP agent with all necessary components:
- ACP (Agent Communication Protocol) server
- MCP (Model Context Protocol) server
- PDF processing capabilities
- Watsonx.ai integration
"""

import asyncio
import logging
import sys
import os
from pathlib import Path

# Add src to Python path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from src.agent import ACPAgent
from src.config import config_manager


def setup_logging():
    """Setup logging configuration."""
    config = config_manager.get_config()
    
    # Create logs directory
    log_file = config.logging.file
    os.makedirs(os.path.dirname(log_file), exist_ok=True)
    
    # Configure logging
    logging.basicConfig(
        level=getattr(logging, config.logging.level.upper()),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_file),
            logging.StreamHandler(sys.stdout)
        ]
    )


async def main():
    """Main function to start the ACP agent."""
    try:
        # Setup logging
        setup_logging()
        logger = logging.getLogger(__name__)
        
        # Load configuration
        config = config_manager.get_config()
        logger.info("Starting IBM ACP Agent...")
        logger.info(f"Configuration loaded from: {config_manager.config_path}")
        
        # Validate configuration
        if not config.watsonx.api_key or config.watsonx.api_key == "your_watsonx_api_key_here":
            logger.error("Watsonx.ai API key not configured. Please update config/config.yaml")
            sys.exit(1)
        
        if not config.watsonx.project_id or config.watsonx.project_id == "your_project_id_here":
            logger.error("Watsonx.ai project ID not configured. Please update config/config.yaml")
            sys.exit(1)
        
        # Create and start ACP agent
        agent = ACPAgent()
        
        logger.info(f"ACP Agent starting on {config.acp.host}:{config.acp.port}")
        logger.info(f"MCP Server will be available on {config.mcp.host}:{config.mcp.port}")
        logger.info(f"Watsonx.ai endpoint: {config.watsonx.endpoint}")
        logger.info(f"Using model: {config.watsonx.model}")
        
        # Start the agent
        await agent.start()
        
    except KeyboardInterrupt:
        logger.info("Shutting down ACP Agent...")
    except Exception as e:
        logger.error(f"Error starting ACP Agent: {e}")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main()) 