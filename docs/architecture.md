# find_job 简历设计管理系统 — 架构文档

## 1. 系统概览

find_job 是一个简历设计管理系统，支持模块化简历编辑、与 GitHub 项目联动（通过 AI）、多格式导出。

## 2. 技术栈

| 层级 | 技术 |
|------|------|
| 前端 | React 18 + Vite + TypeScript + Zustand |
| 后端 | Python FastAPI + SQLAlchemy + SQLite |
| 部署 | Docker Compose |
| AI | Claude API（规划中） |
| 协议 | REST API (JSON) |

## 3. 系统架构图

```
┌─────────────────────────────────────────────┐
│              React Frontend                  │
│         (localhost:5173 dev)                  │
└────────────────┬────────────────────────────┘
                  │ HTTP/REST
┌─────────────────▼────────────────────────────┐
│              FastAPI Backend                 │
│             (localhost:8000)                  │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  │
│  │  Routes   │  │  Service │  │ Repository│  │
│  └──────────┘  └──────────┘  └──────────┘  │
│                    │                         │
│              ┌─────▼─────┐                   │
│              │  SQLite   │                   │
│              └───────────┘                   │
└─────────────────────────────────────────────┘
                  │
         ┌───────▼────────┐
         │  Claude API     │ (规划中)
         │  (AI Features)  │
         └─────────────────┘
```

## 4. 数据模型

简历与模块、字段之间的层级关系：

```
Resume 1─────< Module 1─────< Field
```

- **Resume**：顶层简历实体，包含元数据（名称、描述、主题等）
- **Module**：简历中的一个功能区块（如"工作经历"、"教育背景"），支持重排序
- **Field**：模块中的具体字段（如"公司名称"、"在职时间"），包含键值对数据

## 5. API 端点

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | /api/resumes | 简历列表 |
| POST | /api/resumes | 创建简历 |
| GET | /api/resumes/{id} | 简历详情 |
| PUT | /api/resumes/{id} | 更新简历 |
| DELETE | /api/resumes/{id} | 删除简历 |
| GET | /api/resumes/{id}/modules | 模块列表 |
| POST | /api/resumes/{id}/modules | 创建模块 |
| GET | /api/modules/{id} | 模块详情 |
| PUT | /api/modules/{id} | 更新模块 |
| DELETE | /api/modules/{id} | 删除模块 |
| PATCH | /api/modules/reorder | 批量重排序 |
| GET | /api/modules/{id}/fields | 字段列表 |
| POST | /api/modules/{id}/fields | 创建字段 |
| PUT | /api/fields/{id} | 更新字段 |
| DELETE | /api/fields/{id} | 删除字段 |
| GET | /api/resumes/{id}/export?format=json | 导出 JSON |
| GET | /api/resumes/{id}/export?format=markdown | 导出 Markdown |

## 6. 目录结构

```
find_job/
├── backend/              # FastAPI 后端
│   ├── app/
│   │   ├── api/         # API 路由
│   │   ├── models/      # Pydantic 模型 / SQLAlchemy 模型
│   │   ├── repositories/# 数据访问层
│   │   ├── services/    # 业务逻辑层
│   │   └── main.py      # 应用入口
│   ├── tests/           # pytest 测试
│   └── requirements.txt
├── frontend/             # React 前端 (待创建)
│   ├── src/
│   │   ├── api/         # API 客户端
│   │   ├── components/  # 通用组件
│   │   ├── features/    # 功能模块
│   │   └── store/       # Zustand 状态管理
│   └── package.json
├── docker/               # Docker 配置
│   ├── docker-compose.yml
│   ├── Dockerfile.backend
│   ├── Dockerfile.frontend
│   ├── .env.development
│   └── .env.production
├── docs/                 # 文档
│   ├── architecture.md  # 本文件
│   └── decisions/        # 架构决策记录 (ADR)
├── src/                  # 共享源码（前端 API 层 / 持久化层）
│   ├── api/             # API 层实现
│   └── persistence/     # 数据持久化实现
├── tests/               # 跨模块集成测试
├── tools/               # 工具脚本
│   ├── prompts/         # AI 提示词模板
│   └── scripts/         # 辅助脚本
├── CLAUDE.md            # 项目级指令
├── Makefile             # 常用命令
└── README.md            # 项目说明
```

## 7. 决策记录

已记录在 `docs/decisions/` 目录：

| 编号 | 决策 | 状态 |
|------|------|------|
| ADR-001 | 选择 FastAPI 作为后端框架 | 已接受 |
| ADR-002 | 选择 SQLite 作为开发数据库 | 已接受 |
| ADR-003 | 选择 React + Vite 作为前端框架 | 已接受 |
| ADR-004 | 采用模块化简历架构 | 已接受 |

## 8. 开发环境

```bash
# 安装依赖
make install

# 本地开发（分别启动）
make backend   # 后端 → http://localhost:8000
make frontend  # 前端 → http://localhost:5173

# Docker 开发（同时启动前后端）
make dev

# 运行测试
make test

# 代码检查
make lint

# Docker 生产部署
make docker-up

# 清理
make clean
```

## 9. 安全注意事项

- API 密钥通过环境变量注入，不硬编码在源码中
- CORS 配置限制来源，生产环境需指定真实域名
- 用户输入在 API 层全面验证（Pydantic 模型校验）
- SQLite 仅用于开发/小规模部署，生产环境应迁移至 PostgreSQL
- 敏感文件（.env、*.db）已加入 .gitignore
