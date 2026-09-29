from collections import deque
from datetime import datetime, timedelta
from data.database import get_station_by_code_db, get_active_notices_db, get_all_stations_df
from data.mumbai_central_line import get_all_stations, get_station_by_code

# Map out adjacency to mimic actual Central Line tracks
_ADJACENCY_LIST = {
    'CSMT': ['MSD'], 'MSD': ['CSMT', 'SNRD'], 'SNRD': ['MSD', 'BY'],
    'BY': ['SNRD', 'CHG'], 'CHG': ['BY', 'CRD'], 'CRD': ['CHG', 'PR'],
    'PR': ['CRD', 'DR'], 'DR': ['PR', 'MTN'], 'MTN': ['DR', 'SIN'],
    'SIN': ['MTN', 'CLA'], 'CLA': ['SIN', 'VVH'], 'VVH': ['CLA', 'GC'],
    'GC': ['VVH', 'VK'], 'VK': ['GC', 'KJRD'], 'KJRD': ['VK', 'BND'],
    'BND': ['KJRD', 'NHU'], 'NHU': ['BND', 'MLND'], 'MLND': ['NHU', 'TNA'],
    'TNA': ['MLND', 'KLVA'], 'KLVA': ['TNA', 'MBQ'], 'MBQ': ['KLVA', 'DIVA'],
    'DIVA': ['MBQ', 'KOPR'], 'KOPR': ['DIVA', 'DI'], 'DI': ['KOPR', 'THK'],
    'THK': ['DI', 'KYN'], 'KYN': ['THK', 'SHAD', 'VLDI'],
    # Kasara Branch
    'SHAD': ['KYN', 'ABY'], 'ABY': ['SHAD', 'TLA'], 'TLA': ['ABY', 'KDV'],
    'KDV': ['TLA', 'VSD'], 'VSD': ['KDV', 'ASO'], 'ASO': ['VSD', 'ATG'],
    'ATG': ['ASO', 'KE'], 'KE': ['ATG', 'KSRA'], 'KSRA': ['KE'],
    # Karjat Branch
    'VLDI': ['KYN', 'ULNR'], 'ULNR': ['VLDI', 'ABH'], 'ABH': ['ULNR', 'BUD'],
    'BUD': ['ABH', 'VGI'], 'VGI': ['BUD', 'SHLU'], 'SHLU': ['VGI', 'NRL'],
    'NRL': ['SHLU', 'BVS'], 'BVS': ['NRL', 'KJT'], 'KJT': ['BVS', 'PDI'],
    # Khopoli Branch
    'PDI': ['KJT', 'KLY'], 'KLY': ['PDI', 'DLV'], 'DLV': ['KLY', 'LWJ'],
    'LWJ': ['DLV', 'KHPI'], 'KHPI': ['LWJ']
}

def get_adjacency_list():
    return _ADJACENCY_LIST

def get_connected_stations(code):
    return _ADJACENCY_LIST.get(code.upper(), [])

def resolve_station_code(query):
    if not query:
        return None
    code_upper = str(query).strip().upper()
    if code_upper in _ADJACENCY_LIST:
        return code_upper
    st = get_station_by_code_db(code_upper)
    if st:
        return st['station_code']
    try:
        df = get_all_stations_df()
        q_clean = str(query).strip().lower()
        match = df[df['station_name'].str.lower() == q_clean]
        if not match.empty:
            return match.iloc[0]['station_code']
        match_part = df[df['station_name'].str.lower().str.contains(q_clean, regex=False)]
        if not match_part.empty:
            return match_part.iloc[0]['station_code']
    except Exception:
        pass
    return None

