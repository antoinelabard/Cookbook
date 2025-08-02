import re

from src.entities.Recipe import Recipe
from src.utils.QuantityUnit import QuantityUnit

class Utils:
    @staticmethod
    def filter_recipe_by_name(recipe_name: str, recipes: list[Recipe]) -> Recipe:
        return list(filter(lambda recipe: recipe.name == recipe_name, recipes))[0]

    @staticmethod
    def extract_name_and_quantity_from_ingredient_line(recipe_ingredient_str: str)-> tuple[str, int, str]:
        igr_split = recipe_ingredient_str.split(" : ")
        recipe_ingredient_name = igr_split[0] # get the left part of the "ingredient : quantity" line
        recipe_ingredient_quantity = QuantityUnit.DEFAULT_QUANTITY.value
        recipe_ingredient_quantity_unit = ""
        if len(igr_split) == 2:  # get the right part of the "ingredient : quantity" line
            recipe_ingredient_quantity = int(re.findall(r'\d+', igr_split[1])[0])
            recipe_ingredient_quantity_unit = re.findall(r'\D+', igr_split[1])
            recipe_ingredient_quantity_unit = recipe_ingredient_quantity_unit[0] if len(recipe_ingredient_quantity_unit) > 0 else ''

        return recipe_ingredient_name, recipe_ingredient_quantity, recipe_ingredient_quantity_unit