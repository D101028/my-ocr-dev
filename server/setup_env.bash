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
python3 -c "import texify; from texify.model.model import load_model; from texify.model.processor import load_processor; model = load_model(); processor = load_processor()" || {
    log_warn "texify import failed, attempting to fix transformers configuration..."
    python3 << 'EOF'
import os
config_file = os.path.join(".venv/lib/python3.12/site-packages/transformers/configuration_utils.py")
if os.path.exists(config_file):
    with open(config_file, 'r') as f:
        content = f.read()
    
    # Check if fix is needed and apply it
    if 'def recursive_diff_dict' in content:
        # Find and replace the entire function
        start_idx = content.find('def recursive_diff_dict')
        if start_idx != -1:
            end_idx = -1
            lines = content[start_idx:].split('\n')
            for i, line in enumerate(lines[1:], 1):
                if not line.startswith('    '):
                    end_idx = start_idx + sum(len(l) + 1 for l in lines[:i])
                    break
            if end_idx == -1:
                end_idx = len(content)
            
            new_function = '''def recursive_diff_dict(dict_a, dict_b, config_obj=None):
    """
    Helper function to recursively take the diff between two nested dictionaries. The resulting diff only contains the
    values from `dict_a` that are different from values in `dict_b`.

    dict_b : the default config dictionary. We want to remove values that are in this one
    """
    diff = {}
    default = config_obj.__class__().to_dict() if config_obj is not None and isinstance(config_obj, PretrainedConfig) else {}
    for key, value in dict_a.items():
        obj_value = getattr(config_obj, str(key), None)
        if isinstance(obj_value, PretrainedConfig) and key in dict_b and isinstance(dict_b[key], dict):
            diff_value = recursive_diff_dict(value, dict_b[key], config_obj=obj_value)
            diff[key] = diff_value
        elif key not in dict_b or (value != default.get(key, value)):
            diff[key] = value
    return diff
'''
            fixed_content = content[:start_idx] + new_function + content[end_idx:]
            with open(config_file, 'w') as f:
                f.write(fixed_content)
            print("Fixed recursive_diff_dict function")
EOF
    log_warn "retrying loading texify again..."
    python3 -c "import texify; from texify.model.model import load_model; from texify.model.processor import load_processor; model = load_model(); processor = load_processor()" || {
        log_error "texify import failed, exitting with error"
        exit 1
    }
}

log_info "Setup completed successfully!"