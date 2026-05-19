```dataview
TABLE rows.file.link AS "Notes"
FROM "recettes"
FLATTEN file.etags AS tag
WHERE contains(tag, "composite/")
GROUP BY tag
SORT tag ASC
```
