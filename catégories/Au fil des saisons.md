## Printemps

```dataview
LIST
FROM "recettes"
WHERE ((season = "spring") OR contains(season, "spring"))
AND recipe-type = "meal"
AND meal = "lunch"
AND !tags
```

## Été

```dataview
LIST
FROM "recettes"
WHERE ((season = "summer") OR contains(season, "summer"))
AND recipe-type = "meal"
AND meal = "lunch"
AND !tags
```

## Automne

```dataview
LIST
FROM "recettes"
WHERE ((season = "autumn") OR contains(season, "autumn"))
AND recipe-type = "meal"
AND meal = "lunch"
AND !tags
```

## Hiver

```dataview
LIST
FROM "recettes"
WHERE ((season = "winter") OR contains(season, "winter"))
AND recipe-type = "meal"
AND meal = "lunch"
AND !tags
```

## Toute l'année

```dataview
LIST
FROM "recettes"
WHERE !season
AND recipe-type = "meal"
AND meal = "lunch"
AND !tags
```