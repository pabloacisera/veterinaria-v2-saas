from uuid import UUID

import asyncpg

from src.domain.entities.user import AuthMethod, User, UserRole
from src.domain.repositories.user_repo import UserRepository as UserRepositoryInterface


class UserRepository(UserRepositoryInterface):
    def __init__(self, pool: asyncpg.Pool):
        self.pool = pool

    async def create(self, user: User) -> User:
        async with self.pool.acquire() as conn:
            row = await conn.fetchrow(
                """
                INSERT INTO users (id, company_id, email, password_hash, name,
                                   auth_method, google_id, role, is_active)
                VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9)
                RETURNING id, company_id, email, name, auth_method, google_id,
                          role, is_active, created_at, updated_at
                """,
                user.id, user.company_id, user.email, user.password_hash,
                user.name, user.auth_method.value, user.google_id,
                user.role.value, user.is_active,
            )
            return self._row_to_user(row)

    async def find_by_email(self, email: str) -> User | None:
        async with self.pool.acquire() as conn:
            row = await conn.fetchrow(
                "SELECT * FROM users WHERE email = $1 AND deleted_at IS NULL",
                email,
            )
            return self._row_to_user(row) if row else None

    async def find_by_id(self, user_id: UUID) -> User | None:
        async with self.pool.acquire() as conn:
            row = await conn.fetchrow(
                "SELECT * FROM users WHERE id = $1 AND deleted_at IS NULL",
                user_id,
            )
            return self._row_to_user(row) if row else None

    async def activate(self, user_id: UUID) -> None:
        async with self.pool.acquire() as conn:
            await conn.execute(
                "UPDATE users SET is_active = TRUE, updated_at = NOW() WHERE id = $1",
                user_id,
            )

    async def update_password(self, user_id: UUID, password_hash: str) -> None:
        async with self.pool.acquire() as conn:
            await conn.execute(
                "UPDATE users SET password_hash = $1, updated_at = NOW() WHERE id = $2",
                password_hash, user_id,
            )

    def _row_to_user(self, row: asyncpg.Record) -> User:
        return User(
            id=row["id"],
            company_id=row["company_id"],
            email=row["email"],
            password_hash=row.get("password_hash"),
            name=row["name"],
            auth_method=AuthMethod(row["auth_method"]),
            google_id=row.get("google_id"),
            role=UserRole(row["role"]),
            is_active=row["is_active"],
            created_at=row["created_at"],
            updated_at=row["updated_at"],
        )
