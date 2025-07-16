# IBM ACP Agent - Architecture Documentation

This document provides a detailed overview of the IBM ACP Agent architecture, including system design, component interactions, and protocol implementations.

## System Overview

The IBM ACP Agent is a prototype that demonstrates how IBM agents built with ADK (Agent Development Kit) can use IBM Granite models and MCP (Model Context Protocol) architecture to handle requests from external applications like Microsoft Copilot for PDF processing tasks.

## High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                    External Applications                        │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐  │
│  │ Microsoft       │  │ Custom Client   │  │ Web Interface   │  │
│  │ Copilot         │  │ Applications    │  │ (Optional)      │  │
│  └─────────────────┘  └─────────────────┘  └─────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│                    IBM ACP Gateway                              │
│  ┌─────────────────────────────────────────────────────────────┐  │
│  │              Agent Communication Protocol                   │  │
│  │                    (ACP)                                    │  │
│  └─────────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│                    IBM ACP Agent                                │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐  │
│  │ ACP Server      │  │ MCP Server      │  │ PDF Processor   │  │
│  │ (FastAPI)       │  │ (Model Context) │  │ (PyPDF2/plumber)│  │
│  └─────────────────┘  └─────────────────┘  └─────────────────┘  │
│           │                     │                     │          │
│           └─────────────────────┼─────────────────────┘          │
│                                 │                                │
│  ┌─────────────────────────────────────────────────────────────┐  │
│  │                    Task Orchestrator                        │  │
│  │              (Request Routing & Processing)                 │  │
│  └─────────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│                    IBM Watsonx.ai                               │
│  ┌─────────────────────────────────────────────────────────────┐  │
│  │              IBM Granite Models                             │  │
│  │        (granite-13b-chat-v2, etc.)                         │  │
│  └─────────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
```

## Component Details

### 1. External Applications Layer

**Purpose**: External clients that send requests to the ACP Agent.

**Examples**:
- Microsoft Copilot
- Custom client applications
- Web interfaces
- Other AI assistants

**Communication**: HTTP/HTTPS using ACP protocol

### 2. IBM ACP Gateway (Optional)

**Purpose**: Optional gateway for protocol translation and routing.

**Features**:
- Protocol translation
- Request routing
- Load balancing
- Authentication/Authorization

**Implementation**: Can be IBM's official ACP Gateway or custom implementation

### 3. IBM ACP Agent

The main agent implementation with several key components:

#### 3.1 ACP Server (FastAPI)

**Purpose**: Handles ACP protocol requests and provides REST API endpoints.

**Key Endpoints**:
- `POST /acp/process` - Process PDF documents
- `POST /acp/upload` - Upload and process files
- `GET /acp/status` - Get agent status
- `GET /acp/health` - Health check

**Features**:
- Request validation
- File upload handling
- Response formatting
- Error handling

#### 3.2 MCP Server (Model Context Protocol)

**Purpose**: Implements MCP for standardized model interactions.

**Key Endpoints**:
- `POST /mcp/query` - Handle MCP queries
- `GET /mcp/health` - Health check
- `GET /mcp/capabilities` - Get available methods

**Supported Methods**:
- `text/generate` - Text generation
- `text/summarize` - Text summarization
- `text/answer_question` - Question answering
- `text/extract_key_points` - Key points extraction

#### 3.3 PDF Processor

**Purpose**: Handles PDF document processing and text extraction.

**Features**:
- Text extraction using PyPDF2 and pdfplumber
- Metadata extraction
- Document validation
- Text chunking for processing
- Multiple format support

**Processing Pipeline**:
1. File validation
2. Text extraction
3. Metadata extraction
4. Text chunking
5. Result packaging

#### 3.4 Task Orchestrator

**Purpose**: Coordinates between different components and manages task execution.

**Responsibilities**:
- Request routing
- Task scheduling
- Error handling
- Result aggregation
- Performance monitoring

### 4. IBM Watsonx.ai

**Purpose**: Cloud-based LLM service providing IBM Granite models.

**Models**:
- `ibm-granite/granite-13b-chat-v2` (primary)
- Other Granite model variants

**Features**:
- Text generation
- Summarization
- Question answering
- Content analysis

## Data Flow

### 1. Document Processing Flow

```
External Request
       │
       ▼
   ACP Server
       │
       ▼
   PDF Processor
       │
       ▼
   Text Extraction
       │
       ▼
   Task Orchestrator
       │
       ▼
   MCP Server
       │
       ▼
   Watsonx.ai
       │
       ▼
   Response Generation
       │
       ▼
   External Response
```

### 2. Request Processing Flow

```
1. External Application
   └── Sends ACP request with PDF path and task type

2. ACP Server
   ├── Validates request format
   ├── Checks file existence
   └── Routes to appropriate handler

3. PDF Processor
   ├── Validates PDF file
   ├── Extracts text content
   ├── Extracts metadata
   └── Creates text chunks

