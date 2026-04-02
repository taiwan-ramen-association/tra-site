"""
從內政部國土測繪中心 API 取得台灣所有鄉鎮市區清單
API: https://api.nlsc.gov.tw/other/ListTown1/{縣市代碼}
輸出: districts.json  格式 {"臺北市": ["中正區", ...], ...}
"""
import json
import os
import subprocess
import sys
import warnings
import xml.etree.ElementTree as ET

warnings.filterwarnings('ignore')

def install(pkg):
    subprocess.check_call([sys.executable, '-m', 'pip', 'install', pkg, '-q'])

try:
    import requests
except ImportError:
    install('requests')
    import requests

# 縣市代碼（內政部戶政系統，A-Z 共 22 個有效代碼）
COUNTY_CODES = list('ABCDEFGHIJKLMNOPQRSTUVWXYZ')

API_BASE = 'https://api.nlsc.gov.tw/other/ListTown1'

print('從內政部 API 取得鄉鎮市區清單...')

districts = {}   # { 縣市名: [鄉鎮市區名, ...] }
failed = []

for code in COUNTY_CODES:
    try:
        r = requests.get(f'{API_BASE}/{code}', timeout=10, verify=False)
        if r.status_code != 200 or '<townItem>' not in r.text:
            continue
        root = ET.fromstring(r.content)
        items = root.findall('townItem')
        if not items:
            continue

        town_names = [item.findtext('townname') for item in items]
        districts[code] = town_names
        print(f'  {code}: {len(town_names)} 個鄉鎮市區')

    except Exception as e:
        failed.append(code)
        print(f'  {code}: 失敗 ({e})')

# 取得縣市名稱（從另一支 API ListCounty1）
print('取得縣市名稱...')
county_names = {}
try:
    r = requests.get('https://api.nlsc.gov.tw/other/ListCounty', timeout=10, verify=False)
    if r.status_code == 200:
        root = ET.fromstring(r.content)
        for item in root.findall('countyItem'):
            code = item.findtext('countycode')
            name = item.findtext('countyname')
            if code and name:
                county_names[code] = name
        print(f'  取得 {len(county_names)} 個縣市')
except Exception as e:
    print(f'  縣市名稱 API 失敗: {e}')

# 組合結果 { 縣市名: [鄉鎮市區名, ...] }
result = {}
for code, towns in districts.items():
    county = county_names.get(code, code)  # 若 API 失敗就用代碼
    result[county] = towns

# 寫出 districts.json
script_dir = os.path.dirname(os.path.abspath(__file__))
out_path = os.path.join(script_dir, 'districts.json')
with open(out_path, 'w', encoding='utf-8') as f:
    json.dump(result, f, ensure_ascii=False, indent=2)

total = sum(len(v) for v in result.values())
print(f'\n完成！{len(result)} 個縣市，{total} 個鄉鎮市區')
print(f'儲存至 {out_path}')
if failed:
    print(f'失敗代碼：{failed}')
input('按 Enter 關閉...')
