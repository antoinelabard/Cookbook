## Petits déjeuners

```dataview
LIST
FROM "recettes"
WHERE meal = "breakfast"
AND recipe-type = "meal"
AND !tags
```

## Goûters

```dataview
LIST
FROM "recettes"
WHERE meal = "snack"
AND recipe-type = "meal"
AND !tags
```

## Déjeuners

```dataview
LIST
FROM "recettes"
WHERE meal = "lunch"
AND recipe-type = "meal"
AND !tags
```
