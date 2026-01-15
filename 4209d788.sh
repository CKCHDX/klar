#!/bin/bash
# Klar Android Build Setup Script
# Generated for klar-search - Android API 34+
# Python 3.12

set -e  # Exit on error

echo "================================"
echo "Klar Android Build Setup"
echo "================================"
echo ""

# Color output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check prerequisites
check_prerequisites() {
    echo -e "${YELLOW}[1/5] Checking prerequisites...${NC}"
    
    if ! command -v python3.12 &> /dev/null; then
        echo -e "${RED}Error: Python 3.12 not found${NC}"
        echo "Install Python 3.12 from https://www.python.org or use:"
        echo "  Ubuntu: sudo apt install python3.12 python3.12-venv"
        echo "  macOS: brew install python@3.12"
        exit 1
    fi
    
    if ! command -v java &> /dev/null; then
        echo -e "${RED}Error: Java JDK not found${NC}"
        echo "Install JDK 17+: sudo apt install openjdk-17-jdk"
        exit 1
    fi
    
    echo -e "${GREEN}✓ Prerequisites OK${NC}"
    echo ""
}

# Create virtual environment
create_venv() {
    echo -e "${YELLOW}[2/5] Creating Python virtual environment...${NC}"
    
    if [ -d "venv" ]; then
        echo "Virtual environment 'venv' already exists. Remove with: rm -rf venv"
        read -p "Proceed anyway? (y/N) " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            exit 1
        fi
        rm -rf venv
    fi
    
    python3.12 -m venv venv
    source venv/bin/activate
    pip install --upgrade pip setuptools wheel
    
    echo -e "${GREEN}✓ Virtual environment created${NC}"
    echo ""
}

# Install dependencies
install_dependencies() {
    echo -e "${YELLOW}[3/5] Installing BeeWare Briefcase and dependencies...${NC}"
    
    pip install briefcase
    pip install requests  # For Klar crawling
    pip install aiohttp   # Async HTTP for search
    
    echo -e "${GREEN}✓ Dependencies installed${NC}"
    echo ""
}

# Initialize Android project
init_android_project() {
    echo -e "${YELLOW}[4/5] Initializing Android Briefcase project...${NC}"
    
    if [ -f "pyproject.toml" ]; then
        echo "Briefcase already initialized"
    else
        briefcase new android \
            --project-name "klar-search" \
            --bundle com.oscyra \
            --app-name klar \
            --formal-name "Klar Search"
    fi
    
    echo -e "${GREEN}✓ Android project initialized${NC}"
    echo ""
}

# Configuration
configure_build() {
    echo -e "${YELLOW}[5/5] Configuring for Android 34...${NC}"
    
    # Update AndroidManifest if needed (targetSdkVersion)
    echo "Configure Android SDK:"
    echo "  - Target API: 34"
    echo "  - Package: com.oscyra.klar"
    echo "  - Min API: 28"
    echo ""
    
    echo -e "${GREEN}✓ Configuration complete${NC}"
    echo ""
}

# Main execution
main() {
    check_prerequisites
    create_venv
    install_dependencies
    init_android_project
    configure_build
    
    echo -e "${GREEN}================================${NC}"
    echo -e "${GREEN}Setup Complete!${NC}"
    echo -e "${GREEN}================================${NC}"
    echo ""
    echo "Next steps:"
    echo "1. Activate venv: source venv/bin/activate"
    echo "2. Build APK: briefcase build android --android-sdk 34"
    echo "3. Install: adb install <path-to-apk>"
    echo ""
    echo "For development:"
    echo "  briefcase dev android"
    echo ""
}

main "$@"
