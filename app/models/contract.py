from datetime import datetime

class Contract:
    def __init__(self, contract_number, status, details):
        self.contract_number = contract_number # Primary key
        self.status = status # e.g., NEW, NEGOTIATION, APPROVED, SIGNED, EXECUTED, EXPIRED, RENEWED
        self.details = details # A dictionary to hold other contract specific data
        self.created_at = datetime.utcnow()
        self.updated_at = datetime.utcnow()

    def to_dict(self):
        return {
            "contract_number": self.contract_number,
            "status": self.status,
            "details": self.details,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat()
        }

    @staticmethod
    def from_dict(data):
        contract = Contract(
            data.get('contract_number'),
            data.get('status'),
            data.get('details', {})
        )
        created_at_data = data.get('created_at')
        if isinstance(created_at_data, str):
            contract.created_at = datetime.fromisoformat(created_at_data)
        elif isinstance(created_at_data, datetime):
            contract.created_at = created_at_data
        else:
            contract.created_at = None

        updated_at_data = data.get('updated_at')
        if isinstance(updated_at_data, str):
            contract.updated_at = datetime.fromisoformat(updated_at_data)
        elif isinstance(updated_at_data, datetime):
            contract.updated_at = updated_at_data
        else:
            contract.updated_at = None

        return contract