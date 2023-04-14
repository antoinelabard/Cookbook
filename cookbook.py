#!/usr/bin/python3
import copy
import os
import sys
import yaml
import json
from datetime import datetime
import math
import random

RECIPE_DIR = "recettes"


def singleton(class_):
    instances = {}

    def getinstance(*args, **kwargs):
        if class_ not in instances:
            instances[class_] = class_(*args, **kwargs)
        return instances[class_]

    return getinstance


@singleton
class CookBookRepository:
    RECIPES_TAG = "recipes"
    COOKED_DATES_TAG = "cooked dates"
    COOKBOOK_PATH = 'cookbook_metadata.json'
    menu_path = 'menu.md'
    RECIPE_METADATA_TEMPLATE = {
        COOKED_DATES_TAG: []
    }

    def __init__(self):
        self.cookbook_metadata = self._get_cookbook_metadata()
        self.recipes_metadata = self._get_recipes_metadata()

    def _get_cookbook_metadata(self):
        with open(self.COOKBOOK_PATH, 'r') as f:
            return json.load(f)

    def _set_cookbook_metadata(self, cookbook_metadata):
        self.cookbook_metadata = cookbook_metadata
        self.update_cookbook_metadata()
        with open(self.COOKBOOK_PATH, 'w') as f:
            json.dump(cookbook_metadata, f, indent=4)  # you can add indent=4 when debugging to format the json file

    def update_cookbook_metadata(self):
        for recipe in self.get_recipes_names():
            if recipe not in self.cookbook_metadata.keys():
                self.cookbook_metadata[recipe] = self.RECIPE_METADATA_TEMPLATE

    def get_recipes_names(self):
        return list(map(
            lambda x: x.split('/')[-1].replace('\n', '').replace('.md', ''),
            os.popen(f'find {RECIPE_DIR} -name "*.md"').readlines()
        ))

    def get_recipes_cooked_dates(self):
        recipes_cooked_dates = {}
        for key, value in self.cookbook_metadata.items():
            recipes_cooked_dates[key] = value[self.COOKED_DATES_TAG]
        return recipes_cooked_dates

    def get_recipe_cooked_dates(self, recipe_name):
        if recipe_name not in self.cookbook_metadata.keys():
            return []
        return self.cookbook_metadata[recipe_name][self.COOKED_DATES_TAG]

    def _get_metadata_from_md(self, path):
        """
        :param path: the path to the markdown file containing the metadata
        :return: an empty string if there is no metadata in the file. Otherwise, return a dictionary of the metadata
        """
        lines = ""
        metadata_marker = "---\n"
        with open(path, 'r') as f:
            line = f.readline()
            if line != metadata_marker:  # check if there is metadata in the file
                return ''
            while True:
                line = f.readline()
                if line == metadata_marker:
                    return yaml.safe_load(lines)
                lines += line

    def _get_recipes_metadata(self):
        """
        :return: the metadata of all the files in a dictionary
        """
        self.update_cookbook_metadata()
        files_metadata = {}
        for recipe_name in self.cookbook_metadata.keys():
            file_metadata = self._get_metadata_from_md(f"recettes/{recipe_name}.md")
            if file_metadata != '':
                files_metadata[recipe_name] = file_metadata
        return files_metadata

    def get_recipes_times_cooked(self):
        recipes_cooked_dates = {}
        for name, metadata in self._get_cookbook_metadata().items():
            recipes_cooked_dates[name] = len(metadata[self.COOKED_DATES_TAG])
        return recipes_cooked_dates

    def add_recipe_cooked_date(self, recipe_name):
        self.update_cookbook_metadata()
        if recipe_name not in self.cookbook_metadata.keys():
            self.cookbook_metadata[recipe_name] = self.RECIPE_METADATA_TEMPLATE
        self.cookbook_metadata[recipe_name][self.COOKED_DATES_TAG].append(
            datetime.now().isoformat())
        self._set_cookbook_metadata(self.cookbook_metadata)

    def read_menu(self):
        with open("menu.md", 'r') as f:
            recipes_names = f.readlines()
        recipes_names = list(map(lambda line: line.replace("![[", "").replace("]]\n", ""), recipes_names))
        recipes_names = list(filter(lambda line: line in self.get_recipes_names(), recipes_names))
        return recipes_names

    def add_menu_cooked_dates(self):
        for recipe in self.read_menu():
            self.add_recipe_cooked_date(recipe)


