#!/usr/bin/env python3
"""
Basic usage example for IBM ACP Agent.

This example demonstrates how to:
1. Send requests to the ACP agent
2. Process PDF documents
3. Use different task types
"""

import asyncio
import json
import sys
from pathlib import Path
import httpx

# Add src to Python path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from src.agent.models import ACPRequest, TaskType


async def test_acp_agent():
    """Test the ACP agent with various tasks."""
    
    # ACP agent endpoint
    base_url = "http://localhost:8080"
    
    # Test document path (you'll need to provide a real PDF)
    test_pdf_path = "examples/sample_document.pdf"
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        
        print("🚀 Testing IBM ACP Agent...")
        print("=" * 50)
        
        # 1. Check agent status
        print("\n1. Checking agent status...")
        try:
            response = await client.get(f"{base_url}/acp/status")
            if response.status_code == 200:
                status = response.json()
                print(f"✅ Agent Status: {status['status']}")
                print(f"   Uptime: {status['uptime']:.2f} seconds")
                print(f"   Total Requests: {status['total_requests']}")
                print(f"   Watsonx Status: {status['watsonx_status']}")
            else:
                print(f"❌ Failed to get status: {response.status_code}")
        except Exception as e:
            print(f"❌ Error checking status: {e}")
        
        # 2. Test document summarization
        print("\n2. Testing document summarization...")
        try:
            request = ACPRequest(
                request_id="test_summarize_001",
                task=TaskType.SUMMARIZE,
                document_path=test_pdf_path,
                parameters={"max_length": 300},
                source="example_script"
            )
            
            response = await client.post(
                f"{base_url}/acp/process",
                json=request.dict()
            )
            
            if response.status_code == 200:
                result = response.json()
                if result["success"]:
                    print("✅ Summarization successful!")
                    print(f"   Summary: {result['result']['summary'][:100]}...")
                    print(f"   Processing time: {result['processing_time']:.2f}s")
                else:
                    print(f"❌ Summarization failed: {result['error']}")
            else:
                print(f"❌ Request failed: {response.status_code}")
                
        except Exception as e:
            print(f"❌ Error in summarization: {e}")
        
        # 3. Test question answering
        print("\n3. Testing question answering...")
        try:
            request = ACPRequest(
                request_id="test_qa_001",
                task=TaskType.QUESTION_ANSWER,
                document_path=test_pdf_path,
                parameters={"question": "What are the main topics discussed in this document?"},
                source="example_script"
            )
            
            response = await client.post(
                f"{base_url}/acp/process",
                json=request.dict()
            )
            
            if response.status_code == 200:
                result = response.json()
                if result["success"]:
                    print("✅ Question answering successful!")
                    print(f"   Question: {result['result']['question']}")
                    print(f"   Answer: {result['result']['answer'][:150]}...")
                    print(f"   Processing time: {result['processing_time']:.2f}s")
                else:
                    print(f"❌ Question answering failed: {result['error']}")
            else:
                print(f"❌ Request failed: {response.status_code}")
                
        except Exception as e:
            print(f"❌ Error in question answering: {e}")
        
        # 4. Test key points extraction
        print("\n4. Testing key points extraction...")
        try:
            request = ACPRequest(
                request_id="test_extract_001",
                task=TaskType.EXTRACT,
                document_path=test_pdf_path,
                parameters={"extraction_type": "key_points"},
                source="example_script"
            )
            
            response = await client.post(
                f"{base_url}/acp/process",
                json=request.dict()
            )
            
            if response.status_code == 200:
                result = response.json()
                if result["success"]:
                    print("✅ Key points extraction successful!")
                    print(f"   Key Points: {result['result']['key_points'][:150]}...")
                    print(f"   Processing time: {result['processing_time']:.2f}s")
                else:
                    print(f"❌ Key points extraction failed: {result['error']}")
            else:
                print(f"❌ Request failed: {response.status_code}")
                
        except Exception as e:
            print(f"❌ Error in key points extraction: {e}")
        
        # 5. Test document analysis
        print("\n5. Testing document analysis...")
        try:
            request = ACPRequest(
                request_id="test_analyze_001",
                task=TaskType.ANALYZE,
                document_path=test_pdf_path,
                source="example_script"
            )
            
            response = await client.post(
                f"{base_url}/acp/process",
                json=request.dict()
            )
            
            if response.status_code == 200:
                result = response.json()
                if result["success"]:
                    print("✅ Document analysis successful!")
                    print(f"   Analysis: {result['result']['analysis'][:200]}...")
                    print(f"   Processing time: {result['processing_time']:.2f}s")
                else:
                    print(f"❌ Document analysis failed: {result['error']}")
            else:
                print(f"❌ Request failed: {response.status_code}")
                
        except Exception as e:
            print(f"❌ Error in document analysis: {e}")
        
        print("\n" + "=" * 50)
        print("🏁 Testing completed!")


async def test_mcp_server():
    """Test the MCP server directly."""
    
    print("\n🔧 Testing MCP Server...")
    print("=" * 50)
    
    mcp_url = "http://localhost:8081"
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        
        # Check MCP server health
        try:
            response = await client.get(f"{mcp_url}/mcp/health")
            if response.status_code == 200:
                print("✅ MCP Server is healthy")
            else:
                print(f"❌ MCP Server health check failed: {response.status_code}")
        except Exception as e:
            print(f"❌ MCP Server not available: {e}")
            return
        
        # Get MCP capabilities
        try:
            response = await client.get(f"{mcp_url}/mcp/capabilities")
            if response.status_code == 200:
                capabilities = response.json()
                print("✅ MCP Server capabilities:")
                print(f"   Methods: {capabilities['methods']}")
                print(f"   Models: {capabilities['models']}")
                print(f"   Version: {capabilities['version']}")
            else:
                print(f"❌ Failed to get capabilities: {response.status_code}")
        except Exception as e:
            print(f"❌ Error getting capabilities: {e}")


if __name__ == "__main__":
    print("IBM ACP Agent - Basic Usage Example")
    print("Make sure the agent is running on localhost:8080")
    print("Make sure you have a sample PDF document in examples/sample_document.pdf")
    print()
    
    # Run tests
    asyncio.run(test_acp_agent())
    asyncio.run(test_mcp_server()) 