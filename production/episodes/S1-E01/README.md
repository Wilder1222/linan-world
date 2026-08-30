# S1-E01 生产卡（P3-02）

本目录是 Episode Gate 前的确定性生产卡，不是最终剧本或成片。

- `episode-production-cards.json`：18 个微短章的机器可读生产卡。
- 每卡包含 Character State、Emotion & Action、Relationship Delta、Continuity Ledger、CineWeave Production 控制与十项 QA 占位。
- 最终对白、镜头 ID、活动/幽默的具体场次、U/BG 绑定均保持 `DEFERRED-UNTIL-EPISODE-GATE`。
- 未调用任何外部生成服务；能力、版权和输出回执未解析前，外部执行保持阻断。

下一步：逐章补正式场景与对白，完成 blocking/storyboard/AIGC 资产绑定，再运行 Episode Gate。
