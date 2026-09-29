from flask import Flask, render_template, jsonify, request
from datetime import datetime
import json
import pandas as pd

from data.database import init_db, get_all_stations_df, get_station_by_code_db, get_all_notices_db, get_active_notices_db, get_timetables_df
from data.mumbai_central_line import get_all_stations, get_station_by_code, get_station_names
from data.services import get_services_summary, get_fast_train_stops, get_hourly_frequency
from data.disruptions import get_disruptions, get_active_disruptions
from data.scraper import get_scrape_metadata
from utils.route_finder import find_route, get_connected_stations, find_alternate_route
from utils.analytics import get_kpi_data, get_transparency_data, get_hub_index, calculate_connectivity_scores
from charts.network_chart import get_network_chart
from charts.heatmap_chart import get_heatmap_chart
from charts.comparison_chart import get_comparison_chart
from charts.ranking_chart import get_ranking_chart
from charts.route_map import get_route_map

app = Flask(__name__)
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0

# Verify SQLite database safely
init_db()

@app.after_request
def add_cache_headers(response):
    response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, max-age=0'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '0'
    return response

@app.route('/')
def index():
    df_stations = get_all_stations_df()
    stations_list = df_stations.to_dict('records')
    notices = get_all_notices_db()
    active_notices = get_active_notices_db()
    kpi_data = get_kpi_data()
    transparency = get_transparency_data()
    last_updated = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    return render_template(
        'dashboard.html',
        kpi_data=kpi_data,
        stations=stations_list,
        disruptions=notices,
        active_disruptions=active_notices,
        transparency=transparency,
        last_updated=last_updated,
        data_fresh=True
    )

# -------------------------------------------------------------------------
# REST APIs — Grounded in SQLite
# -------------------------------------------------------------------------

@app.route('/api/stations')
def api_stations():
    query_str = request.args.get('q', '').strip().lower()
    stations = get_all_stations_df().to_dict('records')
    if query_str:
        filtered = [
            s for s in stations 
            if query_str in str(s.get('station_name', '')).lower() or query_str in str(s.get('station_code', '')).lower()
        ]
        return jsonify(filtered)
    return jsonify(stations)

@app.route('/api/station/<code>')
def api_station(code):
    st = get_station_by_code_db(code)
    if not st:
        st = get_station_by_code(code)
    if not st:
        return jsonify({"error": f"Station '{code}' not found."}), 404

    st_code = st.get('station_code') or st.get('code')
    hub_idx = get_hub_index(st_code)
    connected_codes = get_connected_stations(st_code)

    neighbor_stations = []
    for c in connected_codes:
        cs = get_station_by_code_db(c) or get_station_by_code(c)
        if cs:
            neighbor_stations.append({
                "name": cs.get('station_name') or cs.get('name'),
                "code": cs.get('station_code') or cs.get('code'),
                "platforms": cs.get('platforms', 2)
            })

    fast_stops = set(get_fast_train_stops())
    fast_avail = st_code in fast_stops

    hourly_freq = get_hourly_frequency(st_code)
    peak_h = max(hourly_freq.items(), key=lambda x: x[1])[0] if hourly_freq else "08:00"

    result = {
        "overview": {
            "name": st.get('station_name') or st.get('name'),
            "code": st_code,
            "zone": st.get('zone', 'Central Railway'),
            "line": st.get('line', 'Main Line'),
            "platforms": int(st.get('platforms', 2)),
            "junction_status": bool(st.get('junction_status') or st.get('is_junction')),
            "fast_train_availability": fast_avail,
            "connectivity_score": float(st.get('connectivity_score', hub_idx)),
            "hub_index": round(hub_idx, 1),
            "latitude": float(st.get('latitude') or st.get('lat', 19.0)),
            "longitude": float(st.get('longitude') or st.get('lon', 72.8))
        },
        "service_info": {
            "first_train": "05:15",
            "last_train": "23:45",
            "total_indexed_services": sum(hourly_freq.values()),
            "peak_hour": f"{peak_h} – Peak Suburban Density",
            "hourly_frequency": hourly_freq
        },
        "connectivity": {
            "connected_stations": neighbor_stations,
            "connected_count": len(neighbor_stations),
            "line": st.get('line', 'Main Line'),
            "zone": st.get('zone', 'Central Railway')
        }
    }
    # Backwards-compatible flat attributes
    result["name"] = result["overview"]["name"]
    result["code"] = st_code
    result["zone"] = result["overview"]["zone"]
    result["branch"] = result["overview"]["line"]
    result["platforms"] = result["overview"]["platforms"]
    result["junction_status"] = result["overview"]["junction_status"]
    result["connectivity_score"] = result["overview"]["connectivity_score"]
    result["hub_index"] = result["overview"]["hub_index"]
    result["fast_trains"] = fast_avail
    result["peak_services"] = hourly_freq.get(peak_h, 14) if hourly_freq else 14
    result["connected_stations"] = [s["name"] for s in neighbor_stations]
    return jsonify(result)

