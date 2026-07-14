---
name: review-renovate-mr
description: Use this skill when reviewing Renovate-generated dependency upgrade Merge Requests `feature/renovate-*`. Assess changelogs, breaking changes, compatibility, and project impact before deciding whether the MR is safe to merge.
---

# review-renovate-mr

以资深前端工程师的视角 review 当前 Renovate 升包 MR。

## 定位需要 review 的 MR

* 如果用户提供了 MR 地址，直接使用。
* 如果没有提供，则根据当前仓库的 `git remote`（如 `origin`）和当前分支推断对应的 GitLab/GitHub 仓库，并使用 `glab` / `gh` CLI 查找当前分支关联的 Merge Request/Pull Request。

## 重点检查

* 覆盖旧版本到新版本之间的完整版本跨度，而不只是目标版本。
* 查阅 changelog、release notes、migration guide 和官方文档。
* 识别 breaking changes、弃用项、默认行为变化、运行时要求及构建工具兼容性。
* 结合仓库中的实际用法，判断这些变化是否会影响现有代码。
* 检查 lockfile、间接依赖、peer dependencies、类型定义及构建产物变化。
* 评估现有测试是否足以覆盖升级风险，并指出需要补充的验证。

不要因为 CI 通过就默认升级安全。

如果没有明确或完整的 changelog，应分析依赖源码、类型声明、导出结构以及仓库中的实际使用方式，推断潜在行为变化。

## 输出

1. 风险等级
2. 主要发现
3. 建议验证项
4. 是否建议合并

### 风险等级

🟢 **绿灯（Safe）**

可以直接合并。

特征：

* API 与行为保持兼容。
* 无 Breaking Changes。
* 不需要修改业务代码。
* 正常通过 CI 并完成基本验证即可。

---

🟡 **黄灯（Caution）**

API 基本保持兼容，但运行环境或工程配置发生变化，需要额外验证。

典型情况：

* CommonJS/UMD → ESM。
* Node.js、浏览器或 React Native 最低版本提升。
* peerDependencies、构建工具或 Babel/TypeScript 配置发生变化。
* 默认行为改变，但通常无需修改业务代码。
* 打包、Tree Shaking、CSS、Polyfill 等工程层面的变化。

需要确认：

* 能否正常安装。
* 能否正常编译。
* 能否正常运行。
* 是否需要调整工程配置。

---

🔴 **红灯（Breaking）**

存在明确的不兼容变更，不建议直接合并。

典型情况：

* API 删除或修改。
* 参数、返回值或类型发生不兼容变化。
* 配置格式发生 Breaking Change。
* 行为发生重大变化，需要修改业务代码才能继续工作。

需要明确指出：

* 哪些代码会受到影响。
* 建议如何迁移或重构。
* 是否建议拆分为单独 MR 处理。
