"""
Byzantine Maze - Network Simulator
Simulates asynchronous network with variable delays, partitions, and Byzantine nodes.
"""

import asyncio
import random
import time
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Set, Callable, Any
from enum import Enum
import json
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(message)s')

class MessageType(Enum):
    PRE_PREPARE = "PRE_PREPARE"
    PREPARE = "PREPARE"
    COMMIT = "COMMIT"
    VIEW_CHANGE = "VIEW_CHANGE"
    NEW_VIEW = "NEW_VIEW"
    REQUEST = "REQUEST"
    REPLY = "REPLY"

@dataclass
class Message:
    msg_type: MessageType
    sender: int
    view: int
    sequence: int
    value: Any
    timestamp: float = field(default_factory=time.time)
    signature: str = ""  # Simplified signature
    
    def to_dict(self):
        return {
            'type': self.msg_type.value,
            'sender': self.sender,
            'view': self.view,
            'sequence': self.sequence,
            'value': self.value,
            'timestamp': self.timestamp
        }

class NetworkPartition:
    """Simulates network partitions"""
    def __init__(self):
        self.partitioned_groups: List[Set[int]] = []
        self.partition_start: Optional[float] = None
        self.partition_duration: float = 0
        
    def create_partition(self, groups: List[Set[int]], duration: float):
        self.partitioned_groups = groups
        self.partition_start = time.time()
        self.partition_duration = duration
        
    def can_communicate(self, node1: int, node2: int) -> bool:
        if not self.partitioned_groups:
            return True
            
        # Check if partition has expired
        if self.partition_start and time.time() - self.partition_start > self.partition_duration:
            self.partitioned_groups = []
            self.partition_start = None
            return True
            
        # Check if nodes are in the same partition group
        for group in self.partitioned_groups:
            if node1 in group and node2 in group:
                return True
        return False

class NetworkSimulator:
    """Simulates asynchronous network with variable delays"""
    
    def __init__(self, num_nodes: int, f: int):
        self.num_nodes = num_nodes
        self.f = f  # Max Byzantine nodes
        self.nodes: Dict[int, 'Node'] = {}
        self.partition = NetworkPartition()
        self.message_log: List[Dict] = []
        self.min_delay = 0.0  # seconds
        self.max_delay = 5.0  # seconds
        self.running = True
        self.logger = logging.getLogger("Network")
        
    def register_node(self, node: 'Node'):
        self.nodes[node.node_id] = node
        
    async def send_message(self, msg: Message, recipient: int):
        """Send message with simulated delay"""
        if not self.running:
            return
            
        # Check partition
        if not self.partition.can_communicate(msg.sender, recipient):
            self.logger.debug(f"Message blocked by partition: {msg.sender} -> {recipient}")
            return
            
        # Simulate network delay
        delay = random.uniform(self.min_delay, self.max_delay)
        
        # Log message
        self.message_log.append({
            **msg.to_dict(),
            'recipient': recipient,
            'delay': delay,
            'delivered_at': time.time() + delay
        })
        
        await asyncio.sleep(delay)
        
        if self.running and recipient in self.nodes:
            await self.nodes[recipient].receive_message(msg)
            
    async def broadcast(self, msg: Message, exclude: Optional[Set[int]] = None):
        """Broadcast message to all nodes"""
        exclude = exclude or set()
        tasks = []
        for node_id in self.nodes:
            if node_id != msg.sender and node_id not in exclude:
                tasks.append(self.send_message(msg, node_id))
        await asyncio.gather(*tasks)
        
    def create_partition(self, duration: float = 10.0):
        """Create a random network partition"""
        nodes = list(self.nodes.keys())
        random.shuffle(nodes)
        
        # Split into 2-3 groups
        num_groups = random.randint(2, 3)
        groups = []
        start = 0
        for i in range(num_groups):
            end = start + len(nodes) // num_groups + (1 if i < len(nodes) % num_groups else 0)
            groups.append(set(nodes[start:end]))
            start = end
            
        self.partition.create_partition(groups, duration)
        self.logger.info(f"Partition created: {groups}, duration: {duration}s")
        return groups
        
    def get_stats(self) -> Dict:
        return {
            'total_messages': len(self.message_log),
            'avg_delay': sum(m['delay'] for m in self.message_log) / max(len(self.message_log), 1),
            'nodes': self.num_nodes,
            'byzantine_limit': self.f
        }

class NodeState(Enum):
    INIT = "INIT"
    PRE_PREPARE = "PRE_PREPARE"
    PREPARE = "PREPARE"
    COMMIT = "COMMIT"
    DECIDED = "DECIDED"
    VIEW_CHANGE = "VIEW_CHANGE"

