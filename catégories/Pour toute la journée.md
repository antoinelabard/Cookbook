## Petits déjeuners

```dataview
LIST
FROM "recettes"
WHERE meal = "breakfast"
AND !tags
```

## Goûters

```dataview
LIST
FROM "recettes"
WHERE meal = "snack"
AND !tags
```

## Déjeuners

```dataview
LIST
FROM "recettes"
WHERE meal = "lunch"
AND !tags
```
