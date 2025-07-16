#!/usr/bin/env python3
"""
Setup script for IBM ACP Agent.

This script automates the installation and configuration process.
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path


def run_command(command, description):
    """Run a command and handle errors."""
    print(f"🔄 {description}...")
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ {description} completed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed: {e}")
        print(f"Error output: {e.stderr}")
        return False


def check_python_version():
    """Check if Python version is compatible."""
    print("🐍 Checking Python version...")
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print(f"❌ Python 3.8+ required, found {version.major}.{version.minor}")
        return False
    print(f"✅ Python {version.major}.{version.minor}.{version.micro} is compatible")
    return True


def create_virtual_environment():
    """Create and activate virtual environment."""
    if os.path.exists("venv"):
        print("📁 Virtual environment already exists")
        return True
    
    return run_command("python -m venv venv", "Creating virtual environment")


def install_dependencies():
    """Install Python dependencies."""
    # Determine the correct pip command
    if os.name == 'nt':  # Windows
        pip_cmd = "venv\\Scripts\\pip"
    else:  # Unix/Linux/macOS
        pip_cmd = "venv/bin/pip"
    
    commands = [
        (f"{pip_cmd} install --upgrade pip", "Upgrading pip"),
        (f"{pip_cmd} install -r requirements.txt", "Installing dependencies")
    ]
    
    for command, description in commands:
        if not run_command(command, description):
            return False
    
    return True


def create_directories():
    """Create necessary directories."""
    print("📁 Creating directories...")
    directories = ["logs", "temp", "examples", "docs"]
    
    for directory in directories:
        Path(directory).mkdir(exist_ok=True)
        print(f"✅ Created {directory}/ directory")
    
    return True


def setup_configuration():
    """Setup configuration file."""
    config_file = Path("config/config.yaml")
    example_config = Path("config/config.example.yaml")
    
    if config_file.exists():
        print("⚙️  Configuration file already exists")
        return True
    
    if not example_config.exists():
        print("❌ Example configuration file not found")
        return False
    
    try:
        shutil.copy(example_config, config_file)
        print("✅ Configuration file created from template")
        print("📝 Please edit config/config.yaml with your Watsonx.ai credentials")
        return True
    except Exception as e:
        print(f"❌ Failed to create configuration file: {e}")
        return False


def check_docker():
    """Check if Docker is available."""
    print("🐳 Checking Docker availability...")
    try:
        result = subprocess.run(["docker", "--version"], capture_output=True, text=True)
        if result.returncode == 0:
            print("✅ Docker is available")
            return True
        else:
            print("⚠️  Docker not found (optional)")
            return False
    except FileNotFoundError:
        print("⚠️  Docker not found (optional)")
        return False


def create_env_file():
    """Create .env file template."""
    env_file = Path(".env")
    if env_file.exists():
        print("📄 .env file already exists")
        return True
    
    env_content = """# IBM ACP Agent Environment Variables
# Copy this file to .env and fill in your credentials

# Watsonx.ai Configuration
WATSONX_API_KEY=your_watsonx_api_key_here
WATSONX_PROJECT_ID=your_project_id_here
WATSONX_ENDPOINT=https://us-south.ml.cloud.ibm.com

# ACP Configuration
ACP_HOST=localhost
ACP_PORT=8080

# MCP Configuration
MCP_HOST=localhost
MCP_PORT=8081
"""
    
    try:
        with open(env_file, 'w') as f:
            f.write(env_content)
        print("✅ .env file created")
        return True
    except Exception as e:
        print(f"❌ Failed to create .env file: {e}")
        return False


def print_next_steps():
    """Print next steps for the user."""
    print("\n" + "="*60)
    print("🎉 IBM ACP Agent Setup Complete!")
    print("="*60)
    
    print("\n📋 Next Steps:")
    print("1. Activate virtual environment:")
    if os.name == 'nt':  # Windows
        print("   venv\\Scripts\\activate")
    else:  # Unix/Linux/macOS
        print("   source venv/bin/activate")
    
    print("\n2. Configure Watsonx.ai credentials:")
    print("   - Edit config/config.yaml")
    print("   - Or set environment variables in .env file")
    print("   - Get credentials from IBM Cloud Console")
    
    print("\n3. Test the installation:")
    print("   python examples/test_watsonx.py")
    
    print("\n4. Start the agent:")
    print("   python main.py")
    
    print("\n5. Test with examples:")
    print("   python examples/basic_usage.py")
    
    print("\n📚 Documentation:")
    print("   - README.md - Main documentation")
    print("   - docs/INSTALLATION.md - Detailed installation guide")
    print("   - docs/ARCHITECTURE.md - Architecture overview")
    
    print("\n🔗 Useful URLs:")
    print("   - ACP Agent API: http://localhost:8080/docs")
    print("   - MCP Server: http://localhost:8081/mcp/health")
    print("   - Agent Status: http://localhost:8080/acp/status")
    
    print("\n🐳 Docker (optional):")
    print("   docker-compose up -d")
    
    print("\n" + "="*60)


def main():
    """Main setup function."""
    print("🚀 IBM ACP Agent Setup")
    print("="*60)
    
    # Check Python version
    if not check_python_version():
        sys.exit(1)
    
    # Create virtual environment
    if not create_virtual_environment():
        sys.exit(1)
    
    # Install dependencies
    if not install_dependencies():
        sys.exit(1)
    
    # Create directories
    if not create_directories():
        sys.exit(1)
    
    # Setup configuration
    if not setup_configuration():
        sys.exit(1)
    
    # Create .env file
    create_env_file()
    
    # Check Docker
    check_docker()
    
    # Print next steps
    print_next_steps()


if __name__ == "__main__":
    main() 