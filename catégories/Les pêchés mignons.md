## Cheat-meals

```dataview
LIST
FROM #cheat-meal
WHERE recipe-type = "meal"
SORT file.name ASC
```

## Pour les occasions

```dataview
LIST
FROM #occasion
WHERE recipe-type = "meal"
SORT file.name ASC
```
