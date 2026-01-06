import streamlit as st
from datetime import datetime, timedelta
from processors.tle_fetcher import fetch_multiple_catalogs, CATALOGS, is_using_fallback
from processors.orbit_propagator import propagate_multiple, get_current_position
from processors.conjunction_detector import find_conjunctions, assess_collision_risk, get_risk_color
from processors.visualization import create_3d_visualization
from processors.debris_density import (
    calculate_small_debris_risk, 
    get_debris_environment_summary,
    get_risk_color as get_density_risk_color,
    DEBRIS_ZONES,
    KNOWN_DEBRIS_CLUSTERS
)

st.set_page_config(page_title="Space Debris Tracker", layout="wide")

st.title("🛰️ Space Debris & Collision Monitor")
st.markdown("Real-time tracking of satellites and space debris with collision prediction")

with st.sidebar:
    st.header("Settings")
    
    st.subheader("Object Types to Track")
    track_stations = st.checkbox("Space Stations (ISS, etc.)", value=True)
    track_starlink = st.checkbox("Starlink Satellites", value=True)
    track_debris = st.checkbox("Space Debris", value=True)
    
    objects_per_type = st.slider("Objects per category", 5, 50, 15)
    
    st.subheader("Analysis Settings")
    prediction_hours = st.slider("Prediction window (hours)", 1, 48, 24)
    collision_threshold = st.slider("Close approach threshold (km)", 10, 100, 50)
    
    run_analysis = st.button("🚀 Run Analysis", type="primary")

if run_analysis:
    catalogs = []
    if track_stations:
        catalogs.append("stations")
    if track_starlink:
        catalogs.append("starlink")
    if track_debris:
        catalogs.append("debris")
    
    if not catalogs:
        st.warning("Please select at least one object type to track.")
    else:
        with st.spinner("Fetching orbital data..."):
            satellites = fetch_multiple_catalogs(catalogs, limit_per_catalog=objects_per_type)
        
        if not satellites:
            st.error("Could not fetch satellite data. Please try again.")
        else:
            if is_using_fallback():
                st.info(f"📡 Demo Mode: Using realistic sample orbital data ({len(satellites)} objects). External TLE sources are not accessible from this environment.")
            else:
                st.success(f"✅ Loaded {len(satellites)} objects from live orbital data")
            
            with st.spinner("Propagating orbits..."):
                propagation_results = propagate_multiple(
                    satellites, 
                    duration_hours=prediction_hours,
                    step_minutes=10
                )
            
            current_positions = []
            for sat in satellites:
                try:
                    pos = get_current_position(sat)
                    if pos:
                        current_positions.append({
                            'name': sat['name'],
                            'catalog': sat.get('catalog', 'unknown'),
                            'position': pos['position'],
                            'altitude_km': pos['altitude_km']
                        })
                except:
                    pass
            
            with st.spinner("Analyzing potential collisions..."):
                conjunctions = find_conjunctions(
                    satellites,
                    threshold_km=collision_threshold,
                    duration_hours=prediction_hours,
                    step_minutes=15
                )
            
            st.header("3D Orbital Visualization")
            fig = create_3d_visualization(propagation_results, current_positions, conjunctions)
            st.plotly_chart(fig, use_container_width=True)
            
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("Objects Tracked", len(satellites))
            with col2:
                st.metric("Prediction Window", f"{prediction_hours}h")
            with col3:
                st.metric("Close Approaches", len(conjunctions))
            with col4:
                env = get_debris_environment_summary()
                st.metric("Est. Small Debris", f"{env['estimated_small_debris_1_10cm']:,}")
            
            st.header("Tracked Object Collision Risk")
            
            if conjunctions:
                st.warning(f"Found {len(conjunctions)} potential close approaches in the next {prediction_hours} hours")
                
                for i, conj in enumerate(conjunctions[:10]):
                    risk_level, risk_score, risk_desc = assess_collision_risk(conj['distance_km'])
                    risk_color = get_risk_color(risk_level)
                    
                    hours_from_now = conj['time_from_now'].total_seconds() / 3600
                    
                    with st.expander(f"⚠️ {conj['object1']} ↔ {conj['object2']} - {conj['distance_km']:.1f} km", expanded=(i < 3)):
                        cols = st.columns(4)
                        with cols[0]:
                            st.markdown(f"**Risk Level**")
                            st.markdown(f"<span style='color:{risk_color};font-size:24px;font-weight:bold'>{risk_level}</span>", unsafe_allow_html=True)
                        with cols[1]:
                            st.metric("Distance", f"{conj['distance_km']:.1f} km")
                        with cols[2]:
                            st.metric("Time", f"{hours_from_now:.1f}h from now")
                        with cols[3]:
                            st.metric("Risk Score", f"{risk_score}%")
                        
                        st.markdown(f"**Assessment:** {risk_desc}")
                        st.markdown(f"**Object 1:** {conj['object1']} at {conj['altitude1_km']:.0f} km altitude")
                        st.markdown(f"**Object 2:** {conj['object2']} at {conj['altitude2_km']:.0f} km altitude")
                        st.markdown(f"**Predicted Time:** {conj['time'].strftime('%Y-%m-%d %H:%M:%S')} UTC")
            else:
                st.success(f"No close approaches detected within {collision_threshold} km in the next {prediction_hours} hours")
            
            st.header("Small Debris Risk Assessment")
            st.markdown("**Risk of collision with untracked debris (1-10cm) that cannot be individually monitored:**")
            
            if current_positions:
                altitudes = [p['altitude_km'] for p in current_positions]
                unique_altitudes = sorted(set([int(a/50)*50 for a in altitudes]))[:10]
                
                for alt in unique_altitudes:
                    risk_data = calculate_small_debris_risk(alt)
                    risk_color = get_density_risk_color(risk_data['risk_level'])
                    
                    with st.expander(f"Altitude ~{alt} km - {risk_data['zone']}", expanded=False):
                        cols = st.columns(4)
                        with cols[0]:
                            st.markdown(f"**Risk Level**")
                            st.markdown(f"<span style='color:{risk_color};font-size:20px;font-weight:bold'>{risk_data['risk_level']}</span>", unsafe_allow_html=True)
                        with cols[1]:
                            st.metric("Risk Score", f"{risk_data['risk_score']}%")
                        with cols[2]:
                            st.metric("Collision Prob/Year", f"{risk_data['collision_probability']:.6f}")
                        with cols[3]:
                            st.metric("Density Factor", f"{risk_data['density_factor']:.1f}x")
                        
                        st.markdown(f"**Zone:** {risk_data['zone_description']}")
                        if risk_data['nearby_clusters']:
                            st.markdown(f"**Nearby debris sources:** {', '.join(risk_data['nearby_clusters'])}")
            
            st.header("Known Debris Clusters")
            st.markdown("**Major collision and fragmentation events creating debris clouds:**")
            
            for cluster in KNOWN_DEBRIS_CLUSTERS:
                with st.expander(f"💥 {cluster['name']} ({cluster['year']})", expanded=False):
                    cols = st.columns(4)
                    with cols[0]:
                        st.metric("Altitude", f"{cluster['altitude_km']} km")
                    with cols[1]:
                        st.metric("Inclination", f"{cluster['inclination_deg']}°")
                    with cols[2]:
                        st.metric("Tracked Pieces", f"{cluster['tracked_fragments']:,}")
                    with cols[3]:
                        st.metric("Est. Small (<10cm)", f"{cluster['estimated_small_fragments']:,}")
                    st.markdown(f"**Description:** {cluster['description']}")
            
            st.header("Tracked Objects")
            
            stations = [p for p in current_positions if p['catalog'] == 'stations']
            starlinks = [p for p in current_positions if p['catalog'] == 'starlink']
            debris = [p for p in current_positions if 'debris' in p['catalog']]
            
            tab1, tab2, tab3 = st.tabs(["Space Stations", "Starlink", "Debris"])
            
            with tab1:
                if stations:
                    for sat in stations:
                        risk = calculate_small_debris_risk(sat['altitude_km'])
                        st.markdown(f"🟢 **{sat['name']}** - Altitude: {sat['altitude_km']:.0f} km - Small debris risk: {risk['risk_level']}")
                else:
                    st.info("No space stations tracked")
            
            with tab2:
                if starlinks:
                    for sat in starlinks[:20]:
                        risk = calculate_small_debris_risk(sat['altitude_km'])
                        st.markdown(f"🟡 **{sat['name']}** - Altitude: {sat['altitude_km']:.0f} km - Small debris risk: {risk['risk_level']}")
                    if len(starlinks) > 20:
                        st.caption(f"...and {len(starlinks) - 20} more")
                else:
                    st.info("No Starlink satellites tracked")
            
            with tab3:
                if debris:
                    for sat in debris[:20]:
                        risk = calculate_small_debris_risk(sat['altitude_km'])
                        st.markdown(f"🔴 **{sat['name']}** - Altitude: {sat['altitude_km']:.0f} km - Small debris risk: {risk['risk_level']}")
                    if len(debris) > 20:
                        st.caption(f"...and {len(debris) - 20} more")
                else:
                    st.info("No debris tracked")

