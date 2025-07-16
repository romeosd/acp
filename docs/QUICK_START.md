# IBM ACP Agent - Quick Start Guide

Get up and running with the IBM ACP Agent in 5 minutes!

## 🚀 Quick Setup

### 1. Automated Setup (Recommended)

```bash
# Clone the repository
git clone <repository-url>
cd acp

# Run automated setup
python setup.py
```

### 2. Manual Setup

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Create directories
mkdir -p logs temp examples

# Copy configuration
cp config/config.example.yaml config/config.yaml
```

## ⚙️ Configuration

### 1. Get Watsonx.ai Credentials

1. **Sign up for IBM Cloud**: [cloud.ibm.com](https://cloud.ibm.com)
2. **Enable Watsonx.ai**: Navigate to Watsonx.ai in the console
3. **Create a Project**: Click "Create Project" and note the Project ID
4. **Get API Key**: Go to "Manage" → "Access (IAM)" → "API Keys" → "Create"

### 2. Update Configuration

Edit `config/config.yaml`:

```yaml
watsonx:
  api_key: "your_actual_api_key_here"
  project_id: "your_actual_project_id_here"
  endpoint: "https://us-south.ml.cloud.ibm.com"
  model: "ibm-granite/granite-13b-chat-v2"
```

## 🧪 Test Installation

```bash
# Test Watsonx.ai connection
python examples/test_watsonx.py
```

## 🏃‍♂️ Start the Agent

```bash
# Start the agent
python main.py
```

You should see:
```
INFO - Starting IBM ACP Agent...
INFO - ACP Agent starting on localhost:8080
INFO - MCP Server will be available on localhost:8081
```

## 📝 Quick Test

### 1. Check Status

```bash
curl http://localhost:8080/acp/status
```

### 2. Test with Sample PDF

1. **Add a PDF file**:
   ```bash
   cp /path/to/your/document.pdf examples/sample_document.pdf
   ```

2. **Run the example**:
   ```bash
   python examples/basic_usage.py
   ```

### 3. Manual API Test

```bash
# Test summarization
curl -X POST http://localhost:8080/acp/process \
  -H "Content-Type: application/json" \
  -d '{
    "request_id": "test_001",
    "task": "summarize",
    "document_path": "examples/sample_document.pdf",
    "parameters": {"max_length": 300}
  }'
```

## 🔗 API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/acp/process` | POST | Process PDF documents |
| `/acp/upload` | POST | Upload and process files |
| `/acp/status` | GET | Get agent status |
| `/acp/health` | GET | Health check |
| `/mcp/query` | POST | MCP protocol queries |
| `/mcp/health` | GET | MCP server health |

## 📚 Interactive Documentation

Visit the interactive API documentation:
- **ACP Agent**: http://localhost:8080/docs
- **MCP Server**: http://localhost:8081/docs

## 🐳 Docker (Alternative)

```bash
# Build and run with Docker
docker-compose up -d

# Check logs
docker-compose logs -f acp-agent
```

## 🔧 Troubleshooting

### Common Issues

1. **"Watsonx API key not configured"**
   - Edit `config/config.yaml` with your credentials
   - Or set environment variables: `export WATSONX_API_KEY="your_key"`

2. **"Port already in use"**
   - Change ports in `config/config.yaml`
   - Or kill existing processes: `lsof -ti:8080 | xargs kill`

3. **"Module not found"**
   - Activate virtual environment: `source venv/bin/activate`
   - Reinstall dependencies: `pip install -r requirements.txt`

4. **"PDF processing failed"**
   - Ensure PDF file exists and is readable
   - Check file size (max 10MB by default)
   - Verify PDF is not corrupted

### Getting Help

- **Logs**: Check `logs/acp_agent.log`
- **Status**: Visit http://localhost:8080/acp/status
- **Health**: Visit http://localhost:8080/acp/health

## 🎯 Next Steps

1. **Read the full documentation**: `docs/INSTALLATION.md`
2. **Explore the architecture**: `docs/ARCHITECTURE.md`
3. **Try different tasks**: summarization, Q&A, analysis
4. **Integrate with external apps**: Microsoft Copilot, custom clients
5. **Deploy to production**: Docker, cloud platforms

## 📞 Support

- **Issues**: Create an issue in the repository
- **Documentation**: Check the `docs/` directory
- **Examples**: See `examples/` directory for usage patterns

---

**Happy coding! 🚀** 