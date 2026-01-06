import requests
from datetime import datetime, timedelta

TLE_SOURCES = [
    {
        "name": "TLE API",
        "base": "https://tle.ivanstanojevic.me/api/tle",
        "type": "json_api"
    },
    {
        "name": "CelesTrak",
        "base": "https://celestrak.org/NORAD/elements",
        "type": "txt"
    },
]

CATALOG_MAPPINGS = {
    "stations": {"search": "ISS", "page_size": 10},
    "starlink": {"search": "STARLINK", "page_size": 30},
    "debris": {"search": "DEB", "page_size": 20},
}

CATALOGS = {
    "stations": "stations",
    "starlink": "starlink",
    "debris": "debris",
}

FALLBACK_TLE_DATA = {
    "stations": [
        {
            "name": "ISS (ZARYA)",
            "line1": "1 25544U 98067A   24001.50000000  .00016717  00000-0  10270-3 0  9993",
            "line2": "2 25544  51.6400 208.9163 0006703 296.7361  63.3006 15.49560922431058",
            "catalog": "stations"
        },
        {
            "name": "TIANGONG",
            "line1": "1 48274U 21035A   24001.50000000  .00017234  00000-0  20343-3 0  9992",
            "line2": "2 48274  41.4700 290.5642 0006428 322.0843  37.9697 15.62039567147556",
            "catalog": "stations"
        },
    ],
    "starlink": [
        {
            "name": "STARLINK-1007",
            "line1": "1 44713U 19074A   24001.50000000  .00001234  00000-0  12345-4 0  9991",
            "line2": "2 44713  53.0540 120.6789 0001234  90.1234 270.0000 15.06391234  5678",
            "catalog": "starlink"
        },
        {
            "name": "STARLINK-1008",
            "line1": "1 44714U 19074B   24001.50000000  .00001234  00000-0  12345-4 0  9990",
            "line2": "2 44714  53.0540 125.6789 0001234  95.1234 265.0000 15.06391234  5679",
            "catalog": "starlink"
        },
        {
            "name": "STARLINK-1009",
            "line1": "1 44715U 19074C   24001.50000000  .00001234  00000-0  12345-4 0  9999",
            "line2": "2 44715  53.0540 130.6789 0001234 100.1234 260.0000 15.06391234  5670",
            "catalog": "starlink"
        },
        {
            "name": "STARLINK-1010",
            "line1": "1 44716U 19074D   24001.50000000  .00001234  00000-0  12345-4 0  9998",
            "line2": "2 44716  53.0540 135.6789 0001234 105.1234 255.0000 15.06391234  5671",
            "catalog": "starlink"
        },
        {
            "name": "STARLINK-1011",
            "line1": "1 44717U 19074E   24001.50000000  .00001234  00000-0  12345-4 0  9997",
            "line2": "2 44717  53.0540 140.6789 0001234 110.1234 250.0000 15.06391234  5672",
            "catalog": "starlink"
        },
        {
            "name": "STARLINK-1012",
            "line1": "1 44718U 19074F   24001.50000000  .00001234  00000-0  12345-4 0  9996",
            "line2": "2 44718  53.0540 145.6789 0001234 115.1234 245.0000 15.06391234  5673",
            "catalog": "starlink"
        },
        {
            "name": "STARLINK-1013",
            "line1": "1 44719U 19074G   24001.50000000  .00001234  00000-0  12345-4 0  9995",
            "line2": "2 44719  53.0540 150.6789 0001234 120.1234 240.0000 15.06391234  5674",
            "catalog": "starlink"
        },
        {
            "name": "STARLINK-1014",
            "line1": "1 44720U 19074H   24001.50000000  .00001234  00000-0  12345-4 0  9994",
            "line2": "2 44720  53.0540 155.6789 0001234 125.1234 235.0000 15.06391234  5675",
            "catalog": "starlink"
        },
    ],
    "debris": [
        {
            "name": "COSMOS 2251 DEB",
            "line1": "1 33442U 93036SX  24001.50000000  .00000234  00000-0  23456-4 0  9991",
            "line2": "2 33442  74.0366 200.1234 0012345 234.5678 125.4321 14.12345678  1234",
            "catalog": "debris"
        },
        {
            "name": "COSMOS 2251 DEB [2]",
            "line1": "1 33443U 93036SY  24001.50000000  .00000234  00000-0  23456-4 0  9990",
            "line2": "2 33443  74.0366 205.1234 0012345 239.5678 120.4321 14.12345678  1235",
            "catalog": "debris"
        },
        {
            "name": "IRIDIUM 33 DEB",
            "line1": "1 33444U 97051SX  24001.50000000  .00000234  00000-0  23456-4 0  9999",
            "line2": "2 33444  86.4000 180.1234 0012345 244.5678 115.4321 14.34567890  1236",
            "catalog": "debris"
        },
        {
            "name": "IRIDIUM 33 DEB [2]",
            "line1": "1 33445U 97051SY  24001.50000000  .00000234  00000-0  23456-4 0  9998",
            "line2": "2 33445  86.4000 185.1234 0012345 249.5678 110.4321 14.34567890  1237",
            "catalog": "debris"
        },
        {
            "name": "FENGYUN 1C DEB",
            "line1": "1 29479U 99025DKB 24001.50000000  .00000234  00000-0  23456-4 0  9997",
            "line2": "2 29479  98.7000 250.1234 0012345 254.5678 105.4321 14.56789012  1238",
            "catalog": "debris"
        },
        {
            "name": "FENGYUN 1C DEB [2]",
            "line1": "1 29480U 99025DKC 24001.50000000  .00000234  00000-0  23456-4 0  9996",
            "line2": "2 29480  98.7000 255.1234 0012345 259.5678 100.4321 14.56789012  1239",
            "catalog": "debris"
        },
    ]
}

