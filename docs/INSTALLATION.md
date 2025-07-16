# IBM ACP Agent - Installation Guide

This guide provides step-by-step instructions for installing and configuring the IBM ACP Agent on your local machine.

## Prerequisites

### System Requirements

- **Operating System**: macOS, Linux, or Windows
- **Python**: 3.8 or higher
- **Memory**: Minimum 4GB RAM (8GB recommended)
- **Storage**: At least 1GB free space
- **Network**: Internet connection for Watsonx.ai access

### Required Accounts

1. **IBM Cloud Account**: For Watsonx.ai access
   - Sign up at [IBM Cloud](https://cloud.ibm.com/)
   - Enable Watsonx.ai service

2. **Watsonx.ai Project**: 
   - Create a project in Watsonx.ai
   - Get your API key and project ID

## Step-by-Step Installation

### Step 1: Clone the Repository

```bash
git clone <repository-url>
cd acp
```

### Step 2: Create Virtual Environment

```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# On macOS/Linux:
source venv/bin/activate

# On Windows:
venv\Scripts\activate
```

### Step 3: Install Dependencies

```bash
# Upgrade pip
pip install --upgrade pip

# Install requirements
pip install -r requirements.txt
```

### Step 4: Configure Watsonx.ai

1. **Copy configuration template**:
   ```bash
   cp config/config.example.yaml config/config.yaml
   ```

2. **Edit configuration file**:
   ```bash
   # Open config/config.yaml in your preferred editor
   nano config/config.yaml
   # or
   code config/config.yaml
   ```

3. **Update Watsonx.ai settings**:
   ```yaml
   watsonx:
     api_key: "your_actual_api_key_here"
     project_id: "your_actual_project_id_here"
     endpoint: "https://us-south.ml.cloud.ibm.com"
     model: "ibm-granite/granite-13b-chat-v2"
   ```

### Step 5: Get Watsonx.ai Credentials

1. **Log into IBM Cloud**:
   - Go to [IBM Cloud Console](https://cloud.ibm.com/)
   - Navigate to Watsonx.ai

2. **Create a Project**:
   - Click "Create Project"
   - Give it a name (e.g., "ACP Agent Project")
   - Select your region

3. **Get API Key**:
   - Go to "Manage" → "Access (IAM)"
   - Click "API Keys" → "Create an IBM Cloud API key"
   - Copy the API key

4. **Get Project ID**:
   - In your Watsonx.ai project
   - Go to "Settings" → "General"
   - Copy the Project ID

### Step 6: Environment Variables (Optional)

You can also set credentials via environment variables:

```bash
export WATSONX_API_KEY="your_api_key"
export WATSONX_PROJECT_ID="your_project_id"
export WATSONX_ENDPOINT="https://us-south.ml.cloud.ibm.com"
```

### Step 7: Create Required Directories

```bash
# Create logs directory
mkdir -p logs

# Create temp directory
mkdir -p temp

# Create examples directory
mkdir -p examples
```

### Step 8: Test Installation

```bash
# Test basic functionality
python -c "from src.config import config_manager; print('Configuration loaded successfully')"

# Test Watsonx connection (optional)
python examples/test_watsonx.py
```

## Verification

### Check Installation

```bash
# Verify Python packages
pip list | grep -E "(fastapi|uvicorn|pydantic|httpx)"

# Verify configuration
python -c "from src.config import config_manager; config = config_manager.get_config(); print(f'Watsonx endpoint: {config.watsonx.endpoint}')"
```

### Test with Sample PDF

1. **Add a sample PDF**:
   ```bash
   # Copy a sample PDF to examples directory
   cp /path/to/your/document.pdf examples/sample_document.pdf
   ```

2. **Run the agent**:
   ```bash
   python main.py
   ```

3. **Test in another terminal**:
   ```bash
   python examples/basic_usage.py
   ```

## Troubleshooting

### Common Issues

#### 1. Python Version Issues
```bash
# Check Python version
python --version

# If using Python 3.x, ensure you're using the right command
python3 --version
```

#### 2. Virtual Environment Issues
```bash
# Deactivate and recreate virtual environment
deactivate
rm -rf venv
python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows
pip install -r requirements.txt
```

#### 3. Watsonx.ai Connection Issues
- Verify API key is correct
- Check project ID
- Ensure Watsonx.ai service is enabled
- Check network connectivity

#### 4. Port Conflicts
If ports 8080 or 8081 are in use:
```yaml
# Edit config/config.yaml
acp:
  port: 8082  # Change to available port

mcp:
  port: 8083  # Change to available port
```

#### 5. Permission Issues
```bash
# Fix file permissions
chmod +x main.py
chmod +x examples/basic_usage.py
```

### Getting Help

1. **Check logs**:
   ```bash
   tail -f logs/acp_agent.log
   ```

2. **Run with debug logging**:
   ```yaml
   # Edit config/config.yaml
   logging:
     level: "DEBUG"
   ```

3. **Test individual components**:
   ```bash
   # Test PDF processing
   python -c "from src.pdf_processor import PDFProcessor; p = PDFProcessor(); print('PDF processor OK')"
   
   # Test Watsonx client
   python -c "from src.watsonx import WatsonxClient; w = WatsonxClient(); print('Watsonx client OK')"
   ```

## Next Steps

After successful installation:

1. **Read the documentation**: Check `README.md` for usage examples
2. **Try the examples**: Run `examples/basic_usage.py`
3. **Explore the API**: Visit `http://localhost:8080/docs` for interactive API docs
4. **Configure external applications**: Set up Microsoft Copilot or other clients

## Support

For additional help:
- Check the troubleshooting section above
- Review IBM Watsonx.ai documentation
- Create an issue in the repository
- Check IBM ACP and MCP documentation 