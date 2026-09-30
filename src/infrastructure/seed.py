from sqlalchemy.orm import Session
from src.domain.models import EquipmentItem
from src.domain.enums import EquipmentCategory, EquipmentStatus, EquipmentCondition

INITIAL_EQUIPMENT_DATA = [
    # Sjezdové lyže
    {
        "inventory_number": "SKI-101",
        "name": "Atomic Redster G9",
        "category": EquipmentCategory.SKIS,
        "size": "170 cm",
        "year_of_purchase": 2024,
        "condition": EquipmentCondition.GOOD,
        "status": EquipmentStatus.AVAILABLE,
        "daily_rate": 390.0,
        "note": "Po velkém servisu hran na podzim 2025"
    },
    {
        "inventory_number": "SKI-102",
        "name": "Atomic Redster G9",
        "category": EquipmentCategory.SKIS,
        "size": "170 cm",
        "year_of_purchase": 2024,
        "condition": EquipmentCondition.GOOD,
        "status": EquipmentStatus.RENTED,
        "daily_rate": 390.0,
        "note": "Druhý totožný pár, aktuálně zapůjčeno do neděle"
    },
    {
        "inventory_number": "SKI-103",
        "name": "Salomon S/Max 10",
        "category": EquipmentCategory.SKIS,
        "size": "165 cm",
        "year_of_purchase": 2023,
        "condition": EquipmentCondition.GOOD,
        "status": EquipmentStatus.AVAILABLE,
        "daily_rate": 360.0,
        "note": "Oblíbené univerzálky pro pokročilé"
    },
    {
        "inventory_number": "SKI-104",
        "name": "Head Supershape e-Magnum",
        "category": EquipmentCategory.SKIS,
        "size": "177 cm",
        "year_of_purchase": 2022,
        "condition": EquipmentCondition.WORN,
        "status": EquipmentStatus.IN_SERVICE,
        "daily_rate": 340.0,
        "note": "Rýha na skluznici u patky, čeká na zalití kofixem"
    },

    # Snowboardy
    {
        "inventory_number": "SNB-201",
        "name": "Salomon Craft All-Mountain",
        "category": EquipmentCategory.SNOWBOARDS,
        "size": "156 cm",
        "year_of_purchase": 2024,
        "condition": EquipmentCondition.NEW,
        "status": EquipmentStatus.AVAILABLE,
        "daily_rate": 370.0,
        "note": "Nové vázání Rhythm L"
    },
    {
        "inventory_number": "SNB-202",
        "name": "Burton Custom Camber",
        "category": EquipmentCategory.SNOWBOARDS,
        "size": "158 cm",
        "year_of_purchase": 2023,
        "condition": EquipmentCondition.GOOD,
        "status": EquipmentStatus.RENTED,
        "daily_rate": 410.0,
        "note": "Vypůjčeno pro víkendový kurz"
    },

    # Lyžařské boty
    {
        "inventory_number": "BOT-301",
        "name": "Dalbello Panterra 100",
        "category": EquipmentCategory.BOOTS,
        "size": "EU 43 (280 mm)",
        "year_of_purchase": 2023,
        "condition": EquipmentCondition.GOOD,
        "status": EquipmentStatus.AVAILABLE,
        "daily_rate": 180.0,
        "note": "GripWalk podrážka, vložka vysušena"
    },
    {
        "inventory_number": "BOT-302",
        "name": "Salomon S/Pro 90 W",
        "category": EquipmentCategory.BOOTS,
        "size": "EU 39 (250 mm)",
        "year_of_purchase": 2024,
        "condition": EquipmentCondition.NEW,
        "status": EquipmentStatus.AVAILABLE,
        "daily_rate": 190.0,
        "note": "Dámský model, bez vad"
    },
    {
        "inventory_number": "BOT-303",
        "name": "Atomic Hawx Prime 110",
        "category": EquipmentCategory.BOOTS,
        "size": "EU 45 (295 mm)",
        "year_of_purchase": 2022,
        "condition": EquipmentCondition.WORN,
        "status": EquipmentStatus.IN_SERVICE,
        "daily_rate": 180.0,
        "note": "Uvolněná horní přezka, oprava v dílně"
    },

    # Hůlky
    {
        "inventory_number": "POL-401",
        "name": "Leki Spark S",
        "category": EquipmentCategory.POLES,
        "size": "125 cm",
        "year_of_purchase": 2024,
        "condition": EquipmentCondition.GOOD,
        "status": EquipmentStatus.AVAILABLE,
        "daily_rate": 60.0,
        "note": "Systém Trigger S"
    },

    # Letní vybavení - Lodě a vesty
    {
        "inventory_number": "BOAT-501",
        "name": "Kanoe Vydra Plast",
        "category": EquipmentCategory.BOATS,
        "size": "2-místná (450 cm)",
        "year_of_purchase": 2023,
        "condition": EquipmentCondition.GOOD,
        "status": EquipmentStatus.AVAILABLE,
        "daily_rate": 350.0,
        "note": "Plastová osvědčená kanoe včetně 2 dřevěných pádel"
    },
    {
        "inventory_number": "BOAT-502",
        "name": "Raft Colorado 450",
        "category": EquipmentCategory.BOATS,
        "size": "6-místný",
        "year_of_purchase": 2022,
        "condition": EquipmentCondition.GOOD,
        "status": EquipmentStatus.AVAILABLE,
        "daily_rate": 750.0,
        "note": "Včetně nožní pumpy a lepicí sady"
    },
    {
        "inventory_number": "VES-601",
        "name": "Záchranná vesta Hiko Baby",
        "category": EquipmentCategory.VESTS,
        "size": "Dětská XS (do 20 kg)",
        "year_of_purchase": 2024,
        "condition": EquipmentCondition.NEW,
        "status": EquipmentStatus.AVAILABLE,
        "daily_rate": 50.0,
        "note": "S límcem a píšťalkou, certifikace EN ISO 12402"
    },
    {
        "inventory_number": "VES-602",
        "name": "Záchranná vesta Hiko Swift",
        "category": EquipmentCategory.VESTS,
        "size": "L/XL (60-90 kg)",
        "year_of_purchase": 2023,
        "condition": EquipmentCondition.GOOD,
        "status": EquipmentStatus.AVAILABLE,
        "daily_rate": 60.0,
        "note": "Univerzální vodácká vesta"
    }
]

def seed_database_if_empty(db: Session) -> int:
    """Pokud je databáze prázdná, naplní ji realistickými syntetickými daty."""
    existing_count = db.query(EquipmentItem).count()
    if existing_count > 0:
        return 0

    for item_data in INITIAL_EQUIPMENT_DATA:
        item = EquipmentItem(**item_data)
        db.add(item)
    
    db.commit()
    return len(INITIAL_EQUIPMENT_DATA)
