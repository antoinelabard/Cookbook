#!/usr/bin/python3

import os
import sys
import yaml

RECIPE_DIR = "recettes"

files_list_by_dir = lambda directory: os.popen(f'find {directory} -name "*.md"').readlines()


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


def _get_files_metadata():
    """
    :return: the metadata of all the files in a dictionary
    """
    files_metadata = {}
    for file in files_list_by_dir(RECIPE_DIR):
        file_metadata = _get_metadata_from_md(file.replace('\n', ''))
        if file_metadata != '':
            files_metadata[file.split('/')[-1].replace('.md\n', '')] = file_metadata
    return files_metadata


def export_complete_cookbook():
    """
    create a document containing quotes of the recipes contained in the cookbook.
    """

    recipes_list = lambda directory: "{}".format('\n'.join(files_wikilinks(sorted(files_list_by_dir(directory)))))

    complete_cookbook = """# Livre de recettes
    
    {}""".replace("    ", "")

    files_wikilinks = lambda files_list: map(lambda file: '![[{}]]'.format(file.split('/')[-1].replace('.md\n', '')), files_list)

    with open("livre de recettes.md", 'w') as f:
        f.write(complete_cookbook.format(recipes_list(RECIPE_DIR)))


for arg in sys.argv:
    if arg == "export":
        export_complete_cookbook()
