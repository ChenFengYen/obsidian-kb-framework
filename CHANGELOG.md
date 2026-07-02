# Changelog

## 2.0.0 - 2026-07-02

### Changed

- 問題驅動協作成為唯一預設知識建設流程。
- 連結改為閱讀上下文後的人工／AI 語意判斷。
- 筆記品質改以問題、來源、邊界與連結性判斷，不再以行數作為擴寫目標。
- 健康報告預設寫入系統暫存目錄。
- 內建 skills 精簡為 init-domain、review-vault、suggest-next、debrief。

### Removed

- 自動連結注入與 concept index。
- 自動候選擷取、stub 建立與 QuickAdd stub 佇列。
- 批量 enrich 任務與相關 skills。

升級方式見 docs/MIGRATION_V2.md。
