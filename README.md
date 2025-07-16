# IBM ACP Agent Prototype

A prototype demonstrating how IBM agents built with ADK (Agent Development Kit) can use IBM Granite models and MCP (Model Context Protocol) architecture to handle requests from external applications like Microsoft Copilot for PDF processing tasks.

## Architecture Overview

This prototype implements:
- **IBM ACP (Agent Communication Protocol)** for external communication
- **MCP (Model Context Protocol)** for LLM interactions
- **IBM Granite models** via Watsonx.ai for document processing
- **PDF processing capabilities** for summarization and task execution
- **Configurable Watsonx.ai integration** for cloud-based LLM services

## System Architecture

```
┌─────────────────┐    ACP Protocol    ┌──────────────────┐
│ Microsoft       │◄──────────────────►│ IBM ACP Gateway  │
│ Copilot         │                    │                  │
└─────────────────┘                    └──────────────────┘
                                                │
                                                ▼
┌─────────────────┐    MCP Protocol    ┌──────────────────┐
│ IBM Agent       │◄──────────────────►│ MCP Server       │
│ (ADK)           │                    │                  │
└─────────────────┘                    └──────────────────┘
                                                │
                                                ▼
┌─────────────────┐    REST API        ┌──────────────────┐
│ PDF Processor   │◄──────────────────►│ Watsonx.ai       │
│                 │                    │ (Granite Models) │
└─────────────────┘                    └──────────────────┘
```

## Features

- **PDF Document Processing**: Upload and process PDF documents
- **Intelligent Summarization**: Use IBM Granite models for document summarization
- **Task Execution**: Perform various LLM-powered tasks on PDF content
- **ACP Protocol Support**: Handle requests from external applications
- **MCP Integration**: Standardized model context protocol
- **Configurable Cloud Integration**: Easy Watsonx.ai configuration

## Quick Start

### Prerequisites

- Python 3.8+
- IBM Cloud account with Watsonx.ai access
- IBM ACP Gateway (optional, can use local implementation)

### Installation

1. **Clone and Setup**
   ```bash
   git clone <repository>
   cd acp
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

2. **Configure Watsonx.ai**
   ```bash
   cp config/config.example.yaml config/config.yaml
   # Edit config.yaml with your Watsonx.ai credentials
   ```

3. **Start the Agent**
   ```bash
   python main.py
   ```

### Configuration

Edit `config/config.yaml`:
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
```

## Usage Examples

### 1. PDF Summarization
```python
# Send request to agent
request = {
    "task": "summarize",
    "document": "path/to/document.pdf",
    "max_length": 500
}
```

### 2. Document Q&A
```python
request = {
    "task": "question_answer",
    "document": "path/to/document.pdf",
    "question": "What are the main findings?"
}
```

### 3. Content Extraction
```python
request = {
    "task": "extract",
    "document": "path/to/document.pdf",
    "extraction_type": "key_points"
}
```

## API Endpoints

- `POST /acp/process` - Process PDF documents
- `GET /acp/status` - Check agent status
- `POST /mcp/query` - MCP protocol queries

## Development

### Project Structure
```
acp/
├── src/
│   ├── agent/           # IBM ADK agent implementation
│   ├── mcp/            # MCP server and protocol
│   ├── pdf_processor/  # PDF processing utilities
│   └── watsonx/        # Watsonx.ai integration
├── config/             # Configuration files
├── tests/              # Unit tests
├── docs/               # Documentation
└── examples/           # Usage examples
```

### Running Tests
```bash
pytest tests/
```

## Troubleshooting

### Common Issues

1. **Watsonx.ai Connection Error**
   - Verify API key and project ID
   - Check network connectivity
   - Ensure proper endpoint URL

2. **PDF Processing Errors**
   - Verify PDF file is not corrupted
   - Check file permissions
   - Ensure PyPDF2 is properly installed

3. **ACP Protocol Issues**
   - Verify port availability
   - Check firewall settings
   - Ensure proper JSON formatting

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

For issues and questions:
- Create an issue in the repository
- Check the troubleshooting section
- Review IBM ACP and MCP documentation