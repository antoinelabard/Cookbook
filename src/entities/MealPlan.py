from typing import Optional

from src.entities.Recipe import Recipe
from src.entities.Macros import Macros
from src.utils.Utils import Utils


class MealPlan:
    """
    MealPlan is a data class responsible for storing all picked recipes, grouped by meal.
    """

    def __init__(self,
                 lunch: Optional[list[Recipe]] = None,
                 breakfast: Optional[list[Recipe]] = None,
                 snack: Optional[list[Recipe]] = None,
                 misc: Optional[list[Recipe]] = None):
        self._lunch: list[Recipe] = lunch or []
        self._breakfast: list[Recipe] = breakfast or []
        self._snack: list[Recipe] = snack or []
        self._misc: list[Recipe] = misc or []

    def get_lunch(self) -> list[Recipe]:
        return self._lunch
    def set_lunch(self, lunch: list[Recipe]):
        self._lunch = lunch
    def get_breakfast(self) -> list[Recipe]:
        return self._breakfast
    def set_breakfast(self, breakfast: list[Recipe]):
        self._breakfast = breakfast
    def get_snack(self) -> list[Recipe]:
        return self._snack
    def set_snack(self, snack: list[Recipe]):
        self._snack = snack
    def get_misc(self) -> list[Recipe]:
        return self._misc
    def set_misc(self, misc: list[Recipe]):
        self._snack = misc

    def as_list(self) -> list[Recipe]:
        return self._breakfast + self._lunch + self._snack

    @staticmethod
    def _compute_avg_macros_per_meal_aux(recipes: list[Recipe]) -> Macros:
        total_nb_portions = sum([recipe.get_portions() for recipe in recipes])

        return Macros(
            sum([recipe.get_macros().get_energy() * recipe.get_portions() for recipe in recipes]) / total_nb_portions,
            sum([recipe.get_macros().get_proteins() * recipe.get_portions() for recipe in recipes]) / total_nb_portions,
            sum([recipe.get_macros().get_fat() * recipe.get_portions() for recipe in recipes]) / total_nb_portions,
            sum([recipe.get_macros().get_carbs() * recipe.get_portions() for recipe in recipes]) / total_nb_portions,
        )

    def compute_avg_macros_per_meal(self, meal) -> Macros:
        """
        :return: the weighted average macros per portion, grouped by meal (breakfast, lunch, snack)
        """

        if meal == Recipe.Meal.BREAKFAST and self._breakfast:
            return self._compute_avg_macros_per_meal_aux(self._breakfast)
        if meal == Recipe.Meal.LUNCH and self._lunch:
            return self._compute_avg_macros_per_meal_aux(self._lunch)
        if meal == Recipe.Meal.SNACK and self._snack:
            return self._compute_avg_macros_per_meal_aux(self._snack)
        return Macros(0, 0, 0, 0)

    def get_ingredients_list_by_aisle(self) -> dict[str, list[str]]:
        """
        :return: a convenient Markdown list to go to the groceries
        """
        ingredients_list: dict[str, list[str]] = {}

        for recipe in self._breakfast + self._lunch + self._snack:
            ingredients_list = Utils.merge_dicts(ingredients_list, recipe.get_ingredients_list_by_aisle())

        return ingredients_list

    def to_str(self) -> str:
        output: list[str] = []
        output.extend(self._to_str_aux(Recipe.Meal.LUNCH, self._lunch))
        output.extend(self._to_str_aux(Recipe.Meal.BREAKFAST, self._breakfast))
        output.extend(self._to_str_aux(Recipe.Meal.SNACK, self._snack))

        return "\n\n".join(output)

    def _to_str_aux(self, meal: str, recipes: list[Recipe]):
        output: list[str] = []
        recipes_links = "\n".join([f"- [ ] [[{recipe.get_name()}]]" for recipe in recipes])
        if not recipes_links:
            return recipes_links
        output.append(f"# {meal}\n\n{recipes_links}")
        avg_macros = self.compute_avg_macros_per_meal(meal)
        output.append(avg_macros.to_markdown_table())

        return output
