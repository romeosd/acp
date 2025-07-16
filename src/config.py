"""
Configuration management for IBM ACP Agent.
"""

import os
import yaml
from typing import Dict, Any, Optional
from pydantic import BaseModel


class WatsonxConfig(BaseModel):
    """Watsonx.ai configuration."""
    api_key: str
    project_id: str
    endpoint: str = "https://us-south.ml.cloud.ibm.com"
    model: str = "ibm-granite/granite-13b-chat-v2"
    max_tokens: int = 2048
    temperature: float = 0.7


class ACPConfig(BaseModel):
    """ACP (Agent Communication Protocol) configuration."""
    host: str = "localhost"
    port: int = 8080
    protocol: str = "http"
    timeout: int = 30
    max_file_size: int = 10485760  # 10MB


class MCPConfig(BaseModel):
    """MCP (Model Context Protocol) configuration."""
    host: str = "localhost"
    port: int = 8081
    timeout: int = 30


class PDFConfig(BaseModel):
    """PDF processing configuration."""
    max_pages: int = 100
    supported_formats: list = ["pdf"]
    temp_directory: str = "./temp"
    chunk_size: int = 1000


class LoggingConfig(BaseModel):
    """Logging configuration."""
    level: str = "INFO"
    format: str = "json"
    file: str = "logs/acp_agent.log"


class SecurityConfig(BaseModel):
    """Security configuration."""
    enable_auth: bool = False
    api_key_header: str = "X-API-Key"
    allowed_origins: list = ["*"]


class Config(BaseModel):
    """Main configuration class."""
    watsonx: WatsonxConfig
    acp: ACPConfig
    mcp: MCPConfig
    pdf: PDFConfig
    logging: LoggingConfig
    security: SecurityConfig


class ConfigManager:
    """Configuration manager for loading and managing settings."""
    
    def __init__(self, config_path: Optional[str] = None):
        self.config_path = config_path or "config/config.yaml"
        self._config: Optional[Config] = None
    
    def load_config(self) -> Config:
        """Load configuration from YAML file."""
        if self._config is not None:
            return self._config
        
        # Check if config file exists
        if not os.path.exists(self.config_path):
            raise FileNotFoundError(f"Configuration file not found: {self.config_path}")
        
        # Load YAML configuration
        with open(self.config_path, 'r') as file:
            config_data = yaml.safe_load(file)
        
        # Override with environment variables
        config_data = self._override_with_env(config_data)
        
        # Create Config object
        self._config = Config(**config_data)
        return self._config
    
    def _override_with_env(self, config_data: Dict[str, Any]) -> Dict[str, Any]:
        """Override configuration with environment variables."""
        env_mappings = {
            "WATSONX_API_KEY": ("watsonx", "api_key"),
            "WATSONX_PROJECT_ID": ("watsonx", "project_id"),
            "WATSONX_ENDPOINT": ("watsonx", "endpoint"),
            "WATSONX_MODEL": ("watsonx", "model"),
            "ACP_HOST": ("acp", "host"),
            "ACP_PORT": ("acp", "port"),
            "MCP_HOST": ("mcp", "host"),
            "MCP_PORT": ("mcp", "port"),
        }
        
        for env_var, (section, key) in env_mappings.items():
            env_value = os.getenv(env_var)
            if env_value is not None:
                if section not in config_data:
                    config_data[section] = {}
                config_data[section][key] = env_value
        
        return config_data
    
    def get_config(self) -> Config:
        """Get current configuration."""
        if self._config is None:
            return self.load_config()
        return self._config
    
    def reload_config(self) -> Config:
        """Reload configuration from file."""
        self._config = None
        return self.load_config()


# Global configuration instance
config_manager = ConfigManager() 