_using_fallback = False
_last_error = None
_data_source = None

def fetch_from_tle_api(catalog_name, limit):
    """Fetch from TLE API (public CelesTrak mirror)."""
    mapping = CATALOG_MAPPINGS.get(catalog_name, {"search": catalog_name, "page_size": limit})
    search_term = mapping["search"]
    
    url = f"https://tle.ivanstanojevic.me/api/tle?search={search_term}&page_size={limit}"
    
    response = requests.get(url, timeout=15)
    response.raise_for_status()
    
    data = response.json()
    satellites = []
    
    for item in data.get("member", []):
        satellites.append({
            "name": item.get("name", "UNKNOWN"),
            "line1": item.get("line1", ""),
            "line2": item.get("line2", ""),
            "catalog": catalog_name
        })
    
    return satellites

def fetch_tle_data(catalog_name="stations", limit=50):
    """
    Fetch TLE data from available sources.
    Tries TLE API first, then falls back to cached data.
    """
    global _using_fallback, _last_error, _data_source
    
    try:
        satellites = fetch_from_tle_api(catalog_name, limit)
        if satellites:
            _using_fallback = False
            _last_error = None
            _data_source = "TLE API (live data)"
            print(f"Successfully fetched {len(satellites)} objects from TLE API for {catalog_name}")
            return satellites
    except Exception as e:
        _last_error = str(e)
        print(f"TLE API unavailable ({catalog_name}): {e}")
    
    _using_fallback = True
    _data_source = "Cached demo data"
    return get_fallback_data(catalog_name, limit)

def get_fallback_data(catalog_name, limit=50):
    """Get fallback TLE data when external sources are unavailable."""
    catalog_map = {
        "stations": "stations",
        "starlink": "starlink",
        "cosmos-2251-debris": "debris",
        "iridium-33-debris": "debris",
        "fengyun-1c-debris": "debris",
        "debris": "debris",
    }
    
    fallback_key = catalog_map.get(catalog_name, "stations")
    fallback_sats = FALLBACK_TLE_DATA.get(fallback_key, [])
    
    result = []
    for sat in fallback_sats[:limit]:
        sat_copy = sat.copy()
        sat_copy['catalog'] = catalog_name
        result.append(sat_copy)
    
    return result

def is_using_fallback():
    """Check if fallback data is currently being used."""
    return _using_fallback

def get_last_error():
    """Get the last error message if any."""
    return _last_error

def get_data_source():
    """Get the current data source name."""
    return _data_source or "Unknown"

def fetch_multiple_catalogs(catalogs=None, limit_per_catalog=20):
    """Fetch from multiple catalogs and combine."""
    if catalogs is None:
        catalogs = ["stations", "starlink", "debris"]
    
    all_satellites = []
    for cat in catalogs:
        sats = fetch_tle_data(cat, limit=limit_per_catalog)
        all_satellites.extend(sats)
    
    return all_satellites
