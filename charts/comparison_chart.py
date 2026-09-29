import json
import plotly.graph_objects as go
from data.mumbai_central_line import get_station_by_code
from utils.route_finder import find_route

def get_comparison_chart():
    segments = [
        ("CSMT", "DR", "CSMT-Dadar"),
        ("CSMT", "TNA", "CSMT-Thane"),
        ("CSMT", "KYN", "CSMT-Kalyan"),
        ("CSMT", "KSRA", "CSMT-Kasara"),
        ("CSMT", "KJT", "CSMT-Karjat"),
        ("KYN", "KSRA", "Kalyan-Kasara"),
        ("KYN", "KJT", "Kalyan-Karjat")
    ]
    
    labels = []
    fast_times = []
    slow_times = []
    fast_stops = []
    slow_stops = []
    
    for start, end, name in segments:
        # Approximate values
        if name == "CSMT-Dadar": s_stops=7; f_stops=3
        elif name == "CSMT-Thane": s_stops=18; f_stops=6
        elif name == "CSMT-Kalyan": s_stops=25; f_stops=9
        elif name == "CSMT-Kasara": s_stops=38; f_stops=22
        elif name == "CSMT-Karjat": s_stops=39; f_stops=23
        elif name == "Kalyan-Kasara": s_stops=13; f_stops=13
        elif name == "Kalyan-Karjat": s_stops=14; f_stops=14
        else: s_stops=20; f_stops=10
        
        s_time = s_stops * 2
        f_time = f_stops * 1.5 + (s_stops - f_stops) * 0.5
        
        labels.append(name)
        slow_times.append(int(s_time))
        fast_times.append(int(f_time))
        slow_stops.append(s_stops)
        fast_stops.append(f_stops)

    fig = go.Figure()
    
    fig.add_trace(go.Bar(
        x=labels,
        y=fast_times,
        name='Fast',
        marker_color='#1a237e', # Primary blue
        customdata=fast_stops,
        hovertemplate="<b>Fast Train</b><br>%{x}<br>Time: %{y} min<br>Stops: %{customdata}<extra></extra>"
    ))
    
    fig.add_trace(go.Bar(
        x=labels,
        y=slow_times,
        name='Slow',
        marker_color='#00695c', # Secondary teal
        customdata=slow_stops,
        hovertemplate="<b>Slow Train</b><br>%{x}<br>Time: %{y} min<br>Stops: %{customdata}<extra></extra>"
    ))
    
    fig.update_layout(
        barmode='group',
        plot_bgcolor='#ffffff',
        paper_bgcolor='#ffffff',
        margin=dict(l=40, r=20, t=40, b=40),
        xaxis=dict(title='Route Segment', showgrid=False),
        yaxis=dict(title='Time (minutes)', showgrid=True, gridcolor='#e0e0e0'),
        legend=dict(x=0.01, y=0.99, bgcolor='rgba(255,255,255,0.8)')
    )
    
    return json.loads(fig.to_json())
