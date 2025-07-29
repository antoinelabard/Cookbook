import logging

from script.entities.Macros import Macros
from script.utils.QuantityUnit import QuantityUnit


class Ingredient:

    CL_TO_G_RATIO = 10
    ML_TO_G_RATIO = 1

    def __init__(self,
                 name: str,
                 quantity: float = 0,
                 quantity_unit: QuantityUnit = QuantityUnit.G,
                 piece_to_g_ratio = 1,
                 macros: Macros = Macros(1, 1, 1, 1)
                 ):
        self.logger = logging.getLogger(__name__)
        self.logger.addHandler(logging.StreamHandler())
        self.name: str = name
        self.quantity: float = quantity
        self.quantity_unit: QuantityUnit = quantity_unit
        self.piece_to_g_ratio = piece_to_g_ratio
        self.macros: Macros = macros

    def compute_macros_from_quantity(self):
        match self.quantity_unit:
            case QuantityUnit.G:
                self.macros = self.macros * self.quantity / Macros.REFERENCE_QUANTITY
            case QuantityUnit.CL:
                self.macros = self.macros * self.quantity * self.CL_TO_G_RATIO / Macros.REFERENCE_QUANTITY
            case QuantityUnit.ML:
                self.macros = self.macros * self.quantity * self.ML_TO_G_RATIO / Macros.REFERENCE_QUANTITY
            case QuantityUnit.PIECE:
                self.macros = self.macros * self.quantity * self.piece_to_g_ratio / Macros.REFERENCE_QUANTITY
            case _:
                self.logger.warning(f"unit {self.quantity_unit} not recognised for ingredient {self.name}")
