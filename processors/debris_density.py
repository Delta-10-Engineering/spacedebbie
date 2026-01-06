"""
Debris Density Risk Model

Models the statistical risk of collision with untracked small debris
based on orbital altitude, inclination, and known debris concentrations.

Based on NASA and ESA debris environment models.
"""

import numpy as np

DEBRIS_ZONES = {
    "LEO_LOW": {
        "name": "Low LEO (200-600 km)",
        "alt_min": 200,
        "alt_max": 600,
        "density_factor": 0.6,
        "small_debris_flux": 0.00003,
        "description": "Moderate debris density, atmospheric drag clears smaller pieces"
    },
    "LEO_CRITICAL": {
        "name": "Critical LEO (700-1000 km)",
        "alt_min": 700,
        "alt_max": 1000,
        "density_factor": 1.0,
        "small_debris_flux": 0.00012,
        "description": "Highest debris concentration - Cosmos/Iridium collision zone"
    },
    "LEO_HIGH": {
        "name": "High LEO (1000-2000 km)",
        "alt_min": 1000,
        "alt_max": 2000,
        "density_factor": 0.7,
        "small_debris_flux": 0.00008,
        "description": "Significant debris, includes sun-synchronous orbits"
    },
    "MEO": {
        "name": "MEO (2000-35786 km)",
        "alt_min": 2000,
        "alt_max": 35786,
        "density_factor": 0.1,
        "small_debris_flux": 0.000005,
        "description": "Low debris density, GPS constellation zone"
    },
    "GEO": {
        "name": "GEO (35786+ km)",
        "alt_min": 35786,
        "alt_max": 50000,
        "density_factor": 0.05,
        "small_debris_flux": 0.000001,
        "description": "Very low debris, but congested with active satellites"
    }
}

KNOWN_DEBRIS_CLUSTERS = [
    {
        "name": "Cosmos 2251 / Iridium 33 Collision",
        "year": 2009,
        "altitude_km": 790,
        "inclination_deg": 74,
        "tracked_fragments": 2296,
        "estimated_small_fragments": 100000,
        "description": "First accidental hypervelocity collision between satellites"
    },
    {
        "name": "Fengyun-1C ASAT Test",
        "year": 2007,
        "altitude_km": 865,
        "inclination_deg": 98.7,
        "tracked_fragments": 3527,
        "estimated_small_fragments": 150000,
        "description": "Chinese anti-satellite weapon test"
    },
    {
        "name": "Kosmos 1408 ASAT Test",
        "year": 2021,
        "altitude_km": 480,
        "inclination_deg": 82.6,
        "tracked_fragments": 1500,
        "estimated_small_fragments": 50000,
        "description": "Russian anti-satellite weapon test"
    },
    {
        "name": "Upper Stage Explosions (Various)",
        "year": 2000,
        "altitude_km": 850,
        "inclination_deg": 70,
        "tracked_fragments": 5000,
        "estimated_small_fragments": 200000,
        "description": "Accumulated debris from rocket body breakups"
    }
]

def get_altitude_zone(altitude_km):
    """Determine which debris zone an altitude falls into."""
    for zone_key, zone in DEBRIS_ZONES.items():
        if zone["alt_min"] <= altitude_km < zone["alt_max"]:
            return zone_key, zone
    return "UNKNOWN", {"name": "Unknown", "density_factor": 0.1, "small_debris_flux": 0.00001}

def calculate_small_debris_risk(altitude_km, cross_section_m2=10, exposure_years=1):
    """
    Calculate probability of collision with untracked small debris.
    
    Args:
        altitude_km: Orbital altitude in kilometers
        cross_section_m2: Target cross-sectional area in square meters
        exposure_years: Time of exposure in years
    
    Returns:
        dict with risk assessment
    """
    zone_key, zone = get_altitude_zone(altitude_km)
    
    base_flux = zone["small_debris_flux"]
    
    proximity_boost = 1.0
    for cluster in KNOWN_DEBRIS_CLUSTERS:
        alt_diff = abs(altitude_km - cluster["altitude_km"])
        if alt_diff < 100:
            proximity_boost += (100 - alt_diff) / 100 * 0.5
    
    collision_probability = base_flux * cross_section_m2 * exposure_years * proximity_boost
    
    if collision_probability > 0.01:
        risk_level = "CRITICAL"
        risk_score = 90
    elif collision_probability > 0.001:
        risk_level = "HIGH"
        risk_score = 70
    elif collision_probability > 0.0001:
        risk_level = "ELEVATED"
        risk_score = 50
    elif collision_probability > 0.00001:
        risk_level = "MODERATE"
        risk_score = 30
    else:
        risk_level = "LOW"
        risk_score = 10
    
    return {
        "altitude_km": altitude_km,
        "zone": zone["name"],
        "zone_key": zone_key,
        "zone_description": zone.get("description", ""),
        "collision_probability": collision_probability,
        "risk_level": risk_level,
        "risk_score": risk_score,
        "density_factor": zone["density_factor"],
        "nearby_clusters": [c["name"] for c in KNOWN_DEBRIS_CLUSTERS 
                          if abs(altitude_km - c["altitude_km"]) < 150]
    }

def get_debris_environment_summary():
    """Get summary of the debris environment."""
    total_tracked = sum(c["tracked_fragments"] for c in KNOWN_DEBRIS_CLUSTERS)
    total_estimated_small = sum(c["estimated_small_fragments"] for c in KNOWN_DEBRIS_CLUSTERS)
    
    return {
        "total_tracked_debris": total_tracked,
        "estimated_small_debris_1_10cm": total_estimated_small,
        "estimated_debris_under_1cm": total_estimated_small * 10,
        "most_dangerous_zone": "Critical LEO (700-1000 km)",
        "major_events": KNOWN_DEBRIS_CLUSTERS,
        "zones": list(DEBRIS_ZONES.values())
    }

def get_risk_color(risk_level):
    """Get color for risk level visualization."""
    colors = {
        "CRITICAL": "#FF0000",
        "HIGH": "#FF4500",
        "ELEVATED": "#FFA500",
        "MODERATE": "#FFD700",
        "LOW": "#00FF00"
    }
    return colors.get(risk_level, "#FFFFFF")
