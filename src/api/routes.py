from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from src.infrastructure.database import get_db
from src.infrastructure.repositories import EquipmentRepository
from src.services.equipment_service import (
    EquipmentService,
    ItemNotFoundException,
    InventoryNumberAlreadyExistsException,
    BusinessRuleViolationException
)
from src.domain.enums import EquipmentStatus, EquipmentCategory
from src.api.schemas import (
    EquipmentCreateSchema,
    EquipmentResponseSchema,
    EquipmentStatusUpdateSchema,
    ServiceActionSchema,
    DashboardSummaryResponse
)

router = APIRouter(prefix="/api/equipment", tags=["Equipment"])

def get_equipment_service(db: Session = Depends(get_db)) -> EquipmentService:
    repository = EquipmentRepository(db)
    return EquipmentService(repository)

@router.get("/summary", response_model=DashboardSummaryResponse, summary="Přehled pro ranní pultový dashboard")
def get_dashboard_summary(service: EquipmentService = Depends(get_equipment_service)):
    """Vrací agregovaný stav skladu: celkem, volné, půjčené, v servisu."""
    return service.get_dashboard_summary()

@router.get("", response_model=List[EquipmentResponseSchema], summary="Seznam vybavení s filtry")
def list_equipment(
    status: Optional[EquipmentStatus] = Query(None, description="Filtrovat dle stavu"),
    category: Optional[EquipmentCategory] = Query(None, description="Filtrovat dle kategorie"),
    search: Optional[str] = Query(None, description="Hledat v inv. čísle, názvu či velikosti"),
    service: EquipmentService = Depends(get_equipment_service)
):
    return service.list_items(status=status, category=category, search=search)

@router.get("/{item_id}", response_model=EquipmentResponseSchema, summary="Detail konkrétního kusu")
def get_equipment_item(item_id: int, service: EquipmentService = Depends(get_equipment_service)):
    try:
        return service.get_item(item_id)
    except ItemNotFoundException as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))

@router.post("", response_model=EquipmentResponseSchema, status_code=status.HTTP_201_CREATED, summary="Zaevidovat nový kus")
def create_equipment_item(
    payload: EquipmentCreateSchema,
    service: EquipmentService = Depends(get_equipment_service)
):
    try:
        return service.create_item(
            inventory_number=payload.inventory_number,
            name=payload.name,
            category=payload.category,
            size=payload.size,
            year_of_purchase=payload.year_of_purchase,
            daily_rate=payload.daily_rate,
            condition=payload.condition,
            status=payload.status,
            note=payload.note
        )
    except InventoryNumberAlreadyExistsException as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))
    except BusinessRuleViolationException as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

@router.patch("/{item_id}/status", response_model=EquipmentResponseSchema, summary="Změna stavu kusu")
def change_equipment_status(
    item_id: int,
    payload: EquipmentStatusUpdateSchema,
    service: EquipmentService = Depends(get_equipment_service)
):
    try:
        return service.change_status(item_id, payload.status, payload.note)
    except ItemNotFoundException as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except BusinessRuleViolationException as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

@router.post("/{item_id}/send-to-service", response_model=EquipmentResponseSchema, summary="Odeslat kus do servisu")
def send_to_service(
    item_id: int,
    payload: ServiceActionSchema,
    service: EquipmentService = Depends(get_equipment_service)
):
    try:
        return service.send_to_service(item_id, payload.reason_or_work)
    except ItemNotFoundException as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except BusinessRuleViolationException as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

@router.post("/{item_id}/return-from-service", response_model=EquipmentResponseSchema, summary="Vrátit kus ze servisu na pult")
def return_from_service(
    item_id: int,
    payload: ServiceActionSchema,
    service: EquipmentService = Depends(get_equipment_service)
):
    try:
        return service.return_from_service(
            item_id=item_id,
            condition=payload.condition_after,
            service_note=payload.reason_or_work
        )
    except ItemNotFoundException as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except BusinessRuleViolationException as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

@router.delete("/{item_id}", status_code=status.HTTP_204_NO_CONTENT, summary="Smazat chybně zadaný kus")
def delete_equipment_item(item_id: int, service: EquipmentService = Depends(get_equipment_service)):
    try:
        service.delete_item(item_id)
    except ItemNotFoundException as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except BusinessRuleViolationException as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
