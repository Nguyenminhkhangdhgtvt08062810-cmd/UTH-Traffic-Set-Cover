
# Duong dan lam viec: thu muc goc bai nop.
import os as _project_os
from pathlib import Path as _project_Path
_project_os.chdir(_project_Path(__file__).resolve().parent.parent)
import csv
import json
import math
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / 'data'
OUTPUT = DATA / 'nodes'
UTH_LAT, UTH_LON = 10.804816, 106.716878
AREA_RADIUS_M = 500.0
COVER_RADIUS_M = 120.0
ROAD_TYPES = {'primary', 'secondary', 'tertiary', 'residential'}
FALLBACK_COST = 5.0  # chi phi mo phong, khong phai gia lap dat thuc te


def locate(filename):
    """Tim file tai data/osm truoc, sau do data."""
    paths = [DATA / 'osm' / filename, DATA / filename]
    return next((p for p in paths if p.is_file()), None)


def distance_m(lat1, lon1, lat2, lon2):
    lat1, lat2 = math.radians(lat1), math.radians(lat2)
    dlat = lat2 - lat1
    dlon = math.radians(lon2 - lon1)
    a = math.sin(dlat / 2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon / 2)**2
    return 2 * 6371000 * math.asin(min(1.0, math.sqrt(a)))


def normalized(s):
    return ''.join(ch for ch in str(s).lower() if ch.isalnum())


def find_column(fieldnames, aliases):
    names = {normalized(x): x for x in fieldnames}
    return next((names[normalized(a)] for a in aliases if normalized(a) in names), None)


def get_layer(properties):
    if properties.get('layer') is not None:
        return str(properties['layer'])
    if properties.get('bridge') in ('yes', 'true', '1'):
        return '1'
    if properties.get('tunnel') in ('yes', 'true', '1'):
        return '-1'
    return '0'


def extract_junctions(path):
    with path.open('r', encoding='utf-8-sig') as f:
        geojson = json.load(f)
    if geojson.get('type') != 'FeatureCollection':
        raise ValueError('roads.geojson khong phai GeoJSON FeatureCollection')

    adjacent = defaultdict(set)
    ways_at_node = defaultdict(set)
    eligible = 0
    for feature in geojson.get('features', []):
        prop = feature.get('properties') or {}
        if prop.get('highway') not in ROAD_TYPES:
            continue
        geom = feature.get('geometry') or {}
        typ = geom.get('type')
        coords = geom.get('coordinates') or []
        lines = [coords] if typ == 'LineString' else coords if typ == 'MultiLineString' else []
        if not lines:
            continue
        eligible += 1
        layer = get_layer(prop)
        way_id = str(feature.get('id') or prop.get('@id') or f'way_{eligible}')
        for line in lines:
            for point_a, point_b in zip(line, line[1:]):
                try:
                    a = (round(float(point_a[0]), 7), round(float(point_a[1]), 7))
                    b = (round(float(point_b[0]), 7), round(float(point_b[1]), 7))
                except (TypeError, ValueError, IndexError):
                    continue
                if a == b:
                    continue
                u, v = (a, layer), (b, layer)
                adjacent[u].add(v)
                adjacent[v].add(u)
                ways_at_node[u].add(way_id)
                ways_at_node[v].add(way_id)

    junctions = []
    for (coord, layer), neighbors in adjacent.items():
        if len(neighbors) < 3:
            continue
        lon, lat = coord  # GeoJSON su dung [longitude, latitude]
        if distance_m(lat, lon, UTH_LAT, UTH_LON) <= AREA_RADIUS_M:
            junctions.append({
                'latitude': lat, 'longitude': lon, 'layer': layer,
                'degree': len(neighbors), 'ways_at_vertex': len(ways_at_node[(coord, layer)])
            })
    junctions.sort(key=lambda x: (x['latitude'], x['longitude'], x['layer']))
    return junctions, len(geojson.get('features', [])), eligible


def load_cameras(path):
    if path is None:
        return [], 'Khong tim thay camera_locations.csv trong data/osm hoac data.'
    with path.open('r', encoding='utf-8-sig', newline='') as f:
        reader = csv.DictReader(f)
        fields = reader.fieldnames or []
        lat_field = find_column(fields, ['latitude', 'lat', 'camera_lat', 'vi_do', 'y'])
        lon_field = find_column(fields, ['longitude', 'lon', 'lng', 'long', 'camera_lon', 'kinh_do', 'x'])
        cost_field = find_column(fields, ['cost', 'price', 'weight', 'chi_phi'])
        if not lat_field or not lon_field:
            raise ValueError(f'Khong nhan dien duoc cot toa do camera. Ten cot: {fields}')
        cameras = []
        invalid_rows = 0
        missing_costs = 0
        for row in reader:
            try:
                lat, lon = float(row[lat_field]), float(row[lon_field])
                cost_raw = str(row.get(cost_field) or '').strip() if cost_field else ''
                if not cost_raw:
                    missing_costs += 1
                cost = float(cost_raw) if cost_raw else FALLBACK_COST
                if not (-90 <= lat <= 90 and -180 <= lon <= 180 and math.isfinite(cost) and cost > 0):
                    raise ValueError('Invalid coordinate or cost')
                cameras.append({'latitude': lat, 'longitude': lon, 'cost': cost,
                                'source': 'existing_camera_csv' if cost_raw else 'cost_fallback'})
            except (TypeError, ValueError):
                invalid_rows += 1
    return cameras, f'Doc {len(cameras)} camera, bo {invalid_rows} dong loi, {missing_costs} camera dung chi phi mac dinh.'


