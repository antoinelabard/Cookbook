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

## Autres

```dataview
LIST
FROM "recettes"
WHERE meal = "misc"
AND !tags
```

## Déjeuners

```dataview
LIST
FROM "recettes"
WHERE meal = "lunch"
AND !tags
```
