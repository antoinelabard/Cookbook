# Livre de recettes

## 👋 Présentation

> [!faq] Salut ! Moi, c'est Antoine.
>  <div><img src="photo.webp" alt="profile picture" width="100" height="100" style="margin: 20px; float: right; shape: circle();"><p style="text-align:justify;">J'ai mis en ligne ce site web pour partager mon livre de recettes. Il s'agit de toutes les recettes que j'essaie et que je sauvegarde pour ne jamais manquer d'idée !<br><br>N'hésitez pas à me faire part de vos retours ou de vos astuces pour les améliorer.</p></div>

> [!important] [[Menu de la semaine]]

## 🌮 Sélections

```dataview
TABLE without id file.link as "Dernières recettes ajoutées", dateformat(date-added, "yyyy-MM-dd") AS "Ajout"
FROM "recettes" 
SORT date-added DESC
LIMIT 10
```

<br>

```dataview
TABLE without id file.link as "Catégories"
FROM "catégories"
```

## 🤝 Contribution

Vous pouvez retrouver le repository de ce livre sur GitHub : **[https://github.com/antoinelabard/Cookbook](https://github.com/antoinelabard/Cookbook)**. Si vous avez des suggestions d'améliorations des recettes, vous pouvez me contacter ou utiliser GitHub si vous le maîtrisez.

❤️ Merci aux contributeurs du projet :

- Alexis Goblot
- Katy Osmont
- Nicolas Noirault

## 🧑‍💻 Technologies

Ce livre de recette a été rédigé avec **[Obsidian](http://obsidian.md)**. Le site web est généré avec le plugin **[Webpage HTML Export](https://github.com/KosmosisDire/obsidian-webpage-export)** et est hébergé sur **[GitHub Pages](https://pages.github.com/)**.

Un script de génération de menus est également disponible si vous téléchargez le livre de recettes hors ligne. Pour comprendre comment s'en servir, rendez-vous **[ici](https://github.com/antoinelabard/Cookbook/blob/main/cookbook.py)**.
