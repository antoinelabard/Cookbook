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
    PROFILES_PATH = ROOT_DIR / "profiles.yaml"

    def __init__(self):
        self.recipes = self._read_recipes()
        self.profiles = self._read_profiles()

    @classmethod
    def _load_recipe_from_file(cls, path: Path) -> Recipe | None:
        """
        :param path: the path to the markdown file containing the metadata
        :return: None if there is no metadata in the file. Otherwise, return a Recipe object
        """
        lines: str = ""
        metadata_marker: str = "---\n"
        with open(path, 'r') as f:
            line: str = f.readline()
            if line != metadata_marker:  # check if there is a metadata header in the file
                return
            while True:
                # read the file metadata
                line = f.readline()
                if line == metadata_marker:
                    break
                lines += line

        metadata_dict: dict[str, str | list[str]] = yaml.safe_load(lines)
        recipe = Recipe(
            path.name.replace(".md", ""),
            metadata_dict[Constants.RECIPE_TYPE],
            metadata_dict[Constants.DATE_ADDED] if Constants.DATE_ADDED in metadata_dict.keys() else None,
            metadata_dict[Constants.SOURCE] if Constants.SOURCE in metadata_dict.keys() else None,
            metadata_dict[Constants.Meal.MEAL] if Constants.Meal.MEAL in metadata_dict.keys() else None,
            metadata_dict[Constants.Season.SEASON].split(", ") if Constants.Season.SEASON in metadata_dict.keys() else None,
            metadata_dict[Constants.TAGS].split(", ") if Constants.TAGS in metadata_dict.keys() else None
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
