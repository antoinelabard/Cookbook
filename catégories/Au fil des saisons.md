## Printemps

```dataview
LIST
FROM "recettes"
WHERE ((season = "spring") OR contains(season, "spring"))
AND recipe-type = "meal"
```

## Été

```dataview
LIST
FROM "recettes"
WHERE ((season = "summer") OR contains(season, "summer"))
AND recipe-type = "meal"
```

## Automne

```dataview
LIST
FROM "recettes"
WHERE ((season = "autumn") OR contains(season, "autumn"))
AND recipe-type = "meal"
```

## Hiver

```dataview
LIST
FROM "recettes"
WHERE ((season = "winter") OR contains(season, "winter"))
AND recipe-type = "meal"
```
