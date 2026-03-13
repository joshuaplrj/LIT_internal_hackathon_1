# IT-3: EventHorizon — Serverless Event-Driven Architecture for E-Commerce

## Overview

Design a **serverless event-driven backend** for a flash-sale e-commerce platform handling **1 million concurrent users** for 1,000 limited-quantity items.

## Requirements

| Requirement | Target |
|---|---|
| Concurrent users | 1,000,000 |
| Flash sale duration | 10 minutes |
| Limited items | 1,000 |
| Events per user | ~5 |
| Total events | 5,000,000 |
| Overselling | Zero tolerance |
| Order status lag | < 5 seconds |

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                        CDN / Load Balancer                   │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                     API Gateway                              │
└─────────────────────────────────────────────────────────────┘
                              │
        ┌─────────────────────┼─────────────────────┐
        ▼                     ▼                     ▼
┌───────────────┐    ┌───────────────┐    ┌───────────────┐
│ Order Service │    │Inventory Svc  │    │Payment Service│
│   (Lambda)    │    │   (Lambda)    │    │   (Lambda)    │
└───────────────┘    └───────────────┘    └───────────────┘
        │                     │                     │
        └─────────────────────┼─────────────────────┘
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                    Event Bus (SQS/SNS/Kafka)                 │
└─────────────────────────────────────────────────────────────┘
                              │
        ┌─────────────────────┼─────────────────────┐
        ▼                     ▼                     ▼
┌───────────────┐    ┌───────────────┐    ┌───────────────┐
│Fulfillment Svc│    │Notification   │    │  Dead Letter  │
│   (Lambda)    │    │   (Lambda)    │    │    Queue      │
└───────────────┘    └───────────────┘    └───────────────┘
```

## Event Flow

1. User clicks "Buy" → API Gateway
2. Order Service creates order (PENDING)
3. Inventory Check → Reserve item (optimistic lock)
4. Payment Processing → Charge customer
5. Fulfillment → Ship item
6. Notifications → Email/SMS confirmation

## Exactly-Once Inventory

```python
def reserve_inventory(item_id, order_id):
    # Optimistic locking with version
    item = db.get_item(item_id)
    
    if item.quantity <= 0:
        raise OutOfStockError()
    
    # Atomic update with condition
    success = db.update_item(
        item_id,
        condition="quantity > 0 AND version = :expected_version",
        updates={
            "quantity": item.quantity - 1,
            "reserved_by": order_id,
            "version": item.version + 1
        }
    )
    
    if not success:
        # Retry or fail
        raise ConcurrentUpdateError()
    
    return success
```

## Dead Letter Queue

```python
def process_order(event, retry_count=0):
    try:
        # Process order
        result = handle_order(event)
        return result
    except TransientError as e:
        if retry_count < 3:
            # Exponential backoff
            delay = 2 ** retry_count
            schedule_retry(event, delay, retry_count + 1)
        else:
            # Send to DLQ
            send_to_dlq(event, error=str(e))
    except PermanentError as e:
        # Don't retry permanent errors
        send_to_dlq(event, error=str(e))
```

## Observability

### Distributed Tracing

```python
from opentelemetry import trace

tracer = trace.get_tracer(__name__)

@tracer.start_as_current_span("process_order")
def process_order(order_id):
    with tracer.start_as_current_span("validate_order"):
        validate(order_id)
    
    with tracer.start_as_current_span("check_inventory"):
        check_inventory(order_id)
    
    with tracer.start_as_current_span("process_payment"):
        process_payment(order_id)
```

### Metrics

```python
from prometheus_client import Counter, Histogram

orders_total = Counter('orders_total', 'Total orders processed')
order_latency = Histogram('order_latency_seconds', 'Order processing latency')
inventory_conflicts = Counter('inventory_conflicts_total', 'Inventory conflicts')
```

## Load Testing

```python
# k6 load test script
import http from 'k6/http';
import { check, sleep } from 'k6';

export let options = {
    stages: [
        { duration: '1m', target: 100000 },  // Ramp up
        { duration: '10m', target: 1000000 }, // Stay at 1M
        { duration: '1m', target: 0 },        // Ramp down
    ],
};

export default function() {
    let res = http.post('https://api.example.com/orders', JSON.stringify({
        item_id: Math.floor(Math.random() * 1000),
        user_id: Math.floor(Math.random() * 1000000),
    }), {
        headers: { 'Content-Type': 'application/json' },
    });
    
    check(res, {
        'status is 200 or 201': (r) => r.status === 200 || r.status === 201,
        'no overselling': (r) => !r.json().error || r.json().error !== 'OUT_OF_STOCK',
    });
}
```

## Deliverables

1. **Architecture Diagram**: C4 model
2. **Infrastructure-as-Code**: Terraform/Pulumi/CloudFormation
3. **Source Code**: All functions/services
4. **Load Test Results**: Throughput, latency, error rate
5. **Cost Estimate**: Per event and total

## Project Structure

```
IT-3_EventHorizon/
├── README.md
├── infrastructure/
│   ├── main.tf
│   ├── variables.tf
│   └── outputs.tf
├── services/
│   ├── order_service/
│   │   ├── handler.py
│   │   └── requirements.txt
│   ├── inventory_service/
│   │   ├── handler.py
│   │   └── requirements.txt
│   ├── payment_service/
│   │   ├── handler.py
│   │   └── requirements.txt
│   ├── fulfillment_service/
│   │   ├── handler.py
│   │   └── requirements.txt
│   └── notification_service/
│       ├── handler.py
│       └── requirements.txt
├── shared/
│   ├── database.py
│   ├── events.py
│   └── tracing.py
├── tests/
│   ├── load_test.js
│   └── integration_test.py
└── solution_template.py
```

## Tips

1. Idempotency is critical - use idempotency keys
2. Optimistic locking prevents overselling
3. DLQ with exponential backoff handles failures
4. Cache hot items to reduce DB load
5. Pre-warm Lambda functions before flash sale