def write_csv(path, fields, rows):
    with path.open('w', newline='', encoding='utf-8-sig') as f:
        writer = csv.writer(f)
        writer.writerow(fields)
        writer.writerows(rows)


def main():
    roads_file = locate('roads.geojson')
    camera_file = locate('camera_locations.csv')
    if roads_file is None:
        print('LOI: Khong tim thay roads.geojson. Da tim data/osm/ va data/.')
        print('Kiem tra ten file trong VS Code va chay script tai thu muc goc du an.')
        return
    print(f'Du lieu duong: {roads_file.relative_to(ROOT)}')
    print(f'Du lieu camera: {camera_file.relative_to(ROOT) if camera_file else "CHUA CO"}')
    junctions, total_features, eligible_features = extract_junctions(roads_file)
    if not junctions:
        print('LOI: Chua tim thay nut phan nhanh trong ban kinh nghien cuu. Khong xuat ma tran rong.')
        return
    OUTPUT.mkdir(parents=True, exist_ok=True)
    write_csv(OUTPUT / 'intersections_nodes.csv',
              ['intersection_id', 'latitude', 'longitude', 'layer', 'degree', 'ways_at_vertex'],
              [[i, j['latitude'], j['longitude'], j['layer'], j['degree'], j['ways_at_vertex']]
               for i, j in enumerate(junctions, 1)])
    cameras, camera_note = load_cameras(camera_file)
    print(camera_note)
    print(f'OSM features: {total_features}, road features phu hop: {eligible_features}')
    print(f'Nut giao ung vien: {len(junctions)}')
    print('Da tao: data/nodes/intersections_nodes.csv')
    if not cameras:
        print('CHUA TAO ma tran phu: can camera_locations.csv.')
        return

    write_csv(OUTPUT / 'camera_locations_nodes.csv',
              ['camera_id', 'latitude', 'longitude', 'cost', 'source'],
              [[i, c['latitude'], c['longitude'], c['cost'], c['source']] for i, c in enumerate(cameras, 1)])
    matrix = []
    uncovered = []
    for i, junction in enumerate(junctions, 1):
        row = [int(distance_m(junction['latitude'], junction['longitude'],
                              cam['latitude'], cam['longitude']) <= COVER_RADIUS_M)
               for cam in cameras]
        matrix.append(row)
        if not any(row):
            uncovered.append(i)
    write_csv(OUTPUT / 'coverage_matrix_nodes.csv',
              ['intersection_id'] + [f'C{i}' for i in range(1, len(cameras) + 1)],
              [[i] + row for i, row in enumerate(matrix, 1)])
    report = {
        'roads_source': str(roads_file.relative_to(ROOT)).replace('\\', '/'),
        'cameras_source': str(camera_file.relative_to(ROOT)).replace('\\', '/') if camera_file else None,
        'total_osm_features': total_features, 'eligible_road_features': eligible_features,
        'junction_rule': 'Shared OSM geometry vertex with graph degree >=3, within same layer',
        'road_types': sorted(ROAD_TYPES), 'center_lat': UTH_LAT, 'center_lon': UTH_LON,
        'area_radius_m': AREA_RADIUS_M, 'cover_radius_m': COVER_RADIUS_M,
        'intersection_count': len(junctions), 'camera_count': len(cameras),
        'matrix_shape': [len(junctions), len(cameras)],
        'uncovered_intersection_ids': uncovered,
        'is_feasible_full_cover': not bool(uncovered),
        'warning': 'OSM topological junction candidates need manual review. Distance coverage and costs are simulated; not real camera visibility or installation quotations.'
    }
    (OUTPUT / 'model_nodes_summary.json').write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding='utf-8')
    print(f'So camera: {len(cameras)}')
    print(f'Ma tran phu: {len(junctions)} x {len(cameras)}')
    print(f'Nut khong co camera nao phu: {len(uncovered)}')
    if uncovered:
        print('CHUA THE toi uu phu 100%. Can xem lai camera ung vien va ban kinh truoc.')
    else:
        print('Du lieu co nghiem kha thi: hop camera ung vien phu du tat ca nut.')
    print('Da tao trong data/nodes/: camera_locations_nodes.csv, coverage_matrix_nodes.csv, model_nodes_summary.json')
    print('Khong ghi de du lieu goc trong data/osm/.')


if __name__ == '__main__':
    main()

