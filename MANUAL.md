# 台灣拉麵協會網站 — 操作手冊

> 本檔案僅供本機使用，不納入版控。

---

## 目錄結構

```
/
├── index.html              首頁
├── about.html              關於協會
├── news.html               最新消息
├── charter.html            協會章程
├── meetings.html           會議紀錄
├── membership.html         加入會員
├── partners.html           合作夥伴
├── finder.html             拉麵搜尋器（正式版）
├── finder-beta.html        拉麵搜尋器（測試版，功能驗證後同步至 finder.html）
├── domination.html         制霸地圖（各鄉鎮踩點比例視覺化）
├── admin.html              後台管理（需管理員權限）
├── cards.html              店家名片
├── members-zone.html       會務專區
├── other.html              其他
│
├── assets/
│   ├── css/
│   │   └── style.css       共用樣式
│   ├── icons/              Logo、圖示（原 icon/）
│   └── images/             IG 貼文圖片（原 image/）
│
├── data/
│   ├── data.json           店家主資料（由 Google Sheets 自動同步）
│   ├── districts.json      內政部行政區劃資料（自動維護）
│   ├── id_counters.json    各縣市 ID 歷史最大值（防止 ID 重用）
│   ├── news.json           最新消息
│   ├── about.json          關於協會內容
│   ├── charter.json        協會章程內容
│   ├── meetings.json       會議紀錄清單
│   ├── membership.json     會員方案內容
│   ├── partners.json       合作夥伴清單
│   └── instagram.json      IG 貼文清單
│
├── tools/                  本機 Python 工具（不上版控的除外）
│   ├── setup_data.py           資料編輯主工具（A開始編輯 / B完成編輯）
│   ├── compare_hours.py        比對 Google Places 營業時間（含 API Key，不上版控）
│   ├── item_detail.csv         Excel 下拉選單驗證清單
│   └── data.xlsx               Excel 工作檔（不納入版控，每次重新產生）
│
├── .github/workflows/
│   └── sync-sheets.yml     自動同步排程（Google Sheets ↔ data/data.json）
│
├── ads.txt                 Google AdSense 驗證（必須在根目錄）
├── sitemap.xml             SEO 網站地圖（必須在根目錄）
└── google5be78957398a1c67.html  Google Search Console 驗證（必須在根目錄）
```

---

## 常見操作

### 新增最新消息

編輯 `data/news.json`，在陣列開頭新增：

```json
{
  "date": "2026-04-01",
  "title": "標題",
  "body": "內容文字",
  "tag": "公告"
}
```

```bash
git add data/news.json
git commit -m "新增消息：標題"
git push
```

---

### 新增會議紀錄

編輯 `data/meetings.json`，新增一筆：

```json
{
  "date": "2026-04-01",
  "title": "第X次理事會議",
  "summary": "會議摘要",
  "file": ""
}
```

---

### 新增合作夥伴

1. 將 Logo 圖片放入 `assets/icons/` 資料夾
2. 編輯 `data/partners.json`，新增一筆：

```json
{
  "name": "店家名稱",
  "category": "member",
  "logo": "assets/icons/檔名.png",
  "url": null,
  "featured": true
}
```

`category` 可填：`member`（協會會員）、`ramen`（合作拉麵店）、`partner`（合作商家）

---

### 新增 IG 貼文

1. 將圖片放入 `assets/images/` 資料夾
2. 編輯 `data/instagram.json`，在陣列開頭新增：

```json
{
  "image": "assets/images/檔名.jpeg",
  "url": "https://www.instagram.com/p/XXXXXX/"
}
```

---

### 新增／修改店家資料

**方式一：透過 Google Sheets（推薦）**
直接在 Google Sheets「總表csv」工作表編輯，系統每 12 小時自動同步至網站。

**方式二：本機 Excel**

```bash
python tools/setup_data.py
```

啟動後選擇：

- **A【開始編輯】** — 將 data.json 轉成 Excel 並自動開啟，在 Excel 中新增／修改後存檔
- **B【完成編輯】** — 讀取 Excel → 自動補 ID / 縣市 / 正規化格式 → 寫回 JSON 與 Excel
- **0【進階單步】** — 單獨執行任一步驟（更新行政區、補座標等）

編輯完成後：

```bash
git add data/data.json data/id_counters.json
git commit -m "更新店家資料"
git push
```

---

### 比對 Google Places 營業時間

```bash
python tools/compare_hours.py
```

逐一比對「營業中」店家的本地時段與 Google Maps 資料：

| 狀態 | 說明 |
|------|------|
| 吻合 | 無需處理 |
| 本地缺資料 | 自動從 Google 補填週一～週日 |
| 有差異 | 自動以 Google 為準更新 |
| Google 無資料 | 疑似歇業或暫停，**需人工確認** |
| 找不到店家 | Place ID 搜尋失敗，需人工確認 |

執行完畢輸出（均存在 `tools/` 下）：
- `tools/diff_report.csv`：所有店家比對結果總表
- `tools/compare_hours_log.txt`：詳細差異紀錄

> 需要 Google Places API Key（明碼寫在腳本中，僅供本機使用，請勿 push）

---

## 自動化排程（GitHub Actions）

| 排程 | 工作 |
|------|------|
| 每 12 小時 | Google Sheets → data/data.json 同步、補齊座標 |
| 每月 1 日 02:00 | 更新行政區劃清單 |
| 推送 data/data.json 時 | data.json → 回寫 Google Sheets |

手動觸發：GitHub → Actions → Sync Google Sheets → Run workflow

---

## 環境架設（換電腦）

### 需求
- Git
- Python 3.9 以上
- 網路連線

### 步驟

```bash
# 1. Clone 專案
git clone https://github.com/taiwan-ramen-association/taiwan-ramen-association.github.io.git
cd taiwan-ramen-association.github.io

# 2. 安裝 Python 套件
pip install openpyxl requests gspread google-auth
```

### 注意事項
- `tools/data.xlsx` 不納入版控，每次需在本機重新產生（執行 setup_data.py 選 A）
- `tools/compare_hours.py` 含 API Key，不納入版控，換電腦時需自行保管
- GitHub Actions 的自動同步不需要本機設定，在 GitHub 雲端執行
- Google Service Account 金鑰只需設定在 GitHub Secrets，本機工具不需要

---

## 網站部署

靜態網站，直接 push 至 `main` branch 即自動部署至 GitHub Pages，無需額外設定。
