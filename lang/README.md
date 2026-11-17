# Translations

Each UI language is one JSON file in this folder. The app finds them
automatically and lists them under **Settings → Language**.

## Adding a new language

1. Create a copy of `en.json`, either by hand or with
   `python check_translations.py --new fi "Suomi"`
2. In `_meta`, set `code` (file name without `.json`) and `name`
   (how the language appears in the menu, in that language itself).
3. Translate the **values** only. Never change the keys on the left.
4. Run `python check_translations.py` to see missing or untranslated keys.
5. In the app, choose **Settings → Language → Reload language files**.
   You don't need to restart.

## Rules

- Files must be saved as UTF-8.
- Keep symbols such as `→`, `|` and `—` and keyboard shortcuts (`R`, `L`, `Del`, `Ctrl`) as they are.
- If a key is missing, the English text is shown instead, so a partial translation still works.
- Keys starting with `_` (e.g. `_meta`) are not UI text.

## Furniture categories

Built-in categories (`living_room`, `kitchen`, …) are translated here.
Categories you create in the app store their own names per language in
`library/_categories.json`. To rename one in another language, switch the app
to that language and use **Manage categories → Rename**.
