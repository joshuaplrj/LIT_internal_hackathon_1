# AIDS-2: GraphFlood — Real-Time Social Network Misinformation Detection

## Overview

Design a system that detects **misinformation cascades** in a social network in real-time using Graph Neural Networks and temporal modeling.

## Data Provided

| Data | Size | Description |
|---|---|---|
| Social graph | 10M users, 500M edges | Follower/following relationships |
| Content stream | 50K posts/minute | Text, images, timestamps, engagement |
| Fact-check DB | 100K verified claims | True/false/mixed labels |
| Historical cascades | 50K labeled | Misinformation vs. legitimate |

## Requirements

| Metric | Target |
|---|---|
| AUC-ROC | > 0.85 |
| Precision @ Recall=0.70 | > 0.80 |
| Detection time | < 1 hour after posting |
| Feature extraction | < 10 ms per post |
| Inference | < 50 ms per post |
| Graph update | < 100 ms per edge |

## Task

### 1. Cascade Modeling

- **Graph Neural Networks**: Model social network structure
- **Temporal dynamics**: Hawkes processes or neural point processes
- **Content features**: Text embeddings, image features, source credibility

### 2. Early Detection

Detect misinformation within 1 hour (< 100 reshares):
- Fuse graph, temporal, and content signals
- Handle cold-start (new users, new topics)
- Calibrated probability scores

### 3. Real-Time Processing

- Stream processing architecture
- Incremental graph updates
- Efficient feature extraction

### 4. Explainability

- Most influential spreaders
- Key content features
- Credibility score with confidence interval

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Content Stream                            │
│              (50K posts/minute)                              │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                  Feature Extraction                          │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐         │
│  │Text Embedding│  │Image Features│  │Source Cred. │         │
│  └─────────────┘  └─────────────┘  └─────────────┘         │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                    GNN Classifier                            │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐         │
│  │Graph Encoder │  │Temporal Model│  │Fusion Layer │         │
│  └─────────────┘  └─────────────┘  └─────────────┘         │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                  Misinformation Score                        │
│              + Explainability                                │
└─────────────────────────────────────────────────────────────┘
```

## Deliverables

1. **System Architecture**: Streaming pipeline design
2. **GNN Model**: Cascade classification
3. **Temporal Model**: Early detection
4. **Benchmarks**: Real-time processing performance
5. **Explainability Module**: Influence and feature analysis
6. **Test Results**: Performance on provided test set

## Getting Started

1. **Explore the data:**
   ```bash
   python explore_data.py
   ```

2. **Build graph:**
   ```bash
   python build_graph.py
   ```

3. **Train model:**
   ```bash
   python train.py --model gnn_temporal
   ```

4. **Run inference:**
   ```bash
   python inference.py --mode streaming
   ```

## Project Structure

```
AIDS-2_GraphFlood/
├── README.md
├── data/
│   ├── social_graph/
│   │   ├── nodes.csv
│   │   └── edges.csv
│   ├── content_stream/
│   │   └── posts.jsonl
│   ├── fact_check/
│   │   └── claims.csv
│   └── cascades/
│       └── labeled_cascades.csv
├── models/
│   ├── gnn.py
│   ├── temporal.py
│   ├── content_encoder.py
│   └── fusion.py
├── streaming/
│   ├── processor.py
│   ├── feature_extractor.py
│   └── graph_updater.py
├── explainability/
│   ├── influence.py
│   └── feature_importance.py
├── train.py
├── inference.py
└── solution_template.py
```

## Tips

1. Start with simple features before complex GNNs
2. Temporal information is crucial for early detection
3. Source credibility is a strong signal
4. Consider using PyTorch Geometric or DGL for GNNs
5. Stream processing needs careful memory management