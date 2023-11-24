class Recipe:
    def __init__(self,
                 name: str,
                 date_added: str,
                 source: list[str],
                 recipe_type: list[str],
                 meal: list[str],
                 dish: list[str],
                 season: list[str],
                 tags: list[str]):
        self.name: str = name
        self.date_added: str = date_added
        self.source: list[str] = source
        self.recipe_type: list[str] = recipe_type
        self.meal: list[str] = meal
        self.dish: list[str] = dish
        self.season: list[str] = season
        self.tags: list[str] = tags

