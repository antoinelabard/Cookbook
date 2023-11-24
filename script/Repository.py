from __future__ import annotations

from pathlib import Path

import yaml

from script import MealPlan
from script.Recipe import Recipe


def singleton(class_):
    instances = {}

    def getinstance(*args, **kwargs):
        if class_ not in instances:
            instances[class_] = class_(*args, **kwargs)
        return instances[class_]

    return getinstance


@singleton
class CookBookRepository:
    """
    CookBookRepository: Manage the access to the data stored in the cookbook. Any read or write operation must be
        handled by this class. It includes operations to read the general cookbook metadata and the metadata of each of
        the recipes.
    """

    ROOT_DIR: Path = Path(__file__).parent
    RECIPE_DIR: Path = ROOT_DIR / "recettes"
    COMPLETE_COOKBOOK_PATH: Path = ROOT_DIR / "cookbook.md"
    MENU_PATH: Path = ROOT_DIR / "menu.md"

    def __init__(self):
        self.recipes = self._read_recipes()

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
                line = f.readline()
                if line == metadata_marker:
                    metadata_dict: dict[str, str | list[str]] = yaml.safe_load(lines)
                    for key, value in enumerate(metadata_dict):
                        # put the value in a list if it's a string
                        value_list = []
                        value_list.extend(value)
                        metadata_dict[key] = value_list
                        return Recipe(
                            path.name,
                            metadata_dict["date-added"],
                            metadata_dict["source"],
                            metadata_dict["recipe_type"],
                            metadata_dict["meal"],
                            metadata_dict["dish"],
                            metadata_dict["season"],
                            metadata_dict["tags"]
                        )
                lines += line

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

    def write_menu(self, meal_plan: MealPlan) -> None:
        meals_links: list[str] = []
        for meal, recipes in meal_plan.__dict__.items():
            recipes_links = "\n".join([f"- [[{i}]]" for i in recipes])
            meals_links.append(f"{meal}\n\n{recipes_links}")
        with open(self.MENU_PATH, 'w') as f:
            f.write("\n\n".join(meals_links))

    def export_complete_cookbook(self) -> None:
        """
        create a document containing quotes of the recipes contained in the cookbook.
        """
        page_break: str = '\n\n<div style="page-break-after: always;"></div>\n\n'
        complete_cookbook_template: str = "# Livre de recettes\n\n"
        files_wikilinks = [f'![[{path.name}]]' for path in self._get_recipes_paths()]

        with open(self.COMPLETE_COOKBOOK_PATH, 'w') as f:
            f.write(complete_cookbook_template.format(page_break.join(files_wikilinks)))

    def _get_recipes_paths(self) -> list[Path]:
        return [path for path in self.RECIPE_DIR.iterdir() if path.is_file()]
