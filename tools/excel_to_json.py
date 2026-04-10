"""
excel_to_json.py — 純轉換：Excel → JSON
正規化請執行 setup_data.py
"""
import json
import os
import subprocess
import sys

def install(pkg):
    subprocess.check_call([sys.executable, '-m', 'pip', 'install', pkg, '-q'])

try:
    import openpyxl
except ImportError:
    print('安裝 openpyxl 中...')
    install('openpyxl')
    import openpyxl

tools_dir = os.path.dirname(os.path.abspath(__file__))
root_dir  = os.path.dirname(tools_dir)
xlsx_path = os.path.join(tools_dir, 'data.xlsx')
json_path = os.path.join(root_dir, 'data.json')

if not os.path.exists(xlsx_path):
    print('❌ 找不到 data.xlsx，請先執行 json_to_excel.py')
    input('按 Enter 關閉...')
    sys.exit(1)

print('📂 讀取 data.xlsx...')
wb = openpyxl.load_workbook(xlsx_path)
ws = wb.active
rows_raw = list(ws.values)

if not rows_raw:
    print('❌ Excel 是空的')
    input('按 Enter 關閉...')
    sys.exit(1)

headers = [str(h).strip() for h in rows_raw[0]]
rows = []

for row in rows_raw[1:]:
    if all((v is None or str(v).strip() == '') for v in row):
        continue
    obj = {}
    for i, h in enumerate(headers):
        val = row[i] if i < len(row) else ''
        if val is None:
            val = ''
        else:
            val = str(val).strip()
            # 移除 Excel 自動加的 .0（例如 7.0 → 7）
            if val.endswith('.0') and val[:-2].lstrip('-').isdigit():
                val = val[:-2]
        obj[h] = val
    if obj.get('店名', '').strip():
        rows.append(obj)

with open(json_path, 'w', encoding='utf-8') as f:
    json.dump(rows, f, ensure_ascii=False, indent=2)

print(f'✅ 完成！data.json 已更新（共 {len(rows)} 筆）')
print(f'📍 {json_path}')
print()
print('💡 如需正規化資料，請執行 setup_data.py')
print()
input('按 Enter 關閉...')
