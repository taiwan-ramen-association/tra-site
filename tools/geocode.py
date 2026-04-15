import json
import os
import re
import subprocess
import sys
import time

def install(pkg):
    subprocess.check_call([sys.executable, '-m', 'pip', 'install', pkg, '-q'])

try:
    import requests
except ImportError:
    print('安裝 requests 中...')
    install('requests')
    import requests

import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

tools_dir  = os.path.dirname(os.path.abspath(__file__))
root_dir   = os.path.dirname(tools_dir)
json_path  = os.path.join(root_dir, 'data', 'data.json')

# ── 模式選擇 ───────────────────────────────────────────────────────────────────
print('模式選擇：')
print('  1. 只補缺少座標的店家')
print('  2. 重新更正所有店家（使用更精準的 !3d!4d 方法）')
mode = input('請輸入 1 或 2（直接 Enter 預設為 1）：').strip() or '1'

print('📂 讀取 data.json...')
with open(json_path, 'r', encoding='utf-8') as f:
    rows = json.load(f)

if mode == '2':
    # 重跑所有有 Map URL 的店家；沒有 Map URL 且已有座標的跳過
    to_geocode = [r for r in rows if r.get('Map', '').startswith('http') or not r.get('lat')]
    print(f'重新 geocode：{len(to_geocode)} 筆（共 {len(rows)} 筆）')
else:
    to_geocode = [r for r in rows if not r.get('lat') or not r.get('lng')]
    print(f'需要 geocode：{len(to_geocode)} 筆（共 {len(rows)} 筆）')

if not to_geocode:
    print('✅ 所有店家都已有座標，無需更新')
    input('按 Enter 關閉...')
    sys.exit(0)

# ── 設定 ───────────────────────────────────────────────────────────────────────
HEADERS     = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
updated     = 0
failed      = []
consecutive = 0
MAX_CONSEC  = 5

# ── 函式 ───────────────────────────────────────────────────────────────────────
def coords_from_map_url(url):
    """追蹤 Google Maps 縮短網址，從 !3d{lat}!4d{lng} 取得精確圖釘座標"""
    if not url or not url.startswith('http'):
        return None, None
    r = requests.get(url, headers=HEADERS, timeout=10, verify=False, allow_redirects=True)
    final = r.url
    # 最精準：data 參數裡的 !3d{lat}!4d{lng}（實際圖釘位置）
    m = re.search(r'!3d(-?\d+\.\d+)!4d(-?\d+\.\d+)', final)
    if m:
        return float(m.group(1)), float(m.group(2))
    # 備用：/@lat,lng（viewport 中心，略有偏移）
    m = re.search(r'/@(-?\d+\.\d+),(-?\d+\.\d+)', final)
    if m:
        return float(m.group(1)), float(m.group(2))
    return None, None

def geocode_nominatim(address):
    """備用：Nominatim（無 Map URL 時使用）"""
    r = requests.get(
        'https://nominatim.openstreetmap.org/search',
        params={'q': address, 'format': 'json', 'limit': 1},
        headers=HEADERS, timeout=10, verify=False
    )
    results = r.json()
    return (float(results[0]['lat']), float(results[0]['lon'])) if results else (None, None)

# ── 主迴圈 ─────────────────────────────────────────────────────────────────────
for i, row in enumerate(to_geocode):
    name    = row.get('店名', '')
    address = row.get('地址', '') or name
    map_url = row.get('Map', '')
    print(f'[{i+1}/{len(to_geocode)}] {name}')
    try:
        # 第一優先：Google Maps URL → !3d!4d 精確座標
        lat, lng = coords_from_map_url(map_url)
        if lat:
            print(f'  ✓ (Map) {lat:.6f}, {lng:.6f}')

        # 備用：Nominatim
        if not lat:
            lat, lng = geocode_nominatim(address)
            if lat:
                print(f'  ✓ (Nominatim) {lat:.6f}, {lng:.6f}')

        if lat:
            row['lat'] = lat
            row['lng'] = lng
            updated += 1
            consecutive = 0
        else:
            failed.append(name)
            consecutive += 1
            print(f'  ✗ 找不到座標（連續失敗 {consecutive}/{MAX_CONSEC}）')

    except Exception as e:
        failed.append(name)
        consecutive += 1
        print(f'  ✗ 錯誤：{e}（連續失敗 {consecutive}/{MAX_CONSEC}）')

    if consecutive >= MAX_CONSEC:
        print(f'\n⚠ 連續失敗 {MAX_CONSEC} 筆，中斷作業')
        break
    time.sleep(1.1)

with open(json_path, 'w', encoding='utf-8') as f:
    json.dump(rows, f, ensure_ascii=False, indent=2)

print(f'\n✅ 完成！更新 {updated} 筆座標')
if failed:
    print(f'⚠ 找不到座標（{len(failed)} 筆）：{", ".join(failed)}')
print()
input('按 Enter 關閉...')
