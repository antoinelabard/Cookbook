import random

from src.MealPlanFilter import MealPlanFilter
from src.entities.MealPlan import MealPlan
from src.entities.Recipe import Recipe
from src.utils.Utils import Utils


class MealPlanBuilder:
    """
    MealPlanBuilder: Used to generate a new meal plan, given a certain profile established in advance. This class is
    intended to generate meals plan based on the prior cook history of the cookbook. It uses the cookbook metadata
    cooked dates to determine the least cooked recipes matching the indicated filters, and pick among the candidates
    to return the result.
    """

    _logger = Utils.get_logger(__name__)

    def __init__(self, recipes: list[Recipe]):
        self._recipes: list[Recipe] = recipes
        self._meal_plan: MealPlan = MealPlan()

    def pick_recipes_with_filter(self, meal_plan_filter: MealPlanFilter):
        """
        Randomly add to the internal MealPlan some of the recipes matching the provided filters. The selected
        recipes add up to the one already in the MealPlanFilter instance of the builder
        :param meal_plan_filter: the current set of filters to select only the recipe matching the requirements. It also
        provides the quantity of recipes to be picked.
        """

        filtered_recipes: list[Recipe] = [recipe for recipe in self._recipes
                                          if meal_plan_filter.matches_filters(recipe)]
        if not filtered_recipes:
            return

        MealPlanBuilder._logger.info(
            f"Picking {meal_plan_filter.get_quantity() if meal_plan_filter.get_quantity() is not None else 0} recipes "
            + f"among {len(filtered_recipes)}.")
        filtered_recipes_copy: list[Recipe] = filtered_recipes.copy()
        picked_recipes: list[Recipe] = []
        quantity = meal_plan_filter.get_quantity()
        while quantity > 0:
            # select the filtered recipes using a random draw
            index: int = random.randint(0, len(filtered_recipes_copy) - 1)
            picked_recipes.append(filtered_recipes_copy.pop(index))
            quantity -= 1

            if not filtered_recipes_copy:
                filtered_recipes_copy = filtered_recipes.copy()

        if meal_plan_filter.get_meal() == Recipe.Meal.LUNCH:
            self._meal_plan.get_lunch().extend(picked_recipes)
        elif meal_plan_filter.get_meal() == Recipe.Meal.BREAKFAST:
            self._meal_plan.get_breakfast().extend(picked_recipes)
        elif meal_plan_filter.get_meal() == Recipe.Meal.SNACK:
            self._meal_plan.get_snack().extend(picked_recipes)
        else:
            self._meal_plan.get_misc().extend(picked_recipes)

    def add_recipe(self, meal: str, recipe: Recipe):
        match meal:
            case Recipe.Meal.BREAKFAST:
                self._meal_plan.get_breakfast().append(recipe)
            case Recipe.Meal.LUNCH:
                self._meal_plan.get_lunch().append(recipe)
            case Recipe.Meal.SNACK:
                self._meal_plan.get_snack().append(recipe)

    def add_recipes(self, meal: str, recipes: list[Recipe]):
        match meal:
            case Recipe.Meal.BREAKFAST:
                self._meal_plan.get_breakfast().extend(recipes)
            case Recipe.Meal.LUNCH:
                self._meal_plan.get_lunch().extend(recipes)
            case Recipe.Meal.SNACK:
                self._meal_plan.get_snack().extend(recipes)

    def build(self):
        return self._meal_plan
