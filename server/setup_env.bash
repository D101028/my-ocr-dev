#!/bin/bash
set -euo pipefail

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

log_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1" >&2
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

# Check Python availability
if ! command -v python3 &> /dev/null; then
    log_error "Python3 is not installed"
    exit 1
fi

log_info "Setting up virtual environment..."
if [ -d ".venv" ]; then
    log_warn "Virtual environment already exists"
else
    python3 -m venv .venv
    log_info "Virtual environment created"
fi

source .venv/bin/activate
log_info "Virtual environment activated"

# Upgrade pip
log_info "Upgrading pip..."
python3 -m pip install --upgrade pip

# Install dependencies
log_info "Installing paddlepaddle-gpu..."
python3 -m pip install paddlepaddle-gpu==3.3.0 -i https://www.paddlepaddle.org.cn/packages/stable/cu130/ || \
    log_warn "Failed to install paddlepaddle-gpu (GPU may not be available)"

log_info "Installing requirements..."
python3 -m pip install -r requirements.txt || {
    log_error "Failed to install requirements"
    exit 1
}

# Download model weights
log_info "Downloading model weights..."
python3 -c "import paddleocr; paddleocr.PaddleOCR()" || log_warn "PaddleOCR initialization failed"
python3 -c "import texify" || log_warn "texify import failed"

log_info "Setup completed successfully!"