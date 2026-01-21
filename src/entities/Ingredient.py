import copy

from src.entities.Macros import Macros
from src.utils.QuantityUnit import QuantityUnit
from src.utils.Utils import Utils


class Ingredient:
    AISLE = "aisle"
    QUANTITY = "quantity"
    UNCLASSIFIED_AISLE = "Non classé"
    SOURCE_RECIPE_ARROW = " ---> "

    _logger = Utils.get_logger(__name__)

    def __init__(self,
                 name: str,
                 quantity: float = 0,
                 quantity_unit: QuantityUnit = QuantityUnit.G,
                 piece_to_g_ratio: float = QuantityUnit.INVALID_PIECE_TO_G_RATIO.value,
                 macros: Macros = Macros(1, 1, 1, 1),
                 ingredient_line: str = "",
                 aisle: str = UNCLASSIFIED_AISLE,
                 ):
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

    @classmethod
    def from_name(cls, recipe_ingredient_name: str, base_ingredients: list["Ingredient"]) -> "Ingredient":
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
            cls._logger.warning(f"ingredient name {recipe_ingredient_name} not recognised among the base ingredients")
            return Ingredient(
                recipe_ingredient_name
            )

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
        unit_to_g_ratio = 1  # default value when the quantity is in grams
        match self._quantity_unit:
            case QuantityUnit.G:
                unit_to_g_ratio = 1
            case QuantityUnit.KG:
                unit_to_g_ratio =  QuantityUnit.KG_TO_G_RATIO.value
            case QuantityUnit.ML:
                unit_to_g_ratio =  QuantityUnit.ML_TO_G_RATIO.value
            case QuantityUnit.CL:
                unit_to_g_ratio =  QuantityUnit.CL_TO_G_RATIO.value
            case QuantityUnit.L:
                unit_to_g_ratio =  QuantityUnit.L_TO_G_RATIO.value
            case QuantityUnit.CC:
                unit_to_g_ratio =  QuantityUnit.CC_TO_G_RATIO.value
            case QuantityUnit.CS:
                unit_to_g_ratio =  QuantityUnit.CS_TO_G_RATIO.value
            case _:
                Ingredient._logger.warning(f"unit {self._quantity_unit} not recognised for ingredient {self._name}")

        self._macros = self._macros * self._quantity * unit_to_g_ratio / Macros.REFERENCE_QUANTITY

    def ingredient_line_to_str(self, recipe_name: str) -> str:
        """
        :return: an ingredient line in the format 'ingredient ---> [[recipe_name]]
        """

        return (f"{self._ingredient_line}<sup>{Ingredient.SOURCE_RECIPE_ARROW}"
                f"[[{recipe_name}]]</sup>")

    def to_dict(self) -> dict:
        """
        :return: a dictionary export compatible with the Waistline application format. Every ingredient of ingredients.yaml is
        categorized by its aisle in the application.
        """

        if self._piece_to_g_ratio == QuantityUnit.INVALID_PIECE_TO_G_RATIO.value:
            piece_to_g_ratio = 1
            unit = QuantityUnit.G.value
        else:
            piece_to_g_ratio = self._piece_to_g_ratio
            unit = QuantityUnit.PIECE.value.PIECE.value

        energy = self._macros.get_energy() / Macros.REFERENCE_QUANTITY * piece_to_g_ratio
        proteins = self._macros.get_proteins() / Macros.REFERENCE_QUANTITY * piece_to_g_ratio
        fat = self._macros.get_fat() / Macros.REFERENCE_QUANTITY * piece_to_g_ratio
        carbs = self._macros.get_carbs() / Macros.REFERENCE_QUANTITY * piece_to_g_ratio

        return {
            "brand": self._aisle,
            "name": self._name,
            "nutrition": {
                "calories": energy,
                "carbohydrates": proteins,
                "fat": fat,
                "proteins": carbs,
            },
            "portion": 1,  # macros are always for one piece, or for Macros.REFERENCE_QUANTITY
            "uniqueId": self._name,
            "unit": unit
        }
    
    def get_macros_as_markdown_table_line(self, portions: int) -> str:
        """
        Returns a Markdown table line containing the total macros of the recipe per portion
        
        | Ingrédient | Quantité | Énergie | Protéines | Lipides | Glucides |
        |:-----------|:--------:|:-------:|:---------:|:-------:|:--------:|
        |    name    | quantity | energy  | proteins  |   fat   |  carbs   | <--- returns this
        """

        quantity = f"{round(self._quantity / portions)}{self._quantity_unit.value}"
        energy = round(self._macros.get_energy() / portions)
        proteins = round(self._macros.get_proteins() / portions, 1)
        fat = round(self._macros.get_fat() / portions, 1)
        carbs = round(self._macros.get_carbs() / portions, 1)
    
        return f"| {self._name} | {quantity} | {energy} | {proteins} | {fat} | {carbs} |"
