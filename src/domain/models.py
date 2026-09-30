from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, Float, DateTime, Enum as SQLEnum
from sqlalchemy.orm import declarative_base

from src.domain.enums import EquipmentCategory, EquipmentStatus, EquipmentCondition

Base = declarative_base()

class EquipmentItem(Base):
    """
    Klíčová entita inventárního kusu vybavení v půjčovně Hory a voda.
    Splňuje pravidlo: Dva totožné páry lyží tvoří dva samostatné záznamy s unikátním inventárním číslem.
    """
    __tablename__ = "equipment_items"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    inventory_number = Column(String(50), unique=True, index=True, nullable=False)
    name = Column(String(100), nullable=False)
    category = Column(SQLEnum(EquipmentCategory, native_enum=False), nullable=False, index=True)
    size = Column(String(30), nullable=False)
    year_of_purchase = Column(Integer, nullable=False)
    condition = Column(SQLEnum(EquipmentCondition, native_enum=False), default=EquipmentCondition.GOOD, nullable=False)
    status = Column(SQLEnum(EquipmentStatus, native_enum=False), default=EquipmentStatus.AVAILABLE, nullable=False, index=True)
    daily_rate = Column(Float, nullable=False)
    note = Column(String(255), nullable=True)
    
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc), nullable=False)

    def __repr__(self) -> str:
        return f"<EquipmentItem(inv='{self.inventory_number}', name='{self.name}', status='{self.status}')>"
