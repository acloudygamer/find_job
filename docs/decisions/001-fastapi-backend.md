# ADR-001: 选择 FastAPI 作为后端框架

## 状态
已接受

## 背景

构建一个简历设计管理系统后端 API，需要满足以下需求：
- RESTful API 端点，支持 CRUD 操作
- 自动生成 OpenAPI / Swagger 文档
- 异步支持，提高并发性能
- 数据验证与序列化
- 轻量级、易于部署

## 决策

选择 **FastAPI** 作为后端框架，Python 3.11。

### 主要理由

1. **现代化异步框架**：基于 Starlette，支持 async/await，吞吐量高
2. **自动 API 文档**：开箱即用 Swagger UI 和 ReDoc，无需额外配置
3. **Pydantic 集成**：请求/响应数据模型自动验证，减少样板代码
4. **类型安全**：支持 Python 类型注解，与 TypeScript 前端高度兼容
5. **部署简单**：可使用 uvicorn 或 gunicorn 直接运行，Docker 友好

### 备选方案对比

| 框架 | 优势 | 劣势 |
|------|------|------|
| FastAPI | 文档自动生成、类型安全、异步性能好 | 生态相对较新 |
| Flask | 生态成熟、轻量 | 无异步支持、需要手动验证 |
| Django | 功能完整、ORM 强大 | 重量级、学习曲线陡 |

## 后果

### 正面
- API 文档自动生成，减少文档维护成本
- Pydantic 提供的数据验证减少了运行时错误
- 异步特性提升 I/O 密集型操作的性能
- 与 React 前端通过 JSON/TypeScript 类型共享保持一致性

### 负面
- Python GIL 限制 CPU 密集型场景（如 AI 推理），需通过后台任务或外部服务解决
- 框架相对较新，部分边缘场景文档不如 Django 完善

### 相关决策
- ADR-002: 选择 SQLite 作为开发数据库
- ADR-003: 选择 React + Vite 作为前端框架
