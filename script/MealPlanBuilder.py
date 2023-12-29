import random

from script.CookbookRepository import CookbookRepository
from script.MealPlan import MealPlan
from script.MealPlanFilters import MealPlanFilters
from script.Recipe import Recipe


class MealPlanBuilder:
    """
    MealPlanBuilder: Used to generate a new meal plan, given a certain profile established in advance. This class is
    intended to generate meals plan based on the prior cook history of the cookbook. It uses the cookbook metadata
    cooked dates to determine the least cooked recipes matching the indicated filters, and pick among the candidates
    to return the result.
    """

    def __init__(self):
        self.repository: CookbookRepository = CookbookRepository()
        self.meal_plan: MealPlan = MealPlan()
        self.recipes = self.repository.recipes

    def add_recipes(self, filters: MealPlanFilters):
        filtered_recipes: list[Recipe] = [name for name in self.repository.recipes if filters.match_filters(name)]
        if not filtered_recipes:
            return

        filtered_recipes_copy: list[Recipe] = filtered_recipes.copy()
        picked_recipes: list[Recipe] = []
        quantity = filters.quantity
        while quantity > 0:
            # select the filtered recipes using a random draw
            index: int = random.randint(0, len(filtered_recipes_copy) - 1)
            picked_recipes.append(filtered_recipes_copy.pop(index))
            quantity -= 1

            if not filtered_recipes_copy:
                filtered_recipes_copy = filtered_recipes.copy()

        # add the picked recipes to the meal plan
        getattr(self.meal_plan, filters.meal).extend(picked_recipes)

    def build(self):
        return self.meal_plan