4. Task Orchestrator
   ├── Determines task type
   ├── Prepares context
   └── Routes to MCP server

5. MCP Server
   ├── Validates MCP method
   ├── Prepares Watsonx request
   └── Calls Watsonx.ai API

6. Watsonx.ai
   ├── Processes with Granite model
   ├── Generates response
   └── Returns result

7. Response Chain
   └── MCP → Orchestrator → ACP → External Application
```

## Protocol Implementations

### ACP (Agent Communication Protocol)

**Purpose**: Standardized communication protocol for agent interactions.

**Request Format**:
```json
{
  "request_id": "unique_id",
  "task": "summarize|question_answer|extract|analyze",
  "document_path": "/path/to/document.pdf",
  "parameters": {
    "max_length": 500,
    "question": "What is this about?"
  },
  "source": "Microsoft Copilot"
}
```

**Response Format**:
```json
{
  "request_id": "unique_id",
  "success": true,
  "result": {
    "summary": "Document summary...",
    "document_info": {
      "file_name": "document.pdf",
      "page_count": 10
    }
  },
  "processing_time": 2.5
}
```

### MCP (Model Context Protocol)

**Purpose**: Standardized protocol for model interactions.

**Request Format**:
```json
{
  "id": "req_123",
  "method": "text/generate",
  "params": {
    "prompt": "Summarize this document",
    "max_tokens": 500
  }
}
```

**Response Format**:
```json
{
  "id": "req_123",
  "result": {
    "text": "Generated text...",
    "model": "ibm-granite/granite-13b-chat-v2",
    "usage": {
      "prompt_tokens": 100,
      "completion_tokens": 200
    }
  }
}
```

## Configuration Management

### Configuration Structure

```yaml
watsonx:
  api_key: "your_api_key"
  project_id: "your_project_id"
  endpoint: "https://us-south.ml.cloud.ibm.com"
  model: "ibm-granite/granite-13b-chat-v2"

acp:
  host: "localhost"
  port: 8080
  protocol: "http"

mcp:
  host: "localhost"
  port: 8081

pdf:
  max_pages: 100
  chunk_size: 1000
  temp_directory: "./temp"
```

### Environment Variables

The system supports configuration via environment variables:

- `WATSONX_API_KEY`
- `WATSONX_PROJECT_ID`
- `WATSONX_ENDPOINT`
- `ACP_HOST`
- `ACP_PORT`
- `MCP_HOST`
- `MCP_PORT`

## Security Considerations

### Authentication & Authorization

- API key-based authentication for Watsonx.ai
- Optional API key validation for ACP requests
- CORS configuration for web access
- Environment variable support for sensitive data

### Data Privacy

- Temporary file cleanup
- No persistent storage of uploaded documents
- Secure API key handling
- Logging without sensitive data

## Performance Considerations

### Optimization Strategies

1. **Text Chunking**: Large documents are split into manageable chunks
2. **Async Processing**: Non-blocking I/O operations
3. **Connection Pooling**: Reusable HTTP connections
4. **Caching**: Optional response caching
5. **Resource Limits**: Configurable file size and page limits

### Monitoring

- Request/response timing
- Success/failure rates
- Resource usage
- Watsonx.ai API usage
- Error tracking

## Scalability

### Horizontal Scaling

- Stateless design allows multiple instances
- Load balancer support
- Database-free architecture
- Container-ready deployment

### Vertical Scaling

- Configurable resource limits
- Memory-efficient processing
- Async I/O operations
- Modular component design

## Deployment Options

### Local Development

```bash
python main.py
```

### Docker Deployment

```dockerfile
FROM python:3.9-slim
COPY . /app
WORKDIR /app
RUN pip install -r requirements.txt
EXPOSE 8080 8081
CMD ["python", "main.py"]
```

### Cloud Deployment

- IBM Cloud
- AWS Lambda
- Google Cloud Functions
- Azure Functions

## Integration Points

### External Systems

1. **Microsoft Copilot**: Via ACP protocol
2. **Custom Applications**: REST API endpoints
3. **Web Interfaces**: CORS-enabled endpoints
4. **Other AI Assistants**: Standardized protocols

### IBM Services

1. **Watsonx.ai**: Primary LLM service
2. **IBM ACP Gateway**: Optional protocol gateway
3. **IBM Cloud**: Hosting and services
4. **IBM ADK**: Agent development framework

## Future Enhancements

### Planned Features

1. **Multi-modal Support**: Images, audio, video
2. **Streaming Responses**: Real-time processing
3. **Advanced Caching**: Redis integration
4. **Metrics Dashboard**: Performance monitoring
5. **Plugin Architecture**: Extensible task types

### Integration Opportunities

1. **IBM Watson Assistant**: Chatbot integration
2. **IBM Cloud Pak**: Enterprise deployment
3. **IBM Security**: Enhanced security features
4. **IBM Data**: Advanced analytics integration 