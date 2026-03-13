"""
Generate challenge binaries for ZeroDayFactory

This script creates simulated vulnerable servers for testing the pipeline.
In a real challenge, these would be compiled C binaries.
"""

import os
import socket
import threading
import struct
import random
import time


class VulnerableEchoServer:
    """Echo server with stack buffer overflow vulnerability"""
    
    def __init__(self, port: int):
        self.port = port
        self.running = False
    
    def handle_client(self, client_socket):
        """Handle client connection - VULNERABLE"""
        try:
            # Receive data
            data = client_socket.recv(4096)
            
            # VULNERABILITY: No bounds checking on buffer copy
            # Simulates: char buffer[64]; strcpy(buffer, data);
            buffer_size = 64
            
            if len(data) > buffer_size:
                # In a real binary, this would overflow the stack
                print(f"[Echo Server] Buffer overflow detected! Received {len(data)} bytes, buffer is {buffer_size}")
                # Simulate crash
                raise Exception("Segmentation fault (simulated)")
            
            # Echo back
            client_socket.send(data)
            
        except Exception as e:
            print(f"[Echo Server] Error: {e}")
        finally:
            client_socket.close()
    
    def run(self):
        """Run the server"""
        self.running = True
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server.bind(('localhost', self.port))
        server.listen(5)
        server.settimeout(1.0)
        
        print(f"[Echo Server] Listening on port {self.port}")
        
        while self.running:
            try:
                client, addr = server.accept()
                thread = threading.Thread(target=self.handle_client, args=(client,))
                thread.start()
            except socket.timeout:
                continue
            except Exception as e:
                print(f"[Echo Server] Error: {e}")
        
        server.close()


class VulnerableFileTransfer:
    """File transfer server with format string vulnerability"""
    
    def __init__(self, port: int):
        self.port = port
        self.running = False
    
    def handle_client(self, client_socket):
        """Handle client connection - VULNERABLE"""
        try:
            # Receive filename
            data = client_socket.recv(1024).decode('utf-8', errors='ignore')
            
            # VULNERABILITY: Format string in logging
            # Simulates: printf(data); instead of printf("%s", data);
            if '%' in data:
                print(f"[File Transfer] Format string attack detected: {data}")
                # In real binary, this could leak memory or write to arbitrary addresses
                # Simulate information disclosure
                response = f"Error: Invalid filename. Stack data: {hex(id(data))}"
            else:
                response = f"File not found: {data}"
            
            client_socket.send(response.encode())
            
        except Exception as e:
            print(f"[File Transfer] Error: {e}")
        finally:
            client_socket.close()
    
    def run(self):
        """Run the server"""
        self.running = True
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server.bind(('localhost', self.port))
        server.listen(5)
        server.settimeout(1.0)
        
        print(f"[File Transfer] Listening on port {self.port}")
        
        while self.running:
            try:
                client, addr = server.accept()
                thread = threading.Thread(target=self.handle_client, args=(client,))
                thread.start()
            except socket.timeout:
                continue
            except Exception as e:
                print(f"[File Transfer] Error: {e}")
        
        server.close()


class VulnerableChatServer:
    """Chat server with use-after-free vulnerability"""
    
    def __init__(self, port: int):
        self.port = port
        self.running = False
        self.sessions = {}  # Simulates heap-allocated session objects
    
    def handle_client(self, client_socket):
        """Handle client connection - VULNERABLE"""
        session_id = None
        try:
            # Receive auth
            data = client_socket.recv(1024)
            
            # Parse session ID (4 bytes)
            if len(data) >= 4:
                session_id = struct.unpack('<I', data[:4])[0]
            
            # VULNERABILITY: Use-after-free
            # Session can be deleted but pointer still used
            if session_id in self.sessions:
                session = self.sessions[session_id]
                
                # Check if session was marked as deleted (simulating free)
                if session.get('deleted', False):
                    print(f"[Chat Server] Use-after-free detected! Session {session_id} was deleted")
                    # In real binary, this accesses freed memory
                    raise Exception("Use-after-free (simulated)")
                
                # Process message
                message = data[4:].decode('utf-8', errors='ignore')
                response = f"Echo: {message}"
            else:
                # Create new session
                self.sessions[session_id] = {'deleted': False, 'data': 'new'}
                response = "New session created"
            
            client_socket.send(response.encode())
            
        except Exception as e:
            print(f"[Chat Server] Error: {e}")
        finally:
            client_socket.close()
    
    def delete_session(self, session_id: int):
        """Delete a session (simulates free)"""
        if session_id in self.sessions:
            self.sessions[session_id]['deleted'] = True
    
    def run(self):
        """Run the server"""
        self.running = True
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server.bind(('localhost', self.port))
        server.listen(5)
        server.settimeout(1.0)
        
        print(f"[Chat Server] Listening on port {self.port}")
        
        while self.running:
            try:
                client, addr = server.accept()
                thread = threading.Thread(target=self.handle_client, args=(client,))
                thread.start()
            except socket.timeout:
                continue
            except Exception as e:
                print(f"[Chat Server] Error: {e}")
        
        server.close()


