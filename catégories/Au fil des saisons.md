## Printemps

```dataview
LIST
FROM "recettes"
WHERE (season = "spring") OR contains(season, "spring")
```

## Été

```dataview
LIST
FROM "recettes"
WHERE (season = "summer") OR contains(season, "summer")
```

## Automne

```dataview
LIST
FROM "recettes"
WHERE (season = "autumn") OR contains(season, "autumn")
```

## Hiver

```dataview
LIST
FROM "recettes"
WHERE (season = "winter") OR contains(season, "winter")
```
