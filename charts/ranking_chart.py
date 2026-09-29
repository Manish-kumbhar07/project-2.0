import json
import plotly.graph_objects as go
from data.mumbai_central_line import get_all_stations

def get_ranking_chart():
    stations = get_all_stations()
    
    # Sort by connectivity score, take top 15
    sorted_stations = sorted(stations, key=lambda x: x.get('connectivity_score', 0), reverse=True)[:15]
    sorted_stations.reverse() # For horizontal bar
    
    names = []
    scores = []
    colors = []
    hover_texts = []
    
    for s in sorted_stations:
        name = s.get('name', '')
        score = s.get('connectivity_score', 0)
        zone = s.get('zone', 'Unknown')
        platforms = s.get('platforms', 2)
        fast = "Yes" if s.get('fast_train_stop') else "No"
        
        names.append(name)
        scores.append(score)
        
        # Color by zone
        if 'South Mumbai' in zone: color = '#1a237e' # primary
        elif 'Central Mumbai' in zone: color = '#3949ab' # primary-light
        elif 'Eastern Suburbs' in zone: color = '#00695c' # secondary
        elif 'Thane' in zone: color = '#26a69a' # secondary-light
        elif 'Kalyan' in zone: color = '#f57f17' # tertiary
        else: color = '#ffb300' # tertiary-light
        
        colors.append(color)
        hover_texts.append(f"Station: {name}<br>Score: {score}<br>Zone: {zone}<br>Platforms: {platforms}<br>Fast Train: {fast}")
        
    fig = go.Figure(go.Bar(
        x=scores,
        y=names,
        orientation='h',
        marker_color=colors,
        text=scores,
        textposition='auto',
        hoverinfo='text',
        hovertext=hover_texts
    ))
    
    fig.update_layout(
        plot_bgcolor='#ffffff',
        paper_bgcolor='#ffffff',
        margin=dict(l=120, r=20, t=20, b=40),
        xaxis=dict(title='Connectivity Score', showgrid=True, gridcolor='#e0e0e0'),
        yaxis=dict(showgrid=False)
    )
    
    return json.loads(fig.to_json())
