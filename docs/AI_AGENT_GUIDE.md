# AI 代理行為說明

本文件說明框架中 AI 代理的設計邏輯，供開發者和進階使用者參考。

## 架構

```
使用者 ←→ AI 代理（終端 CLI）←→ 腳本工具 + Obsidian Vault
         ↑ 核心介面                  ↑ 支撐層
```

AI 代理的行為由 `CLAUDE.md`（系統提示）和 `.claude/skills/`（指令定義）控制。

## 三大職責

### 1. 知識引導

- **問題驅動模式**：使用者提問 → 搜尋 vault → 綜合回答 → 標缺口 → 建議更新
- **即時捕獲**：對話中識別可沉澱的洞見，提示使用者確認
- **Session 回收**：對話結束時回顧所有討論，列出可寫入筆記的洞見

### 2. 歸檔管理

- `/onboard`：新筆記入庫（概念連結注入 + 候選發現）
- `/enrich`：批量充實薄弱筆記
- `/process-inbox`：處理 QuickAdd 建立的概念佇列
- 自動呼叫腳本工具（concept_index、inject_links 等）

### 3. 架構諮詢

- `/review-vault`：結合 vault_health.py 數據 + note_graph.py 分析，給出架構建議
- `/suggest-next`：基於學習目標和知識缺口，推薦下一步
- MOC 設計指導：按 LYT 原則建議 MOC 結構

## 行為適配

AI 根據 `vault_config.yaml` 的 `learning.experience_level` 調整行為：

| 等級 | AI 行為 |
|:--|:--|
| beginner | 多解釋概念、主動建議結構、詳細引導每個步驟 |
| intermediate | 聚焦知識缺口、協助深化、適度解釋 |
| advanced | 以討論為主、使用者主導、簡潔回應 |

## 知識回收模式

由 `capture.mode` 配置控制：

| 模式 | 行為 |
|:--|:--|
| `debrief` | 僅 session 結束時回顧 |
| `inline+debrief` | 對話中即時標示 + 結束回顧 |
| `journal+debrief` | 建立探索日誌 + 結束回顧 |

## 自訂 AI 行為

修改 `CLAUDE.md` 可以調整 AI 的核心行為。關鍵段落：

- **情境路由**：控制 AI 對不同使用者意圖的反應
- **Session Protocol**：控制對話開始/結束時的自動行為
- **問題驅動模式**：控制知識探索的流程
- **充實度分級**：控制筆記品質判斷標準

## 新增 Skill

在 `.claude/skills/` 下建立新目錄和 `SKILL.md`：

```yaml
---
name: my-skill
description: 描述
disable-model-invocation: true
argument-hint: [可選參數說明]
---

# Skill 標題

## 任務
（AI 應該做什麼）

## 步驟
（具體步驟）

## 注意事項
（限制和偏好）
```
