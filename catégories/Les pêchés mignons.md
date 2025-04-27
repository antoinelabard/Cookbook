## Cheat-meals

```dataview
LIST
FROM "recettes"
WHERE recipe-type = "meal"
AND tags = "cheat-meal"
SORT file.name ASC
```

## Pour les occasions

```dataview
LIST
FROM "recettes"
WHERE recipe-type = "meal"
AND tags = "occasion"
SORT file.name ASC
```
