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
                 piece_to_g_ratio: float = QuantityUnit.INVALID_PIECE_TO_G_RATIO.value,
                 macros: Macros = Macros(1, 1, 1, 1),
                 ingredient_line: str = "",
                 aisle: str = Constants.UNCLASSIFIED_AISLE,
                 ):
        self._logger = logging.getLogger(__name__)
        self._name: str = name
        self._quantity: float = quantity
        self._quantity_unit: QuantityUnit = quantity_unit
        self._piece_to_g_ratio: float = piece_to_g_ratio
        self._macros: Macros = macros
        self._ingredient_line: str = ingredient_line
        self._aisle: str = aisle

    def get_name(self) -> str:
        return self._name

    def set_name(self, name: str):
        self._name = name

    def set_quantity(self, quantity: float):
        self._quantity = quantity

    def get_quantity_unit(self) -> QuantityUnit:
        return self._quantity_unit

    def set_quantity_unit(self, quantity_unit: QuantityUnit):
        self._quantity_unit = quantity_unit

    def get_piece_to_g_ratio(self) -> float:
        return self._piece_to_g_ratio

    def get_macros(self) -> Macros:
        return self._macros

    def set_ingredient_line(self, ingredient_line):
        self._ingredient_line = ingredient_line

    def get_aisle(self) -> str:
        return self._aisle

    @staticmethod
    def from_name(recipe_ingredient_name: str, base_ingredients: list["Ingredient"]):
        """
        :param recipe_ingredient_name: without the quantity or the unit
        :param base_ingredients
        :return: an Ingredient object with the data of the best matching base ingredient in the provided list
        """

        ingredients_candidates = []
        for base_ingredient in base_ingredients:
            if base_ingredient._name.lower() in recipe_ingredient_name.lower():
                ingredients_candidates.append(base_ingredient)
        if not ingredients_candidates:
            return None

        # keep the match with the most characters
        return copy.deepcopy(sorted(ingredients_candidates, key=lambda igr: len(igr._name))[-1])

    def compute_macros_from_quantity(self):
        """
        Affect to the self.macros attribute a Macro object containing the macros of the ingredient, given the macros of
        the associated base ingredient and the quantity of the ingredient.
        """

        if self._quantity_unit in QuantityUnit.PIECE.value or self._quantity_unit == QuantityUnit.VOID:
            self._macros = self._macros * self._quantity * self._piece_to_g_ratio / Macros.REFERENCE_QUANTITY
            return
        match self._quantity_unit:
            case QuantityUnit.G:
                self._macros = self._macros * self._quantity / Macros.REFERENCE_QUANTITY
            case QuantityUnit.KG:
                self._macros = self._macros * self._quantity * QuantityUnit.KG_TO_G_RATIO.value / Macros.REFERENCE_QUANTITY
            case QuantityUnit.ML:
                self._macros = self._macros * self._quantity * QuantityUnit.ML_TO_G_RATIO.value / Macros.REFERENCE_QUANTITY
            case QuantityUnit.CL:
                self._macros = self._macros * self._quantity * QuantityUnit.CL_TO_G_RATIO.value / Macros.REFERENCE_QUANTITY
            case QuantityUnit.L:
                self._macros = self._macros * self._quantity * QuantityUnit.L_TO_G_RATIO.value / Macros.REFERENCE_QUANTITY
            case QuantityUnit.CC:
                self._macros = self._macros * self._quantity * QuantityUnit.CC_TO_G_RATIO.value / Macros.REFERENCE_QUANTITY
            case QuantityUnit.CS:
                self._macros = self._macros * self._quantity * QuantityUnit.CS_TO_G_RATIO.value / Macros.REFERENCE_QUANTITY
            case _:
                self._logger.warning(f"unit {self._quantity_unit} not recognised for ingredient {self._name}")

    def ingredient_line_to_str(self, recipe_name: str) -> str:
        """
        :return: an ingredient line in the format 'ingredient ---> [[recipe_name]]
        """

        return (f"{self._ingredient_line}<sup>{Constants.SOURCE_RECIPE_ARROW}"
                f"[[{recipe_name}]]</sup>")

    def to_dict(self) -> dict:
        """
        :returns: a dictionary export compatible with the Waistline application format. Every ingredient of ingredients.yaml is
        categorised by its aisle in the application.
        """

        if self._piece_to_g_ratio == QuantityUnit.INVALID_PIECE_TO_G_RATIO.value:
            energy = self._macros.get_energy() / Macros.REFERENCE_QUANTITY
            proteins = self._macros.get_proteins() / Macros.REFERENCE_QUANTITY
            lipids = self._macros.get_lipids() / Macros.REFERENCE_QUANTITY
            carbs = self._macros.get_carbs() / Macros.REFERENCE_QUANTITY
            unit = QuantityUnit.PIECE.value.PIECE.value
        else:
            energy = self._macros.get_energy() / Macros.REFERENCE_QUANTITY * self._piece_to_g_ratio
            proteins = self._macros.get_proteins() / Macros.REFERENCE_QUANTITY * self._piece_to_g_ratio
            lipids = self._macros.get_lipids() / Macros.REFERENCE_QUANTITY * self._piece_to_g_ratio
            carbs = self._macros.get_carbs() / Macros.REFERENCE_QUANTITY * self._piece_to_g_ratio
            unit = QuantityUnit.G.value

        return {
            "brand": self._aisle,
            "name": self._name,
            "nutrition": {
                "calories": energy,
                "carbohydrates": proteins,
                "fat": lipids,
                "proteins": carbs,
            },
            "portion": 1,  # macros are always for one piece, or for Macros.REFERENCE_QUANTITYg
            "uniqueId": self._name,
            "unit": unit
        }
