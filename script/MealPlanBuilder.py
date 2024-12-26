import random

from script.Constants import Constants
from script.CookbookRepository import CookbookRepository
from script.MealPlan import MealPlan
from script.MealPlanFilter import MealPlanFilter
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

    def add_recipes(self, meal_plan_filter: MealPlanFilter):
        """
        Randomly add to the internal MealPlan some of the recipes matching the provided filters. The selected
        recipes add up to the one already in the MealPlanFilter instance of the builder
        :param meal_plan_filter: the
        current set of filters to select only the recipe matching the requirements. It also provides the quantity of
        recipes to be picked.
        """
        filtered_recipes: list[Recipe] = [recipe for recipe in self.repository.recipes if meal_plan_filter.matches_filters(recipe)]
        if not filtered_recipes:
            return

        filtered_recipes_copy: list[Recipe] = filtered_recipes.copy()
        picked_recipes: list[Recipe] = []
        quantity = meal_plan_filter.quantity
        while quantity > 0:
            # select the filtered recipes using a random draw
            index: int = random.randint(0, len(filtered_recipes_copy) - 1)
            picked_recipes.append(filtered_recipes_copy.pop(index))
            quantity -= 1

            if not filtered_recipes_copy:
                filtered_recipes_copy = filtered_recipes.copy()

        if meal_plan_filter.meal == Constants.Meal.LUNCH:
            self.meal_plan.lunch.extend(picked_recipes)
        elif meal_plan_filter.meal == Constants.Meal.BREAKFAST:
            self.meal_plan.breakfast.extend(picked_recipes)
        elif meal_plan_filter.meal == Constants.Meal.SNACK:
            self.meal_plan.snack.extend(picked_recipes)
        else:
            self.meal_plan.misc.extend(picked_recipes)

    def build(self):
        return self.meal_plan
