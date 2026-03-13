#!/bin/bash
# Setup script for ZeroDayFactory challenge

echo "=== ZeroDayFactory Setup ==="

# Create directories
mkdir -p binaries
mkdir -p crashes
mkdir -p exploits
mkdir -p analysis_results

# Check for required tools
echo "Checking for required tools..."

check_tool() {
    if command -v $1 &> /dev/null; then
        echo "  ✓ $1 found"
        return 0
    else
        echo "  ✗ $1 not found"
        return 1
    fi
}

check_tool gdb
check_tool objdump
check_tool readelf
check_tool strings
check_tool file

# Optional tools
echo ""
echo "Optional tools (recommended):"
check_tool ghidra
check_tool rizin
check_tool afl-fuzz
check_tool angr

# Compile challenge binaries (simulated - in real challenge these would be pre-compiled)
echo ""
echo "Setting up challenge binaries..."

# Note: In the actual challenge, binaries would be provided pre-compiled
# This is a placeholder for the setup process

cat > binaries/README.txt << EOF
Challenge binaries should be placed in this directory:

- vuln_server_1 (Echo Server, port 9001)
- vuln_server_2 (File Transfer, port 9002)
- vuln_server_3 (Chat Server, port 9003)
- vuln_server_4 (Game Server, port 9004)
- vuln_server_5 (API Gateway, port 9005)

All binaries are ELF x86-64, stripped, with ASLR disabled.
EOF

echo "Setup complete!"
echo ""
echo "Next steps:"
echo "  1. Place challenge binaries in ./binaries/"
echo "  2. Run ./run_servers.sh to start the services"
echo "  3. Run your analysis pipeline"
