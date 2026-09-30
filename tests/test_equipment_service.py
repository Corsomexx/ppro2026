import pytest
from src.domain.enums import EquipmentCategory, EquipmentStatus, EquipmentCondition
from src.services.equipment_service import (
    EquipmentService,
    InventoryNumberAlreadyExistsException,
    BusinessRuleViolationException,
    ItemNotFoundException,
)

def test_create_equipment_item_success(equipment_service: EquipmentService):
    item = equipment_service.create_item(
        inventory_number="SKI-999",
        name="Atomic Redster X9",
        category=EquipmentCategory.SKIS,
        size="175 cm",
        year_of_purchase=2024,
        daily_rate=450.0,
        condition=EquipmentCondition.NEW
    )
    assert item.id is not None
    assert item.inventory_number == "SKI-999"
    assert item.status == EquipmentStatus.AVAILABLE
    assert item.daily_rate == 450.0

def test_duplicate_inventory_number_raises_exception(equipment_service: EquipmentService):
    equipment_service.create_item(
        inventory_number="SNB-001",
        name="Salomon Craft",
        category=EquipmentCategory.SNOWBOARDS,
        size="156 cm",
        year_of_purchase=2023,
        daily_rate=350.0
    )
    
    with pytest.raises(InventoryNumberAlreadyExistsException):
        equipment_service.create_item(
            inventory_number="SNB-001",
            name="Jiný kus s týmž číslem",
            category=EquipmentCategory.SNOWBOARDS,
            size="156 cm",
            year_of_purchase=2023,
            daily_rate=350.0
        )

def test_negative_daily_rate_raises_exception(equipment_service: EquipmentService):
    with pytest.raises(BusinessRuleViolationException):
        equipment_service.create_item(
            inventory_number="SKI-NEG",
            name="Vadná cena",
            category=EquipmentCategory.SKIS,
            size="170 cm",
            year_of_purchase=2024,
            daily_rate=-100.0
        )

def test_send_to_service_and_return(equipment_service: EquipmentService):
    item = equipment_service.create_item(
        inventory_number="SKI-SERV",
        name="Head Supershape",
        category=EquipmentCategory.SKIS,
        size="170 cm",
        year_of_purchase=2024,
        daily_rate=400.0
    )
    assert item.status == EquipmentStatus.AVAILABLE

    # Odeslání do servisu
    updated = equipment_service.send_to_service(item.id, "Servis skluznice")
    assert updated.status == EquipmentStatus.IN_SERVICE
    assert "Servis skluznice" in updated.note

    # Obchodní pravidlo: Kus v servisu nelze přímo zapůjčit
    with pytest.raises(BusinessRuleViolationException):
        equipment_service.change_status(item.id, EquipmentStatus.RENTED)

    # Návrat ze servisu
    returned = equipment_service.return_from_service(
        item.id,
        condition=EquipmentCondition.GOOD,
        service_note="Hrany a vosk hotovo"
    )
    assert returned.status == EquipmentStatus.AVAILABLE
    assert returned.condition == EquipmentCondition.GOOD

def test_dashboard_summary_calculation(equipment_service: EquipmentService):
    equipment_service.create_item("A1", "Lyže 1", EquipmentCategory.SKIS, "170", 2024, 300, status=EquipmentStatus.AVAILABLE)
    equipment_service.create_item("A2", "Lyže 2", EquipmentCategory.SKIS, "170", 2024, 300, status=EquipmentStatus.RENTED)
    equipment_service.create_item("A3", "Lyže 3", EquipmentCategory.SKIS, "170", 2024, 300, status=EquipmentStatus.IN_SERVICE)

    summary = equipment_service.get_dashboard_summary()
    assert summary["total"] == 3
    assert summary["available"] == 1
    assert summary["rented"] == 1
    assert summary["in_service"] == 1
