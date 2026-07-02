# 論文處理指南

## 目標

將論文保留為可追溯的 source note，並在真正回答研究問題時，將經確認的洞見整合到概念筆記與 MOC。

## 目錄

```text
PDF-raw/{citekey}.pdf
  → PDF-md/{citekey}.md
  → 人工審查
  → Final-md/{citekey}.md
```

`PDF-md` 可以是機器協助產生的工作版本；`Final-md` 是人工審查後的高品質版本。兩者都不會觸發自動概念連結。

## 建議內容

- 書目與 citekey
- 研究問題與背景
- 方法與資料
- 主要結果
- 限制與適用邊界
- 與目前研究的關聯
- 可追溯的圖表引用
- 待驗證問題

## 圖表工具

啟用 `paper_pipeline` 後可使用 `extract_figures.py` 與 `insert_figures.py`。先 dry-run，目視確認圖號、caption 與實際內容，再寫入 Markdown。

## 知識整合

當論文被用來回答問題時：

1. 指出它支持或反駁哪個主張。
2. 檢查是否已有概念筆記。
3. 優先更新既有筆記並連回 `[[citekey]]`。
4. 單篇新發現標示為待多源驗證。
5. 不因術語出現就建立新概念或批量加入 wikilink。
