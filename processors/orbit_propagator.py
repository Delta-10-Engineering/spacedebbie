from sgp4.api import Satrec, jday
from datetime import datetime, timedelta
import numpy as np

EARTH_RADIUS_KM = 6371.0

def propagate_satellite(tle_data, start_time=None, duration_hours=24, step_minutes=10):
    """
    Propagate a satellite orbit using SGP4.
    Returns list of positions in ECI coordinates (km).
    """
    satellite = Satrec.twoline2rv(tle_data['line1'], tle_data['line2'])
    
    if start_time is None:
        start_time = datetime.utcnow()
    
    positions = []
    times = []
    
    steps = int((duration_hours * 60) / step_minutes)
    
    for i in range(steps):
        current_time = start_time + timedelta(minutes=i * step_minutes)
        jd, fr = jday(
            current_time.year, current_time.month, current_time.day,
            current_time.hour, current_time.minute, current_time.second
        )
        
        error, position, velocity = satellite.sgp4(jd, fr)
        
        if error == 0:
            positions.append(position)
            times.append(current_time)
    
    return {
        'name': tle_data['name'],
        'catalog': tle_data.get('catalog', 'unknown'),
        'positions': positions,
        'times': times
    }

def propagate_multiple(satellites, start_time=None, duration_hours=24, step_minutes=10):
    """Propagate multiple satellites."""
    results = []
    for sat in satellites:
        try:
            result = propagate_satellite(sat, start_time, duration_hours, step_minutes)
            if result['positions']:
                results.append(result)
        except Exception as e:
            print(f"Error propagating {sat.get('name', 'unknown')}: {e}")
    return results

def get_current_position(tle_data, at_time=None):
    """Get satellite position at a specific time."""
    if at_time is None:
        at_time = datetime.utcnow()
    
    satellite = Satrec.twoline2rv(tle_data['line1'], tle_data['line2'])
    jd, fr = jday(
        at_time.year, at_time.month, at_time.day,
        at_time.hour, at_time.minute, at_time.second
    )
    
    error, position, velocity = satellite.sgp4(jd, fr)
    
    if error == 0:
        altitude = np.sqrt(sum(p**2 for p in position)) - EARTH_RADIUS_KM
        return {
            'position': position,
            'velocity': velocity,
            'altitude_km': altitude,
            'time': at_time
        }
    return None
