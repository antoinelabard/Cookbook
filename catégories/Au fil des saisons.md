## Printemps

```dataview
LIST
FROM "recettes"
WHERE ((season = "spring") OR contains(season, "spring"))
AND recipe-type = "meal"
AND meal = "lunch"
AND !tags
SORT file.name ASC
```

## Été

```dataview
LIST
FROM "recettes"
WHERE ((season = "summer") OR contains(season, "summer"))
AND recipe-type = "meal"
AND meal = "lunch"
AND !tags
SORT file.name ASC
```

## Automne

```dataview
LIST
FROM "recettes"
WHERE ((season = "autumn") OR contains(season, "autumn"))
AND recipe-type = "meal"
AND meal = "lunch"
AND !tags
SORT file.name ASC
```

## Hiver

```dataview
LIST
FROM "recettes"
WHERE ((season = "winter") OR contains(season, "winter"))
AND recipe-type = "meal"
AND meal = "lunch"
AND !tags
SORT file.name ASC
```

## Toute l'année

```dataview
LIST
FROM "recettes"
WHERE !season
AND recipe-type = "meal"
AND meal = "lunch"
AND !tags
SORT file.name ASC
```
