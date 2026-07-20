#!/bin/bash
set -e

echo "=== Veterinaria V2 - Clear All Data ==="

echo "Truncating core_db tables..."
docker compose exec core_db psql -U veterinaria_v2 -d core_db -c "
TRUNCATE TABLE 
  users, 
  companies, 
  subscriptions, 
  clients, 
  pets, 
  supplies, 
  procedures, 
  consultations, 
  consultation_procedures, 
  consultation_supplies, 
  cash_movements, 
  store_sales, 
  store_sale_items, 
  documentos_generados, 
  admin_reset_tokens, 
  mp_webhook_events, 
  tenant_mp_credentials, 
  rag_embeddings, 
  chat_conversations, 
  backups_log 
CASCADE;
"

echo "Clearing Redis (sessions, activation codes, cache)..."
docker compose exec redis redis-cli -n 0 FLUSHDB
docker compose exec redis redis-cli -n 1 FLUSHDB
docker compose exec redis redis-cli -n 2 FLUSHDB
docker compose exec redis redis-cli -n 3 FLUSHDB

echo "=== All data cleared ==="
