#!/usr/bin/python3

import os
import sys
import yaml
import json
from datetime import datetime

RECIPE_DIR = "recettes"


def _delete_all_indexes():
    for file in os.listdir(RECIPE_DIR):
        os.unlink(os.path.join(RECIPE_DIR, file))


def _get_metadata_from_md(path):
    """
    :param path: the path to the markdown file containing the metadata
    :return: an empty string if there is no metadata in the file. Otherwise, return a dictionary of the metadata
    """

    metadata_marker = "---\n"
    with open(path, 'r') as f:
        lines = f.readlines()
    metadata = ""
    if lines[0] != metadata_marker:
        return ''
    for i in lines[1:]:  # skip first line as it is metadata_marker
        if i == metadata_marker:
            break
        metadata += i
    return yaml.safe_load(metadata)


def _get_recipes_metadata():
    """
    :return: the metadata of all the files in a dictionary
    """
    files_metadata = {}
    for file in CookBookRepository.RECIPES_NAMES_LIST:
        file_metadata = _get_metadata_from_md(file.replace('\n', ''))
        if file_metadata != '':
            files_metadata[file.split('/')[-1].replace('.md\n', '')] = file_metadata
    return files_metadata


def export_complete_cookbook():
    """
    create a document containing quotes of the recipes contained in the cookbook.
    """

    recipes_list = lambda: "{}".format('\n'.join(files_wikilinks(sorted(CookBookRepository.RECIPES_NAMES_LIST))))

    complete_cookbook = """# Livre de recettes
    
    {}""".replace("    ", "")

    files_wikilinks = lambda files_list: map(lambda file: '![[{}]]'.format(file.split('/')[-1].replace('.md\n', '')), files_list)

    with open("livre de recettes.md", 'w') as f:
        f.write(complete_cookbook.format(recipes_list()))


class CookBookRepository:
    RECIPES_NAMES_LIST = list(map(
        lambda x: x.split('/')[-1].replace('\n', '').replace('.md', ''),
        os.popen(f'find {RECIPE_DIR} -name "*.md"').readlines()
    ))

    RECIPES_TAG = "recipes"
    COOKED_DATES_TAG = "cooked dates"

    RECIPE_METADATA_TEMPLATE = {COOKED_DATES_TAG: []}

    @staticmethod
    def get_cookbook_metadata():
        with open('recipes_metadata.json', 'r') as f:
            return json.load(f)

    @staticmethod
    def set_cookbook_metadata(recipes_metadata):
        with open('recipes_metadata.json', 'w') as f:
            json.dump(recipes_metadata, f, indent=4)  # you can add indent=4 when debugging to format the json file

    @staticmethod
    def get_recipes_cooked_dates():
        recipes_cooked_dates = {}
        for key, value in CookBookRepository.get_cookbook_metadata()[CookBookRepository.RECIPES_TAG].items():
            recipes_cooked_dates[key] = value[CookBookRepository.COOKED_DATES_TAG]
        return recipes_cooked_dates

    @staticmethod
    def get_recipe_cooked_dates(recipe_name):
        cookbook_metadata = CookBookRepository.get_cookbook_metadata()
        if recipe_name not in cookbook_metadata[CookBookRepository.RECIPES_TAG].keys():
            return []
        return cookbook_metadata[CookBookRepository.RECIPES_TAG][recipe_name][CookBookRepository.COOKED_DATES_TAG]

    @staticmethod
    def add_recipe_cooked_date(recipe_name):
        CookBookRepository.update_recipes_list()
        cookbook_metadata = CookBookRepository.get_cookbook_metadata()
        if recipe_name not in cookbook_metadata[CookBookRepository.RECIPES_TAG].keys():
            cookbook_metadata[CookBookRepository.RECIPES_TAG][recipe_name] = CookBookRepository.RECIPE_METADATA_TEMPLATE
        cookbook_metadata[CookBookRepository.RECIPES_TAG][recipe_name][CookBookRepository.COOKED_DATES_TAG].append(datetime.now().isoformat())
        CookBookRepository.set_cookbook_metadata(cookbook_metadata)

    @staticmethod
    def update_recipes_list():
        cookbook_metadata = CookBookRepository.get_cookbook_metadata()
        for recipe in CookBookRepository.RECIPES_NAMES_LIST:
            if recipe not in cookbook_metadata[CookBookRepository.RECIPES_TAG].keys():
                cookbook_metadata[CookBookRepository.RECIPES_TAG][recipe] = CookBookRepository.RECIPE_METADATA_TEMPLATE
        CookBookRepository.set_cookbook_metadata(cookbook_metadata)


for arg in sys.argv:
    if arg == "export":
        export_complete_cookbook()
