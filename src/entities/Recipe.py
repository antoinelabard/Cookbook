from typing import Optional

from src.entities.Ingredient import Ingredient
from src.entities.Macros import Macros


class Recipe:
    """
    Recipe represents a cookbook recipe. It is a convenient way to access the metadata of a given recipe.
    """

    def __init__(self,
                 name: str,
                 recipe_type: str,
                 ingredients: list[Ingredient],
                 instructions: list[str],
                 date_added: Optional[str] = None,
                 source: Optional[str] = None,
                 meal: Optional[str] = None,
                 seasons: Optional[list[str]] = None,
                 portions: int = 4,
                 tags: Optional[list[str]] = None):
        self.name: str = name
        self.recipe_type: str = recipe_type
        self.date_added: Optional[str] = date_added if date_added else None
        self.source: Optional[str] = source
        self.meal: Optional[str] = meal if meal else None

        if isinstance(seasons, list):
            self.seasons: list[str] = seasons
        elif seasons is None:
            self.seasons: list[str] = []

        self.portions: float = portions

        if isinstance(tags, list):
            self.tags: list[str] = tags
        elif tags is None:
            self.tags: list[str] = []

        self.ingredients: list[Ingredient] = ingredients
        self.instructions: list[str] = instructions

        self.macros: Macros = self.compute_recipe_macros()

    def compute_recipe_macros(self):
        macros = Macros()
        for i in self.ingredients:
            macros += i.macros

        return macros / self.portions
