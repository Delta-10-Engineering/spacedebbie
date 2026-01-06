import numpy as np
from datetime import datetime, timedelta
from .orbit_propagator import get_current_position

def calculate_distance(pos1, pos2):
    """Calculate Euclidean distance between two positions in km."""
    return np.sqrt(sum((a - b) ** 2 for a, b in zip(pos1, pos2)))

def find_conjunctions(satellites, threshold_km=50, duration_hours=24, step_minutes=5):
    """
    Find close approaches between satellites.
    Returns list of conjunction events.
    """
    start_time = datetime.utcnow()
    steps = int((duration_hours * 60) / step_minutes)
    
    conjunctions = []
    
    for step in range(steps):
        current_time = start_time + timedelta(minutes=step * step_minutes)
        
        positions = []
        for sat in satellites:
            try:
                pos_data = get_current_position(sat, current_time)
                if pos_data:
                    positions.append({
                        'name': sat['name'],
                        'catalog': sat.get('catalog', 'unknown'),
                        'position': pos_data['position'],
                        'altitude_km': pos_data['altitude_km'],
                        'time': current_time
                    })
            except:
                continue
        
        for i in range(len(positions)):
            for j in range(i + 1, len(positions)):
                dist = calculate_distance(
                    positions[i]['position'],
                    positions[j]['position']
                )
                
                if dist < threshold_km:
                    conjunctions.append({
                        'object1': positions[i]['name'],
                        'object2': positions[j]['name'],
                        'distance_km': round(dist, 2),
                        'time': current_time,
                        'time_from_now': current_time - start_time,
                        'altitude1_km': round(positions[i]['altitude_km'], 1),
                        'altitude2_km': round(positions[j]['altitude_km'], 1),
                    })
    
    conjunctions.sort(key=lambda x: x['distance_km'])
    
    return conjunctions

def assess_collision_risk(distance_km):
    """Assess collision risk based on distance."""
    if distance_km < 1:
        return "CRITICAL", 95, "Immediate collision risk"
    elif distance_km < 5:
        return "HIGH", 80, "Very close approach - high risk"
    elif distance_km < 10:
        return "ELEVATED", 60, "Close approach - monitor closely"
    elif distance_km < 25:
        return "MODERATE", 40, "Notable approach"
    elif distance_km < 50:
        return "LOW", 20, "Distant approach"
    else:
        return "MINIMAL", 5, "Safe distance"

def get_risk_color(risk_level):
    """Get color for risk level."""
    colors = {
        "CRITICAL": "#FF0000",
        "HIGH": "#FF4500", 
        "ELEVATED": "#FFA500",
        "MODERATE": "#FFD700",
        "LOW": "#90EE90",
        "MINIMAL": "#00FF00"
    }
    return colors.get(risk_level, "#FFFFFF")
