from app.crm.models import LeadRecord
from app.crm.repository import LeadRepository


class LeadManager:
    def __init__(self, repository: LeadRepository | None = None) -> None:
        self.repository = repository or LeadRepository()

    def create_or_update(self, lead: LeadRecord) -> LeadRecord:
        self.repository.save(lead)
        return lead