class Node:
    """Base node implementation"""
    
    def __init__(self, node_id: int, network: NetworkSimulator, is_byzantine: bool = False):
        self.node_id = node_id
        self.network = network
        self.is_byzantine = is_byzantine
        self.view = 0
        self.sequence = 0
        self.state = NodeState.INIT
        self.prepared_values: Dict[int, Set[int]] = {}  # seq -> set of node_ids
        self.committed_values: Dict[int, Set[int]] = {}
        self.decided_values: Dict[int, Any] = {}
        self.message_buffer: List[Message] = []
        self.primary = 0  # Current primary for view
        self.logger = logging.getLogger(f"Node-{node_id}")
        
    def is_primary(self) -> bool:
        return self.node_id == (self.primary + self.view) % self.network.num_nodes
        
    async def receive_message(self, msg: Message):
        """Receive and process message"""
        if self.is_byzantine:
            await self.byzantine_receive(msg)
        else:
            await self.honest_receive(msg)
            
    async def honest_receive(self, msg: Message):
        """Honest node message processing"""
        self.message_buffer.append(msg)
        
        if msg.msg_type == MessageType.REQUEST:
            if self.is_primary():
                await self.start_consensus(msg.value)
                
        elif msg.msg_type == MessageType.PRE_PREPARE:
            if self.validate_pre_prepare(msg):
                await self.send_prepare(msg.sequence, msg.value)
                
        elif msg.msg_type == MessageType.PREPARE:
            self.record_prepare(msg)
            if self.is_prepared(msg.sequence):
                await self.send_commit(msg.sequence, msg.value)
                
        elif msg.msg_type == MessageType.COMMIT:
            self.record_commit(msg)
            if self.is_committed(msg.sequence):
                await self.decide(msg.sequence, msg.value)
                
        elif msg.msg_type == MessageType.VIEW_CHANGE:
            await self.handle_view_change(msg)
            
    async def byzantine_receive(self, msg: Message):
        """Byzantine node - can behave arbitrarily"""
        # Byzantine nodes can:
        # 1. Not respond (silent)
        # 2. Send conflicting messages
        # 3. Delay responses strategically
        # 4. Send invalid messages
        
        behavior = random.choice(['silent', 'conflicting', 'delayed', 'invalid', 'honest'])
        
        if behavior == 'silent':
            pass  # Don't respond
            
        elif behavior == 'conflicting':
            # Send conflicting values to different nodes
            conflicting_msg = Message(
                msg_type=msg.msg_type,
                sender=self.node_id,
                view=msg.view,
                sequence=msg.sequence,
                value=f"CONFLICTING_{random.randint(1000, 9999)}"
            )
            # Send to half the nodes
            targets = random.sample(list(self.network.nodes.keys()), 
                                   len(self.network.nodes) // 2)
            for target in targets:
                await self.network.send_message(conflicting_msg, target)
                
        elif behavior == 'delayed':
            # Delay response significantly
            await asyncio.sleep(random.uniform(3, 5))
            await self.honest_receive(msg)
            
        elif behavior == 'invalid':
            # Send malformed message
            invalid_msg = Message(
                msg_type=MessageType.PREPARE,
                sender=self.node_id,
                view=-1,  # Invalid view
                sequence=-1,
                value=None
            )
            await self.network.broadcast(invalid_msg)
            
        else:  # honest
            await self.honest_receive(msg)
            
    async def start_consensus(self, value: Any):
        """Primary starts consensus on a value"""
        if not self.is_primary():
            return
            
        self.sequence += 1
        msg = Message(
            msg_type=MessageType.PRE_PREPARE,
            sender=self.node_id,
            view=self.view,
            sequence=self.sequence,
            value=value
        )
        await self.network.broadcast(msg)
        
    def validate_pre_prepare(self, msg: Message) -> bool:
        """Validate pre-prepare message"""
        if msg.sender != (self.primary + msg.view) % self.network.num_nodes:
            return False
        if msg.view < self.view:
            return False
        return True
        
    async def send_prepare(self, sequence: int, value: Any):
        """Send prepare message"""
        msg = Message(
            msg_type=MessageType.PREPARE,
            sender=self.node_id,
            view=self.view,
            sequence=sequence,
            value=value
        )
        await self.network.broadcast(msg)
        
    def record_prepare(self, msg: Message):
        """Record prepare message"""
        if msg.sequence not in self.prepared_values:
            self.prepared_values[msg.sequence] = set()
        self.prepared_values[msg.sequence].add(msg.sender)
        
    def is_prepared(self, sequence: int) -> bool:
        """Check if value is prepared (2f+1 prepares)"""
        if sequence not in self.prepared_values:
            return False
        return len(self.prepared_values[sequence]) >= 2 * self.network.f + 1
        
    async def send_commit(self, sequence: int, value: Any):
        """Send commit message"""
        msg = Message(
            msg_type=MessageType.COMMIT,
            sender=self.node_id,
            view=self.view,
            sequence=sequence,
            value=value
        )
        await self.network.broadcast(msg)
        
    def record_commit(self, msg: Message):
        """Record commit message"""
        if msg.sequence not in self.committed_values:
            self.committed_values[msg.sequence] = set()
        self.committed_values[msg.sequence].add(msg.sender)
        
    def is_committed(self, sequence: int) -> bool:
        """Check if value is committed (2f+1 commits)"""
        if sequence not in self.committed_values:
            return False
        return len(self.committed_values[sequence]) >= 2 * self.network.f + 1
        
    async def decide(self, sequence: int, value: Any):
        """Decide on a value"""
        self.decided_values[sequence] = value
        self.state = NodeState.DECIDED
        self.logger.info(f"Decided on sequence {sequence}: {value}")
        
    async def handle_view_change(self, msg: Message):
        """Handle view change message"""
        if msg.view > self.view:
            self.view = msg.view
            self.state = NodeState.VIEW_CHANGE
            self.logger.info(f"View change to {self.view}")
            
    async def request_view_change(self):
        """Request view change (e.g., if primary is suspected faulty)"""
        msg = Message(
            msg_type=MessageType.VIEW_CHANGE,
            sender=self.node_id,
            view=self.view + 1,
            sequence=self.sequence,
            value=None
        )
        await self.network.broadcast(msg)

class AdaptiveAdversary:
    """Controls Byzantine nodes with adaptive strategy"""
    
    def __init__(self, network: NetworkSimulator, byzantine_nodes: List[int]):
        self.network = network
        self.byzantine_nodes = byzantine_nodes
        self.observed_messages: List[Message] = []
        self.strategy = "maximize_disruption"
        
    def observe(self, msg: Message):
        """Observe network messages"""
        self.observed_messages.append(msg)
        
    def get_strategy(self, context: Dict) -> Dict:
        """Determine optimal Byzantine strategy based on observed state"""
        # Analyze message patterns
        honest_prepare_count = sum(1 for m in self.observed_messages 
                                   if m.msg_type == MessageType.PREPARE 
                                   and m.sender not in self.byzantine_nodes)
        
        if honest_prepare_count >= 2 * self.network.f:
            # Consensus is close - try to disrupt with conflicting commits
            return {
                'action': 'conflicting_commits',
                'target_sequences': list(set(m.sequence for m in self.observed_messages 
                                            if m.msg_type == MessageType.PREPARE))
            }
        else:
            # Try to prevent prepare phase completion
            return {
                'action': 'withhold_messages',
                'duration': random.uniform(2, 4)
            }

async def run_simulation(num_nodes: int = 10, duration: float = 60.0):
    """Run a complete Byzantine consensus simulation"""
    
    f = (num_nodes - 1) // 3  # Max Byzantine nodes
    network = NetworkSimulator(num_nodes, f)
    
    # Create nodes
    nodes = []
    byzantine_count = random.randint(1, f)
    byzantine_ids = random.sample(range(num_nodes), byzantine_count)
    
    for i in range(num_nodes):
        is_byzantine = i in byzantine_ids
        node = Node(i, network, is_byzantine)
        network.register_node(node)
        nodes.append(node)
        
    print(f"Network: {num_nodes} nodes, {byzantine_count} Byzantine (max {f})")
    print(f"Byzantine nodes: {byzantine_ids}")
    
    # Create adversary
    adversary = AdaptiveAdversary(network, byzantine_ids)
    
    # Run simulation
    start_time = time.time()
    sequence = 0
    
    while time.time() - start_time < duration:
        # Randomly create partitions
        if random.random() < 0.1:  # 10% chance per iteration
            partition_duration = random.uniform(2, 10)
            network.create_partition(partition_duration)
            
        # Submit values for consensus
        if random.random() < 0.3:  # 30% chance to submit new value
            sequence += 1
            value = f"value_{sequence}_{random.randint(1000, 9999)}"
            primary = nodes[(network.nodes[0].primary + network.nodes[0].view) % num_nodes]
            
            msg = Message(
                msg_type=MessageType.REQUEST,
                sender=-1,  # Client
                view=primary.view,
                sequence=sequence,
                value=value
            )
            await primary.receive_message(msg)
            
        await asyncio.sleep(0.5)
        
    # Collect results
    results = {
        'num_nodes': num_nodes,
        'byzantine_count': byzantine_count,
        'byzantine_ids': byzantine_ids,
        'network_stats': network.get_stats(),
        'decisions': {}
    }
    
    for node in nodes:
        results['decisions'][node.node_id] = {
            'is_byzantine': node.is_byzantine,
            'decided_values': node.decided_values,
            'final_view': node.view
        }
        
    # Check safety (all honest nodes decided same values)
    honest_decisions = [set(node.decided_values.items()) 
                       for node in nodes if not node.is_byzantine]
    safety_holds = all(d == honest_decisions[0] for d in honest_decisions)
    results['safety_holds'] = safety_holds
    
    return results

if __name__ == '__main__':
    results = asyncio.run(run_simulation(num_nodes=10, duration=30))
    print("\n=== Simulation Results ===")
    print(json.dumps(results, indent=2, default=str))
