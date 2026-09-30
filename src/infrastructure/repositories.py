from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import or_

from src.domain.models import EquipmentItem
from src.domain.enums import EquipmentStatus, EquipmentCategory

class EquipmentRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, item_id: int) -> Optional[EquipmentItem]:
        return self.db.query(EquipmentItem).filter(EquipmentItem.id == item_id).first()

    def get_by_inventory_number(self, inventory_number: str) -> Optional[EquipmentItem]:
        return (
            self.db.query(EquipmentItem)
            .filter(EquipmentItem.inventory_number == inventory_number)
            .first()
        )

    def list_all(
        self,
        status: Optional[EquipmentStatus] = None,
        category: Optional[EquipmentCategory] = None,
        search: Optional[str] = None
    ) -> List[EquipmentItem]:
        query = self.db.query(EquipmentItem)

        if status:
            query = query.filter(EquipmentItem.status == status)
        if category:
            query = query.filter(EquipmentItem.category == category)
        if search:
            search_pattern = f"%{search.strip()}%"
            query = query.filter(
                or_(
                    EquipmentItem.inventory_number.ilike(search_pattern),
                    EquipmentItem.name.ilike(search_pattern),
                    EquipmentItem.size.ilike(search_pattern)
                )
            )

        return query.order_by(EquipmentItem.category, EquipmentItem.inventory_number).all()

    def count_by_status(self) -> dict:
        """Agregace pro pultový dashboard rychlého přehledu."""
        items = self.db.query(EquipmentItem.status).all()
        counts = {status: 0 for status in EquipmentStatus}
        for item in items:
            if item[0] in counts:
                counts[item[0]] += 1
        return counts

    def create(self, item: EquipmentItem) -> EquipmentItem:
        self.db.add(item)
        self.db.commit()
        self.db.refresh(item)
        return item

    def update(self, item: EquipmentItem) -> EquipmentItem:
        self.db.commit()
        self.db.refresh(item)
        return item

    def delete(self, item: EquipmentItem) -> None:
        self.db.delete(item)
        self.db.commit()
