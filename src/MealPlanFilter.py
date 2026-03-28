import datetime
from typing import Optional

from src.entities.Recipe import Recipe
from src.utils.MonthEnum import MonthEnum


class MealPlanFilter:
    """
    MealPlanFilter is a set of filters to select the recipes among all the ones present in the cookbook. Several
    MealPlanFilters can be combined in a profile, to get recipes following different requirement. For example,
    you may need to select a given quantity of lunches, and then another one of breakfasts.
    """

    def __init__(self,
                 portions: int,
                 recipe_type: str,
                 meal: Optional[str] = None,
                 is_in_season: bool = False,
                 tags: list[str] = None,
                 ):
        self._portions: Optional[int] = portions
        self._recipe_type: str = recipe_type
        self._meal: Optional[str] = meal if meal else None
        self._is_in_season: bool = is_in_season
        self._tags: list[str] = tags or []

    def get_portions(self) -> float:
        return self._portions

    def get_meal(self) -> str:
        return self._meal

    def matches_filters(self, recipe: Recipe) -> bool:
        # recipe type
        if self._recipe_type != recipe.get_recipe_type():
            return False

        # meal
        if self._meal != recipe.get_meal():
            return False

        # seasons
        if self._is_in_season:
            if recipe.get_seasons() and MonthEnum.from_number(datetime.date.today().month) not in recipe.get_seasons():
                # The season tag is present in the recipe, but the season doesn't match the current one
                return False

        # tags
        if set(self._tags) != set(recipe.get_tags()):  # verifies identity independently of the order in the collections
            return False

        return True
