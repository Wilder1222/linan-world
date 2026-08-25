# S1-E01 生产包（P3-02 → P3-03）

本目录是 Episode Gate 前的确定性生产卡与正式交付预审稿，不是最终成片。

- `episode-production-cards.json`：18 个微短章的机器可读生产卡。
- 每卡包含 Character State、Emotion & Action、Relationship Delta、Continuity Ledger、CineWeave Production 控制与十项 QA 占位。
- `episode-formal-delivery.json`：P3-03 汇总包，包含 18 个正式剧本场景、54 个草案镜头和 18 条连续性记录。
- `script-scenes.json`：逐章对白与动作第一版；`storyboard.json`：Blocking/Storyboard 草案；`continuity-ledger.json`：人物知识、道具、空间与关系连续性。
- U/BG 绑定与最终生成仍保持 `DEFERRED-UNTIL-EPISODE-GATE`；十项 QA 仍为 `PENDING`（阈值 90）。
- 未调用任何外部生成服务；能力、版权和输出回执未解析前，外部执行保持阻断。

预审：`qa/reviews/p3-e01-formal-preflight-review.json` 为 `REVIEWED-P3-PREFLIGHT-PASS`。

下一步：进入人工 Episode Gate，逐章评分十项 QA；未通过前不生成 U/BG、不调用外部 provider、不推进 E02/E03。
