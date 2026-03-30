# find_job 项目指令

> 本文件为项目级最高优先级指令，覆盖全局默认行为。

## 项目背景

find_job 是一个简历设计管理系统，支持模块化简历编辑、与 GitHub 项目联动（通过 AI）、多格式导出。

## 目录结构

```
find_job/
├── backend/              # FastAPI 后端（app/api、app/models、app/repositories、app/services）
├── frontend/             # React 前端（React 18 + Vite + TypeScript + Zustand）
├── docker/              # Docker Compose 及 Dockerfile 配置
├── docs/                # 架构文档及决策记录
│   ├── architecture.md  # 系统架构总览
│   └── decisions/       # ADR 决策记录
├── src/                 # 共享源码（前端 API 层 / 持久化层）
│   ├── api/             # API 层实现
│   └── persistence/     # 数据持久化实现
├── tests/               # 跨模块集成测试
├── tools/               # 工具脚本
│   ├── prompts/         # AI 提示词模板
│   └── scripts/         # 辅助脚本
└── CLAUDE.md           # 本文件
```

## 技术栈

| 层级 | 技术 |
|------|------|
| 前端 | React 18 + Vite + TypeScript + Zustand |
| 后端 | Python FastAPI + SQLAlchemy + SQLite |
| 部署 | Docker Compose |
| AI | Claude API（规划中） |

## 测试规则

所有测试日志的输出格式必须包含 `[TEST-MEM]` 前缀。

## 开发命令

```bash
# 安装依赖
make install

# 本地开发（分别启动）
make backend   # http://localhost:8000
make frontend  # http://localhost:5173

# Docker 开发
make dev

# 运行测试
make test

# 代码检查
make lint

# 格式化
make format

# Docker 部署
make docker-up
make docker-down

# 清理
make clean
```

## 代码规范

遵循以下全局规范（优先级递减）：
1. **本文件（项目指令）**：最高优先级
2. `~/.claude/rules/common/*.md`（全局编码规范）
3. `~/.claude/rules/common/coding-style.md`（不可变性、错误处理）
4. `~/.claude/rules/common/patterns.md`（仓储模式、API 响应格式）

### 关键规范摘要

- **不可变性**：始终创建新对象，不修改现有对象
- **错误处理**：每层显式处理错误，用户友好提示 + 详细日志
- **输入验证**：在 API 层全面验证用户输入
- **文件大小**：单个文件不超过 800 行，优先拆分
- **函数大小**：单个函数不超过 50 行，优先拆分
- **深度嵌套**：不超过 4 层嵌套

## API 契约

后端 API 契约定义在 FastAPI 应用中，通过 Swagger UI 访问：
- 开发环境：`http://localhost:8000/docs`
- ReDoc：`http://localhost:8000/redoc`

### 核心端点

| 方法 | 路径 | 说明 |
|------|------|------|
| CRUD | /api/resumes | 简历管理 |
| CRUD | /api/modules | 模块管理 |
| CRUD | /api/fields | 字段管理 |
| PATCH | /api/modules/reorder | 批量重排序 |
| GET | /api/resumes/{id}/export | 导出（json/markdown） |

## 测试要求

- 最低测试覆盖率：**80%**
- 单元测试：独立函数、工具类
- 集成测试：API 端点、数据库操作
- 使用 pytest（后端）和 Vitest（前端）

## 安全要求

- API 密钥不硬编码，始终使用环境变量
- 所有用户输入在 API 层验证（Pydantic 模型）
- CORS 配置限制来源，生产环境指定真实域名
- 敏感文件（.env、*.db）已加入 .gitignore，不提交至版本控制

## 架构决策

所有重要架构决策记录在 `docs/decisions/` 目录（ADR 格式）：
- ADR-001: 选择 FastAPI 作为后端框架
- ADR-002: 选择 SQLite 作为开发数据库
- ADR-003: 选择 React + Vite 作为前端框架
- ADR-004: 采用模块化简历架构

## 协作流程

复杂功能实现遵循以下流程：
1. **规划** → 使用 planner agent 分解任务
2. **TDD** → 使用 tdd-guide agent，先写测试
3. **实现** → 遵循代码规范
4. **审查** → 使用 code-reviewer agent
5. **提交** → conventional commits 格式
