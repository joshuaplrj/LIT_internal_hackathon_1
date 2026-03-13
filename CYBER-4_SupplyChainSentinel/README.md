# CYBER-4: Supply Chain Sentinel — Software Supply Chain Attack Detection

## Overview

Build a detection system for **software supply chain attacks** across npm, PyPI, and Docker Hub dependencies used by 50 internal microservices.

## Data Provided

| Data | Description |
|---|---|
| Dependency graph | 500 packages across 50 services (JSON) |
| Source code | 50 microservice snapshots |
| SBOM | Software Bill of Materials per service |
| Anomaly reports | Unexpected network connections, high CPU, data access |

## Task

### 1. Vulnerability Scanning

Scan all 500 dependencies for:
- Known CVEs
- Typosquatting
- Malicious patterns
- Known vulnerable versions

### 2. Supply Chain Attack Detection

Identify compromised packages:
- Injected malware
- Dependency confusion
- Account takeover
- Backdoor injection

### 3. Attack Analysis

For each compromised package:
- **Attack vector**: How was it compromised?
- **Payload**: What does the malicious code do?
- **Blast radius**: Which services are affected?

### 4. Remediation Plan

Prioritized by risk:
- Patched versions
- Alternative packages
- Architectural changes

## Detection Techniques

### Static Analysis

```python
# Check for suspicious patterns
SUSPICIOUS_PATTERNS = [
    r'eval\(',           # Code execution
    r'exec\(',           # Code execution
    r'child_process',    # Shell access
    r'base64',           # Obfuscation
    r'crypto\.createHash', # Cryptomining
    r'https?://[^\s]+\.(ru|cn|tk)',  # Suspicious domains
    r'process\.env',     # Environment variable theft
    r'fs\.readFile',     # File system access
]

def scan_package(package_path):
    findings = []
    for file in get_source_files(package_path):
        content = read_file(file)
        for pattern in SUSPICIOUS_PATTERNS:
            if re.search(pattern, content):
                findings.append({
                    'file': file,
                    'pattern': pattern,
                    'line': get_line_number(content, pattern)
                })
    return findings
```

### Dependency Confusion Detection

```python
def check_dependency_confusion(package_name, internal_registry):
    # Check if package exists in public registry with same name
    public_version = get_npm_version(package_name)
    internal_version = get_internal_version(package_name, internal_registry)
    
    if public_version and internal_version:
        if public_version > internal_version:
            return {
                'risk': 'HIGH',
                'reason': 'Public package has higher version than internal'
            }
    
    # Check for typosquatting
    similar_names = find_similar_packages(package_name)
    if similar_names:
        return {
            'risk': 'MEDIUM',
            'reason': f'Similar packages exist: {similar_names}'
        }
    
    return {'risk': 'LOW'}
```

### Behavioral Analysis

```python
def analyze_behavior(package):
    behaviors = {
        'network_access': False,
        'file_system_access': False,
        'process_execution': False,
        'environment_access': False,
        'obfuscation': False
    }
    
    # Run in sandbox
    result = sandbox_execute(package.install_script)
    
    # Monitor system calls
    syscalls = result.get_syscalls()
    
    if any('connect' in sc for sc in syscalls):
        behaviors['network_access'] = True
    if any('open' in sc for sc in syscalls):
        behaviors['file_system_access'] = True
    if any('exec' in sc for sc in syscalls):
        behaviors['process_execution'] = True
    
    return behaviors
```

### Typosquatting Detection

```python
def detect_typosquatting(package_name, popular_packages):
    for popular in popular_packages:
        # Levenshtein distance
        distance = levenshtein(package_name, popular)
        if distance == 1:
            return {
                'risk': 'HIGH',
                'similar_to': popular,
                'distance': distance
            }
        
        # Homoglyph detection
        if has_homoglyphs(package_name, popular):
            return {
                'risk': 'HIGH',
                'similar_to': popular,
                'type': 'homoglyph'
            }
    
    return {'risk': 'LOW'}
```

## Blast Radius Analysis

```python
def analyze_blast_radius(compromised_package, dependency_graph):
    affected_services = []
    
    # Direct dependents
    direct = dependency_graph.get_dependents(compromised_package)
    
    # Transitive dependents
    transitive = set()
    for service in direct:
        transitive.update(get_all_dependents(service, dependency_graph))
    
    return {
        'direct': direct,
        'transitive': list(transitive),
        'total_affected': len(direct) + len(transitive)
    }
```

## Deliverables

1. **Detection Tool**: Source code + results
2. **Compromise Report**: Per affected package
3. **Blast Radius Analysis**: Service impact mapping
4. **Remediation Plan**: Prioritized actions

## Scoring

| Criterion | Points |
|---|---|
| Detection accuracy | 30 |
| Attack vector identification | 25 |
| Blast radius analysis | 20 |
| Remediation quality | 15 |
| Tool automation | 10 |

## Project Structure

```
CYBER-4_SupplyChainSentinel/
├── README.md
├── data/
│   ├── dependency_graph.json
│   ├── services/
│   ├── sbom/
│   └── anomalies.json
├── scanner/
│   ├── static_analysis.py
│   ├── dependency_checker.py
│   ├── typosquatting.py
│   └── behavioral.py
├── analysis/
│   ├── blast_radius.py
│   ├── attack_vector.py
│   └── payload_analysis.py
├── remediation/
│   ├── planner.py
│   └── patches/
├── run_scan.py
└── solution_template.py
```

## Tips

1. Start with known vulnerability databases (NVD, Snyk, GitHub Advisory)
2. Typosquatting is common - check Levenshtein distance
3. Check install scripts (preinstall, postinstall) for malicious code
4. Transitive dependencies are often the weak link
5. Behavioral analysis in a sandbox catches what static analysis misses
