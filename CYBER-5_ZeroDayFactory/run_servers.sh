#!/bin/bash
# Run all challenge servers

echo "=== Starting ZeroDayFactory Challenge Servers ==="

# Disable ASLR
echo "Disabling ASLR..."
echo 0 | sudo tee /proc/sys/kernel/randomize_va_space 2>/dev/null || echo "  (Note: ASLR disable requires sudo)"

# Kill any existing servers
echo "Stopping any existing servers..."
pkill -f vuln_server 2>/dev/null
sleep 1

# Start servers
echo ""
echo "Starting servers..."

start_server() {
    local binary=$1
    local port=$2
    local name=$3
    
    if [ -f "binaries/$binary" ]; then
        echo "  Starting $name on port $port..."
        ./binaries/$binary $port &
        echo "    PID: $!"
    else
        echo "  ✗ $name binary not found"
    fi
}

start_server "vuln_server_1" "9001" "Echo Server"
start_server "vuln_server_2" "9002" "File Transfer"
start_server "vuln_server_3" "9003" "Chat Server"
start_server "vuln_server_4" "9004" "Game Server"
start_server "vuln_server_5" "9005" "API Gateway"

echo ""
echo "Servers started. Press Ctrl+C to stop all servers."
echo ""
echo "To test connectivity:"
echo "  nc localhost 9001  # Echo Server"
echo "  nc localhost 9002  # File Transfer"
echo "  nc localhost 9003  # Chat Server"
echo "  nc localhost 9004  # Game Server"
echo "  nc localhost 9005  # API Gateway"

# Wait for interrupt
trap 'echo ""; echo "Stopping servers..."; pkill -f vuln_server; exit 0' INT
wait