class VulnerableGameServer:
    """Game server with integer overflow vulnerability"""
    
    def __init__(self, port: int):
        self.port = port
        self.running = False
    
    def handle_client(self, client_socket):
        """Handle client connection - VULNERABLE"""
        try:
            # Receive game data
            data = client_socket.recv(1024)
            
            if len(data) >= 8:
                # Parse: num_items (4 bytes), item_size (4 bytes)
                num_items = struct.unpack('<I', data[:4])[0]
                item_size = struct.unpack('<I', data[4:8])[0]
                
                # VULNERABILITY: Integer overflow in size calculation
                # Simulates: total_size = num_items * item_size; malloc(total_size);
                total_size = num_items * item_size
                
                # Check for overflow
                if num_items > 0 and item_size > 0:
                    if total_size // num_items != item_size:
                        print(f"[Game Server] Integer overflow detected! {num_items} * {item_size} = {total_size}")
                        # In real binary, this could lead to heap overflow
                        raise Exception("Integer overflow (simulated)")
                
                # Check for excessive allocation
                if total_size > 1024 * 1024:  # 1MB limit
                    print(f"[Game Server] Excessive allocation: {total_size} bytes")
                    raise Exception("Allocation too large")
                
                response = f"Processed {num_items} items of size {item_size}"
            else:
                response = "Invalid data"
            
            client_socket.send(response.encode())
            
        except Exception as e:
            print(f"[Game Server] Error: {e}")
        finally:
            client_socket.close()
    
    def run(self):
        """Run the server"""
        self.running = True
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server.bind(('localhost', self.port))
        server.listen(5)
        server.settimeout(1.0)
        
        print(f"[Game Server] Listening on port {self.port}")
        
        while self.running:
            try:
                client, addr = server.accept()
                thread = threading.Thread(target=self.handle_client, args=(client,))
                thread.start()
            except socket.timeout:
                continue
            except Exception as e:
                print(f"[Game Server] Error: {e}")
        
        server.close()


class VulnerableAPIGateway:
    """API gateway with heap overflow vulnerability"""
    
    def __init__(self, port: int):
        self.port = port
        self.running = False
        self.cache = {}  # Simulates heap-allocated cache
    
    def handle_client(self, client_socket):
        """Handle client connection - VULNERABLE"""
        try:
            # Receive request
            data = client_socket.recv(4096)
            
            # Parse request (simplified)
            lines = data.decode('utf-8', errors='ignore').split('\n')
            
            if lines:
                # VULNERABILITY: Heap overflow in cache key handling
                # Simulates: char *key = malloc(32); strcpy(key, user_input);
                key = lines[0][:100]  # User controls this
                
                # Check for overflow
                if len(key) > 32:
                    print(f"[API Gateway] Heap overflow detected! Key length: {len(key)}")
                    # In real binary, this overflows heap buffer
                    raise Exception("Heap overflow (simulated)")
                
                # Store in cache
                self.cache[key] = {'data': 'cached', 'time': time.time()}
                
                response = f"Cached: {key}"
            else:
                response = "Invalid request"
            
            client_socket.send(response.encode())
            
        except Exception as e:
            print(f"[API Gateway] Error: {e}")
        finally:
            client_socket.close()
    
    def run(self):
        """Run the server"""
        self.running = True
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server.bind(('localhost', self.port))
        server.listen(5)
        server.settimeout(1.0)
        
        print(f"[API Gateway] Listening on port {self.port}")
        
        while self.running:
            try:
                client, addr = server.accept()
                thread = threading.Thread(target=self.handle_client, args=(client,))
                thread.start()
            except socket.timeout:
                continue
            except Exception as e:
                print(f"[API Gateway] Error: {e}")
        
        server.close()


def main():
    """Start all servers"""
    print("=== ZeroDayFactory Challenge Servers ===\n")
    
    servers = [
        VulnerableEchoServer(9001),
        VulnerableFileTransfer(9002),
        VulnerableChatServer(9003),
        VulnerableGameServer(9004),
        VulnerableAPIGateway(9005),
    ]
    
    threads = []
    for server in servers:
        thread = threading.Thread(target=server.run)
        thread.daemon = True
        thread.start()
        threads.append(thread)
    
    print("\nAll servers started. Press Ctrl+C to stop.\n")
    
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nShutting down servers...")


if __name__ == "__main__":
    main()
