#!/bin/bash
set -e

echo "=== Create Super Admin ==="

if [ ! -f ".env" ]; then
    echo "ERROR: .env file not found."
    exit 1
fi

source .env

if [ -z "$SUPER_ADMIN_EMAIL" ] || [ -z "$SUPER_ADMIN_PASSWORD" ]; then
    echo "ERROR: SUPER_ADMIN_EMAIL and SUPER_ADMIN_PASSWORD must be set in .env"
    exit 1
fi

echo "Creating admin user: $SUPER_ADMIN_EMAIL"

cd backend
if [ -f ".venv/bin/python" ]; then
    .venv/bin/python -c "
import asyncio, os, asyncpg
from src.infrastructure.auth.password import PasswordService
from src.domain.entities.user import User, AuthMethod, UserRole
from uuid import uuid7

async def main():
    pool = await asyncpg.create_pool(os.getenv('DATABASE_URL'))
    async with pool.acquire() as conn:
        existing = await conn.fetchrow(
            \"SELECT id FROM users WHERE email = \$1 AND deleted_at IS NULL\",
            os.getenv('SUPER_ADMIN_EMAIL')
        )
        if existing:
            print('Admin user already exists')
            return
        pwd = PasswordService()
        user_id = uuid7()
        await conn.execute(\"\"\"
            INSERT INTO users (id, company_id, email, password_hash, name, auth_method, role, is_active)
            VALUES (\$1, \$2, \$3, \$4, \$5, 'manual', 'admin', TRUE)
        \"\"\", user_id, None, os.getenv('SUPER_ADMIN_EMAIL'),
            pwd.hash(os.getenv('SUPER_ADMIN_PASSWORD')), 'Super Admin')
        print(f'Admin created with id: {user_id}')
    await pool.close()

asyncio.run(main())
"
else
    echo "ERROR: Python virtual env not found."
    exit 1
fi

echo "=== Admin created ==="
