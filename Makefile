.PHONY: up down migrate seed reset clear test test-unit test-integration test-e2e lint format logs shell-backend tunnel

up:
	@bash scripts/dev-up.sh

down:
	@bash scripts/dev-down.sh

migrate:
	@bash scripts/migrate.sh

seed:
	@bash scripts/seed-test-data.sh

reset:
	@bash scripts/dev-reset-db.sh

clear:
	@bash scripts/dev-clear-data.sh

test: test-unit test-integration

test-unit:
	@bash scripts/test-unit.sh

test-integration:
	@bash scripts/test-integration.sh

test-e2e:
	@bash scripts/test-e2e.sh

lint:
	@bash scripts/lint.sh

format:
	@bash scripts/format.sh

logs:
	@bash scripts/logs.sh

shell-backend:
	@docker compose exec backend bash

tunnel:
	@bash scripts/start-tunnel.sh

dev:
	@bash scripts/start-all.sh
