import plotly.graph_objects as go
import numpy as np

EARTH_RADIUS_KM = 6371.0

def create_earth_sphere():
    """Create a 3D sphere representing Earth."""
    u = np.linspace(0, 2 * np.pi, 50)
    v = np.linspace(0, np.pi, 50)
    
    x = EARTH_RADIUS_KM * np.outer(np.cos(u), np.sin(v))
    y = EARTH_RADIUS_KM * np.outer(np.sin(u), np.sin(v))
    z = EARTH_RADIUS_KM * np.outer(np.ones(np.size(u)), np.cos(v))
    
    return go.Surface(
        x=x, y=y, z=z,
        colorscale=[[0, '#1E90FF'], [0.5, '#228B22'], [1, '#1E90FF']],
        showscale=False,
        opacity=0.8,
        name='Earth',
        hoverinfo='skip'
    )

def get_orbit_color(catalog):
    """Get color based on object type."""
    colors = {
        'stations': '#00FF00',
        'starlink': '#FFD700',
        'active': '#00BFFF',
        'debris': '#FF4500',
        'cosmos-2251-debris': '#FF0000',
        'iridium-33-debris': '#FF6347',
        'unknown': '#FFFFFF'
    }
    return colors.get(catalog, '#FFFFFF')

def create_orbit_trace(propagation_result):
    """Create a 3D line trace for an orbit."""
    positions = propagation_result['positions']
    if not positions:
        return None
    
    x = [p[0] for p in positions]
    y = [p[1] for p in positions]
    z = [p[2] for p in positions]
    
    color = get_orbit_color(propagation_result.get('catalog', 'unknown'))
    
    return go.Scatter3d(
        x=x, y=y, z=z,
        mode='lines',
        line=dict(color=color, width=2),
        name=propagation_result['name'],
        hovertemplate=f"<b>{propagation_result['name']}</b><br>Type: {propagation_result.get('catalog', 'unknown')}<extra></extra>"
    )

def create_current_position_marker(name, position, catalog, altitude):
    """Create a marker for current satellite position."""
    color = get_orbit_color(catalog)
    
    return go.Scatter3d(
        x=[position[0]],
        y=[position[1]],
        z=[position[2]],
        mode='markers',
        marker=dict(size=8, color=color, symbol='diamond'),
        name=f"{name} (now)",
        hovertemplate=f"<b>{name}</b><br>Altitude: {altitude:.0f} km<br>Type: {catalog}<extra></extra>"
    )

def create_3d_visualization(propagation_results, current_positions=None, conjunctions=None):
    """Create full 3D visualization with Earth, orbits, and conjunctions."""
    fig = go.Figure()
    
    fig.add_trace(create_earth_sphere())
    
    for result in propagation_results:
        trace = create_orbit_trace(result)
        if trace:
            fig.add_trace(trace)
    
    if current_positions:
        for pos_data in current_positions:
            marker = create_current_position_marker(
                pos_data['name'],
                pos_data['position'],
                pos_data.get('catalog', 'unknown'),
                pos_data.get('altitude_km', 0)
            )
            fig.add_trace(marker)
    
    if conjunctions:
        for conj in conjunctions[:5]:
            fig.add_annotation(
                text=f"Close approach: {conj['distance_km']:.1f} km",
                showarrow=False,
                yref="paper", y=0.95 - conjunctions.index(conj) * 0.05
            )
    
    max_range = 15000
    fig.update_layout(
        scene=dict(
            xaxis=dict(range=[-max_range, max_range], showgrid=False, showticklabels=False, title=''),
            yaxis=dict(range=[-max_range, max_range], showgrid=False, showticklabels=False, title=''),
            zaxis=dict(range=[-max_range, max_range], showgrid=False, showticklabels=False, title=''),
            bgcolor='black',
            aspectmode='cube'
        ),
        paper_bgcolor='black',
        plot_bgcolor='black',
        margin=dict(l=0, r=0, t=30, b=0),
        legend=dict(
            font=dict(color='white'),
            bgcolor='rgba(0,0,0,0.5)'
        ),
        height=700
    )
    
    return fig
