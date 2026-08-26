.PHONY: help install test run-backend run-frontend run scan build docker-up docker-down clean

help:
	@echo "======================================================================"
	@echo "  HTF Supply & Demand Zone Scanner - Developer Commands"
	@echo "======================================================================"
	@echo "  make install       - Install Python & Node.js dependencies"
	@echo "  make test          - Run full pytest test suite (31+ tests)"
	@echo "  make run-backend   - Start FastAPI Uvicorn server on port 8000"
	@echo "  make run-frontend  - Start React Vite frontend dev server"
	@echo "  make scan          - Trigger on-demand EOD batch scan"
	@echo "  make docker-up     - Launch full stack in Docker containers"
	@echo "  make docker-down   - Stop Docker containers"
	@echo "======================================================================"

install:
	pip install -r requirements.txt
	cd frontend && npm install

test:
	python -m pytest tests/ -v

run-backend:
	python -m uvicorn app.main:app --reload --port 8000

run-frontend:
	cd frontend && npm run dev

scan:
	python -m scratch.test_scan

build:
	cd frontend && npm run build

docker-up:
	docker-compose up --build -d

docker-down:
	docker-compose down
