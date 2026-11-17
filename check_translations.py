# -*- coding: utf-8 -*-
"""
Translation helper for MyCAD.

    python check_translations.py           -> check every lang/*.json against en.json
    python check_translations.py --new fi "Suomi"
                                           -> create lang/fi.json from en.json to translate

The check lists keys that are missing (shown in English in the app), keys that
no longer exist in en.json, values that are still identical to English, and
mismatched {placeholders}.
"""
import json
import os
import re
import sys

LANG_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "lang")
REF = "en"


def load(path):
    with open(path, "r", encoding="utf-8") as fp:
        return json.load(fp)


def strings(data):
    return {k: v for k, v in data.items() if not k.startswith("_")}


def new_language(code, name):
    src = os.path.join(LANG_DIR, f"{REF}.json")
    dst = os.path.join(LANG_DIR, f"{code}.json")
    if os.path.exists(dst):
        print(f"{dst} already exists - not overwriting.")
        return 1
    data = {"_meta": {"code": code, "name": name, "author": "", "version": ""}}
    data.update(strings(load(src)))
    with open(dst, "w", encoding="utf-8", newline="\n") as fp:
        json.dump(data, fp, indent=4, ensure_ascii=False)
        fp.write("\n")
    print(f"Created {dst}. Translate the values (not the keys), then run this script again.")
    return 0


def check():
    ref = strings(load(os.path.join(LANG_DIR, f"{REF}.json")))
    placeholder = re.compile(r"\{[^}]*\}")
    problems = 0
    for fname in sorted(os.listdir(LANG_DIR)):
        if not fname.endswith(".json") or fname == f"{REF}.json":
            continue
        try:
            data = load(os.path.join(LANG_DIR, fname))
        except json.JSONDecodeError as e:
            print(f"\n{fname}: INVALID JSON - {e}")
            problems += 1
            continue
        meta = data.get("_meta", {})
        tr = strings(data)
        missing = [k for k in ref if k not in tr]
        extra = [k for k in tr if k not in ref]
        same = [k for k in ref if k in tr and tr[k] == ref[k] and re.search(r"[A-Za-z]{3}", ref[k])]
        ph = [k for k in ref if k in tr and
              sorted(placeholder.findall(ref[k])) != sorted(placeholder.findall(tr[k]))]
        done = len(ref) - len(missing)
        print(f"\n{fname}  ({meta.get('name', '?')})  {done}/{len(ref)} keys")
        for title, keys in (("missing", missing), ("unused (not in en.json)", extra),
                            ("same as English - check if translated", same),
                            ("placeholder mismatch", ph)):
            if keys:
                print(f"  {title}:")
                for k in keys:
                    print(f"    {k}: {ref.get(k, tr.get(k))!r}")
        problems += len(missing) + len(ph)
    return 1 if problems else 0


if __name__ == "__main__":
    if len(sys.argv) >= 3 and sys.argv[1] == "--new":
        sys.exit(new_language(sys.argv[2], sys.argv[3] if len(sys.argv) > 3 else sys.argv[2]))
    sys.exit(check())
