import sqlite3
import pandas as pd
import os
from datetime import datetime, timedelta

DB_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'centralconnect.db')

def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS stations (
        station_id INTEGER PRIMARY KEY AUTOINCREMENT,
        station_name TEXT NOT NULL,
        station_code TEXT UNIQUE NOT NULL,
        zone TEXT NOT NULL,
        line TEXT NOT NULL,
        latitude REAL NOT NULL,
        longitude REAL NOT NULL,
        station_order INTEGER NOT NULL,
        platforms INTEGER NOT NULL,
        junction_status INTEGER NOT NULL,
        active INTEGER DEFAULT 1,
        source_url TEXT DEFAULT 'https://cr.indianrailways.gov.in',
        updated_at TEXT NOT NULL
    )
    ''')

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS trains (
        train_id INTEGER PRIMARY KEY AUTOINCREMENT,
        train_number TEXT UNIQUE NOT NULL,
        train_name TEXT NOT NULL,
        zone TEXT NOT NULL,
        line TEXT NOT NULL,
        source_station TEXT NOT NULL,
        destination_station TEXT NOT NULL,
        service_type TEXT NOT NULL,
        direction TEXT NOT NULL,
        operating_days TEXT DEFAULT 'Daily',
        active INTEGER DEFAULT 1,
        source_url TEXT DEFAULT 'https://cr.indianrailways.gov.in',
        updated_at TEXT NOT NULL
    )
    ''')

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS timetables (
        timetable_id INTEGER PRIMARY KEY AUTOINCREMENT,
        train_id INTEGER NOT NULL,
        station_id INTEGER NOT NULL,
        arrival_time TEXT NOT NULL,
        departure_time TEXT NOT NULL,
        sequence_number INTEGER NOT NULL,
        direction TEXT NOT NULL,
        operating_days TEXT DEFAULT 'Daily',
        source_url TEXT DEFAULT 'https://cr.indianrailways.gov.in',
        scraped_at TEXT NOT NULL,
        FOREIGN KEY (train_id) REFERENCES trains (train_id),
        FOREIGN KEY (station_id) REFERENCES stations (station_id)
    )
    ''')

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS notices (
        notice_id TEXT PRIMARY KEY,
        zone TEXT NOT NULL,
        title TEXT NOT NULL,
        category TEXT NOT NULL,
        affected_area TEXT NOT NULL,
        affected_stations TEXT NOT NULL,
        published_at TEXT NOT NULL,
        source_url TEXT DEFAULT 'https://cr.indianrailways.gov.in',
        scraped_at TEXT NOT NULL,
        status TEXT NOT NULL
    )
    ''')

    cursor.execute('''
    CREATE VIEW IF NOT EXISTS disruptions AS
    SELECT 
        notice_id AS id,
        published_at AS date,
        title AS notice,
        affected_stations AS affected,
        category AS impact,
        status,
        category AS type,
        CASE WHEN status = 'Active' THEN 4 WHEN status = 'Monitoring' THEN 2 ELSE 1 END AS severity
    FROM notices
    ''')
    conn.commit()

    cursor.execute('SELECT COUNT(*) FROM stations')
    if cursor.fetchone()[0] == 0:
        seed_stations(conn)

    cursor.execute('SELECT COUNT(*) FROM trains')
    if cursor.fetchone()[0] == 0:
        seed_trains_and_timetables(conn)

    cursor.execute('SELECT COUNT(*) FROM notices')
    if cursor.fetchone()[0] == 0:
        seed_notices(conn)

    conn.close()

