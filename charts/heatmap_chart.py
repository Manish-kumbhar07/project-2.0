import json
import numpy as np
import plotly.graph_objects as go
from data.mumbai_central_line import get_all_stations
from data.services import get_hourly_frequency, get_fast_train_stops

def get_heatmap_chart(day='weekday', branch='all', train_type='all'):
    stations = get_all_stations()
    
    if branch != 'all':
        branch_key = branch.lower()
        if branch_key == 'main':
            stations = [s for s in stations if 'branch' not in s.get('zone', '').lower()]
        else:
            stations = [s for s in stations if branch_key in s.get('zone', '').lower()]
        
    fast_stops = get_fast_train_stops()
    if train_type == 'fast':
        stations = [s for s in stations if s.get('code') in fast_stops]
    elif train_type == 'slow':
        stations = [s for s in stations if s.get('code') not in fast_stops]
        
    y_labels = [s.get('name') for s in stations]
    x_labels = [f"{h:02d}:00" for h in range(5, 24)]
    
    z_data = []
    
    # Peak hours: 8, 9, 10, 11 (idx 3 to 6) and 17, 18, 19, 20 (idx 12 to 15)
    for station in stations:
        row = []
        base_freq = station.get('peak_services_per_hour', 10)
        
        if train_type == 'fast' and station.get('code') not in fast_stops:
            base_freq = 0
            
        for h in range(5, 24):
            freq = base_freq
            if h in [8, 9, 10, 11, 17, 18, 19, 20]:
                pass # Peak
            else:
                freq = int(freq * 0.5) # Off-peak 50%
                
            if day == 'weekend':
                freq = int(freq * 0.7) # Weekend 70%
                
            # Random noise to make it realistic
            freq = max(0, freq + np.random.randint(-1, 2))
            row.append(freq)
            
        z_data.append(row)
        
    fig = go.Figure(data=go.Heatmap(
        z=z_data,
        x=x_labels,
        y=y_labels,
        colorscale=[[0, '#f5f5f5'], [0.3, '#4db6ac'], [0.6, '#00695c'], [1.0, '#1a237e']],
        hovertemplate="<b>%{y}</b><br>Time: %{x}<br>Services: %{z}<extra></extra>"
    ))
    
    fig.update_layout(
        plot_bgcolor='#ffffff',
        paper_bgcolor='#ffffff',
        margin=dict(l=100, r=20, t=20, b=50),
        xaxis=dict(tickangle=-45),
        yaxis=dict(autorange='reversed')
    )
    
    return json.loads(fig.to_json())
