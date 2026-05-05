# 台灣拉麵協會 — 開發上下文

## 專案概覽
台灣拉麵協會網站。前台 `finder-beta.html`，後台 `admin.html`。
部署：GitHub Pages（public repo）。

## 技術棧
- Firebase（Firestore、Auth、Storage、FCM、Cloud Functions）
- Leaflet.js 地圖
- Vanilla JS（無前端框架）

## 關鍵路徑
- 前台：`D:/ramen-finder-tmp/finder-beta.html`
- 後台：`D:/ramen-finder-tmp/admin.html`
- Firebase rules 快照（private git）：`D:/ramen-finder-tmp/_memory/rules/`
  - Firestore：`_memory/rules/firestore.txt`
  - Storage：`_memory/rules/storage.txt`
  - Storage rules 本地參考：`_memory/rules/storage.rules`
- 開發筆記（private repo）：`D:/ramen-finder-tmp/_memory/`

## 功能狀態（2026-05）
| 功能 | 狀態 |
|------|------|
| 收藏、踩點、評論（含照片、留言、Feed） | ✅ 完整 |
| 照片 tab（Google Places API） | ✅ 完整 |
| 菜單 tab | ✅ 完整 |
| 排行榜 | ⏸ 暫緩，勿動 |
| 挑戰任務 | ⏸ 暫緩，勿動 |
| 排隊回報 | ⏸ 暫緩，勿動 |

## 協作規則
- **任何程式碼修改前，先說明計畫，等確認後才動工**
- 不自行開 PR 或 git push
- 不要跑 PR

## Firebase 規則管理
- 規則由 Firebase Console 手動維護，不透過 CLI deploy
- 本機快照放 `_local/`（已加入 .gitignore）
- 有規則變更建議時，說明後讓使用者手動抄到 Firebase Console

## 角色體系
`all → viewer → member → director → admin`

## 待處理事項（詳見 `_memory/deferred.md`）
- [ ] Admin Storage 孤兒照片清理工具
- [ ] 排隊回報伺服器端 Rate Limiting（待功能開放時補）
