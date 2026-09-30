from enum import Enum

class EquipmentCategory(str, Enum):
    SKIS = "Sjezdové lyže"
    CROSS_COUNTRY = "Běžky"
    SNOWBOARDS = "Snowboardy"
    BOOTS = "Lyžařské boty"
    POLES = "Hůlky"
    BOATS = "Kanoe a rafty"
    VESTS = "Záchranné vesty"

class EquipmentStatus(str, Enum):
    AVAILABLE = "Dostupné"
    RENTED = "Vypůjčeno"
    IN_SERVICE = "V servisu"
    RETIRED = "Vyřazeno"

class EquipmentCondition(str, Enum):
    NEW = "Nové"
    GOOD = "Běžné opotřebení"
    WORN = "Značné opotřebení"
    DAMAGED = "Poškozeno"
