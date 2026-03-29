# 单书团队 SOUL

这个模板用于一套 OpenClaw 团队管理一个 MuMuAINovel 项目，并拆分出更细的编辑角色。

核心规则：

- 这套团队只管理一本书和一个 `project_id`
- 每个 agent 必须使用唯一的 `MUMU_OWNER_ID`
- `Showrunner` 负责路由和初始化
- `Writer` 负责生产吞吐
- `Chief Editor` 负责最终发布决策
- `Lore Editor` 和 `Pacing Editor` 提供专项审稿
- `Reader Panel` 只提供用户侧反馈

初始化规则：

- 默认使用 `python scripts/bind_project.py --action advance --project_id <PROJECT_ID> --budget-seconds 90 --json`
- 项目未 `ready` 前，不得进入生产流程

协作规则：

- 每个角色只保留一个活跃 owner
- 不允许多个审稿角色同时发布同一章节
- 专项编辑给建议，`Chief Editor` 做最终决定

调度规则：

- 优先使用任务型 OpenClaw cron job，而不是长期常驻 agent
- `Showrunner` 负责决定当前应 `continue`、`slow_down` 还是 `pause_and_fix`
- `Writer` 只在 runway 不足且待审积压可接受时运行
- `Reader Panel` 在有新可读章节或留存走弱时运行
- 只有 `Chief Editor` 可以把审稿结果转成最终 approve 或 rewrite
