from script import Recipe

class MealPlanFilters:
    # used at the beginning of a filter to tell that you must not have it among the meal metadata (ex: !tag)
    FILTER_NEGATION = "!"
    def __init__(self,
                 season: list[str],
                 recipe_type: list[str],
                 dish: list[str],
                 tags: list[str],
                 ):
        self.season: list[str] = season
        self.recipe_type: list[str] = recipe_type
        self.dish: list[str] = dish
        self.tags: list[str] = tags

    def matches_filters(self, recipe: Recipe) -> bool:
        recipe_attributes = recipe.__dict__
        for profile_attribute, profile_tags_list in self.__dict__:
            for profile_tag in profile_tags_list:
                must_contain: bool = profile_tag[0] != self.FILTER_NEGATION
                profile_tag: str = profile_tag.strip(self.FILTER_NEGATION)
                recipe_tags_list: list[str] = recipe_attributes[profile_tag]
                # the recipe has a tag that it shouldn't have
                if not must_contain and profile_tag in recipe_tags_list:
                    return False
                # the recipe doesn't have a tag that it should have
                if must_contain and profile_tag not in recipe_tags_list:
                    return False
                return True
