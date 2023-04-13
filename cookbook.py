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


def export_complete_cookbook():
    """
    create a document containing quotes of the recipes contained in the cookbook.
    """

    recipes_list = lambda: "{}".format('\n'.join(files_wikilinks(sorted(CookBookRepository.RECIPES_NAMES_LIST))))

    complete_cookbook = """# Livre de recettes
    
    {}""".replace("    ", "")

    files_wikilinks = lambda files_list: \
        map(lambda file: '![[{}]]'.format(file.split('/')[-1].replace('.md\n', '')), files_list)

    with open("livre de recettes.md", 'w') as f:
        f.write(complete_cookbook.format(recipes_list()))


class CookBookRepository:
    RECIPES_NAMES_LIST = list(map(
        lambda x: x.split('/')[-1].replace('\n', '').replace('.md', ''),
        os.popen(f'find {RECIPE_DIR} -name "*.md"').readlines()
    ))

    RECIPES_TAG = "recipes"
    COOKED_DATES_TAG = "cooked dates"

    RECIPE_METADATA_TEMPLATE = {
        COOKED_DATES_TAG: []
    }

    @staticmethod
    def get_cookbook_metadata():
        with open('cookbook_metadata.json', 'r') as f:
            return json.load(f)

    @staticmethod
    def set_cookbook_metadata(cookbook_metadata):
        with open('cookbook_metadata.json', 'w') as f:
            json.dump(cookbook_metadata, f, indent=4)  # you can add indent=4 when debugging to format the json file

    @staticmethod
    def get_recipes_cooked_dates():
        recipes_cooked_dates = {}
        for key, value in CookBookRepository.get_cookbook_metadata().items():
            recipes_cooked_dates[key] = value[CookBookRepository.COOKED_DATES_TAG]
        return recipes_cooked_dates

    @staticmethod
    def get_recipe_cooked_dates(recipe_name):
        cookbook_metadata = CookBookRepository.get_cookbook_metadata()
        if recipe_name not in cookbook_metadata.keys():
            return []
        return cookbook_metadata[recipe_name][CookBookRepository.COOKED_DATES_TAG]

    @staticmethod
    def _get_metadata_from_md(path):
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

    @staticmethod
    def get_recipes_metadata():
        """
        :return: the metadata of all the files in a dictionary
        """
        CookBookRepository.update_cookbook_metadata()
        files_metadata = {}
        for recipe_name in CookBookRepository.get_cookbook_metadata().keys():
            file_metadata = CookBookRepository._get_metadata_from_md(f"recettes/{recipe_name}.md")
            if file_metadata != '':
                files_metadata[recipe_name] = file_metadata
        return files_metadata

    @staticmethod
    def get_recipes_times_cooked():
        recipes_cooked_dates = {}
        for key, value in CookBookRepository.get_cookbook_metadata().items():
            recipes_cooked_dates[key] = len(value[CookBookRepository.COOKED_DATES_TAG])
        return recipes_cooked_dates

    @staticmethod
    def add_recipe_cooked_date(recipe_name):
        CookBookRepository.update_cookbook_metadata()
        cookbook_metadata = CookBookRepository.get_cookbook_metadata()
        if recipe_name not in cookbook_metadata.keys():
            cookbook_metadata[recipe_name] = CookBookRepository.RECIPE_METADATA_TEMPLATE
        cookbook_metadata[recipe_name][CookBookRepository.COOKED_DATES_TAG].append(
            datetime.now().isoformat())
        CookBookRepository.set_cookbook_metadata(cookbook_metadata)

    @staticmethod
    def update_cookbook_metadata():
        cookbook_metadata = CookBookRepository.get_cookbook_metadata()
        for recipe in CookBookRepository.RECIPES_NAMES_LIST:
            if recipe not in cookbook_metadata.keys():
                cookbook_metadata[recipe] = CookBookRepository.RECIPE_METADATA_TEMPLATE
        CookBookRepository.set_cookbook_metadata(cookbook_metadata)


class MealGenerator:
    """
    MealGenerator
    """
    NB_PORTIONS_PER_RECIPE = 4  # I plan to set the number of portions for each recipe
    NB_LUNCHES_PER_DAY = 2
    NB_BREAKFASTS_PER_DAY = 2

    week_plan_profile = lambda nb_people=1: {
        "meals": {
            "lunch": math.ceil(
                7 * MealGenerator.NB_LUNCHES_PER_DAY * nb_people / MealGenerator.NB_PORTIONS_PER_RECIPE),
            "breakfast": math.ceil(
                2 * MealGenerator.NB_BREAKFASTS_PER_DAY * nb_people / MealGenerator.NB_PORTIONS_PER_RECIPE),
            "snack": math.ceil(
                2 * nb_people / MealGenerator.NB_PORTIONS_PER_RECIPE),
        },
        "filters": {
            "type": "meal",
            "opportunity": None
        }
    }

    @staticmethod
    def generate_meal_plan(profile):
        recipes_metadata = CookBookRepository.get_recipes_metadata()
        cookbook_metadata = CookBookRepository.get_cookbook_metadata()
        recipes_names = list(cookbook_metadata.keys())

        def match_filter(name, flt):
            if profile["filters"][flt] is None and flt not in recipes_metadata[name]:
                return True
            if flt not in recipes_metadata[name]:
                return False
            return recipes_metadata[name][flt] == profile["filters"][flt]

        def match_meal(name, meal):
            if "meal" not in recipes_metadata[name]:
                return False
            return recipes_metadata[name]["meal"] == meal

        def filter_recipes(rcp_names):
            rcp_nm = copy.copy(rcp_names)
            for flt in profile["filters"]:
                rcp_nm = list(filter(lambda name: match_filter(name, flt), recipes_names))
            return rcp_nm

        def pick_recipes_per_meal(rcp_names):
            meal_plan = {}
            for meal, quantity in profile["meals"].items():
                rcp_nm = copy.copy(rcp_names)
                rcp_nm = list(filter(lambda name: match_meal(name, meal), rcp_nm))
                # sort by least cooked recipe ascending
                rcp_nm.sort(key=lambda a: len(cookbook_metadata[a]["cooked dates"]))
                if len(rcp_nm) > 2 * quantity:  # two times more meals than what the profile needs
                    rcp_nm = rcp_nm[:int(len(rcp_nm) / 2 + 1)]  # select the 50% less cooked recipes
                random.shuffle(rcp_nm)
                # select the desired quantity if there is enough filtered recipes
                if len(rcp_nm) > quantity:
                    rcp_nm = rcp_nm[:int(quantity)]
                meal_plan[meal] = rcp_nm

            return meal_plan

        meal_plan = pick_recipes_per_meal(filter_recipes(recipes_names))

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


for arg in sys.argv:
    if arg == "export":
        export_complete_cookbook()
    if arg == "update":
        CookBookRepository.update_cookbook_metadata()