else:
    st.info("👈 Configure settings in the sidebar and click 'Run Analysis' to start tracking")
    
    env = get_debris_environment_summary()
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total Tracked Debris", f"{env['total_tracked_debris']:,}")
    with col2:
        st.metric("Est. Small Debris (1-10cm)", f"{env['estimated_small_debris_1_10cm']:,}")
    with col3:
        st.metric("Est. Tiny Debris (<1cm)", f"{env['estimated_debris_under_1cm']:,}")
    
    st.markdown("""
    ### How it works
    1. **Data Source**: Real orbital data from CelesTrak (TLE format) with fallback data
    2. **Orbit Propagation**: SGP4 algorithm predicts positions over time
    3. **Tracked Collision Detection**: Analyzes pairwise distances between tracked objects
    4. **Small Debris Risk**: Statistical model estimates collision probability with untracked debris
    5. **3D Visualization**: Interactive globe showing all tracked objects
    
    ### Object Types
    - 🟢 **Space Stations**: ISS and other manned spacecraft
    - 🟡 **Starlink**: SpaceX satellite constellation  
    - 🔴 **Debris**: Tracked fragments from past collisions/explosions
    
    ### Risk Assessment
    - **Tracked objects**: Real-time close approach prediction
    - **Small debris (1-10cm)**: Statistical risk based on altitude and known debris clusters
    - **Micro debris (<1cm)**: Millions of pieces - managed by shielding, not avoidance
    """)
    
    st.subheader("Debris Danger Zones")
    for zone_key, zone in DEBRIS_ZONES.items():
        st.markdown(f"**{zone['name']}**: {zone['description']} (Density: {zone['density_factor']:.1f}x)")
