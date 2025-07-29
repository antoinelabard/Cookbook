import logging

from script.entities.Macros import Macros
from script.utils.QuantityUnit import QuantityUnit


class Ingredient:

    def __init__(self,
                 name: str,
                 quantity: float = 0,
                 quantity_unit: QuantityUnit = QuantityUnit.G,
                 piece_to_g_ratio: float = -1,
                 macros: Macros = Macros(1, 1, 1, 1)
                 ):
        self.logger = logging.getLogger(__name__)
        self.logger.addHandler(logging.StreamHandler())
        self.name: str = name
        self.quantity: float = quantity
        self.quantity_unit: QuantityUnit = quantity_unit
        self.piece_to_g_ratio: float = piece_to_g_ratio
        self.macros: Macros = macros

    def compute_macros_from_quantity(self):
        if self.quantity_unit in QuantityUnit.PIECE.value or self.quantity_unit == QuantityUnit.VOID:
            self.macros = self.macros * self.quantity * self.piece_to_g_ratio / Macros.REFERENCE_QUANTITY
            return
        match self.quantity_unit:
            case QuantityUnit.G:
                self.macros = self.macros * self.quantity / Macros.REFERENCE_QUANTITY
            case QuantityUnit.KG:
                self.macros = self.macros * self.quantity * QuantityUnit.KG_TO_G_RATIO.value / Macros.REFERENCE_QUANTITY
            case QuantityUnit.ML:
                self.macros = self.macros * self.quantity * QuantityUnit.ML_TO_G_RATIO.value / Macros.REFERENCE_QUANTITY
            case QuantityUnit.CL:
                self.macros = self.macros * self.quantity * QuantityUnit.CL_TO_G_RATIO.value / Macros.REFERENCE_QUANTITY
            case QuantityUnit.L:
                self.macros = self.macros * self.quantity * QuantityUnit.L_TO_G_RATIO.value / Macros.REFERENCE_QUANTITY
            case QuantityUnit.CC:
                self.macros = self.macros * self.quantity * QuantityUnit.CC_TO_G_RATIO.value / Macros.REFERENCE_QUANTITY
            case QuantityUnit.CS:
                self.macros = self.macros * self.quantity * QuantityUnit.CS_TO_G_RATIO.value / Macros.REFERENCE_QUANTITY
            case _:
                self.logger.warning(f"unit {self.quantity_unit} not recognised for ingredient {self.name}")
