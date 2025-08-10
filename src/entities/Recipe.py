from typing import Optional
from typing import Self

from src.entities.Ingredient import Ingredient
from src.entities.Macros import Macros
from src.utils.Constants import Constants
from src.utils.QuantityUnit import QuantityUnit
from src.utils.Utils import Utils


class Recipe:
    """
    Recipe represents a cookbook recipe. It is a convenient way to access the metadata of a given recipe.
    """

    def __init__(self,
                 name: str,
                 recipe_type: str,
                 ingredients: list[Ingredient | Self],
                 instructions: list[str],
                 date_added: Optional[str] = None,
                 source: Optional[str] = None,
                 meal: Optional[str] = None,
                 seasons: Optional[list[str]] = None,
                 portions: int = QuantityUnit.DEFAULT_NB_PORTIONS.value,
                 quantity: int = 1,
                 tags: Optional[list[str]] = None):
        self._name: str = name
        self._recipe_type: str = recipe_type
        self._date_added: Optional[str] = date_added if date_added else None
        self._source: Optional[str] = source
        self._meal: Optional[str] = meal if meal else None
        self._macros = Macros()

        if isinstance(seasons, list):
            self._seasons: list[str] = seasons
        elif seasons is None:
            self._seasons: list[str] = []

        self._portions: int = portions

        if isinstance(tags, list):
            self._tags: list[str] = tags
        elif tags is None:
            self._tags: list[str] = []

        self._ingredients: list[Ingredient | Self] = ingredients
        self._instructions: list[str] = instructions
        self._quantity = quantity

    def get_name(self) -> str:
        return self._name

    def get_recipe_type(self) -> str:
        return self._recipe_type

    def get_meal(self) -> str:
        return self._meal

    def get_seasons(self) -> list[str]:
        return self._seasons

    def get_portions(self) -> int:
        return self._portions

    def get_tags(self) -> list[str]:
        return self._tags

    def get_ingredients(self) -> list[Ingredient]:
        return self._ingredients

    def get_macros(self) -> Macros:
        return self._macros

    def set_macros(self, macros: Macros):
        self._macros = macros

    def get_quantity(self) -> int:
        return self._quantity

    def set_quantity(self, quantity: int):
        self._quantity = quantity

    def compute_macros(self, quantity: int = 1):
        """
        Assign to self.macros a Macro object containing the sum of all the macros of the ingredients in
        the recipe. This total can be multiplied by quantity if the recipe is used as an ingredient in another.
        """

        macros = Macros()
        for i in self._ingredients:
            macros += i.get_macros()

        self._macros = macros * quantity

    def get_ingredients_list_by_aisle(self) -> dict[str, list[str]]:
        """
        :return: the ingredients as groceries list lines, grouped by aisle
        """

        ingredients_by_aisle = {}
        for ingredient in self._ingredients:
            if isinstance(ingredient, Recipe):
                recipe_list = ingredient.get_ingredients_list_by_aisle()
                for key in recipe_list.keys():
                    recipe_list[key] = [
                        f"{sub_ingredient}<sup>{Constants.SOURCE_RECIPE_ARROW}==[[{self._name}]]==</sup>"
                        for sub_ingredient in recipe_list[key]]
                ingredients_by_aisle = Utils.merge_dicts(ingredients_by_aisle, recipe_list)
                continue

            if ingredient.get_aisle() not in ingredients_by_aisle.keys():
                ingredients_by_aisle[ingredient.get_aisle()] = []
            ingredients_by_aisle[ingredient.get_aisle()].append(ingredient.ingredient_line_to_str(self._name))

        return ingredients_by_aisle

    @staticmethod
    def filter_recipe_by_name(recipe_name: str, recipes: list["Recipe"]) -> Optional["Recipe"]:
        """
        :return: the matching recipe object, given a name
        """

        return next(filter(lambda recipe: recipe.get_name() == recipe_name, recipes), None)

    def get_macros_as_markdown_table_line(self):
        """
        Return a Markdown table line containing the total macros of the recipe per portion
        | Recette | Énergie | Protéines | Lipides | Glucides |
        |:--------|:-------:|:---------:|:-------:|:--------:|
        | recipes | energy  | proteins  | lipids  |  carbs   | <--- returns this
        """
        energy = round(self._macros.get_energy() / self._portions)
        proteins = round(self._macros.get_proteins() / self._portions)
        lipids = round(self._macros.get_lipids() / self._portions)
        carbs = round(self._macros.get_carbs() / self._portions)

        return f"| [[{self._name}]] | {energy} | {proteins} | {lipids} | {carbs} |"

    def to_dict(self) -> dict:
        """
        :returns: a dictionary export compatible with the Waistline application format. Every recipe is categorised by
        its meal in the application.
        """

        return {
            "brand": self._meal,
            "name": self._name,
            "nutrition": {
                "calories": round(self._macros.get_energy() / self._portions),
                "carbohydrates": round(self._macros.get_carbs() / self._portions),
                "fat": round(self._macros.get_lipids() / self._portions),
                "proteins": round(self._macros.get_proteins() / self._portions),
            },
            "portion": 1,  # macros are always for one portion of the recipe
            "uniqueId": self._name,
            "unit": "unit"
        }
