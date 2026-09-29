def get_disruptions():
    return [
        {
            "id": "D001",
            "date": "2026-09-29 08:15",
            "notice": "Signal failure at Dadar causing 15 min delays on slow line.",
            "affected": "Dadar, Parel, Matunga",
            "impact": "Major",
            "status": "Active",
            "type": "Signal Issue",
            "severity": 4
        },
        {
            "id": "D002",
            "date": "2026-09-29 09:30",
            "notice": "Track maintenance at Kalyan.",
            "affected": "Kalyan, Thakurli, Shahad",
            "impact": "Minor",
            "status": "Monitoring",
            "type": "Maintenance",
            "severity": 2
        },
        {
            "id": "D003",
            "date": "2026-09-29 07:45",
            "notice": "Point failure at CSMT resolved.",
            "affected": "CSMT, Masjid",
            "impact": "Critical",
            "status": "Resolved",
            "type": "Technical",
            "severity": 5
        },
        {
            "id": "D004",
            "date": "2026-09-29 12:00",
            "notice": "Speed restrictions due to heavy rain alert.",
            "affected": "Kasara, Khardi, Atgaon",
            "impact": "Major",
            "status": "Active",
            "type": "Weather",
            "severity": 3
        },
        {
            "id": "D005",
            "date": "2026-09-29 14:20",
            "notice": "Trespassing incident, train cleared, residual delays.",
            "affected": "Kurla, Vidyavihar",
            "impact": "Minor",
            "status": "Resolved",
            "type": "Security",
            "severity": 2
        }
    ]

def get_active_disruptions():
    all_disruptions = get_disruptions()
    return [d for d in all_disruptions if d["status"] in ["Active", "Monitoring"]]
