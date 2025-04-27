## Petits déjeuners

```dataview
LIST
FROM "recettes"
WHERE meal = "breakfast"
AND recipe-type = "meal"
AND !tags
SORT file.name ASC
```

## Goûters

```dataview
LIST
FROM "recettes"
WHERE meal = "snack"
AND recipe-type = "meal"
AND !tags
SORT file.name ASC
```

## Déjeuners

```dataview
LIST
FROM "recettes"
WHERE meal = "lunch"
AND recipe-type = "meal"
AND !tags
SORT file.name ASC
```
