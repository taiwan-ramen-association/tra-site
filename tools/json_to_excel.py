import csv
import json
import os
import subprocess
import sys

# 安裝需要的套件
def install(pkg):
    subprocess.check_call([sys.executable, '-m', 'pip', 'install', pkg, '-q'])

try:
    import openpyxl
except ImportError:
    print('安裝 openpyxl 中...')
    install('openpyxl')
    import openpyxl

# ── 地址解析 ──────────────────────────────────────────────────────────────────
def _load_districts():
    path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'districts.json')  # tools/districts.json
    try:
        with open(path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        return {}

_DISTRICTS = _load_districts()

def parse_city_district(addr):
    """從地址拆出縣市與鄉鎮市區（比對內政部官方清單）"""
    if not addr or not _DISTRICTS:
        return '', ''
    addr_n = addr.replace('台', '臺')
    for county, towns in _DISTRICTS.items():
        if addr_n.startswith(county):
            rest = addr_n[len(county):]
            for town in towns:
                if rest.startswith(town):
                    return county, town
    return '', ''

# ── 路徑設定 ──────────────────────────────────────────────────────────────────
tools_dir  = os.path.dirname(os.path.abspath(__file__))
root_dir   = os.path.dirname(tools_dir)
json_path  = os.path.join(root_dir, 'data.json')
xlsx_path  = os.path.join(tools_dir, 'data.xlsx')

# ── 讀取 JSON ─────────────────────────────────────────────────────────────────
print('📂 讀取 data.json...')
with open(json_path, 'r', encoding='utf-8') as f:
    rows = json.load(f)

if not rows:
    print('❌ data.json 是空的')
    input('按 Enter 關閉...')
    sys.exit(1)

# 若縣市或鄉鎮市區為空，自動從地址解析
for row in rows:
    if not row.get('縣市', '').strip() or not row.get('鄉鎮市區', '').strip():
        city, district = parse_city_district(row.get('地址', ''))
        if not row.get('縣市', '').strip():
            row['縣市'] = city
        if not row.get('鄉鎮市區', '').strip():
            row['鄉鎮市區'] = district

# ── 星期排序正規化 ─────────────────────────────────────────────────────────────
DAY_ORDER = {'一': 1, '二': 2, '三': 3, '四': 4, '五': 5, '六': 6, '日': 7}
DAY_FIELDS = {'營業日', '店休日'}

def normalize_days(value):
    """將逗號分隔的星期字串排序為一二三四五六日順序"""
    if not value or not isinstance(value, str):
        return value
    parts = [p.strip() for p in value.split(',')]
    # 若任一部分不在 DAY_ORDER，視為非星期格式，原樣返回
    if not all(p in DAY_ORDER for p in parts if p):
        return value
    parts_sorted = sorted(parts, key=lambda d: DAY_ORDER.get(d, 99))
    return ', '.join(parts_sorted)

# ── 寫入 Excel ────────────────────────────────────────────────────────────────
wb = openpyxl.Workbook()
ws = wb.active
ws.title = '店家資料'

headers = list(rows[0].keys())

# 標題列樣式
from openpyxl.styles import PatternFill, Font, Alignment
header_fill = PatternFill(start_color='C8272D', end_color='C8272D', fill_type='solid')
header_font = Font(color='FFFFFF', bold=True, size=11)

for col_idx, h in enumerate(headers, 1):
    cell = ws.cell(row=1, column=col_idx, value=h)
    cell.fill   = header_fill
    cell.font   = header_font
    cell.alignment = Alignment(horizontal='center', vertical='center')

# 資料列
for row_idx, row in enumerate(rows, 2):
    for col_idx, h in enumerate(headers, 1):
        val = row.get(h, '')
        if h in DAY_FIELDS:
            val = normalize_days(val)
        ws.cell(row=row_idx, column=col_idx, value=val)

# 凍結第一列
ws.freeze_panes = 'A2'

# 自動調整欄寬（最大 40）
for col in ws.columns:
    max_len = max((len(str(cell.value or '')) for cell in col), default=0)
    ws.column_dimensions[col[0].column_letter].width = min(max_len + 2, 40)

# ── 資料驗證（下拉選單）────────────────────────────────────────────────────────
csv_path = os.path.join(tools_dir, 'item_detail.csv')
if os.path.exists(csv_path):
    from openpyxl.worksheet.datavalidation import DataValidation

    # 讀取 item_detail.csv
    with open(csv_path, 'r', encoding='utf-8-sig') as f:
        reader = csv.reader(f)
        vld_headers = next(reader)
        vld_cols = {h: [] for h in vld_headers}
        for row in reader:
            for i, h in enumerate(vld_headers):
                val = row[i].strip() if i < len(row) else ''
                if val:
                    vld_cols[h].append(val)

    # 建隱藏工作表存放選項清單
    ws_vld = wb.create_sheet('驗證清單')
    ws_vld.sheet_state = 'hidden'
    for col_idx, h in enumerate(vld_headers, 1):
        ws_vld.cell(row=1, column=col_idx, value=h)
        for row_idx, val in enumerate(vld_cols[h], 2):
            ws_vld.cell(row=row_idx, column=col_idx, value=val)

    # 對主工作表套用下拉驗證
    last_row = len(rows) + 1
    col_letter = {h: None for h in vld_headers}
    for col_idx, h in enumerate(headers, 1):
        if h in vld_cols:
            from openpyxl.utils import get_column_letter
            col_letter[h] = get_column_letter(col_idx)

    for vld_col_idx, h in enumerate(vld_headers, 1):
        letter = col_letter.get(h)
        if not letter or not vld_cols[h]:
            continue
        from openpyxl.utils import get_column_letter
        vld_col_letter = get_column_letter(vld_col_idx)
        vld_range = f'驗證清單!${vld_col_letter}$2:${vld_col_letter}${len(vld_cols[h]) + 1}'
        dv = DataValidation(type='list', formula1=vld_range, showDropDown=False, allow_blank=True)
        dv.sqref = f'{letter}2:{letter}{last_row}'
        ws.add_data_validation(dv)

    print('✅ 已套用下拉選單驗證')

wb.save(xlsx_path)
print(f'✅ 完成！已產生 data.xlsx（共 {len(rows)} 筆）')
print(f'📍 檔案位置：{xlsx_path}')
print()
print('👉 請用 Excel 開啟 data.xlsx 進行編輯')
print('👉 編輯完存檔後，執行 excel_to_json.py 轉回 JSON')
print()
input('按 Enter 關閉...')
