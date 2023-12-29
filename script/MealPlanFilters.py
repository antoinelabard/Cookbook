from script import Recipe


class MealPlanFilters:
    # used at the beginning of a filter to tell that you must not have it among the meal metadata (ex: !tag)
    FILTER_NEGATION = "!"

    def __init__(self,
                 quantity: int,
                 recipe_type: list[str] | None = None,
                 season: list[str] | None = None,
                 meal: list[str] | None = None,
                 dish: list[str] | None = None,
                 tags: list[str] | None = None,
                 ):
        self.quantity = quantity
        self.recipe_type: list[str] = recipe_type or []
        self.season: list[str] = season or []
        self.meal: list[str] = meal or []
        self.dish: list[str] = dish or []
        self.tags: list[str] = tags or []

    def matches_filters(self, recipe: Recipe) -> bool:
        recipe_attributes = recipe.__dict__
        for _, filter_attribute_values in self.__dict__:
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
