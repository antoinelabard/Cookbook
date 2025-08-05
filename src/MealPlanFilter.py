import datetime
from typing import Optional

from src.entities import Recipe
from src.utils.Constants import Constants


class MealPlanFilter:
    """
    MealPlanFilter is a set of filters to select the recipes among all the ones present in the cookbook. Several
    MealPlanFilters can be combined in a profile, to get recipes following different requirement. For example,
    you may need to select a given quantity of lunches, and then another one of breakfasts.
    """

    def __init__(self,
                 quantity: int,
                 recipe_type: str,
                 meal: Optional[str] = None,
                 season: bool = False,
                 tags: list[str] = None,
                 ):
        self._quantity: Optional[int] = quantity
        self._recipe_type: str = recipe_type
        self._meal: Optional[str] = meal if meal else None
        self._is_in_season: bool = season
        self._tags: list[str] = tags or []

    def get_quantity(self) -> float:
        return self._quantity

    def get_meal(self) -> str:
        return self._meal

    @staticmethod
    def _get_current_season() -> str:
        date = datetime.date.today()
        spring_beginning = datetime.date(date.year, 3, 20)
        summer_beginning = datetime.date(date.year, 6, 21)
        autumn_beginning = datetime.date(date.year, 9, 23)
        winter_beginning = datetime.date(date.year, 12, 21)

        if spring_beginning <= date < summer_beginning:
            return Constants.Season.SPRING
        if summer_beginning <= date < autumn_beginning:
            return Constants.Season.SUMMER
        if autumn_beginning <= date < winter_beginning:
            return Constants.Season.AUTUMN
        return Constants.Season.WINTER

    def matches_filters(self, recipe: Recipe) -> bool:
        # recipe type
        if self._recipe_type != recipe.get_recipe_type():
            return False

        # meal
        if self._meal != recipe.get_meal():
            return False

        # seasons
        if self._is_in_season:
            if recipe.get_seasons() and self._get_current_season() not in recipe.get_seasons():
                # The season tag is present in the recipe, but the season doesn't match the current one
                return False

        # tags
        if set(self._tags) != set(recipe.get_tags()):  # verifies identity independently of the order in the collections
            return False

        return True
