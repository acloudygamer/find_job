.PHONY: install dev backend frontend test clean docker-up docker-down lint format

# 安装所有依赖
install:
	cd backend && pip install -r requirements.txt
	cd frontend && npm install

# Docker 开发环境（dev profile 同时启动前后端）
dev:
	docker compose -f docker/docker-compose.yml --profile dev up

# 构建并启动所有服务
docker-up:
	docker compose -f docker/docker-compose.yml up --build

# 停止并清理容器
docker-down:
	docker compose -f docker/docker-compose.yml down

# 启动后端（本地开发）
backend:
	cd backend && uvicorn app.main:app --reload --port 8000

# 启动前端（本地开发）
frontend:
	cd frontend && npm run dev

# 运行测试
test:
	cd backend && pytest --cov=app --cov-report=term-missing
	cd frontend && npm run test

# 代码检查
lint:
	cd backend && ruff check app/
	cd frontend && npm run lint

# 代码格式化
format:
	cd backend && ruff format app/
	cd frontend && npm run format

# 清理构建产物
clean:
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete 2>/dev/null || true
	cd backend && rm -f find_job.db
	cd frontend && rm -rf dist

# 生产构建
build:
	docker compose -f docker/docker-compose.yml build
