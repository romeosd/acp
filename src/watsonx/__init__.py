"""
Watsonx.ai integration module for IBM ACP Agent.
"""

from .client import WatsonxClient
from .models import WatsonxRequest, WatsonxResponse

__all__ = ["WatsonxClient", "WatsonxRequest", "WatsonxResponse"] 