# ADR-003: 选择 React + Vite 作为前端框架

## 状态
已接受

## 背景

find_job 前端需要：
- 简历编辑界面，支持拖拽排序模块
- 实时预览简历效果
- 与后端 API 交互（CRUD + 导出）
- 未来可能引入 AI 辅助编辑功能

### 约束
- 团队已有 React + TypeScript 经验
- 需要良好的开发体验（热重载、快速启动）
- 期望长期维护，前端生态稳定

## 决策

选择 **React 18 + Vite + TypeScript + Zustand** 作为前端技术栈。

### 主要理由

#### Vite
1. **极快的启动速度**：基于 ESM，无需打包即可服务，开发体验流畅
2. **HMR 优化**：模块级别热替换，编辑保存后毫秒级响应
3. **开箱即用**：无需复杂配置，原生支持 TypeScript、JSX、CSS 模块

#### React 18
1. **成熟的组件化生态**：社区丰富，组件库选择多（shadcn/ui、Radix UI）
2. **Concurrent Features**：Suspense、transition 支持复杂 UI 场景
3. **与 Vite 集成良好**：社区认可的标准组合

#### Zustand
1. **极简 API**：比 Redux 少 90% 样板代码
2. **Hooks 原生**：基于 React Hooks，无 Provider 嵌套地狱
3. **轻量**：打包体积小，无外部依赖

#### TypeScript
1. **类型安全**：与 FastAPI Pydantic 模型高度对齐
2. **IDE 支持优秀**：VS Code 中智能提示完善
3. **重构友好**：大型项目中类型检查显著降低回归风险

### 备选方案对比

| 方案 | 优势 | 劣势 |
|------|------|------|
| React + Vite | 启动快、HMR 好、类型安全 | 需要自行选择状态管理 |
| Next.js (App Router) | SSR/SSG、内置路由 | 重量级，对于纯 CRUD 场景过度设计 |
| Vue 3 + Vite | 上手简单、文档友好 | 团队技术栈偏好 React |
| Svelte | 极致轻量、编译时响应式 | 社区生态相对较小 |

## 后果

### 正面
- 开发启动时间从 Webpack 的 30s+ 降至 Vite 的 <1s
- TypeScript 与 FastAPI 类型共享，减少前后端接口不一致问题
- Zustand 状态管理简单直观，新成员上手成本低
- 组件库生态丰富（如需 UI 组件可快速引入）

### 负面
- React 18 Server Components 场景下需注意服务端/客户端边界
- Zustand 适合中小规模状态管理，大型复杂场景（多人协作编辑）可能需要引入 CRDT 等方案
- Vite 在非现代浏览器上开发时可能需要额外配置（生产构建不受影响）

### 相关决策
- ADR-001: 选择 FastAPI 作为后端框架（JSON API 协议对齐）
- ADR-002: 选择 SQLite 作为开发数据库
- ADR-004: 采用模块化简历架构（影响前端状态设计）
