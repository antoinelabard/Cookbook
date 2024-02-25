import datetime

from script import Recipe


class MealPlanFilter:
    # used at the beginning of a filter to tell that you must not have it among the meal metadata (ex: !tag)
    FILTER_NEGATION = "!"

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
            return "spring"
        if summer_beginning <= date < autumn_beginning:
            return "summer"
        if autumn_beginning <= date < winter_beginning:
            return "autumn"
        return "winter"

    def matches_filters(self, recipe: Recipe) -> bool:
        # recipe type
        if self.recipe_type != recipe.recipe_type:
            return False

        # meal
        if self.meal != recipe.meal:
            return False

        # seasons
        if self.is_in_season and not recipe.seasons:
            return False
        if self.is_in_season and self._get_current_season() not in recipe.seasons:
            return False

        # tags
        if self.tags is not None:
            if recipe.tags is None:
                return False
            for tag in self.tags:
                if tag not in recipe.tags:
                    return False

        return True
