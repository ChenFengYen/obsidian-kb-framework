# 領域自訂指南

## vault_config.yaml

在 `domains` 增加領域後，setup 會建立 `OV-{Domain}/Map`、`Note` 與 `Pic`。`keywords` 只用於搜尋與路由提示，不會用於自動連結。

```yaml
domains:
  Neuroscience:
    description: "神經科學"
    keywords: [neuroscience, neural circuits]
```

## 使用者背景

`learning` 與 `user_profile` 讓 Agent 了解目前焦點、經驗和知識缺口。它們只影響建議排序，不應成為自動生成筆記的依據。

## Capture 模式

- `debrief`：只在結束時回收洞見。
- `inline+debrief`：討論中提示候選，結束時再整理。
- `journal+debrief`：另保留探索日誌。

不論模式，寫入知識筆記前都要取得使用者確認。

## Skills

可在 `.claude/skills/{name}/SKILL.md` 新增技能。每個 skill 應包含觸發條件、輸入、核准點、輸出位置與驗證方法，並遵守 proposal-first 與禁止自動語意連結的規則。

## 可選模組

```yaml
modules:
  zotero: true
  paper_pipeline: true
```

Zotero 與 paper pipeline 是來源管理工具，不改變 v2 的問題驅動知識建設原則。
