# CYBER-5: Zero-Day Factory — Automated Vulnerability Discovery

## Overview

You are given **5 compiled binary executables** (ELF format, x86-64, no source code, no debug symbols) that are networked services listening on various ports. Each binary contains **at least 2 memory corruption vulnerabilities**. Your task is to build an automated pipeline to discover and exploit these vulnerabilities.

## Challenge Binaries

The 5 binaries simulate different network services:

| Binary | Service | Port | Description |
|---|---|---|---|
| `vuln_server_1` | Echo Server | 9001 | Simple echo service with custom protocol |
| `vuln_server_2` | File Transfer | 9002 | FTP-like file transfer service |
| `vuln_server_3` | Chat Server | 9003 | Multi-user chat with authentication |
| `vuln_server_4` | Game Server | 9004 | Simple multiplayer game server |
| `vuln_server_5` | API Gateway | 9005 | REST API proxy with caching |

## Vulnerability Types

Each binary contains at least 2 of the following vulnerability types:

- **Stack Buffer Overflow**: Writing beyond stack-allocated buffer bounds
- **Heap Buffer Overflow**: Writing beyond heap-allocated buffer bounds
- **Use-After-Free**: Accessing memory after it has been freed
- **Format String**: Uncontrolled format string in printf-family functions
- **Integer Overflow**: Arithmetic overflow leading to buffer overflow
- **Off-by-One**: Single byte overflow due to fencepost error

## Task

Build an **automated vulnerability discovery pipeline** that:

1. **Static Analysis**
   - Disassemble the binary
   - Reconstruct control flow graph
   - Identify potentially vulnerable functions
   - Perform data flow analysis

2. **Dynamic Analysis**
   - Fuzzing (coverage-guided, grammar-based, or hybrid)
   - Symbolic execution
   - Taint analysis
   - Crash detection and triage

3. **Exploit Development**
   - Determine exploitability of crashes
   - Develop proof-of-concept exploits
   - Demonstrate controlled EIP/RIP hijack

## Constraints

- Must run on provided Linux environment
- No commercial tools (IDA Pro) — use Ghidra/Rizin/Binary Ninja (free versions)
- Must not cause denial-of-service to evaluation environment
- ASLR is disabled for testing

## Deliverables

1. **Pipeline Source Code**: Your automated analysis tools
2. **Vulnerability Report**: For each binary:
   - Vulnerability type and location
   - Severity rating (CVSS score)
   - Exploitability assessment
   - Triggering input
3. **Proof-of-Concept Exploits**: At least 5 total (1 per binary minimum)
4. **Performance Metrics**:
   - Code coverage achieved
   - Crashes found
   - Time taken
   - False positive rate

## Scoring

| Criterion | Points |
|---|---|
| Number of vulnerabilities found (out of 10+) | 40 |
| Localization accuracy | 20 |
| Exploit reliability | 25 |
| Pipeline automation quality | 15 |

## Getting Started

1. **Setup environment:**
   ```bash
   ./setup.sh
   ```

2. **Run the binaries:**
   ```bash
   ./run_servers.sh
   ```

3. **Start your analysis:**
   ```bash
   python pipeline.py --binary vuln_server_1
   ```

## Recommended Tools

- **Disassembly/Decompilation**: Ghidra, Rizin/Cutter
- **Fuzzing**: AFL++, libFuzzer, Honggfuzz
- **Symbolic Execution**: angr, Triton, KLEE
- **Debugging**: GDB with pwndbg/GEF, rr
- **Exploit Development**: pwntools, ROPgadget

## Tips

1. Start with static analysis to understand the binary structure
2. Use fuzzing to find low-hanging fruit quickly
3. Symbolic execution can find deeper bugs but is slower
4. Focus on input parsing and network handling code
5. Look for custom memory allocators or data structures
