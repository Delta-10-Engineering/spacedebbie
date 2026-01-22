# Space Debris & Collision Monitor

## Overview
A Streamlit web application for real-time tracking of satellites and space debris with 3D visualization and collision prediction. Uses real orbital data from CelesTrak and SGP4 propagation to predict close approaches.

## Project Structure
```
├── app.py                          # Main Streamlit web interface
├── processors/
│   ├── __init__.py
│   ├── tle_fetcher.py              # Fetches TLE data from CelesTrak
│   ├── orbit_propagator.py         # SGP4 orbit propagation
│   ├── conjunction_detector.py     # Collision/close approach detection
│   ├── visualization.py            # 3D Plotly visualization
│   ├── debris_density.py           # Small debris risk model
│   ├── streak_finder.py            # Legacy FITS streak detection
│   └── orbit_math.py               # Legacy trajectory analysis
└── .streamlit/
    └── config.toml                 # Streamlit server configuration
```

## Key Features
- **Real Orbital Data**: Fetches live TLE data from CelesTrak (ISS, Starlink, debris)
- **Fallback Data**: Works offline with cached TLE data when CelesTrak is unreachable
- **3D Visualization**: Interactive Plotly globe showing Earth and orbiting objects
- **Orbit Propagation**: SGP4 algorithm predicts positions up to 48 hours ahead
- **Collision Detection**: Finds close approaches between tracked objects
- **Risk Assessment**: Categorizes collision risk (Critical/High/Elevated/Moderate/Low/Minimal)
- **Small Debris Model**: Statistical risk from untracked 1-10cm debris based on altitude zones

## Technical Components
- **tle_fetcher.py**: Downloads TLE data from CelesTrak with fallback cache
- **orbit_propagator.py**: Uses SGP4 to propagate satellite positions over time
- **conjunction_detector.py**: Analyzes pairwise distances to find close approaches
- **visualization.py**: Creates 3D Plotly visualization with Earth sphere and orbit traces
- **debris_density.py**: Models debris density by altitude zone and known collision clusters

## Object Types
- Space Stations (ISS and manned spacecraft)
- Starlink satellites
- Space debris (Cosmos-2251, Iridium-33 fragments)

## Running the App
```
streamlit run app.py --server.port 5000
```

## Dependencies
- streamlit, astropy, numpy, scikit-image, sep, matplotlib, poliastro, sgp4, plotly, requests
