from datetime import datetime
from uuid import UUID

import asyncpg

from src.domain.entities.subscription import Subscription, SubscriptionStatus, PlanType
from src.domain.repositories.subscription_repo import SubscriptionRepository as SubscriptionRepositoryInterface


class SubscriptionRepository(SubscriptionRepositoryInterface):
    def __init__(self, pool: asyncpg.Pool):
        self.pool = pool

    async def create(self, subscription: Subscription) -> Subscription:
        async with self.pool.acquire() as conn:
            row = await conn.fetchrow(
                """
                INSERT INTO subscriptions (id, company_id, plan, status, mp_preapproval_id, mp_plan_id,
                                           start_date, end_date, trial_end_date, next_billing_date, grace_period_end)
                VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11)
                RETURNING *
                """,
                subscription.id, subscription.company_id, subscription.plan.value,
                subscription.status.value, subscription.mp_preapproval_id,
                subscription.mp_plan_id, subscription.start_date, subscription.end_date,
                subscription.trial_end_date, subscription.next_billing_date,
                subscription.grace_period_end,
            )
            return self._row_to_subscription(row)

    async def find_by_company(self, company_id: UUID) -> Subscription | None:
        async with self.pool.acquire() as conn:
            row = await conn.fetchrow(
                "SELECT * FROM subscriptions WHERE company_id = $1 AND deleted_at IS NULL",
                company_id,
            )
            return self._row_to_subscription(row) if row else None

    async def find_by_preapproval(self, mp_preapproval_id: str) -> Subscription | None:
        async with self.pool.acquire() as conn:
            row = await conn.fetchrow(
                "SELECT * FROM subscriptions WHERE mp_preapproval_id = $1 AND deleted_at IS NULL",
                mp_preapproval_id,
            )
            return self._row_to_subscription(row) if row else None

    async def update_status(self, subscription_id: UUID, status: SubscriptionStatus) -> Subscription:
        async with self.pool.acquire() as conn:
            row = await conn.fetchrow(
                "UPDATE subscriptions SET status = $1, updated_at = NOW() WHERE id = $2 RETURNING *",
                status.value, subscription_id,
            )
            return self._row_to_subscription(row)

    async def update_mp_data(self, subscription_id: UUID, mp_preapproval_id: str, mp_plan_id: str) -> Subscription:
        async with self.pool.acquire() as conn:
            row = await conn.fetchrow(
                """
                UPDATE subscriptions SET mp_preapproval_id = $1, mp_plan_id = $2, updated_at = NOW()
                WHERE id = $3 RETURNING *
                """,
                mp_preapproval_id, mp_plan_id, subscription_id,
            )
            return self._row_to_subscription(row)

    async def update_billing(self, subscription_id: UUID, next_billing_date: datetime) -> Subscription:
        async with self.pool.acquire() as conn:
            row = await conn.fetchrow(
                "UPDATE subscriptions SET next_billing_date = $1, updated_at = NOW() WHERE id = $2 RETURNING *",
                next_billing_date, subscription_id,
            )
            return self._row_to_subscription(row)

    async def list_expiring_soon(self, days: int = 7) -> list[Subscription]:
        async with self.pool.acquire() as conn:
            rows = await conn.fetch(
                """
                SELECT * FROM subscriptions
                WHERE status = 'activa' AND deleted_at IS NULL
                  AND end_date IS NOT NULL
                  AND end_date <= NOW() + INTERVAL '1 day' * $1
                  AND end_date > NOW()
                """,
                days,
            )
            return [self._row_to_subscription(r) for r in rows]

    async def list_expired(self) -> list[Subscription]:
        async with self.pool.acquire() as conn:
            rows = await conn.fetch(
                """
                SELECT * FROM subscriptions
                WHERE status IN ('activa', 'vencida') AND deleted_at IS NULL
                  AND end_date IS NOT NULL AND end_date <= NOW()
                """,
            )
            return [self._row_to_subscription(r) for r in rows]

    async def list_active_with_billing_today(self) -> list[Subscription]:
        async with self.pool.acquire() as conn:
            rows = await conn.fetch(
                """
                SELECT * FROM subscriptions
                WHERE status = 'activa' AND deleted_at IS NULL
                  AND next_billing_date IS NOT NULL
                  AND next_billing_date::date <= CURRENT_DATE
                """,
            )
            return [self._row_to_subscription(r) for r in rows]

    async def extend_end_date(self, subscription_id: UUID, end_date: datetime) -> Subscription:
        async with self.pool.acquire() as conn:
            row = await conn.fetchrow(
                "UPDATE subscriptions SET end_date = $1, status = 'activa', updated_at = NOW() WHERE id = $2 RETURNING *",
                end_date, subscription_id,
            )
            return self._row_to_subscription(row)

    async def mark_blocked(self, company_id: UUID) -> None:
        async with self.pool.acquire() as conn:
            await conn.execute(
                "UPDATE subscriptions SET status = 'bloqueada', updated_at = NOW() WHERE company_id = $1 AND deleted_at IS NULL",
                company_id,
            )

    def _row_to_subscription(self, row: asyncpg.Record) -> Subscription:
        return Subscription(
            id=row["id"],
            company_id=row["company_id"],
            plan=PlanType(row["plan"]),
            status=SubscriptionStatus(row["status"]),
            mp_preapproval_id=row.get("mp_preapproval_id"),
            mp_plan_id=row.get("mp_plan_id"),
            start_date=row["start_date"],
            end_date=row.get("end_date"),
            trial_end_date=row.get("trial_end_date"),
            next_billing_date=row.get("next_billing_date"),
            grace_period_end=row.get("grace_period_end"),
            created_at=row["created_at"],
            updated_at=row["updated_at"],
        )
