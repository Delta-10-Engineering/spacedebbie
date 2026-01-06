from astropy.time import Time
import numpy as np

def get_streak_centroid(lines):
    """Calculate the average centroid of all detected streaks."""
    if not lines:
        return None
    
    centroids = []
    for line in lines:
        p0, p1 = line
        cx = (p0[0] + p1[0]) / 2
        cy = (p0[1] + p1[1]) / 2
        centroids.append((cx, cy))
    
    avg_x = np.mean([c[0] for c in centroids])
    avg_y = np.mean([c[1] for c in centroids])
    return (avg_x, avg_y)

def get_longest_streak_length(lines):
    """Get the length of the longest detected streak."""
    if not lines:
        return 0
    
    max_len = 0
    for line in lines:
        p0, p1 = line
        length = np.sqrt((p1[0]-p0[0])**2 + (p1[1]-p0[1])**2)
        if length > max_len:
            max_len = length
    return max_len

def check_impact_risk(header1, header2, lines1, lines2):
    """
    Determines collision risk based on angular velocity and trajectory.
    Now compares streaks between both frames for proper motion analysis.
    """
    
    t1_str = header1.get('DATE-OBS', None)
    t2_str = header2.get('DATE-OBS', None)
    
    if not t1_str or not t2_str:
        return "Unknown (No Time Data)", 0, {}

    try:
        t1 = Time(t1_str, format='isot', scale='utc')
        t2 = Time(t2_str, format='isot', scale='utc')
        delta_t = (t2 - t1).sec
    except:
        return "Time Parse Error", 0, {}

    if delta_t == 0:
        return "Simultaneous Frames", 0, {}

    centroid1 = get_streak_centroid(lines1)
    centroid2 = get_streak_centroid(lines2)
    
    streak_len_1 = get_longest_streak_length(lines1)
    streak_len_2 = get_longest_streak_length(lines2)
    avg_streak_len = (streak_len_1 + streak_len_2) / 2 if streak_len_1 and streak_len_2 else max(streak_len_1, streak_len_2)
    
    inter_frame_motion = 0
    if centroid1 and centroid2:
        inter_frame_motion = np.sqrt((centroid2[0]-centroid1[0])**2 + (centroid2[1]-centroid1[1])**2)
    
    pixel_scale = 2.0
    
    if inter_frame_motion > 0:
        distance_moved_arcsec = inter_frame_motion * pixel_scale
    else:
        distance_moved_arcsec = avg_streak_len * pixel_scale
        
    velocity_arcsec_per_sec = distance_moved_arcsec / abs(delta_t)
    
    status = "Stable Orbit (GEO/High LEO)"
    risk_score = 10

    if velocity_arcsec_per_sec > 500:
        status = "CRITICAL: Very High Angular Velocity (Possible Re-entry/Low Altitude)"
        risk_score = 95
    elif velocity_arcsec_per_sec > 50:
        status = "WARNING: Fast Moving LEO Object"
        risk_score = 60

    details = {
        "time_delta_sec": abs(delta_t),
        "velocity_arcsec_sec": round(velocity_arcsec_per_sec, 2),
        "inter_frame_motion_px": round(inter_frame_motion, 2),
        "avg_streak_length_px": round(avg_streak_len, 2)
    }

    return status, risk_score, details
