from enum import Enum

from script.Macros import Macros


class Ingredient:
    class Unit(Enum):
        G = "g"
        CL = "cl"
        NONE = ""

    def __init__(self,
                 name: str,
                 quantity: float | None = None,
                 quantity_unit: Unit = Unit.NONE,
                 macros: Macros = Macros()
                 ):
        self.name: str = name
        self.quantity: float | None = quantity
        self.quantity_unit: Ingredient.Unit = quantity_unit
        self.macros: Macros = macros
