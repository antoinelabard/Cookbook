class Recipe:

    def __init__(self,
                 name: str,
                 date_added: str,
                 source: list[str],
                 recipe_type: list[str],
                 dish: list[str],
                 meal: list[str],
                 tags: list[str]):
        self.name = name
        self.date_added = date_added
        self.source = source
        self.recipe_type = recipe_type
        self.dish = dish
        self.meal = meal
        self.tags = tags
