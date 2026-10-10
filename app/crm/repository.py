import json
from pathlib import Path

from app.crm.models import LeadRecord


class LeadRepository:
    def __init__(self, data_dir: str | None = None):
        self.data_dir = Path(data_dir or "data/leads")
        self.data_dir.mkdir(parents=True, exist_ok=True)

    def save(self, lead: LeadRecord) -> None:
        path = self.data_dir / f"{lead.lead_id}.json"
        path.write_text(json.dumps(lead.to_dict(), ensure_ascii=False, indent=2), encoding="utf-8")

    def load(self, lead_id: str) -> LeadRecord | None:
        path = self.data_dir / f"{lead_id}.json"
        if not path.exists():
            return None
        payload = json.loads(path.read_text(encoding="utf-8"))
        return LeadRecord(**payload)
