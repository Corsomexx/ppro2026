from typing import List, Optional, Dict
from src.domain.models import EquipmentItem
from src.domain.enums import EquipmentStatus, EquipmentCategory, EquipmentCondition
from src.infrastructure.repositories import EquipmentRepository

class BusinessRuleViolationException(Exception):
    """Výjimka porušení byznys pravidla půjčovny."""
    pass

class InventoryNumberAlreadyExistsException(BusinessRuleViolationException):
    """Inventární číslo již existuje v systému."""
    pass

class ItemNotFoundException(Exception):
    """Položka vybavení nebyla nalezena."""
    pass

class EquipmentService:
    """
    Aplikační služba zapouzdřující byznys logiku a pravidla pro správu vybavení půjčovny.
    Striktně odděluje byznys pravidla od kontrolerů i perzistentní vrstvy.
    """
    def __init__(self, repository: EquipmentRepository):
        self.repository = repository

    def get_item(self, item_id: int) -> EquipmentItem:
        item = self.repository.get_by_id(item_id)
        if not item:
            raise ItemNotFoundException(f"Kus vybavení s ID {item_id} nebyl nalezen.")
        return item

    def list_items(
        self,
        status: Optional[EquipmentStatus] = None,
        category: Optional[EquipmentCategory] = None,
        search: Optional[str] = None
    ) -> List[EquipmentItem]:
        return self.repository.list_all(status=status, category=category, search=search)

    def get_dashboard_summary(self) -> Dict[str, int]:
        """Poskytuje data pro pultový dashboard 'sobota ráno'."""
        status_counts = self.repository.count_by_status()
        total_items = sum(status_counts.values())
        return {
            "total": total_items,
            "available": status_counts.get(EquipmentStatus.AVAILABLE, 0),
            "rented": status_counts.get(EquipmentStatus.RENTED, 0),
            "in_service": status_counts.get(EquipmentStatus.IN_SERVICE, 0),
            "retired": status_counts.get(EquipmentStatus.RETIRED, 0),
        }

    def create_item(
        self,
        inventory_number: str,
        name: str,
        category: EquipmentCategory,
        size: str,
        year_of_purchase: int,
        daily_rate: float,
        condition: EquipmentCondition = EquipmentCondition.GOOD,
        status: EquipmentStatus = EquipmentStatus.AVAILABLE,
        note: Optional[str] = None
    ) -> EquipmentItem:
        # Byznys pravidlo: Unikátnost inventárního čísla
        inv_clean = inventory_number.strip().upper()
        existing = self.repository.get_by_inventory_number(inv_clean)
        if existing:
            raise InventoryNumberAlreadyExistsException(
                f"Inventární číslo '{inv_clean}' je již obsazeno kusem: {existing.name}."
            )

        if daily_rate < 0:
            raise BusinessRuleViolationException("Denní sazba půjčovného nesmí být záporná.")

        item = EquipmentItem(
            inventory_number=inv_clean,
            name=name.strip(),
            category=category,
            size=size.strip(),
            year_of_purchase=year_of_purchase,
            daily_rate=daily_rate,
            condition=condition,
            status=status,
            note=note.strip() if note else None
        )
        return self.repository.create(item)

    def change_status(
        self,
        item_id: int,
        new_status: EquipmentStatus,
        note: Optional[str] = None
    ) -> EquipmentItem:
        item = self.get_item(item_id)

        # Byznys pravidlo: Vyřazený kus nelze aktivovat bez administrativního zásahu
        if item.status == EquipmentStatus.RETIRED and new_status != EquipmentStatus.RETIRED:
            raise BusinessRuleViolationException("Vyřazený kus (RETIRED) nelze vrátit přímo do oběhu.")

        # Byznys pravidlo klienta: Kus v servisu nelze přímo půjčit!
        if item.status == EquipmentStatus.IN_SERVICE and new_status == EquipmentStatus.RENTED:
            raise BusinessRuleViolationException(
                f"Kus {item.inventory_number} je v servisu a nelze jej přímo zapůjčit! Musí být nejdříve ukončen servis."
            )

        item.status = new_status
        if note:
            item.note = note.strip()

        return self.repository.update(item)

    def send_to_service(self, item_id: int, reason: str) -> EquipmentItem:
        """Přesune kus do servisu a zaznamená důvod."""
        item = self.get_item(item_id)
        if item.status == EquipmentStatus.RENTED:
            raise BusinessRuleViolationException("Kus je aktuálně zapůjčen u zákazníka, nelze jej poslat do servisu.")
        
        item.status = EquipmentStatus.IN_SERVICE
        item.note = f"Do servisu: {reason.strip()}"
        return self.repository.update(item)

    def return_from_service(
        self,
        item_id: int,
        condition: EquipmentCondition = EquipmentCondition.GOOD,
        service_note: Optional[str] = None
    ) -> EquipmentItem:
        """Ukončí servis a vrátí kus do dostupného fondu k půjčování."""
        item = self.get_item(item_id)
        if item.status != EquipmentStatus.IN_SERVICE:
            raise BusinessRuleViolationException(f"Kus {item.inventory_number} se nenachází v servisu.")

        item.status = EquipmentStatus.AVAILABLE
        item.condition = condition
        if service_note:
            item.note = f"Servis dokončen: {service_note.strip()}"
        return self.repository.update(item)

    def delete_item(self, item_id: int) -> None:
        """Smaže kus – povoleno pouze pokud nebyl nikdy půjčen nebo byl chybně zaevidován."""
        item = self.get_item(item_id)
        if item.status == EquipmentStatus.RENTED:
            raise BusinessRuleViolationException("Nelze smazat kus, který je právě zapůjčen!")
        self.repository.delete(item)
