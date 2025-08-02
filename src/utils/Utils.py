from src.entities.Recipe import Recipe


def filter_recipe_by_name(recipe_name: str, recipes: list[Recipe]) -> Recipe:
    return list(filter(lambda recipe: recipe.name == recipe_name, recipes))[0]
