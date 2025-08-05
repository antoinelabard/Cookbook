import copy
import logging

from src.entities.Macros import Macros
from src.utils.Constants import Constants
from src.utils.QuantityUnit import QuantityUnit


class Ingredient:

    def __init__(self,
                 name: str,
                 quantity: float = 0,
                 quantity_unit: QuantityUnit = QuantityUnit.G,
                 piece_to_g_ratio: float = -1,
                 macros: Macros = Macros(1, 1, 1, 1),
                 ingredient_line: str = "",
                 aisle: str = "Unclassified"
                 ):
        self.logger = logging.getLogger(__name__)
        self.name: str = name
        self.quantity: float = quantity
        self.quantity_unit: QuantityUnit = quantity_unit
        self.piece_to_g_ratio: float = piece_to_g_ratio
        self.macros: Macros = macros
        self.ingredient_line: str = ingredient_line
        self.aisle = aisle

    @staticmethod
    def from_name(recipe_ingredient_name: str, base_ingredients: list["Ingredient"]):
        """
        :param recipe_ingredient_name: without the quantity or the unit
        :param base_ingredients
        :return: an Ingredient object with the data of the best matching base ingredient in the provided list
        """

        ingredients_candidates = []
        for base_ingredient in base_ingredients:
            if base_ingredient.name.lower() in recipe_ingredient_name.lower():
                ingredients_candidates.append(base_ingredient)
        if not ingredients_candidates:
            return None

        # keep the match with the most characters
        return copy.deepcopy(sorted(ingredients_candidates, key=lambda igr: len(igr.name))[-1])

    def compute_macros_from_quantity(self):
        """
        Affect to the self.macros attribute a Macro object containing the macros of the ingredient, given the macros of
        the associated base ingredient and the quantity of the ingredient.
        """

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

    def ingredient_line_to_str(self, recipe_name: str) -> str:
        """
        :return: an ingredient line in the format 'ingredient ---> [[recipe_name]]
        """

        return (f"{self.ingredient_line}<sup>{Constants.SOURCE_RECIPE_ARROW}"
                f"[[{recipe_name}]]</sup>")
