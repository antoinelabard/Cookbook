class Recipe:
    def __init__(self,
                 name: str,
                 date_added: str | None = None,
                 source: list[str] | None = None,
                 recipe_type: list[str] | None = None,
                 meal: list[str] | None = None,
                 dish: list[str] | None = None,
                 season: list[str] | None = None,
                 tags: list[str] | None = None):
        self.name: str = name
        self.date_added: str | None = date_added
        self.source: list[str] | None = source
        self.recipe_type: list[str] | None = recipe_type
        self.meal: list[str] | None = meal
        self.dish: list[str] | None = dish
        self.season: list[str] | None = season
        self.tags: list[str] | None = tags
