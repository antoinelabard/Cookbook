import datetime

from script import Recipe


class MealPlanFilters:
    # used at the beginning of a filter to tell that you must not have it among the meal metadata (ex: !tag)
    FILTER_NEGATION = "!"

    def __init__(self,
                 quantity: int | None = None,
                 recipe_type: list[str] | None = None,
                 season: list[str] | None = None,
                 meal: list[str] | None = None,
                 dish: list[str] | None = None,
                 tags: list[str] | None = None,
                 ):
        self.quantity: int | None = quantity
        self.recipe_type: list[str] = recipe_type or []
        self.season: list[str] = season or []
        self.meal: list[str] = meal or []
        self.dish: list[str] = dish or []
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
        recipe_attributes = recipe.__dict__
        for key, filter_attribute_values in self.__dict__.items():
            if key == "quantity":
                continue
            if key == "season":
                if "season" not in recipe_attributes:
                    # the recipe does not specify a  particular season
                    return True
                if self._get_current_season() not in recipe_attributes:
                    return False
            for filter_attribute_value in filter_attribute_values:
                must_contain: bool = filter_attribute_value[0] != self.FILTER_NEGATION
                filter_attribute_value: str = filter_attribute_value.strip(self.FILTER_NEGATION)
                recipe_attributes_values: list[str] = recipe_attributes[filter_attribute_value]
                if filter_attribute_values == ["None"] and recipe_attributes_values != []:
                    # the recipe shouldn't have values for this attribute at all
                    return False
                if not must_contain and filter_attribute_value in recipe_attributes_values:
                    # the recipe has a tag that it shouldn't have
                    return False
                if must_contain and filter_attribute_value not in recipe_attributes_values:
                    # the recipe doesn't have a tag that it should have
                    return False
            return True
