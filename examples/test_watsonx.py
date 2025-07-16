#!/usr/bin/env python3
"""
Simple test script to verify Watsonx.ai connectivity.

This script tests the basic connectivity and functionality of the Watsonx.ai client.
"""

import asyncio
import sys
from pathlib import Path

# Add src to Python path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from src.watsonx import WatsonxClient
from src.config import config_manager


async def test_watsonx_connection():
    """Test Watsonx.ai connection and basic functionality."""
    
    print("🧪 Testing Watsonx.ai Connection...")
    print("=" * 50)
    
    try:
        # Load configuration
        config = config_manager.get_config()
        print(f"✅ Configuration loaded")
        print(f"   Endpoint: {config.watsonx.endpoint}")
        print(f"   Model: {config.watsonx.model}")
        
        # Create Watsonx client
        client = WatsonxClient()
        print("✅ Watsonx client created")
        
        # Test simple text generation
        print("\n📝 Testing text generation...")
        from src.watsonx.models import WatsonxRequest
        
        request = WatsonxRequest(
            prompt="Hello, this is a test message. Please respond with a brief greeting.",
            max_tokens=50,
            temperature=0.7
        )
        
        response = await client.generate_text(request)
        print("✅ Text generation successful!")
        print(f"   Response: {response.text}")
        print(f"   Model: {response.model}")
        if response.usage:
            print(f"   Usage: {response.usage}")
        
        # Test summarization
        print("\n📋 Testing text summarization...")
        test_text = """
        Artificial Intelligence (AI) is a branch of computer science that aims to create 
        intelligent machines that work and react like humans. Some of the activities 
        computers with artificial intelligence are designed for include speech recognition, 
        learning, planning, and problem solving. AI has been used in various applications 
        including medical diagnosis, stock trading, robot control, law, scientific discovery, 
        and toys. The field was founded on the assumption that human intelligence can be 
        precisely described and simulated by machines.
        """
        
        summary = await client.summarize_text(test_text, max_length=100)
        print("✅ Summarization successful!")
        print(f"   Summary: {summary}")
        
        # Test question answering
        print("\n❓ Testing question answering...")
        answer = await client.answer_question(
            test_text, 
            "What is artificial intelligence?"
        )
        print("✅ Question answering successful!")
        print(f"   Answer: {answer}")
        
        print("\n" + "=" * 50)
        print("🎉 All tests passed! Watsonx.ai integration is working correctly.")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        print("\nTroubleshooting tips:")
        print("1. Check your Watsonx.ai API key in config/config.yaml")
        print("2. Verify your project ID is correct")
        print("3. Ensure you have access to the Granite model")
        print("4. Check your internet connection")
        return False
    
    return True


def test_configuration():
    """Test configuration loading."""
    print("⚙️  Testing configuration...")
    
    try:
        config = config_manager.get_config()
        
        # Check required fields
        if not config.watsonx.api_key or config.watsonx.api_key == "your_watsonx_api_key_here":
            print("❌ Watsonx.ai API key not configured")
            return False
        
        if not config.watsonx.project_id or config.watsonx.project_id == "your_project_id_here":
            print("❌ Watsonx.ai project ID not configured")
            return False
        
        print("✅ Configuration is valid")
        return True
        
    except Exception as e:
        print(f"❌ Configuration error: {e}")
        return False


if __name__ == "__main__":
    print("IBM ACP Agent - Watsonx.ai Test")
    print("This script tests the Watsonx.ai integration")
    print()
    
    # Test configuration first
    if not test_configuration():
        print("\nPlease configure your Watsonx.ai credentials in config/config.yaml")
        sys.exit(1)
    
    # Test Watsonx connection
    success = asyncio.run(test_watsonx_connection())
    
    if success:
        print("\n✅ All tests completed successfully!")
        print("You can now run the main agent with: python main.py")
    else:
        print("\n❌ Tests failed. Please check the error messages above.")
        sys.exit(1) 