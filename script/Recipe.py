class Recipe:
    """
    Recipe represents a cookbook recipe. It is a convenient way to access the metadata of a given recipe.
    """
    def __init__(self,
                 name: str,
                 recipe_type: str,
                 date_added: str | None = None,
                 source: str | None = None,
                 meal: str | None = None,
                 seasons: list[str] | None = None,
                 tags: list[str] | None = None):
        self.name: str = name
        self.recipe_type: str = recipe_type
        self.date_added: str | None = date_added if date_added else None
        self.source: str | None = source
        self.meal: str | None = meal if meal else None

        if isinstance(seasons, list):
            self.seasons: list[str] = seasons
        elif seasons is None:
            self.seasons: list[str] = []
        else:
            self.seasons: list[str] = [seasons]

        if isinstance(tags, list):
            self.tags: list[str] = tags
        elif tags is None:
            self.tags: list[str] = []
        else:
            self.tags: list[str] = [tags]

