#!/usr/bin/python3

"""
NAME
    cookbook.py - Generate custom meals.

SYNOPSIS
    ./cookbook.py [OPTION]...

DESCRIPTION
    cookbook.py is intended to generate a random menu matching some filters. Those filters can be given as command line
    arguments, but they also can be given via profiles defines in the script. This script is used to make sure that no
    human mind is involved in the random generation of menus, as it is bad at randomness and risks promote some recipes
    over others. The idea is to randomly pick the recipes matching the provided filters using a draw without discount
    and bet on the equiprobability of each recipe to be chosen in order to statistically select every recipe over time.

CONFIGURATION
    cookbook.py can take several arguments:
        - export: create a markdown file containing wikilinks for all the recipes of the cookbook. It can be read using
        Obsidian (https://obsidian.md).
        - plan=PLAN: generate a menu following the filters pointed by PLAN (defined in the script)
        - filter=VALUE: set a custom filter that the recipes need to match. Here is the list of filters with their
        expected value:
            - type: "meal"|"ingredient"|"inedible"
            - opportunity: None|"cheat-meal"|"party"|"pleasure"
            - lunch: integer
            - breakfast: integer
            - snack: integer
            - appetizer: integer
"""
from __future__ import annotations
import sys
from enum import Enum
from typing import Dict, Any, Tuple, List, Callable

import yaml
import math
import random
from pathlib import Path




def process_arguments():
    args = {
        Tag.TYPE: Tag.MEAL,
        Tag.LUNCH: 0,
        Tag.BREAKFAST: 0,
        Tag.SNACK: 0,
        Tag.APPETIZER: 0,
        Tag.OPPORTUNITY: None,
        Tag.NB_PEOPLE: 1
    }
    for arg in sys.argv:
        if "export" in arg:
            CookBookRepository().export_complete_cookbook()
            return
        if "plan" in arg:
            plan = arg.split('=')[-1]
            if plan == "week":
                args[Tag.TYPE] = Tag.MEAL
                args[Tag.OPPORTUNITY] = None
                args[Tag.LUNCH] = math.ceil(7 * Options.NB_LUNCHES_PER_DAY / Options.NB_PORTIONS_PER_RECIPE)
                print(math.ceil(7 * Options.NB_LUNCHES_PER_DAY / Options.NB_PORTIONS_PER_RECIPE))
                args[Tag.BREAKFAST] = math.ceil(7 * Options.NB_BREAKFASTS_PER_DAY / Options.NB_PORTIONS_PER_RECIPE)
                args[Tag.SNACK] = math.ceil(7 * Options.NB_SNACKS_PER_DAY / Options.NB_PORTIONS_PER_RECIPE)
                args[Tag.APPETIZER] = 0
        if '=' in arg:
            s = arg.split('=')
            args[s[0]] = s[-1]
    MealGenerator(
        recipe_type=args[Tag.TYPE],
        opportunity=args[Tag.OPPORTUNITY],
        nb_lunch=int(args[Tag.LUNCH]),
        nb_breakfast=int(args[Tag.BREAKFAST]),
        nb_snack=int(args[Tag.SNACK]),
        nb_appetizers=int(args[Tag.APPETIZER]),
    ).generate_meal_plan(int(args[Tag.NB_PEOPLE]))


if __name__ == "__main__":
    process_arguments()