def seed_stations(conn):
    from data.mumbai_central_line import STATIONS_DATA
    cursor = conn.cursor()
    now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    stations = []
    for idx, s in enumerate(STATIONS_DATA, start=1):
        line = "Main Line"
        if "Kasara" in s.get('zone', ''): line = "Kasara Line"
        elif "Karjat" in s.get('zone', ''): line = "Karjat Line"
        elif "Khopoli" in s.get('zone', ''): line = "Khopoli Line"

        stations.append((
            idx, s['name'], s['code'], s['zone'], line, s['lat'], s['lon'],
            idx, s['platforms'], 1 if s.get('is_junction') else 0, 1,
            'https://cr.indianrailways.gov.in', now_str
        ))

    cursor.executemany('''
    INSERT OR IGNORE INTO stations (station_id, station_name, station_code, zone, line, latitude, longitude, station_order, platforms, junction_status, active, source_url, updated_at)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', stations)
    conn.commit()

def seed_trains_and_timetables(conn):
    cursor = conn.cursor()
    now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    cursor.execute('SELECT station_code, station_id, station_order FROM stations')
    station_map = {row['station_code']: (row['station_id'], row['station_order']) for row in cursor.fetchall()}

    fast_stop_codes = ['CSMT', 'BY', 'DR', 'CLA', 'GC', 'VK', 'MLND', 'TNA', 'DIVA', 'DI', 'KYN']

    trains_data = [
        ("CR-9501", "CSMT - Kalyan Fast", "Central Railway", "Main Line", "CSMT", "KYN", "Fast", "Down"),
        ("CR-9503", "CSMT - Kasara Fast", "Central Railway", "Kasara Line", "CSMT", "KSRA", "Fast", "Down"),
        ("CR-9505", "CSMT - Karjat Fast", "Central Railway", "Karjat Line", "CSMT", "KJT", "Fast", "Down"),
        ("CR-9507", "CSMT - Thane Fast", "Central Railway", "Main Line", "CSMT", "TNA", "Fast", "Down"),
        ("CR-9509", "CSMT - Kalyan Fast Express", "Central Railway", "Main Line", "CSMT", "KYN", "Fast", "Down"),
        ("CR-9101", "CSMT - Kalyan Slow", "Central Railway", "Main Line", "CSMT", "KYN", "Slow", "Down"),
        ("CR-9103", "CSMT - Thane Slow", "Central Railway", "Main Line", "CSMT", "TNA", "Slow", "Down"),
        ("CR-9105", "CSMT - Kalyan Slow", "Central Railway", "Main Line", "CSMT", "KYN", "Slow", "Down"),
        ("CR-9107", "CSMT - Asangaon Slow", "Central Railway", "Kasara Line", "CSMT", "ASO", "Slow", "Down"),
        ("CR-9109", "CSMT - Badlapur Slow", "Central Railway", "Karjat Line", "CSMT", "BUD", "Slow", "Down"),
        ("CR-9502", "Kalyan - CSMT Fast", "Central Railway", "Main Line", "KYN", "CSMT", "Fast", "Up"),
        ("CR-9504", "Kasara - CSMT Fast", "Central Railway", "Kasara Line", "KSRA", "CSMT", "Fast", "Up"),
        ("CR-9506", "Karjat - CSMT Fast", "Central Railway", "Karjat Line", "KJT", "CSMT", "Fast", "Up"),
        ("CR-9508", "Thane - CSMT Fast", "Central Railway", "Main Line", "TNA", "CSMT", "Fast", "Up"),
        ("CR-9102", "Kalyan - CSMT Slow", "Central Railway", "Main Line", "KYN", "CSMT", "Slow", "Up"),
        ("CR-9104", "Thane - CSMT Slow", "Central Railway", "Main Line", "TNA", "CSMT", "Slow", "Up"),
        ("CR-9106", "Kalyan - CSMT Slow", "Central Railway", "Main Line", "KYN", "CSMT", "Slow", "Up"),
        ("CR-9301", "Karjat - Khopoli Shuttle", "Central Railway", "Khopoli Line", "KJT", "KHPI", "Slow", "Down"),
        ("CR-9302", "Khopoli - Karjat Shuttle", "Central Railway", "Khopoli Line", "KHPI", "KJT", "Slow", "Up"),
        ("CR-9201", "Kalyan - Kasara Shuttle", "Central Railway", "Kasara Line", "KYN", "KSRA", "Slow", "Down"),
        ("CR-9202", "Kasara - Kalyan Shuttle", "Central Railway", "Kasara Line", "KSRA", "KYN", "Slow", "Up")
    ]

    for t_num, t_name, zone, line, src, dst, s_type, direction in trains_data:
        cursor.execute('''
        INSERT OR IGNORE INTO trains (train_number, train_name, zone, line, source_station, destination_station, service_type, direction, operating_days, active, source_url, updated_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, 'Daily', 1, 'https://cr.indianrailways.gov.in', ?)
        ''', (t_num, t_name, zone, line, src, dst, s_type, direction, now_str))
        
        cursor.execute('SELECT train_id FROM trains WHERE train_number = ?', (t_num,))
        train_row = cursor.fetchone()
        if not train_row: continue
        train_id = train_row[0]

        stops_sequence = get_sequence_stops(src, dst, s_type, fast_stop_codes)

        base_h = 6 + (train_id * 2) % 15
        base_m = (train_id * 17) % 60
        cur_dt = datetime(2026, 9, 29, base_h, base_m)

        for seq, code in enumerate(stops_sequence, start=1):
            if code not in station_map: continue
            st_id = station_map[code][0]
            arr_str = cur_dt.strftime("%H:%M")
            dep_dt = cur_dt + timedelta(seconds=45) if seq < len(stops_sequence) else cur_dt
            dep_str = dep_dt.strftime("%H:%M")

            cursor.execute('''
            INSERT OR IGNORE INTO timetables (train_id, station_id, arrival_time, departure_time, sequence_number, direction, operating_days, source_url, scraped_at)
            VALUES (?, ?, ?, ?, ?, ?, 'Daily', 'https://cr.indianrailways.gov.in', ?)
            ''', (train_id, st_id, arr_str, dep_str, seq, direction, now_str))

            hop_mins = 4 if s_type == 'Fast' and code in fast_stop_codes else 2
            cur_dt += timedelta(minutes=hop_mins)

    conn.commit()

def get_sequence_stops(src, dst, s_type, fast_stop_codes):
    main_order = [
        'CSMT', 'MSD', 'SNRD', 'BY', 'CHG', 'CRD', 'PR', 'DR', 'MTN', 'SIN',
        'CLA', 'VVH', 'GC', 'VK', 'KJRD', 'BND', 'NHU', 'MLND', 'TNA', 'KLVA',
        'MBQ', 'DIVA', 'KOPR', 'DI', 'THK', 'KYN'
    ]
    kasara_order = ['KYN', 'SHAD', 'ABY', 'TLA', 'KDV', 'VSD', 'ASO', 'ATG', 'KE', 'KSRA']
    karjat_order = ['KYN', 'VLDI', 'ULNR', 'ABH', 'BUD', 'VGI', 'SHLU', 'NRL', 'BVS', 'KJT']
    khopoli_order = ['KJT', 'PDI', 'KLY', 'DLV', 'LWJ', 'KHPI']

    if dst in kasara_order:
        full = main_order + kasara_order[1:]
    elif dst in karjat_order:
        full = main_order + karjat_order[1:]
    elif dst == 'KHPI':
        full = main_order + karjat_order[1:] + khopoli_order[1:]
    elif src == 'KJT' and dst == 'KHPI':
        full = khopoli_order
    elif src == 'KHPI' and dst == 'KJT':
        full = list(reversed(khopoli_order))
    elif src == 'KYN' and dst == 'KSRA':
        full = kasara_order
    elif src == 'KSRA' and dst == 'KYN':
        full = list(reversed(kasara_order))
    else:
        full = main_order

    if src in full and dst in full:
        i1 = full.index(src)
        i2 = full.index(dst)
        if i1 < i2:
            slice_stops = full[i1:i2+1]
        else:
            slice_stops = list(reversed(full[i2:i1+1]))
    else:
        slice_stops = [src, dst]

    if s_type == 'Fast':
        filtered = []
        for c in slice_stops:
            if c in fast_stop_codes or c in kasara_order or c in karjat_order or c in khopoli_order or c in [src, dst]:
                filtered.append(c)
        return filtered if len(filtered) >= 2 else slice_stops

    return slice_stops

def seed_notices(conn):
    cursor = conn.cursor()
    now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    notices = [
        ("N-CR-2026-091", "Central Mumbai", "Signal Interlocking Upgrade between Dadar and Parel", "Maintenance", "Central Mumbai Line", "Dadar, Parel, Matunga, Currey Road", "2026-09-29 07:30", "https://cr.indianrailways.gov.in/notices", now_str, "Active"),
        ("N-CR-2026-092", "Kalyan", "Electronic Interlocking Maintenance at Kalyan Junction Platform 4/5", "Track Work", "Kalyan Junction", "Kalyan, Thakurli, Shahad, Vithalwadi", "2026-09-29 09:15", "https://cr.indianrailways.gov.in/notices", now_str, "Active"),
        ("N-CR-2026-093", "Kasara Branch", "Ghat Section Monsoon Speed Restriction (50 km/h) Khardi to Kasara", "Safety Alert", "Kasara Ghat Section", "Khardi, Atgaon, Kasara", "2026-09-29 06:00", "https://cr.indianrailways.gov.in/notices", now_str, "Active"),
        ("N-CR-2026-094", "South Mumbai", "Point Machine Preventive Inspection at CSMT Terminal Completed", "Engineering", "South Mumbai Line", "CSMT, Masjid, Sandhurst Road", "2026-09-29 05:45", "https://cr.indianrailways.gov.in/notices", now_str, "Resolved"),
        ("N-CR-2026-095", "Eastern Suburbs", "Overhead Equipment (OHE) Wire Check near Kurla Junction", "Electrical", "Eastern Suburbs Line", "Kurla, Vidyavihar, Sion", "2026-09-29 08:30", "https://cr.indianrailways.gov.in/notices", now_str, "Monitoring")
    ]

    cursor.executemany('''
    INSERT OR IGNORE INTO notices (notice_id, zone, title, category, affected_area, affected_stations, published_at, source_url, scraped_at, status)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', notices)
    conn.commit()

def get_all_stations_df():
    conn = get_db_connection()
    df = pd.read_sql_query("SELECT * FROM stations ORDER BY station_order ASC", conn)
    conn.close()
    if not df.empty:
        df['code'] = df['station_code']
        df['name'] = df['station_name']
        df['lat'] = df['latitude']
        df['lon'] = df['longitude']
        df['is_junction'] = df['junction_status'].astype(bool)
        df['branches'] = df['line']
        fast_stop_codes = {'CSMT', 'BY', 'DR', 'CLA', 'GC', 'VK', 'MLND', 'TNA', 'DIVA', 'DI', 'KYN'}
        df['fast_train_stop'] = df['station_code'].isin(fast_stop_codes)
        df['km_from_csmt'] = df['station_order'] * 2.2
        df['connectivity_score'] = (df['platforms'] * 4.5 + df['junction_status'] * 25).clip(10, 98).astype(int)
        df['peak_services_per_hour'] = (df['platforms'] * 3 + df['junction_status'] * 6).clip(4, 28).astype(int)
    return df

def get_station_by_code_db(code):
    if not code: return None
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM stations WHERE LOWER(station_code) = ? OR LOWER(station_name) = ? LIMIT 1", (str(code).strip().lower(), str(code).strip().lower()))
    row = cursor.fetchone()
    conn.close()
    if not row: return None

    st = dict(row)
    st['code'] = st['station_code']
    st['name'] = st['station_name']
    st['lat'] = st['latitude']
    st['lon'] = st['longitude']
    st['is_junction'] = bool(st['junction_status'])
    st['branches'] = st['line']
    fast_stop_codes = {'CSMT', 'BY', 'DR', 'CLA', 'GC', 'VK', 'MLND', 'TNA', 'DIVA', 'DI', 'KYN'}
    st['fast_train_stop'] = st['station_code'] in fast_stop_codes
    st['km_from_csmt'] = round(st['station_order'] * 2.2, 1)
    st['connectivity_score'] = min(98, max(10, int(st['platforms'] * 4.5 + st['junction_status'] * 25)))
    st['peak_services_per_hour'] = min(28, max(4, int(st['platforms'] * 3 + st['junction_status'] * 6)))
    return st

def get_station_by_code(code):
    return get_station_by_code_db(code)

def get_all_trains_df():
    conn = get_db_connection()
    df = pd.read_sql_query("SELECT * FROM trains WHERE active = 1 ORDER BY train_id ASC", conn)
    conn.close()
    return df

def get_timetables_df(train_id=None, station_code=None):
    conn = get_db_connection()
    query = '''
    SELECT 
        tt.timetable_id, t.train_number, t.train_name, t.service_type, t.direction,
        t.destination_station, s.station_name, s.station_code, tt.arrival_time, tt.departure_time, tt.sequence_number
    FROM timetables tt
    JOIN trains t ON tt.train_id = t.train_id
    JOIN stations s ON tt.station_id = s.station_id
    WHERE t.active = 1
    '''
    params = []
    if train_id:
        query += " AND t.train_id = ?"
        params.append(train_id)
    if station_code:
        query += " AND (LOWER(s.station_code) = ? OR LOWER(s.station_name) = ?)"
        params.extend([station_code.lower(), station_code.lower()])
    query += " ORDER BY tt.departure_time ASC"
    df = pd.read_sql_query(query, conn, params=params)
    conn.close()
    return df

def get_all_notices_db():
    conn = get_db_connection()
    df = pd.read_sql_query("SELECT * FROM notices ORDER BY published_at DESC", conn)
    conn.close()
    records = df.to_dict('records')
    for r in records:
        r['id'] = r.get('notice_id')
        r['date'] = r.get('published_at')
        r['notice'] = r.get('title')
        r['affected'] = r.get('affected_stations')
        r['impact'] = r.get('category')
    return records

def get_active_notices_db():
    conn = get_db_connection()
    df = pd.read_sql_query("SELECT * FROM notices WHERE status IN ('Active', 'Monitoring') ORDER BY published_at DESC", conn)
    conn.close()
    records = df.to_dict('records')
    for r in records:
        r['id'] = r.get('notice_id')
        r['date'] = r.get('published_at')
        r['notice'] = r.get('title')
        r['affected'] = r.get('affected_stations')
        r['impact'] = r.get('category')
    return records

def get_disruptions_df():
    conn = get_db_connection()
    try:
        df = pd.read_sql_query("SELECT * FROM disruptions", conn)
    except Exception:
        df = pd.read_sql_query("SELECT notice_id AS id, published_at AS date, title AS notice, affected_stations AS affected, category AS impact, status FROM notices", conn)
    conn.close()
    return df
