import json
import plotly.graph_objects as go
from data.database import get_all_stations_df, get_station_by_code_db
from utils.route_finder import find_route, get_adjacency_list

def get_network_chart():
    df_stations = get_all_stations_df()
    adjacency_list = get_adjacency_list()
    
    node_x = []
    node_y = []
    node_text = []
    node_color = []
    node_size = []
    custom_data = []
    node_labels = []
    
    for _, station in df_stations.iterrows():
        node_x.append(float(station['longitude']))
        node_y.append(float(station['latitude']))
        name = station['station_name']
        code = station['station_code']
        zone = station['zone']
        score = int(station['connectivity_score'])
        fast = "Yes" if station.get('fast_train_stop') else "No"
        
        node_text.append(f"<b>{name} ({code})</b><br>Zone: {zone}<br>Connectivity Score: {score}%<br>Fast Train Stop: {fast}")
        custom_data.append(code)
        
        if station.get('junction_status') or station.get('is_junction'):
            node_color.append('#f57f17') # Tertiary amber for junctions
            node_size.append(max(12, min(22, int(score * 0.24))))
            node_labels.append(code)
        else:
            node_color.append('#1a237e') # Primary blue
            node_size.append(max(7, min(14, int(score * 0.16))))
            node_labels.append('')
        
    edge_x = []
    edge_y = []
    
    st_map = {r['station_code']: (float(r['longitude']), float(r['latitude'])) for _, r in df_stations.iterrows()}

    for node, neighbors in adjacency_list.items():
        if node not in st_map: continue
        x0, y0 = st_map[node]
        for neighbor in neighbors:
            if neighbor not in st_map: continue
            x1, y1 = st_map[neighbor]
            edge_x.extend([x0, x1, None])
            edge_y.extend([y0, y1, None])
            
    fig = go.Figure()
    
    fig.add_trace(go.Scatter(
        x=edge_x, y=edge_y,
        line=dict(width=2, color='#90a4ae'),
        hoverinfo='none',
        mode='lines',
        name='Track Connections'
    ))
    
    fig.add_trace(go.Scatter(
        x=node_x, y=node_y,
        mode='markers+text',
        hoverinfo='text',
        text=node_labels,
        textposition='top right',
        textfont=dict(size=10, color='#1a237e', family='sans-serif'),
        hovertext=node_text,
        customdata=custom_data,
        marker=dict(
            showscale=False,
            color=node_color,
            size=node_size,
            line=dict(width=1.5, color='#ffffff')
        ),
        name='Stations'
    ))
    
    fig.update_layout(
        plot_bgcolor='#ffffff',
        paper_bgcolor='#ffffff',
        showlegend=False,
        hovermode='closest',
        margin=dict(b=20, l=20, r=20, t=20),
        xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
        yaxis=dict(showgrid=False, zeroline=False, showticklabels=False)
    )
    
    return json.loads(fig.to_json())

def get_route_map(src='CSMT', dst='TNA'):
    """
    Renders an interactive route map focused on the travel corridor between src and dst.
    """
    df_all = get_all_stations_df()
    adjacency = get_adjacency_list()

    base_edge_x = []
    base_edge_y = []

    st_coord_map = {row['station_code']: (float(row['longitude']), float(row['latitude'])) for _, row in df_all.iterrows()}

    for node, neighbors in adjacency.items():
        if node in st_coord_map:
            x0, y0 = st_coord_map[node]
            for nbr in neighbors:
                if nbr in st_coord_map:
                    x1, y1 = st_coord_map[nbr]
                    base_edge_x.extend([x0, x1, None])
                    base_edge_y.extend([y0, y1, None])

    fig = go.Figure()

    fig.add_trace(go.Scatter(
        x=base_edge_x,
        y=base_edge_y,
        mode='lines',
        line=dict(color='#d1d5db', width=2),
        hoverinfo='none',
        name='Central Line Network'
    ))

    route_res = find_route(src, dst)
    if route_res and route_res.get('timeline'):
        timeline = route_res['timeline']
        active_x = [pt['lon'] for pt in timeline]
        active_y = [pt['lat'] for pt in timeline]

        fig.add_trace(go.Scatter(
            x=active_x,
            y=active_y,
            mode='lines',
            line=dict(color='#1a237e', width=4),
            hoverinfo='none',
            name='Travel Corridor'
        ))

        node_colors = []
        node_sizes = []
        hover_texts = []

        for st in timeline:
            if st.get('is_origin'):
                node_colors.append('#2e7d32')
                node_sizes.append(15)
                role = "ORIGIN"
            elif st.get('is_destination'):
                node_colors.append('#c62828')
                node_sizes.append(15)
                role = "DESTINATION"
            elif st.get('is_junction'):
                node_colors.append('#f57f17')
                node_sizes.append(11)
                role = "JUNCTION INTERCHANGE"
            else:
                node_colors.append('#3949ab')
                node_sizes.append(8)
                role = "STOP"

            hover_texts.append(
                f"<b>{st['station_name']} ({st['station_code']})</b><br>"
                f"Role: {role}<br>"
                f"Platform: {st['platforms']}<br>"
                f"Scheduled Time: {st['time']}"
            )

        fig.add_trace(go.Scatter(
            x=active_x,
            y=active_y,
            mode='markers+text',
            text=[st['station_code'] if (st.get('is_origin') or st.get('is_destination') or st.get('is_junction')) else '' for st in timeline],
            textposition='top right',
            textfont=dict(size=11, color='#0d1642', family='sans-serif'),
            marker=dict(
                size=node_sizes,
                color=node_colors,
                line=dict(color='#ffffff', width=2)
            ),
            hoverinfo='text',
            hovertext=hover_texts,
            name='Route Stations'
        ))

    fig.update_layout(
        plot_bgcolor='#ffffff',
        paper_bgcolor='#ffffff',
        showlegend=False,
        hovermode='closest',
        margin=dict(l=20, r=20, t=20, b=20),
        xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
        yaxis=dict(showgrid=False, zeroline=False, showticklabels=False)
    )

    return json.loads(fig.to_json())