class MealGenerator:
    """
    MealGenerator
    """
    NB_PORTIONS_PER_RECIPE = 4  # I plan to set the number of portions for each recipe
    NB_LUNCHES_PER_DAY = 2
    NB_BREAKFASTS_PER_DAY = 2

    week_plan_profile = {
        "meals": {
            "lunch": math.ceil(
                7 * NB_LUNCHES_PER_DAY / NB_PORTIONS_PER_RECIPE),
            "breakfast": math.ceil(
                2 * NB_BREAKFASTS_PER_DAY / NB_PORTIONS_PER_RECIPE),
            "snack": math.ceil(
                2 / NB_PORTIONS_PER_RECIPE),
        },
        "filters": {
            "type": "meal",
            "opportunity": None
        }
    }

    def __init__(self):
        self.repository = CookBookRepository()

    def generate_meal_plan(self, nb_people=1, profile=week_plan_profile):
        recipes_names = repository.get_recipes_names()

        def match_filter(name, flt):
            if profile["filters"][flt] is None and flt not in repository.recipes_metadata[name]:
                return True
            if flt not in repository.recipes_metadata[name]:
                return False
            return repository.recipes_metadata[name][flt] == profile["filters"][flt]

        def match_meal(name, meal):
            if "meal" not in repository.recipes_metadata[name]:
                return False
            return repository.recipes_metadata[name]["meal"] == meal

        def pick_recipes_per_meal():
            meal_plan = {}
            for meal, quantity in profile["meals"].items():
                total_quantity = quantity * nb_people
                rcp_names = copy.copy(recipes_names)
                for flt in profile["filters"]:
                    rcp_names = list(filter(lambda name: match_filter(name, flt), rcp_names))
                rcp_names = list(filter(lambda name: match_meal(name, meal), rcp_names))
                # sort by least cooked recipe ascending
                rcp_names.sort(key=lambda name: len(repository.cookbook_metadata[name]["cooked dates"]))
                if len(rcp_names) > 2 * total_quantity:  # two times more meals than what the profile needs
                    rcp_names = rcp_names[:math.ceil(len(rcp_names) / 2)]  # select the 50% less cooked recipes
                random.shuffle(rcp_names)
                # select the desired quantity if there is enough filtered recipes
                if len(rcp_names) > total_quantity:
                    rcp_names = rcp_names[:int(total_quantity)]
                meal_plan[meal] = rcp_names

            return meal_plan

        meal_plan = pick_recipes_per_meal()

        with open("menu.md", 'w') as f:
            lunch_str = "\n".join([f"![[{i}]]" for i in meal_plan['lunch']])
            breakfast_str = "\n".join([f"![[{i}]]" for i in meal_plan['breakfast']])
            snack_str = "\n".join([f"![[{i}]]" for i in meal_plan['snack']])

            file_str = f"""# Menu
                
                ## Lunch
                
                {lunch_str}
                
                ## Breakfast
                
                {breakfast_str}
                
                ## Snack
                
                {snack_str}
                """.replace("                ", "")

            print(file_str)
            f.write(file_str)


repository = CookBookRepository()
mealGenerator = MealGenerator()


def export_complete_cookbook():
    """
    create a document containing quotes of the recipes contained in the cookbook.
    """

    complete_cookbook = """# Livre de recettes
    
    {}""".replace("    ", "")

    files_wikilinks = lambda files_list: \
        map(lambda file: '![[{}]]'.format(file.split('/')[-1].replace('.md\n', '')), files_list)

    wikilinks_str = lambda: '\n'.join(files_wikilinks(sorted(repository.get_recipes_names())))
    with open("livre de recettes.md", 'w') as f:
        f.write(complete_cookbook.format(wikilinks_str()))


for arg in sys.argv:
    if arg == "export":
        export_complete_cookbook()
    if arg == "update":
        repository.update_cookbook_metadata()
    if arg == "plan":
        mealGenerator.generate_meal_plan()
    if arg == "save":
        repository.add_menu_cooked_dates()