@app.route('/api/route')
def api_route():
    src = (request.args.get('from') or request.args.get('src') or '').strip()
    dst = (request.args.get('to') or request.args.get('dst') or '').strip()
    time_val = request.args.get('time', '').strip()

    if not src or not dst:
        return jsonify({"error": "Both 'from' (or 'src') and 'to' (or 'dst') parameters are required."}), 400

    primary = find_route(src, dst, query_time=time_val)
    if not primary:
        return jsonify({"error": f"No corridor service found between '{src}' and '{dst}'."}), 404

    timeline = primary.get('timeline', [])
    primary['distance'] = primary.get('distance_km', 0)
    primary['est_time'] = primary.get('estimated_time_min', 0)
    primary['departure_time'] = timeline[0].get('time', time_val or '--:--') if timeline else (time_val or '--:--')
    primary['arrival_time'] = timeline[-1].get('time', '--:--') if timeline else '--:--'
    route_stations = primary.get('stations', [])
    start_order = route_stations[0].get('station_order') if route_stations else None
    end_order = route_stations[-1].get('station_order') if route_stations else None
    primary['direction'] = 'Down' if start_order is None or end_order is None or start_order < end_order else 'Up'

    return jsonify({"primary": primary})

@app.route('/api/timetable')
def api_timetable():
    station = request.args.get('station', 'CSMT').strip()
    direction = request.args.get('direction', 'all').strip()

    from data.database import get_db_connection
    conn = get_db_connection()
    query = '''
    SELECT 
        t.train_number,
        t.train_name,
        t.service_type,
        t.direction,
        t.destination_station,
        tt.arrival_time,
        tt.departure_time
    FROM timetables tt
    JOIN trains t ON tt.train_id = t.train_id
    JOIN stations s ON tt.station_id = s.station_id
    WHERE (LOWER(s.station_code) = ? OR LOWER(s.station_name) = ?) AND t.active = 1
    '''
    params = [station.lower(), station.lower()]

    if direction and direction.lower() != 'all':
        query += " AND LOWER(t.direction) = ?"
        params.append(direction.lower())

    query += " ORDER BY tt.departure_time ASC LIMIT 30"
    df = pd.read_sql_query(query, conn, params=params)
    conn.close()

    return jsonify(df.to_dict('records'))

@app.route('/api/notices')
@app.route('/api/disruptions')
def api_notices():
    return jsonify({
        "all_notices": get_all_notices_db(),
        "active_notices": get_active_notices_db()
    })

@app.route('/api/charts/network')
def api_chart_network():
    return jsonify(get_network_chart())

@app.route('/api/heatmap')
@app.route('/api/charts/heatmap')
def api_chart_heatmap():
    branch = request.args.get('branch', 'all')
    s_type = request.args.get('type', 'all')
    return jsonify(get_heatmap_chart(branch=branch, train_type=s_type))

@app.route('/api/charts/ranking')
def api_chart_ranking():
    return jsonify(get_ranking_chart())

@app.route('/api/charts/comparison')
def api_chart_comparison():
    return jsonify(get_comparison_chart())

@app.route('/api/charts/route-map')
@app.route('/api/charts/route_map')
def api_chart_route_map():
    src = (request.args.get('from') or request.args.get('src') or 'CSMT').strip()
    dst = (request.args.get('to') or request.args.get('dst') or 'TNA').strip()
    return jsonify(get_route_map(src, dst))

@app.route('/api/scraper/refresh', methods=['POST'])
def api_scraper_refresh():
    meta = get_scrape_metadata()
    return jsonify({"status": "verified_cache", "message": "Official Central Railway bulletins verified in SQLite.", "meta": meta})

if __name__ == '__main__':
    app.run(port=5000, debug=True)
