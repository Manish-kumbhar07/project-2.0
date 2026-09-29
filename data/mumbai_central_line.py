import pandas as pd

STATIONS_DATA = [
    {"name": "CSMT", "code": "CSMT", "zone": "South Mumbai", "km_from_csmt": 0.0, "lat": 18.9398, "lon": 72.8355, "platforms": 18, "is_junction": True, "branches": "Harbour Line", "connectivity_score": 98, "fast_train_stop": True, "peak_services_per_hour": 50},
    {"name": "Masjid", "code": "MSD", "zone": "South Mumbai", "km_from_csmt": 1.2, "lat": 18.9515, "lon": 72.8378, "platforms": 4, "is_junction": False, "branches": "", "connectivity_score": 60, "fast_train_stop": False, "peak_services_per_hour": 35},
    {"name": "Sandhurst Road", "code": "SNRD", "zone": "South Mumbai", "km_from_csmt": 2.2, "lat": 18.9600, "lon": 72.8383, "platforms": 4, "is_junction": True, "branches": "Harbour Line", "connectivity_score": 65, "fast_train_stop": False, "peak_services_per_hour": 35},
    {"name": "Byculla", "code": "BY", "zone": "South Mumbai", "km_from_csmt": 4.1, "lat": 18.9774, "lon": 72.8335, "platforms": 4, "is_junction": False, "branches": "", "connectivity_score": 75, "fast_train_stop": True, "peak_services_per_hour": 40},
    {"name": "Chinchpokli", "code": "CHG", "zone": "South Mumbai", "km_from_csmt": 5.1, "lat": 18.9839, "lon": 72.8315, "platforms": 2, "is_junction": False, "branches": "", "connectivity_score": 50, "fast_train_stop": False, "peak_services_per_hour": 25},
    {"name": "Currey Road", "code": "CRD", "zone": "South Mumbai", "km_from_csmt": 6.0, "lat": 18.9947, "lon": 72.8329, "platforms": 2, "is_junction": False, "branches": "", "connectivity_score": 55, "fast_train_stop": False, "peak_services_per_hour": 25},
    {"name": "Parel", "code": "PR", "zone": "Central Mumbai", "km_from_csmt": 7.4, "lat": 19.0084, "lon": 72.8361, "platforms": 4, "is_junction": False, "branches": "", "connectivity_score": 70, "fast_train_stop": False, "peak_services_per_hour": 30},
    {"name": "Dadar", "code": "DR", "zone": "Central Mumbai", "km_from_csmt": 8.7, "lat": 19.0191, "lon": 72.8427, "platforms": 8, "is_junction": True, "branches": "Western Line", "connectivity_score": 100, "fast_train_stop": True, "peak_services_per_hour": 60},
    {"name": "Matunga", "code": "MTN", "zone": "Central Mumbai", "km_from_csmt": 10.3, "lat": 19.0279, "lon": 72.8510, "platforms": 4, "is_junction": False, "branches": "", "connectivity_score": 55, "fast_train_stop": False, "peak_services_per_hour": 25},
    {"name": "Sion", "code": "SIN", "zone": "Central Mumbai", "km_from_csmt": 12.9, "lat": 19.0396, "lon": 72.8622, "platforms": 4, "is_junction": False, "branches": "", "connectivity_score": 60, "fast_train_stop": False, "peak_services_per_hour": 25},
    {"name": "Kurla", "code": "CLA", "zone": "Eastern Suburbs", "km_from_csmt": 15.6, "lat": 19.0664, "lon": 72.8797, "platforms": 8, "is_junction": True, "branches": "Harbour Line", "connectivity_score": 95, "fast_train_stop": True, "peak_services_per_hour": 55},
    {"name": "Vidyavihar", "code": "VVH", "zone": "Eastern Suburbs", "km_from_csmt": 18.0, "lat": 19.0792, "lon": 72.8953, "platforms": 4, "is_junction": False, "branches": "", "connectivity_score": 50, "fast_train_stop": False, "peak_services_per_hour": 20},
    {"name": "Ghatkopar", "code": "GC", "zone": "Eastern Suburbs", "km_from_csmt": 19.5, "lat": 19.0863, "lon": 72.9090, "platforms": 6, "is_junction": True, "branches": "Metro Line 1", "connectivity_score": 90, "fast_train_stop": True, "peak_services_per_hour": 45},
    {"name": "Vikhroli", "code": "VK", "zone": "Eastern Suburbs", "km_from_csmt": 23.4, "lat": 19.1090, "lon": 72.9281, "platforms": 4, "is_junction": False, "branches": "", "connectivity_score": 65, "fast_train_stop": True, "peak_services_per_hour": 30},
    {"name": "Kanjurmarg", "code": "KJRD", "zone": "Eastern Suburbs", "km_from_csmt": 25.4, "lat": 19.1248, "lon": 72.9329, "platforms": 4, "is_junction": False, "branches": "", "connectivity_score": 50, "fast_train_stop": False, "peak_services_per_hour": 20},
    {"name": "Bhandup", "code": "BND", "zone": "Eastern Suburbs", "km_from_csmt": 27.2, "lat": 19.1436, "lon": 72.9372, "platforms": 4, "is_junction": False, "branches": "", "connectivity_score": 55, "fast_train_stop": False, "peak_services_per_hour": 20},
    {"name": "Nahur", "code": "NHU", "zone": "Eastern Suburbs", "km_from_csmt": 29.2, "lat": 19.1557, "lon": 72.9463, "platforms": 2, "is_junction": False, "branches": "", "connectivity_score": 40, "fast_train_stop": False, "peak_services_per_hour": 15},
    {"name": "Mulund", "code": "MLND", "zone": "Eastern Suburbs", "km_from_csmt": 31.5, "lat": 19.1724, "lon": 72.9566, "platforms": 4, "is_junction": False, "branches": "", "connectivity_score": 75, "fast_train_stop": True, "peak_services_per_hour": 35},
    {"name": "Thane", "code": "TNA", "zone": "Thane", "km_from_csmt": 34.0, "lat": 19.1866, "lon": 72.9754, "platforms": 10, "is_junction": True, "branches": "Trans-Harbour Line", "connectivity_score": 98, "fast_train_stop": True, "peak_services_per_hour": 60},
    {"name": "Kalwa", "code": "KLVA", "zone": "Thane", "km_from_csmt": 36.4, "lat": 19.2017, "lon": 72.9979, "platforms": 4, "is_junction": False, "branches": "", "connectivity_score": 50, "fast_train_stop": False, "peak_services_per_hour": 20},
    {"name": "Mumbra", "code": "MBQ", "zone": "Thane", "km_from_csmt": 40.5, "lat": 19.1895, "lon": 73.0245, "platforms": 4, "is_junction": False, "branches": "", "connectivity_score": 50, "fast_train_stop": False, "peak_services_per_hour": 20},
    {"name": "Diva", "code": "DIVA", "zone": "Thane", "km_from_csmt": 42.6, "lat": 19.1890, "lon": 73.0421, "platforms": 6, "is_junction": True, "branches": "Vasai-Roha Line", "connectivity_score": 70, "fast_train_stop": True, "peak_services_per_hour": 30},
    {"name": "Kopar", "code": "KOPR", "zone": "Thane", "km_from_csmt": 47.1, "lat": 19.2132, "lon": 73.0768, "platforms": 4, "is_junction": False, "branches": "", "connectivity_score": 45, "fast_train_stop": False, "peak_services_per_hour": 15},
    {"name": "Dombivli", "code": "DI", "zone": "Thane", "km_from_csmt": 48.4, "lat": 19.2183, "lon": 73.0867, "platforms": 6, "is_junction": False, "branches": "", "connectivity_score": 85, "fast_train_stop": True, "peak_services_per_hour": 40},
    {"name": "Thakurli", "code": "THK", "zone": "Thane", "km_from_csmt": 49.9, "lat": 19.2274, "lon": 73.1042, "platforms": 4, "is_junction": False, "branches": "", "connectivity_score": 40, "fast_train_stop": False, "peak_services_per_hour": 15},
    {"name": "Kalyan", "code": "KYN", "zone": "Kalyan", "km_from_csmt": 53.9, "lat": 19.2384, "lon": 73.1325, "platforms": 8, "is_junction": True, "branches": "Kasara Line;Karjat Line", "connectivity_score": 95, "fast_train_stop": True, "peak_services_per_hour": 50},
    
    # Kasara Branch
    {"name": "Shahad", "code": "SHAD", "zone": "Kasara Branch", "km_from_csmt": 57.1, "lat": 19.2559, "lon": 73.1555, "platforms": 2, "is_junction": False, "branches": "", "connectivity_score": 35, "fast_train_stop": False, "peak_services_per_hour": 10},
    {"name": "Ambivli", "code": "ABY", "zone": "Kasara Branch", "km_from_csmt": 60.1, "lat": 19.2741, "lon": 73.1793, "platforms": 2, "is_junction": False, "branches": "", "connectivity_score": 35, "fast_train_stop": False, "peak_services_per_hour": 10},
    {"name": "Titwala", "code": "TLA", "zone": "Kasara Branch", "km_from_csmt": 64.9, "lat": 19.2974, "lon": 73.2084, "platforms": 2, "is_junction": False, "branches": "", "connectivity_score": 50, "fast_train_stop": True, "peak_services_per_hour": 15},
    {"name": "Khadavli", "code": "KDV", "zone": "Kasara Branch", "km_from_csmt": 72.3, "lat": 19.3458, "lon": 73.2388, "platforms": 2, "is_junction": False, "branches": "", "connectivity_score": 30, "fast_train_stop": False, "peak_services_per_hour": 8},
    {"name": "Vasind", "code": "VSD", "zone": "Kasara Branch", "km_from_csmt": 80.2, "lat": 19.4004, "lon": 73.2657, "platforms": 2, "is_junction": False, "branches": "", "connectivity_score": 40, "fast_train_stop": True, "peak_services_per_hour": 10},
    {"name": "Asangaon", "code": "ASO", "zone": "Kasara Branch", "km_from_csmt": 85.8, "lat": 19.4390, "lon": 73.3033, "platforms": 2, "is_junction": False, "branches": "", "connectivity_score": 45, "fast_train_stop": True, "peak_services_per_hour": 10},
    {"name": "Atgaon", "code": "ATG", "zone": "Kasara Branch", "km_from_csmt": 95.3, "lat": 19.4897, "lon": 73.3516, "platforms": 2, "is_junction": False, "branches": "", "connectivity_score": 25, "fast_train_stop": False, "peak_services_per_hour": 6},
    {"name": "Khardi", "code": "KE", "zone": "Kasara Branch", "km_from_csmt": 107.5, "lat": 19.5694, "lon": 73.3934, "platforms": 2, "is_junction": False, "branches": "", "connectivity_score": 20, "fast_train_stop": False, "peak_services_per_hour": 6},
    {"name": "Kasara", "code": "KSRA", "zone": "Kasara Branch", "km_from_csmt": 120.5, "lat": 19.6461, "lon": 73.4796, "platforms": 4, "is_junction": False, "branches": "", "connectivity_score": 50, "fast_train_stop": True, "peak_services_per_hour": 10},
    
    # Karjat Branch
    {"name": "Vithalwadi", "code": "VLDI", "zone": "Karjat Branch", "km_from_csmt": 56.4, "lat": 19.2223, "lon": 73.1517, "platforms": 2, "is_junction": False, "branches": "", "connectivity_score": 35, "fast_train_stop": False, "peak_services_per_hour": 10},
    {"name": "Ulhasnagar", "code": "ULNR", "zone": "Karjat Branch", "km_from_csmt": 58.4, "lat": 19.2198, "lon": 73.1666, "platforms": 2, "is_junction": False, "branches": "", "connectivity_score": 40, "fast_train_stop": False, "peak_services_per_hour": 12},
    {"name": "Ambernath", "code": "ABH", "zone": "Karjat Branch", "km_from_csmt": 60.5, "lat": 19.2016, "lon": 73.1837, "platforms": 4, "is_junction": False, "branches": "", "connectivity_score": 60, "fast_train_stop": True, "peak_services_per_hour": 20},
    {"name": "Badlapur", "code": "BUD", "zone": "Karjat Branch", "km_from_csmt": 68.3, "lat": 19.1539, "lon": 73.2355, "platforms": 4, "is_junction": False, "branches": "", "connectivity_score": 65, "fast_train_stop": True, "peak_services_per_hour": 18},
    {"name": "Vangani", "code": "VGI", "zone": "Karjat Branch", "km_from_csmt": 79.1, "lat": 19.0717, "lon": 73.2842, "platforms": 2, "is_junction": False, "branches": "", "connectivity_score": 30, "fast_train_stop": False, "peak_services_per_hour": 8},
    {"name": "Shelu", "code": "SHLU", "zone": "Karjat Branch", "km_from_csmt": 82.9, "lat": 19.0347, "lon": 73.3083, "platforms": 2, "is_junction": False, "branches": "", "connectivity_score": 25, "fast_train_stop": False, "peak_services_per_hour": 8},
    {"name": "Neral", "code": "NRL", "zone": "Karjat Branch", "km_from_csmt": 86.8, "lat": 19.0289, "lon": 73.3225, "platforms": 4, "is_junction": True, "branches": "Matheran Hill Railway", "connectivity_score": 50, "fast_train_stop": True, "peak_services_per_hour": 12},
    {"name": "Bhivpuri Road", "code": "BVS", "zone": "Karjat Branch", "km_from_csmt": 93.3, "lat": 18.9715, "lon": 73.3235, "platforms": 2, "is_junction": False, "branches": "", "connectivity_score": 20, "fast_train_stop": False, "peak_services_per_hour": 6},
    {"name": "Karjat", "code": "KJT", "zone": "Karjat Branch", "km_from_csmt": 100.0, "lat": 18.9099, "lon": 73.3283, "platforms": 4, "is_junction": True, "branches": "Khopoli Branch", "connectivity_score": 75, "fast_train_stop": True, "peak_services_per_hour": 15},
    
    # Khopoli Branch
    {"name": "Palasdhari", "code": "PDI", "zone": "Khopoli Branch", "km_from_csmt": 103.1, "lat": 18.8926, "lon": 73.3361, "platforms": 2, "is_junction": False, "branches": "", "connectivity_score": 15, "fast_train_stop": False, "peak_services_per_hour": 4},
    {"name": "Kelavli", "code": "KLY", "zone": "Khopoli Branch", "km_from_csmt": 106.8, "lat": 18.8711, "lon": 73.3421, "platforms": 2, "is_junction": False, "branches": "", "connectivity_score": 10, "fast_train_stop": False, "peak_services_per_hour": 4},
    {"name": "Dolavli", "code": "DLV", "zone": "Khopoli Branch", "km_from_csmt": 108.3, "lat": 18.8576, "lon": 73.3438, "platforms": 2, "is_junction": False, "branches": "", "connectivity_score": 10, "fast_train_stop": False, "peak_services_per_hour": 4},
    {"name": "Lowjee", "code": "LWJ", "zone": "Khopoli Branch", "km_from_csmt": 111.4, "lat": 18.8305, "lon": 73.3444, "platforms": 2, "is_junction": False, "branches": "", "connectivity_score": 10, "fast_train_stop": False, "peak_services_per_hour": 4},
    {"name": "Khopoli", "code": "KHPI", "zone": "Khopoli Branch", "km_from_csmt": 114.2, "lat": 18.7845, "lon": 73.3468, "platforms": 2, "is_junction": False, "branches": "", "connectivity_score": 25, "fast_train_stop": True, "peak_services_per_hour": 4},
]

def get_stations_dataframe():
    return pd.DataFrame(STATIONS_DATA)

def get_all_stations():
    return STATIONS_DATA

def get_station_by_code(code):
    for station in STATIONS_DATA:
        if station['code'].lower() == code.lower() or station['name'].lower() == code.lower():
            return station
    return None

def get_station_names():
    return [{"code": s["code"], "name": s["name"]} for s in STATIONS_DATA]
