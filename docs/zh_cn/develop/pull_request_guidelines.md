# PR 规范

本文档用于说明向 MaaPracticeBoilerplate 提交 Pull Request（PR）时的基本约定，也可作为基于本模板创建 MaaFramework 项目后的协作参考。

## 基本原则

- **目标分支**：向本模板仓库提交 PR 时，默认目标分支为 `main`。
- **范围单一**：一个 PR 只解决一个明确问题，避免混入无关格式化、重构或功能改动。
- **说明完整**：PR 描述应写清楚改动原因、影响范围和验证方式。
- **优先复用**：修改模板能力前，先确认是否已有 MaaFramework、MaaCommonAssets 或工作流配置可复用。
- **自己负责**：可以使用 AI 辅助，但提交者必须理解并能解释 PR 中的关键改动。

## 分支与提交

### 分支命名

推荐使用以下格式：

| 类型 | 示例 | 适用场景 |
| ------ | ------ | ---------- |
| `feat/<name>` | `feat/add-sample-task` | 新增模板能力或示例 |
| `fix/<name>` | `fix/check-workflow` | 修复 Bug |
| `docs/<name>` | `docs/pr-guidelines` | 文档改动 |
| `refactor/<name>` | `refactor/resource-layout` | 不改变行为的结构调整 |
| `chore/<name>` | `chore/update-deps` | 工具、依赖、构建等维护工作 |

### 提交信息

推荐遵循 [约定式提交（Conventional Commits）](https://www.conventionalcommits.org/zh-hans/v1.0.0/)：

```text
<type>(<scope>): <subject>
```

示例：

```text
docs: 补充 PR 规范
fix(ci): 修复资源检查触发路径
chore: 更新 MaaFramework 依赖版本
```

`scope` 可选，建议填写影响范围。`subject` 使用简短描述，不以句号结尾。

## PR 标题

PR 标题建议与提交信息保持一致，方便维护者快速判断变更类型：

| 推荐标题 | 不推荐标题 |
| ---------- | ------------ |
| `docs: 补充 PR 规范` | `update docs` |
| `fix(ci): 修复资源检查触发路径` | `修一下工作流` |
| `feat: 添加示例任务配置` | `添加东西` |

如果 PR 仍在开发中，请使用 GitHub Draft PR，而不是在标题前长期保留 `WIP`。

## PR 描述

PR 描述至少应包含以下信息：

### 关联内容

- 关联 Issue：`Closes #123`、`Fixes #123` 或 `Related #123`
- 如果没有 Issue，请说明需求来源、复现方式或为什么需要这个改动

### 变更摘要

用 2～5 条 bullet 说明改了什么，例如：

- 更新开发文档中的配置说明
- 调整 GitHub Actions 资源检查流程
- 新增模板项目的 PR 提交说明

### 验证记录

说明你做过哪些验证。不要只写“已测试”，应写清楚执行了什么、结果如何。

推荐格式：

```markdown
## 验证

- [x] 执行 `npm ci && npx @nekosu/maa-tools check`
- [x] 执行 `python tools/validate_schema.py --schema-dir deps/tools --resource-dirs assets/resource --exclude-dirs assets/resource/announcement --interface-files assets/interface.json`
- [x] 检查文档链接可正常跳转
```

### 截图、日志与素材

涉及界面、资源识别、工作流失败或 Bug 修复时，应尽量提供：

- 修改前后的行为对比
- 失败日志或 GitHub Actions 链接
- 新增或修改资源文件的路径
- 必要的截图或复现步骤

## 变更要求

### 模板资源改动

- 坐标、ROI、模板图片等资源应遵循 MaaFramework 的 720p 基准约定。
- 新增任务或资源时，需要检查 `assets/interface.json`、`assets/resource` 与任务配置是否一致。
- 不要提交本地缓存、运行产物、调试截图或下载得到的大体积模型文件。
- 修改 schema、资源目录或工作流时，需要说明对基于模板创建项目的影响。

### Python / 工具改动

- 保持脚本逻辑简单可读，避免引入不必要的依赖。
- 修改工具脚本后，应补充对应命令的验证结果。
- 涉及长流程或用户可中断操作时，应考虑异常处理和退出路径。

### 文档与配置改动

- 用户可见流程、模板使用方式或开发约定发生变化时，应同步更新文档。
- 依赖、构建、发布相关改动需要说明动机，并提交对应锁文件变更。
- 如果改动会影响基于模板创建的新项目，请在 PR 描述中明确说明迁移影响。

## 提交前检查清单

提交 PR 前至少自查：

- [ ] PR 目标分支是 `main`
- [ ] PR 标题清晰，最好符合约定式提交格式
- [ ] 变更范围单一，没有混入无关改动
- [ ] 已同步最新 `origin/main`
- [ ] 已说明变更原因、影响范围和验证结果
- [ ] 涉及资源、工作流或脚本时，已提供必要日志或复现信息
- [ ] 文档已随用户可见行为或开发约定同步更新
- [ ] 没有提交缓存、构建产物、调试文件或大体积模型文件

## 评审与合并

- 维护者可能要求补充日志、复现步骤、截图或验证记录；请在同一 PR 中继续修正。
- 如果评审意见涉及设计方向，请先回复确认方案，再继续大量改动。
- PR 被合并后，如发现后续问题，请新开 Issue 或 PR 跟进，不要在已合并 PR 中继续讨论新的无关需求。
