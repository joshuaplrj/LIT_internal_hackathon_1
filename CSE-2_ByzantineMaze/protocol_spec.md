# Byzantine Maze - Protocol Specification

## Overview

This document specifies a Byzantine Fault Tolerant (BFT) consensus protocol designed for asynchronous networks with network partitions and adaptive adversaries.

## System Model

### Network Assumptions
- **Asynchronous**: Messages have variable, unbounded delays but are eventually delivered
- **Partitions**: Network can undergo temporary partitions of up to T seconds
- **Nodes**: N = 3f + 1 nodes, where up to f can be Byzantine

### Adversary Model
- **Adaptive**: Byzantine nodes can observe all messages and strategically respond
- **Capabilities**: Byzantine nodes can:
  - Send conflicting messages to different nodes
  - Delay messages strategically
  - Send invalid/malformed messages
  - Collude with other Byzantine nodes

## Protocol Description

### Message Types

| Message | Description | Sender |
|---------|-------------|--------|
| REQUEST | Client request for consensus | Client |
| PRE_PREPARE | Primary proposes value | Primary |
| PREPARE | Node agrees with proposal | Any node |
| COMMIT | Node commits to value | Any node |
| VIEW_CHANGE | Request to change view | Any node |
| NEW_VIEW | New view confirmation | New primary |

### Normal Case Operation

```
Client          Primary         Replica 1      Replica 2      Replica 3
   |               |               |               |               |
   |---REQUEST---->|               |               |               |
   |               |---PRE_PREPARE>|               |               |
   |               |---PRE_PREPARE-|-------------->|               |
   |               |---PRE_PREPARE-|---------------|-------------->|
   |               |               |               |               |
   |               |<---PREPARE----|               |               |
   |               |<---PREPARE----|---------------|               |
   |               |<---PREPARE----|---------------|---------------|
   |               |               |               |               |
   |               |---COMMIT----->|               |               |
   |               |---COMMIT------|-------------->|               |
   |               |---COMMIT------|---------------|-------------->|
   |               |               |               |               |
   |               |<---COMMIT-----|               |               |
   |               |<---COMMIT-----|---------------|               |
   |               |<---COMMIT-----|---------------|---------------|
   |               |               |               |               |
   |<--REPLY-------|               |               |               |
```

### Phase 1: Pre-Prepare

1. Client sends REQUEST to primary
2. Primary assigns sequence number and broadcasts PRE_PREPARE
3. PRE_PREPARE contains: (view, sequence, value, digest)

### Phase 2: Prepare

1. Upon receiving valid PRE_PREPARE, replica broadcasts PREPARE
2. Replica collects 2f+1 PREPARE messages for (view, sequence)
3. Value is "prepared" when 2f+1 matching PREPAREs received

### Phase 3: Commit

1. When value is prepared, replica broadcasts COMMIT
2. Replica collects 2f+1 COMMIT messages for (view, sequence)
3. Value is "committed" when 2f+1 matching COMMITs received
4. Replica executes request and sends REPLY to client

### View Change Protocol

Triggered when:
- Primary is suspected faulty (timeout on PRE_PREPARE)
- View change message received with higher view number

```
Node 1          Node 2          Node 3          Node 4 (New Primary)
   |               |               |               |
   |--VIEW_CHANGE->|               |               |
   |--VIEW_CHANGE--|-------------->|               |
   |--VIEW_CHANGE--|---------------|-------------->|
   |               |               |               |
   |               |--VIEW_CHANGE->|               |
   |               |--VIEW_CHANGE--|-------------->|
   |               |               |               |
   |               |               |--VIEW_CHANGE->|
   |               |               |               |
   |               |               |<---NEW_VIEW---|
   |               |<---NEW_VIEW---|               |
   |<---NEW_VIEW---|               |               |
```

## Safety Properties

### Property 1: Agreement
If any honest node decides on value v, then all honest nodes that decide will decide on v.

**Proof sketch**: 
- To decide, a node needs 2f+1 COMMIT messages
- Any two sets of 2f+1 nodes intersect in at least f+1 honest nodes
- Honest nodes only COMMIT after seeing 2f+1 PREPAREs
- Therefore, all honest nodes that decide must have seen the same value

### Property 2: Validity
If all honest nodes propose the same value v, then v will be decided.

**Proof sketch**:
- Primary will receive REQUEST and broadcast PRE_PREPARE
- All honest nodes will send PREPARE for v
- 2f+1 PREPAREs will be collected (f Byzantine + f+1 honest)
- Consensus proceeds normally

### Property 3: Termination (under partial synchrony)
Eventually, all honest nodes will decide.

**Note**: In fully asynchronous networks, FLP impossibility applies. This protocol guarantees termination under partial synchrony assumptions (eventual message delivery within unknown bound Δ).

## Liveness Guarantees

### View Change Liveness
- If primary is faulty, honest nodes will timeout and initiate view change
- New primary is deterministic (round-robin)
- Eventually, an honest primary will be selected

### Partition Tolerance
- Protocol maintains safety during partitions
- Liveness resumes after partition heals
- View changes may be triggered by partition-induced timeouts

## Complexity Analysis

### Message Complexity
- Normal case: O(n²) messages per consensus instance
- View change: O(n²) messages

### Time Complexity (under synchrony)
- Normal case: 3 message delays
- View change: 5 message delays

### Storage Complexity
- O(n) messages per sequence number
- Garbage collection after decision

## Implementation Notes

### Cryptographic Assumptions
- Digital signatures for authentication
- Hash functions for message digests
- PKI for node identity

### Optimization Opportunities
1. **Batching**: Group multiple requests into single consensus
2. **Pipelining**: Overlap consensus instances
3. **Fast path**: Optimistic commit with 2f+1 messages
4. **Checkpointing**: Garbage collect old sequence numbers

## Test Scenarios

### Scenario 1: Normal Operation
- 10 nodes, 3 Byzantine
- No partitions
- Expected: All honest nodes decide same values

### Scenario 2: Network Partition
- 10 nodes split into groups of 6 and 4
- Partition lasts 5 seconds
- Expected: Safety maintained, liveness resumes after heal

### Scenario 3: Adaptive Adversary
- Byzantine nodes observe and strategically delay
- Expected: Protocol eventually decides despite delays

### Scenario 4: Primary Failure
- Primary is Byzantine and doesn't send PRE_PREPARE
- Expected: View change triggered, new primary elected

## References

1. Castro, M., & Liskov, B. (1999). Practical Byzantine Fault Tolerance.
2. Lamport, L., Shostak, R., & Pease, M. (1982). The Byzantine Generals Problem.
3. Fischer, M. J., Lynch, N. A., & Paterson, M. S. (1985). Impossibility of Distributed Consensus with One Faulty Process.
