from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field, ConfigDict

from src.domain.enums import EquipmentCategory, EquipmentStatus, EquipmentCondition

class EquipmentCreateSchema(BaseModel):
    inventory_number: str = Field(..., description="Lihovkou psané unikátní číslo kusu", json_schema_extra={"example": "SKI-105"})
    name: str = Field(..., description="Název modelu a značka", json_schema_extra={"example": "Atomic Redster G9"})
    category: EquipmentCategory = Field(...)
    size: str = Field(..., description="Délka či velikost", json_schema_extra={"example": "170 cm"})
    year_of_purchase: int = Field(..., ge=1990, le=2030, json_schema_extra={"example": 2024})
    daily_rate: float = Field(..., ge=0, json_schema_extra={"example": 390.0})
    condition: EquipmentCondition = Field(default=EquipmentCondition.GOOD)
    status: EquipmentStatus = Field(default=EquipmentStatus.AVAILABLE)
    note: Optional[str] = Field(None, json_schema_extra={"example": "Nově navoskováno"})

class EquipmentStatusUpdateSchema(BaseModel):
    status: EquipmentStatus = Field(..., description="Nový stav kusu")
    note: Optional[str] = Field(None, description="Doplňující poznámka ke změně")

class ServiceActionSchema(BaseModel):
    reason_or_work: str = Field(..., min_length=2, json_schema_extra={"example": "Oprava vytržené hrany"})
    condition_after: Optional[EquipmentCondition] = Field(default=EquipmentCondition.GOOD)

class EquipmentResponseSchema(BaseModel):
    id: int
    inventory_number: str
    name: str
    category: EquipmentCategory
    size: str
    year_of_purchase: int
    daily_rate: float
    condition: EquipmentCondition
    status: EquipmentStatus
    note: Optional[str]
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)

class DashboardSummaryResponse(BaseModel):
    total: int
    available: int
    rented: int
    in_service: int
    retired: int
