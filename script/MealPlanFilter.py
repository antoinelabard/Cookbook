import datetime

from script import Recipe
from script.Constants import Constants


class MealPlanFilter:
    """
    MealPlanFilter is a set of filters to select the recipes among all the ones present in the cookbook. Several
    MealPlanFilters can be combined in a profile, to get recipes following different requirement. For example,
    you may need to select a given quantity of lunches, and then another one of breakfasts.
    """

    def __init__(self,
                 quantity: int,
                 recipe_type: str,
                 meal: str | None = None,
                 season: bool = False,
                 tags: list[str] | None = None,
                 ):
        self.quantity: int | None = quantity
        self.recipe_type: str = recipe_type
        self.meal: str | None = meal if meal else None
        self.is_in_season: bool = season
        self.tags: list[str] = tags or []

    def _get_current_season(self) -> str:
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
        if self.recipe_type != recipe.recipe_type:
            return False

        # meal
        if self.meal != recipe.meal:
            return False

        # seasons
        if self.is_in_season:
            if recipe.seasons and self._get_current_season() not in recipe.seasons:
                # The season tag is present in the recipe, but the season doesn't match the current one
                return False

        # tags
        if set(self.tags) != set(recipe.tags):  # verifies identity independently of the order in the collections
            return False

        return True
