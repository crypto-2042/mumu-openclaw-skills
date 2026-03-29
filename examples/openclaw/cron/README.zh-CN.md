# OpenClaw Cron 布局示例

这个示例给出单书团队的任务型调度模型。

完整操作步骤请结合以下 runbook：

- [OpenClaw 运作手册（中文）](../../../docs/openclaw-operations-runbook.zh-CN.md)
- [OpenClaw 运作手册（英文）](../../../docs/openclaw-operations-runbook.md)

先安装 skill：

```bash
clawhub install mumuai-novel-skills
```

然后为每本书配置一组逻辑 job：

- `showrunner-scan`
- `writer-run`
- `editor-run`
- `reader-panel-run`

每个 job 共享：

- `MUMU_API_URL`
- `MUMU_USERNAME`
- `MUMU_PASSWORD`
- `PROJECT_ID`
- 可选 `STYLE_ID`

每个 job 必须使用不同的 `MUMU_OWNER_ID`。

推荐 owner 命名：

- `book-a-showrunner`
- `book-a-writer`
- `book-a-chief-editor`
- `book-a-reader-panel`

## 推荐职责

### `showrunner-scan`

- 频率：每 30 分钟一次
- 职责：
  - 检查书的当前状态
  - 决定 `continue`、`slow_down` 或 `pause_and_fix`
  - 唤醒下一个任务型角色

### `writer-run`

- 职责：
  - 扩纲
  - 只在书的状态足够健康时继续生成章节

### `editor-run`

- 职责：
  - 抓取待审章节
  - 分析质量和连续性
  - approve 或 rewrite

### `reader-panel-run`

- 职责：
  - 提供用户侧阅读评价
  - 报告当前节奏是否适合继续连载

## 建议的防呆规则

- 不要配置盲目的自动发布。
- 不要让 `Writer` 和 `Chief Editor` 同时处理同一章节。
- 不要复用 `MUMU_OWNER_ID`。
- 一套书就是一套团队，也是一组独立的调度单元。
