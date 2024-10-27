from __future__ import annotations

from pathlib import Path

import yaml

from script import MealPlan
from script.Constants import Constants
from script.MealPlanFilter import MealPlanFilter
from script.Recipe import Recipe


def singleton(class_):
    instances = {}

    def getinstance(*args, **kwargs):
        if class_ not in instances:
            instances[class_] = class_(*args, **kwargs)
        return instances[class_]

    return getinstance


@singleton
class CookbookRepository:
    """
    CookBookRepository: Manage the access to the data stored in the cookbook. Any read or write operation must be
    handled by this class. It includes operations to read the general cookbook metadata and the metadata of each of
    the recipes.
    """

    ROOT_DIR: Path = Path(__file__).parent.parent
    RECIPE_DIR: Path = ROOT_DIR / "recettes"
    COMPLETE_COOKBOOK_PATH: Path = ROOT_DIR / "cookbook.md"
    MENU_PATH: Path = ROOT_DIR / "menu.md"
    INGREDIENTS_PATH: str = ROOT_DIR / "ingredients.md"
    PROFILES_PATH = ROOT_DIR / "profiles.yaml"
    INGREDIENTS_AISLES_PATH = ROOT_DIR / "ingredients.yaml"

    def __init__(self):
        self.recipes = self._read_recipes()
        self.profiles = self._read_profiles()

    @classmethod
    def _load_recipe_from_file(cls, path: Path) -> Recipe | None:
        """
        :param path: the path to the markdown file containing the metadata
        :return: A recipe object
        """
        with open(path, 'r') as f:
            lines = f.readlines()

        metadata_delimiter: str = "---\n"
        ingredients_delimiter: str = "## Ingrédients"
        instructions_delimiter: str = "## Préparation"

        # the following tests check if it contains the standard section delimiters, so is formatted as a recipe
        joined_lines: str = "".join(lines)
        if metadata_delimiter not in joined_lines:
            return
        if ingredients_delimiter not in joined_lines:
            return
        if instructions_delimiter not in joined_lines:
            return

        # split the file in 3 sections
        # the indexes lines indexes are tuned to remove unwanted lines and only keep the metadata, ingredients list and instructions
        metadata_range: list[int] = [1]  # the metadata is at the beginning of the file
        ingredients_range: list[int] = []
        instructions_range: list[int] = []
        for i in range(1, len(lines)):
            if metadata_delimiter in lines[i]:
                metadata_range.append(i)
            if ingredients_delimiter in lines[i]:
                ingredients_range.append(i + 2)
            if instructions_delimiter in lines[i]:
                ingredients_range.append(i - 1)
                instructions_range.append(i + 2)
        instructions_range.append(len(lines))

        metadata: dict[str, str | list[str]] = yaml.safe_load("".join(lines[metadata_range[0]:metadata_range[1]]))
        ingredients = lines[ingredients_range[0]:ingredients_range[1]]
        ingredients = list(map(lambda ingredient: ingredient.replace("- [ ] ", ""), ingredients))
        ingredients = list(map(lambda ingredient: ingredient.replace("\n", ""), ingredients))
        instructions = lines[instructions_range[0]:instructions_range[1]]
        instructions = list(map(lambda instruction: instruction.replace("\n", ""), instructions))
        recipe = Recipe(
            path.name.replace(".md", ""),
            metadata[Constants.RECIPE_TYPE],
            ingredients,
            instructions,
            metadata[Constants.DATE_ADDED] if Constants.DATE_ADDED in metadata.keys() else None,
            metadata[Constants.SOURCE] if Constants.SOURCE in metadata.keys() else None,
            metadata[Constants.Meal.MEAL] if Constants.Meal.MEAL in metadata.keys() else None,
            metadata[Constants.Season.SEASON].split(", ") if Constants.Season.SEASON in metadata.keys() else None,
            metadata[Constants.TAGS].split(", ") if Constants.TAGS in metadata.keys() else None
        )

        return recipe

    def _read_recipes(self) -> list[Recipe]:
        """
        :return: the list of all the recipes in the cookbook
        """
        recipes: list[Recipe] = []
        for recipe_path in self._get_recipes_paths():
            recipe = self._load_recipe_from_file(recipe_path)
            if recipe is not None:
                recipes.append(recipe)
        return recipes

    def write_meal_plan(self, meal_plan: MealPlan) -> None:
        """
        Write down in a file the provided MealPlan.
        :param meal_plan: the MealPlan to write down
        """
        meals_links: list[str] = []
        for meal, recipes in meal_plan.__dict__.items():
            recipes_links = "\n".join([f"- [ ] [[{recipe.name}]]" for recipe in recipes])
            if recipes_links:
                meals_links.append(f"# {meal}\n\n{recipes_links}")
        with open(self.MENU_PATH, 'w') as f:
            f.write("\n\n".join(meals_links))

    def export_complete_cookbook(self) -> None:
        """
        Create a document containing quotes of the recipes contained in the cookbook.
        """
        page_break: str = '\n\n<div style="page-break-after: always;"></div>\n\n'
        complete_cookbook_template: str = "# Livre de recettes\n\n{}"
        files_wikilinks = sorted([f'![[{path.name}]]' for path in self._get_recipes_paths()])

        with open(self.COMPLETE_COOKBOOK_PATH, 'w') as f:
            f.write(complete_cookbook_template.format(page_break.join(files_wikilinks)))

    def _get_recipes_paths(self) -> list[Path]:
        """
        :return: the list of the absolute paths of all the recipes in the cookbook
        """
        return [path for path in self.RECIPE_DIR.iterdir() if path.is_file()]

    def _read_profiles(self) -> dict[str, list[MealPlanFilter]]:
        """
        Retrieve the profiles from "profiles.yaml" and present the data as an dictionary for which the keys are the
        profiles names and the values are a list of MealPlanFilters for each profile.
        :return: the dictionary of profiles
        """
        with open(self.PROFILES_PATH, "r") as f:
            data = yaml.safe_load("\n".join(f.readlines()))
        profiles = {}
        for profile, profile_filters in data.items():
            profiles[profile] = []
            for profile_filter in profile_filters:
                meal = None
                is_in_season = False
                tags = None
                if Constants.Meal.MEAL in profile_filter.keys():
                    meal = profile_filter[Constants.Meal.MEAL]
                if Constants.Season.IS_IN_SEASON in profile_filter.keys():
                    is_in_season = profile_filter[Constants.Season.IS_IN_SEASON]
                if Constants.TAGS in profile_filter.keys():
                    tags = profile_filter[Constants.TAGS]
                meal_plan_filter = MealPlanFilter(
                    profile_filter[Constants.QUANTITY],
                    profile_filter[Constants.RECIPE_TYPE],
                    meal,
                    is_in_season,
                    tags,
                )
                profiles[profile].append(meal_plan_filter)

        return profiles

    def _read_recipes_from_menu(self) -> list[Recipe]:
        """
        Read the recipes names listed in the menu file pointed by MENU_PATH
        :return: a list of recipes names
        """
        with open(self.MENU_PATH, 'r') as f:
            lines = f.readlines()

        # filter the recipes cited in the names list
        names = list(map(lambda name: name.split("[[")[1].split("]]")[0] if "[[" in name else "", lines))
        return list(filter(lambda recipe: recipe.name in names, self.recipes))

    def write_ingredients(self):
        """
        Write the ingredients of the given Recipe list in the file pointed by INGREDIENTS_PATH.
        The ingredients are categorized by aisle following the convention described in INGREDIENTS_AISLES_PATH
        """
        ingredients: list[str] = [ingredient.lower() for sublist in list(map(lambda recipe: recipe.ingredients, self._read_recipes_from_menu())) for ingredient in sublist]
        ingredients_aisles_reference = self._read_ingredients_aisles()

        ingredients_aisles = {aisle: [] for aisle in ingredients_aisles_reference.keys()}
        for aisle in ingredients_aisles_reference.keys():
            for ingredient_reference in ingredients_aisles_reference[aisle]:
                i = 0
                while i < len(ingredients):
                    if ingredient_reference.lower() in ingredients[i]:
                        ingredients_aisles[aisle].append(ingredients.pop(i))
                    else:
                        i += 1
        ingredients_aisles["Unclassified"] = ingredients

        ingredients = []
        for aisle in ingredients_aisles.keys():
            if not ingredients_aisles[aisle]:
                continue
            ingredients.append(f"- [ ] {aisle} :\n" + "\n".join([f"  - [ ] {ingredient}" for ingredient in ingredients_aisles[aisle]]))

        with open(self.INGREDIENTS_PATH, 'w') as f:
            f.write("\n".join(ingredients))

    def _read_ingredients_aisles(self) -> dict[list[str]]:
        """
        read from the file INGREDIENTS_AISLES_PATH the associations between ingredients and aisles
        :return: a dict for which the keys are the aisles and the values are a list of ingredients
        """
        with open(self.INGREDIENTS_AISLES_PATH, 'r') as f:
            lines = f.readlines()
        return yaml.safe_load("".join(lines))
