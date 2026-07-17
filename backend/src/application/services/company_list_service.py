from src.domain.entities.subscription import Subscription


class CompanyListService:
    def __init__(self, company_repo, subscription_repo):
        self.company_repo = company_repo
        self.subscription_repo = subscription_repo

    async def build_company_rows(self, companies):
        items = []
        for company in companies:
            sub = await self.subscription_repo.find_by_company(company.id)
            items.append(self._row(company, sub))
        return items

    async def build_company_rows_all(self):
        companies = await self.company_repo.list_all(page=1, page_size=999999)
        return await self.build_company_rows(companies)

    def _row(self, company, sub: Subscription | None):
        return {
            "id": str(company.id),
            "cuit": company.cuit or "",
            "nombre": company.name,
            "plan": sub.plan.value if sub else "",
            "estado": sub.status.value if sub else "sin_suscripcion",
            "inicio": sub.start_date.isoformat() if sub and sub.start_date else None,
            "fin": sub.end_date.isoformat() if sub and sub.end_date else None,
            "requests_usados": 0,
        }
