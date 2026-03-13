# IT-1: SmartCity Digital Twin — Real-Time Urban Simulation Platform

## Overview

Build a **real-time digital twin** of a downtown area (5 km × 5 km) to optimize traffic, energy consumption, and emergency response.

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                      Frontend (WebGL)                        │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐         │
│  │ 3D City View │  │   Heatmaps  │  │  Analytics  │         │
│  └─────────────┘  └─────────────┘  └─────────────┘         │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                        API Gateway                           │
└─────────────────────────────────────────────────────────────┘
                              │
        ┌─────────────────────┼─────────────────────┐
        ▼                     ▼                     ▼
┌───────────────┐    ┌───────────────┐    ┌───────────────┐
│ Traffic Service│    │ Energy Service│    │Emergency Svc  │
└───────────────┘    └───────────────┘    └───────────────┘
        │                     │                     │
        ▼                     ▼                     ▼
┌─────────────────────────────────────────────────────────────┐
│                    Stream Processing                         │
│              (Kafka / Redis Streams / NATS)                  │
└─────────────────────────────────────────────────────────────┘
                              │
        ┌─────────────────────┼─────────────────────┐
        ▼                     ▼                     ▼
┌───────────────┐    ┌───────────────┐    ┌───────────────┐
│  Time-Series  │    │   Graph DB    │    │    Cache      │
│     (DB)      │    │  (Road Net)   │    │   (Redis)     │
└───────────────┘    └───────────────┘    └───────────────┘
```

## Data Sources

### Real-Time Feeds (Simulated)
- **Traffic sensors**: 1000 sensors, updated every 30s
- **Weather data**: Updated every 5 min
- **Power grid**: Updated every 1 min
- **Emergency calls**: Real-time

### Static Data
- **Road network**: OpenStreetMap format
- **Building footprints**: GeoJSON
- **Elevation data**: DEM raster

### Historical Data
- 1 year of traffic patterns
- Energy usage logs
- Incident records

## Features

### 1. Real-Time Data Ingestion
- Handle up to 10,000 events/second
- Stream processing with low latency (< 100ms)
- Data validation and normalization

### 2. 3D Visualization
- WebGL-based city rendering
- Real-time overlays:
  - Traffic density heatmap
  - Energy consumption
  - Active incidents
- Camera controls and navigation

### 3. Predictive Analytics
- **Traffic**: 30-minute congestion prediction
- **Energy**: 1-hour demand forecast
- **Emergency**: Response time estimation

### 4. What-If Scenarios
- Road closure simulation
- New infrastructure placement
- Event impact analysis

## Tech Stack

### Backend
- **Language**: Python (FastAPI) or Node.js (Express)
- **Stream Processing**: Redis Streams or Kafka
- **Time-Series DB**: TimescaleDB or InfluxDB
- **Graph DB**: Neo4j or NetworkX
- **Cache**: Redis

### Frontend
- **Framework**: React or Vue.js
- **3D Engine**: Three.js or Cesium
- **Charts**: D3.js or Chart.js
- **Maps**: Mapbox GL or Leaflet

### Infrastructure
- **Containers**: Docker + Docker Compose
- **Orchestration**: Kubernetes (optional)
- **Monitoring**: Prometheus + Grafana

## Getting Started

1. **Setup environment:**
   ```bash
   ./setup.sh
   ```

2. **Start services:**
   ```bash
   docker-compose up -d
   ```

3. **Generate simulated data:**
   ```bash
   python data_generator.py
   ```

4. **Access the application:**
   - Frontend: http://localhost:3000
   - API: http://localhost:8000
   - API Docs: http://localhost:8000/docs

## Project Structure

```
IT-1_SmartCity/
├── README.md
├── docker-compose.yml
├── setup.sh
├── backend/
│   ├── app/
│   │   ├── main.py
│   │   ├── api/
│   │   ├── services/
│   │   ├── models/
│   │   └── utils/
│   ├── requirements.txt
│   └── Dockerfile
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   ├── services/
│   │   └── utils/
│   ├── package.json
│   └── Dockerfile
├── data/
│   ├── road_network.geojson
│   ├── buildings.geojson
│   └── elevation.tif
├── data_generator.py
└── solution_template.py
```

## Deliverables

1. **Deployed Application**: Docker containers
2. **Architecture Document**: System design and decisions
3. **Performance Benchmarks**: Load test results
4. **Demo Video**: 5-minute walkthrough

## Scoring

| Criterion | Points |
|---|---|
| Data ingestion (10K events/sec) | 25 |
| 3D visualization quality | 20 |
| Predictive accuracy | 25 |
| What-if scenario support | 15 |
| Concurrent users (50+) | 15 |