def find_route(start_code, end_code, query_time=None):
    start = resolve_station_code(start_code)
    end = resolve_station_code(end_code)
    
    if not start or not end or start not in _ADJACENCY_LIST or end not in _ADJACENCY_LIST:
        return None
        
    queue = deque([[start]])
    visited = {start}
    path = None
    
    while queue:
        current_path = queue.popleft()
        node = current_path[-1]
        
        if node == end:
            path = current_path
            break
            
        for neighbor in _ADJACENCY_LIST.get(node, []):
            if neighbor not in visited:
                visited.add(neighbor)
                queue.append(current_path + [neighbor])
                
    if not path:
        return None
        
    stations = []
    for code in path:
        st = get_station_by_code_db(code)
        if not st:
            st = get_station_by_code(code)
        stations.append(st)
        
    # Calculate distance and time
    dist_km = abs(float(stations[-1].get('km_from_csmt', 0)) - float(stations[0].get('km_from_csmt', 0)))
    
    # Establish base departure time
    if query_time:
        try:
            now_dt = datetime.strptime(query_time, "%H:%M")
        except Exception:
            now_dt = datetime.now()
    else:
        now_dt = datetime.now()
        
    timeline = []
    cur_time = now_dt
    for i, st in enumerate(stations):
        code = st.get('station_code') or st.get('code')
        name = st.get('station_name') or st.get('name')
        lat = float(st.get('latitude') or st.get('lat') or 19.0)
        lon = float(st.get('longitude') or st.get('lon') or 72.8)
        platforms = st.get('platforms', 2)
        is_junc = bool(st.get('junction_status') or st.get('is_junction'))
        
        if i > 0:
            cur_time += timedelta(minutes=2.3)
            
        timeline.append({
            "station_code": code,
            "station_name": name,
            "lat": lat,
            "lon": lon,
            "platforms": platforms,
            "is_origin": (i == 0),
            "is_destination": (i == len(stations) - 1),
            "is_junction": is_junc,
            "time": cur_time.strftime("%H:%M")
        })
        
    total_est_min = max(4, int((cur_time - now_dt).total_seconds() / 60))
    fast_available = all(bool(s.get('fast_train_stop')) for s in stations) if len(stations) > 4 else False
    service_type = "Fast Suburban" if fast_available else "Slow Suburban"
    
    # Check matching disruptions
    matching_disruptions = []
    try:
        active_notices = get_active_notices_db()
        path_set = set(path)
        path_names = {str(s.get('station_name', '')).lower() for s in stations}
        for n in active_notices:
            affected = n.get('affected_stations', '')
            aff_list = [x.strip() for x in affected.split(',') if x.strip()]
            matched_st = [a for a in aff_list if a.upper() in path_set or a.lower() in path_names]
            if matched_st:
                matching_disruptions.append({
                    "title": n.get('title'),
                    "affected_stations": affected,
                    "matched": matched_st,
                    "description": n.get('description')
                })
    except Exception:
        pass
        
    # Generate subsequent train runs
    more_options = []
    dep_base = now_dt
    for idx, delta_m in enumerate([10, 22, 35]):
        t_dep = dep_base + timedelta(minutes=delta_m)
        t_arr = t_dep + timedelta(minutes=total_est_min)
        more_options.append({
            "train_number": f"CR-9{100 + idx*4}",
            "train_type": "Fast Suburban" if (idx % 2 == 1 and fast_available) else service_type,
            "departure": t_dep.strftime("%H:%M"),
            "arrival": t_arr.strftime("%H:%M"),
            "duration_min": total_est_min,
            "stops": len(path) - 1
        })
        
    return {
        "path": path,
        "stations": stations,
        "timeline": timeline,
        "stops": len(path) - 1,
        "distance_km": round(dist_km, 2),
        "estimated_time_min": total_est_min,
        "service_type": service_type,
        "fast_available": fast_available,
        "route_description": f"Direct route via Central Line {service_type}",
        "train_number": f"CR-9{now_dt.hour*10 + (1 if now_dt.minute % 2 == 1 else 2)}",
        "matching_disruptions": matching_disruptions,
        "more_options": more_options
    }

def find_alternate_route(start, end):
    return find_route(start, end)
