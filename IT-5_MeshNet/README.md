# IT-5: MeshNet — Decentralized IoT Fleet Management Protocol

## Overview

Design a **self-organizing mesh network** for 10,000 IoT sensors across 500 km² of farmland with constrained battery life and unreliable connectivity.

## Requirements

| Requirement | Target |
|---|---|
| Network size | 10,000 nodes |
| Coverage area | 500 km² |
| Battery life | 2 years |
| Topology adaptation | < 60 seconds |
| Data delivery | < 5 minutes |
| Node loss tolerance | Up to 50% |

## Network Model

```
┌─────────────────────────────────────────────────────────────┐
│                      Gateway Node                            │
│                    (Internet Connected)                      │
└─────────────────────────────────────────────────────────────┘
                              ▲
                              │
        ┌─────────────────────┼─────────────────────┐
        │                     │                     │
        ▼                     ▼                     ▼
┌───────────────┐    ┌───────────────┐    ┌───────────────┐
│  Router Node  │    │  Router Node  │    │  Router Node  │
│   (Cluster    │    │   (Cluster    │    │   (Cluster    │
│    Head)      │    │    Head)      │    │    Head)      │
└───────────────┘    └───────────────┘    └───────────────┘
        │                     │                     │
   ┌────┴────┐           ┌────┴────┐           ┌────┴────┐
   ▼         ▼           ▼         ▼           ▼         ▼
┌─────┐   ┌─────┐     ┌─────┐   ┌─────┐     ┌─────┐   ┌─────┐
│Sensor│   │Sensor│     │Sensor│   │Sensor│     │Sensor│   │Sensor│
└─────┘   └─────┘     └─────┘   └─────┘     └─────┘   └─────┘
```

## Radio Propagation Model

### Log-Distance Path Loss

$$PL(d) = PL(d_0) + 10n\log_{10}\left(\frac{d}{d_0}\right) + X_\sigma$$

Where:
- $PL(d_0)$ = path loss at reference distance
- $n$ = path loss exponent (2-4 for outdoor)
- $X_\sigma$ = shadow fading (Gaussian)

### Link Budget

$$P_r = P_t + G_t + G_r - PL(d)$$

## Battery Model

### Energy Consumption

| State | Current | Duration |
|---|---|---|
| Sleep | 10 μA | Most of time |
| Listen | 20 mA | When receiving |
| Transmit | 50 mA | When sending |
| Processing | 15 mA | When computing |

### Battery Life Calculation

$$T_{battery} = \frac{C_{battery}}{I_{avg}}$$

Where:
$$I_{avg} = \frac{\sum(I_{state} \times t_{state})}{T_{total}}$$

## Routing Protocol

### Adaptive Routing Algorithm

```python
class MeshRouter:
    def __init__(self, node_id, battery_level, position):
        self.node_id = node_id
        self.battery = battery_level
        self.position = position
        self.routing_table = {}
        self.neighbors = {}
    
    def select_route(self, destination):
        # Multi-objective routing
        candidates = self.get_routes(destination)
        
        best_route = None
        best_score = float('inf')
        
        for route in candidates:
            # Score based on multiple factors
            score = (
                0.4 * route.hop_count +
                0.3 * route.expected_latency +
                0.2 * route.energy_cost +
                0.1 * route.reliability
            )
            
            if score < best_score:
                best_score = score
                best_route = route
        
        return best_route
    
    def update_topology(self, neighbor_id, rssi, battery):
        self.neighbors[neighbor_id] = {
            'rssi': rssi,
            'battery': battery,
            'last_seen': time.time()
        }
        
        # Trigger route recalculation if needed
        if self.needs_reroute(neighbor_id):
            self.recalculate_routes()
```

### Energy-Aware Clustering

```python
def elect_cluster_head(nodes):
    # Weighted election based on:
    # - Battery level (higher is better)
    # - Centrality (more central is better)
    # - Recent activity (avoid overuse)
    
    scores = {}
    for node in nodes:
        scores[node.id] = (
            0.5 * node.battery_level +
            0.3 * node.centrality +
            0.2 * (1 - node.recent_usage)
        )
    
    # Node with highest score becomes cluster head
    return max(scores, key=scores.get)
```

## Data Collection Protocol

### Trickle Algorithm

```python
class TrickleTimer:
    def __init__(self, imin=1, imax=16, k=1):
        self.I = imin  # Interval
        self.imin = imin
        self.imax = imax
        self.k = k  # Redundancy constant
        self.c = 0  # Counter
    
    def transmit(self):
        t = random.uniform(self.I/2, self.I)
        sleep(t)
        
        if self.c < self.k:
            self.send_data()
        
        self.I = min(self.I * 2, self.imax)
        self.c = 0
    
    def receive_inconsistent(self):
        self.I = self.imin
        self.c = 0
```

## OTA Update Protocol

```python
class OTAUpdater:
    def __init__(self, firmware_hash, chunk_size=256):
        self.firmware_hash = firmware_hash
        self.chunk_size = chunk_size
        self.received_chunks = {}
    
    def receive_chunk(self, chunk_id, data, signature):
        # Verify signature
        if not verify_signature(data, signature):
            return False
        
        # Store chunk
        self.received_chunks[chunk_id] = data
        
        # Check if complete
        if self.is_complete():
            firmware = self.assemble_firmware()
            if hash(firmware) == self.firmware_hash:
                self.apply_update(firmware)
                return True
        
        return False
    
    def propagate_update(self, neighbors):
        # Epidemic propagation
        for neighbor in neighbors:
            missing_chunks = neighbor.get_missing_chunks()
            for chunk_id in missing_chunks:
                if chunk_id in self.received_chunks:
                    neighbor.receive_chunk(
                        chunk_id,
                        self.received_chunks[chunk_id]
                    )
```

## Simulation

```python
class NetworkSimulator:
    def __init__(self, num_nodes, area_size):
        self.nodes = self.deploy_nodes(num_nodes, area_size)
        self.time = 0
    
    def deploy_nodes(self, num_nodes, area_size):
        nodes = []
        for i in range(num_nodes):
            position = (
                random.uniform(0, area_size),
                random.uniform(0, area_size)
            )
            nodes.append(SensorNode(i, position))
        return nodes
    
    def simulate_step(self, dt):
        # Update radio propagation
        self.update_links()
        
        # Process messages
        self.process_messages()
        
        # Update battery levels
        self.update_batteries(dt)
        
        # Check for failures
        self.check_failures()
        
        self.time += dt
    
    def run(self, duration):
        while self.time < duration:
            self.simulate_step(1.0)  # 1 second steps
```

## Deliverables

1. **Protocol Specification**: Detailed design document
2. **Simulator Source Code**: Complete implementation
3. **Simulation Results**: For 100, 1,000, and 10,000 nodes
4. **Performance Metrics**: Delivery rate, latency, energy, lifetime

## Project Structure

```
IT-5_MeshNet/
├── README.md
├── protocol/
│   ├── routing.py
│   ├── clustering.py
│   ├── data_collection.py
│   └── ota_update.py
├── simulation/
│   ├── network.py
│   ├── node.py
│   ├── radio.py
│   └── battery.py
├── analysis/
│   ├── metrics.py
│   └── visualization.py
├── run_simulation.py
└── solution_template.py
```

## Tips

1. Clustering reduces energy consumption significantly
2. Trickle timer adapts to network conditions
3. Epidemic propagation is robust but energy-intensive
4. Sleep scheduling is critical for battery life
5. Test with realistic node failure patterns
