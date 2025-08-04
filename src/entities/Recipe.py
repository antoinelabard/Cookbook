from typing import Optional
from typing import Self

from src.entities.Ingredient import Ingredient
from src.entities.Macros import Macros
from src.utils.Constants import Constants
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
                 portions: int = 4,
                 tags: Optional[list[str]] = None):
        self.name: str = name
        self.recipe_type: str = recipe_type
        self.date_added: Optional[str] = date_added if date_added else None
        self.source: Optional[str] = source
        self.meal: Optional[str] = meal if meal else None

        if isinstance(seasons, list):
            self.seasons: list[str] = seasons
        elif seasons is None:
            self.seasons: list[str] = []

        self.portions: float = portions

        if isinstance(tags, list):
            self.tags: list[str] = tags
        elif tags is None:
            self.tags: list[str] = []

        self.ingredients: list[Ingredient | Self] = ingredients
        self.instructions: list[str] = instructions

        self.macros: Macros = self.compute_recipe_macros()

    def compute_recipe_macros(self):
        """
        :returns: to the self.macros attribute a Macro object containing the sum of all the macros of the ingredients in
        the recipe
        """

        macros = Macros()
        for i in self.ingredients:
            macros += i.macros

        return macros / self.portions

    def get_ingredients_list_by_aisle(self) -> dict[str, list[str]]:
        """
        :return: the ingredients as groceries list lines, grouped by aisle
        """

        ingredients_by_aisle = {}
        for ingredient in self.ingredients:
            if isinstance(ingredient, Recipe):
                recipe_list = ingredient.get_ingredients_list_by_aisle()
                for key in recipe_list.keys():
                    recipe_list[key] = [
                        f"{sub_ingredient}<sup>{Constants.SOURCE_RECIPE_ARROW}==[[{self.name}]]==</sup>"
                        for sub_ingredient in recipe_list[key]]
                ingredients_by_aisle = Utils.merge_dicts(ingredients_by_aisle, recipe_list)
                continue

            if ingredient.aisle not in ingredients_by_aisle.keys():
                ingredients_by_aisle[ingredient.aisle] = []
            ingredients_by_aisle[ingredient.aisle].append(ingredient.ingredient_line_to_str(self.name))

        return ingredients_by_aisle

    @staticmethod
    def filter_recipe_by_name(recipe_name: str, recipes: list["Recipe"]) -> Optional["Recipe"]:
        """
        :return: the matching recipe object, given a name
        """

        return next(filter(lambda recipe: recipe.name == recipe_name, recipes), None)
