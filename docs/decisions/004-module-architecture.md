# ADR-004: 采用模块化简历架构

## 状态
已接受

## 背景

简历是一种高度结构化的文档，但不同用户的简历在内容组织和展示需求上差异很大：
- 技术简历可能需要"项目经历"模块
- 学术简历需要"发表论文"模块
- 设计师简历需要"作品集链接"模块

此外，用户可能需要：
- 自定义模块名称和顺序
- 同一模块在不同简历中复用
- 未来引入 AI 时，对模块级别的语义理解

## 决策

采用 **简历 → 模块 → 字段** 三层数据模型：

```
Resume (简历)
  └── Module (模块)  ← 支持重排序、复用
        └── Field (字段)  ← 键值对数据
```

### 设计原则

1. **模块独立**：每个模块有独立的 CRUD 接口，可单独更新
2. **字段灵活**：字段以 key-value 形式存储，支持任意结构化数据
3. **重排序**：模块和字段均支持通过 `PATCH /api/modules/reorder` 批量重排序
4. **导出无关**：数据模型与导出格式解耦，通过服务层实现多种导出格式

### 数据模型定义

```
Resume {
  id: UUID
  name: str
  description: str | None
  theme: str | None        # 主题/模板标识
  created_at: datetime
  updated_at: datetime
}

Module {
  id: UUID
  resume_id: UUID          # 所属简历（外键）
  name: str                # 模块名称，如"工作经历"
  module_type: str         # 模块类型标识，便于 AI 理解
  order: int               # 排序序号
  created_at: datetime
  updated_at: datetime
}

Field {
  id: UUID
  module_id: UUID          # 所属模块（外键）
  key: str                # 字段键，如"company_name"
  value: str              # 字段值
  order: int              # 排序序号
  created_at: datetime
  updated_at: datetime
}
```

## 后果

### 正面
- **灵活性**：用户可自由组合模块，适配不同简历场景
- **可扩展性**：新增模块类型或字段类型无需修改数据模型
- **AI 友好**：模块类型字段使 AI 能够理解语义，实现智能内容生成
- **导出灵活**：同一数据可导出为 JSON、Markdown、PDF 等多种格式
- **版本兼容**：模块结构变更通过 API 层处理，不影响存储层

### 负面
- 字段以 key-value 存储，适合结构化数据，但复杂嵌套结构（如多级列表）需要额外设计
- 模块间无引用关系（如"技能"模块引用"工作经历"中的技术栈），如需关联需扩展数据模型
- 重排序操作需要前端配合实现良好的拖拽交互体验

### 相关决策
- ADR-001: FastAPI 后端（支持嵌套路由和 PATCH 操作）
- ADR-002: SQLite 数据库（支持递归 CTE 查询）
- ADR-003: React 前端（Zustand 支持扁平状态管理，适配层级数据结构）
