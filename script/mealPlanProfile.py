class MealPlanProfile:
    def __init__(self,
                 season: list[str],
                 recipe_type: list[str],
                 meal: list[str],
                 dish: list[str],
                 tags: list[str],
                 ):
        self.season: list[str] = season
        self.recipe_type: list[str] = recipe_type
        self.meal: list[str] = meal
        self.dish: list[str] = dish
        self.tags: list[str] = tags
