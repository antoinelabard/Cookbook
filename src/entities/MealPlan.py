from typing import Optional

from src.entities import Recipe
from src.utils.Constants import Constants
from src.entities.Macros import Macros


class MealPlan:
    """
    MealPlan is a data class responsible for storing all the meals of a meal plan.
    """

    def __init__(self,
                 lunch: Optional[list[Recipe]] = None,
                 breakfast: Optional[list[Recipe]] = None,
                 snack: Optional[list[Recipe]] = None,
                 misc: Optional[list[Recipe]] = None):
        self.lunch: list[Recipe] = lunch or []
        self.breakfast: list[Recipe] = breakfast or []
        self.snack: list[Recipe] = snack or []
        self.misc: list[Recipe] = misc or []

    def as_list(self) -> list[Recipe]:
        return self.breakfast + self.lunch + self.snack

    def _compute_avg_macros_per_meal_aux(self, recipes: list[Recipe]) -> Macros:
        total_nb_portions = sum(map(lambda recipe: recipe.portions, recipes))

        suum = sum(map(lambda recipe: recipe.macros.energy * recipe.portions, recipes)) / total_nb_portions,

        return Macros(
            round(sum(map(lambda recipe: recipe.macros.energy * recipe.portions, recipes)) / total_nb_portions),
            round(sum(map(lambda recipe: recipe.macros.proteins * recipe.portions, recipes)) / total_nb_portions),
            round(sum(map(lambda recipe: recipe.macros.lipids * recipe.portions, recipes)) / total_nb_portions),
            round(sum(map(lambda recipe: recipe.macros.carbs * recipe.portions, recipes)) / total_nb_portions),
        )

    def compute_avg_macros_per_meal(self, meal) -> Macros:
        """
        return the weighted average macros per portion, filtered by meal (breakfast, lunch, snack)
        :return: a dict of meals and macros.
        """

        match meal:
            case Constants.Meal.BREAKFAST:
                return self._compute_avg_macros_per_meal_aux(self.breakfast)
            case Constants.Meal.LUNCH:
                return self._compute_avg_macros_per_meal_aux(self.lunch)
            case Constants.Meal.SNACK:
                return self._compute_avg_macros_per_meal_aux(self.snack)
        return Macros(0, 0, 0, 0)
