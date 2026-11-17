# -*- coding: utf-8 -*-
"""
Floor Plan Maker V15 (Multi-language & Multi-units)
===================================================
UI languages are loaded from separate JSON files in the lang/ folder, the
furniture library and its categories from the library/ folder.
Metric and Imperial unit conversion. Walls have height/thickness and can hold
doors and windows; the plan can be viewed in 3D (built-in software renderer
on a Tk Canvas) and exported as Wavefront OBJ.
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox, colorchooser
from math import sqrt, cos, sin, tan, radians, pi, atan2, hypot, ceil
import json
import os
import sys
import shutil
import re
import time
import unicodedata

# ─────────────────────────────────────────────────────────────────────────────
#  Paths - everything lives next to the script, so the app behaves the same
#  no matter which folder it was started from.
# ─────────────────────────────────────────────────────────────────────────────
if getattr(sys, "frozen", False):
    # Built with PyInstaller (EXE / standalone): keep settings, library and
    # language files next to the executable, not in the temporary unpack dir.
    APP_DIR = os.path.dirname(os.path.abspath(sys.executable))
    BUNDLE_DIR = getattr(sys, "_MEIPASS", APP_DIR)
else:
    try:
        APP_DIR = os.path.dirname(os.path.abspath(__file__))
    except NameError:
        APP_DIR = os.getcwd()
    BUNDLE_DIR = APP_DIR

CONFIG_PATH = os.path.join(APP_DIR, "config.json")

# ─────────────────────────────────────────────────────────────────────────────
#  Translations
#  Every UI language is a separate JSON file in the lang/ folder
#  (lang/et.json, lang/en.json, ...). To add a language, copy en.json to
#  e.g. lang/fi.json, change "_meta" -> "code"/"name" and translate the
#  values - it shows up in Settings -> Language automatically. Keys missing
#  from a language file fall back to English, then to FALLBACK_STRINGS below.
# ─────────────────────────────────────────────────────────────────────────────
LANG_DIR = os.path.join(APP_DIR, "lang")
DEFAULT_LANGUAGE = "et"

# Built-in English strings: only used when lang/ is missing or a key is not
# present in any language file. lang/en.json is written from this on first run.
FALLBACK_STRINGS = {
    "title": "Floor Plan Maker V15",
    "file": "File",
    "save_proj": "Save Project...",
    "load_proj": "Open Project...",
    "settings": "Settings",
    "language": "Language",
    "units": "Unit System",
    "metric": "Metric",
    "imperial": "Imperial",
    "select": "Select",
    "wall": "Wall",
    "freehand": "Freehand",
    "edit": "Edit",
    "hide_furn": "Hide Furniture",
    "style": "Style",
    "line_width": "Line width",
    "line_wall": "4 px (wall)",
    "line_furn": "2 px (furniture / detail)",
    "color": "Color",
    "black": "Black",
    "blue": "Blue",
    "red": "Red",
    "add_room": "Add Room",
    "width": "Width",
    "height": "Height",
    "create_room": "Create Room",
    "grid": "Grid",
    "help": "Help",
    "floor": "Floor",
    "add_floor": "Add Floor",
    "ghost_info": "Gray dashed lines = walls of the floor below (cannot be selected/moved)",
    "furniture": "Furniture",
    "furn_help": "Click → Place  |  R / L = Rotate",
    "saved_title": "Saved",
    "saved_msg": "Project saved:",
    "error_title": "Error",
    "json_files": "JSON files",
    "all_files": "All files",
    "help_r": "R / r — rotate furniture clockwise",
    "help_l": "L / l — rotate furniture counter-clockwise",
    "help_del": "Del — delete selected",
    "help_ctrl_click": "Ctrl + click — add to selection",
    "help_shift_click": "Shift + click — remove from selection",
    "help_drag": "Drag empty area — multi-select items",
    "help_zoom": "Ctrl + scroll — zoom",
    "help_pan": "Middle mouse — pan view",
    "living_room": "Living Room",
    "dining_room": "Dining Room",
    "bedroom": "Bedroom",
    "kitchen": "Kitchen",
    "bathroom": "Bathroom",
    "stairs": "Stairs",
    "sofa_3_lbl": "Sofa 3-seater",
    "sofa_2_lbl": "Sofa 2-seater",
    "armchair_lbl": "Armchair",
    "coffee_tbl_lbl": "Coffee Table",
    "tv_stand_lbl": "TV Stand",
    "tv_lbl": "TV",
    "table_rect_lbl": "Dining Table (rect)",
    "table_round_lbl": "Round Table",
    "chair_lbl": "Chair",
    "bed_double_lbl": "Double Bed",
    "bed_single_lbl": "Single Bed",
    "wardrobe_lbl": "Wardrobe",
    "desk_lbl": "Desk",
    "fridge_lbl": "Fridge",
    "stove_lbl": "Stove",
    "sink_k_lbl": "Kitchen Sink",
    "dishwasher_lbl": "Dishwasher",
    "kitchen_cnt_lbl": "Kitchen Counter",
    "bath_lbl": "Bathtub",
    "shower_lbl": "Shower",
    "toilet_lbl": "Toilet",
    "sink_b_lbl": "Bathroom Sink",
    "wash_mach_lbl": "Washing Machine",
    "stairs_lbl": "Stairs",
    "spiral_stairs_lbl": "Spiral Stairs",
    "ladder_lbl": "Ladder",
    "measure": "Measure",
    "clear_measure": "Clear Measurements",
    "auto_rooms": "Auto Rooms",
    "room_lbl": "Room",
    "theme": "Theme",
    "theme_light": "Light",
    "theme_dark": "Dark",
    "help_measure": "M — measuring tool",
    "help_esc": "Esc — cancel current drawing",
    "new_furniture": "+ New Furniture",
    "furn_name": "Name",
    "furn_category": "Category",
    "furn_draw_help": "Draw one or more shapes, then Save. Ctrl + wheel zooms, wheel scrolls (Shift + wheel sideways). Select tool: drag to move a shape. Polygon: click points, double-click to finish.",
    "undo_point": "Undo Point",
    "clear_shape": "Clear Points",
    "finish_shape": "Finish Shape",
    "furn_tool_polygon": "✏ Polygon",
    "furn_tool_rect": "▭ Rectangle",
    "furn_tool_circle": "◯ Circle",
    "furn_tool_triangle": "△ Triangle",
    "furn_tool_select": "✥ Select",
    "rotate_left": "⟲ Rotate",
    "rotate_right": "⟳ Rotate",
    "delete_element": "🗑 Delete Shape",
    "clear_all": "🧹 Clear All",
    "furn_name_required": "Please enter a name",
    "furn_shape_required": "Draw at least 3 points first",
    "custom_cat": "Custom",
    "save": "Save",
    "cancel": "Cancel",
    "door_lbl": "Door",
    "furn_colour": "Colour",
    "furn_library_list": "Existing Furniture",
    "furn_builtin_readonly": "Built-in furniture can be deleted but not edited.",
    "delete": "Delete",
    "new_item": "New",
    "update": "Update",
    "confirm_title": "Confirm",
    "confirm_delete_furniture": "Delete this furniture piece from the library?",
    "categories": "Categories",
    "manage_categories": "Manage Categories...",
    "new_category": "New Category",
    "category_name": "Category name",
    "rename": "Rename",
    "add": "Add",
    "close": "Close",
    "ok": "OK",
    "category_exists": "A category with this name already exists.",
    "category_not_empty": "This category still has furniture in it. Move the furniture to another category or delete it first.",
    "confirm_delete_category": "Delete this category?",
    "category_name_required": "Please enter a category name",
    "reload_languages": "Reload language files",
    "items_count": "pcs",
    "door_tool": "Door",
    "window_tool": "Window",
    "view_3d": "3D View",
    "export_obj": "Export 3D (OBJ)...",
    "obj_files": "OBJ 3D model",
    "exported_title": "Exported",
    "exported_msg": "3D model saved:",
    "wall_props": "Wall Properties",
    "wall_height": "Wall height",
    "wall_thickness": "Wall thickness",
    "apply_all_walls": "Apply to all walls on this floor",
    "wall_defaults": "Wall Defaults...",
    "opening_props_door": "Door Properties",
    "opening_props_window": "Window Properties",
    "sill_height": "Sill height",
    "hinge_other_end": "Hinge on the other side",
    "swing_other_side": "Opens to the other side",
    "furn_props": "Furniture Properties",
    "height_3d": "Height (3D)",
    "elevation": "Height above floor",
    "invalid_number": "Please enter valid numbers (not negative).",
    "show_all_floors": "All floors",
    "reset_view": "Reset view",
    "refresh": "Refresh",
    "view3d_help": "Drag: rotate  |  Right drag: pan  |  Wheel: zoom  |  WASD / QE: move",
    "help_openings": "Door / Window — click on a wall to add, drag in Edit mode to move",
    "help_door_r": "R / L — change the swing of the selected door",
    "help_dbl": "Double-click — properties (wall, door, window, furniture)",
    "doors_windows": "Doors & Windows",
    "window_lbl": "Window",
    "auto_stack": "Stack",
    "stack_copies": "Add copies on top (pcs)",
    "help_dup": "Ctrl + D — copy selected furniture on top of itself",
    "help_stack": "Stack on — furniture put on other furniture goes on top of it",
    "help_title": "Keyboard shortcuts",
    "help_more": "More instructions: Info_EN.txt next to the program",
    "hs_general": "General",
    "hs_view": "Moving around",
    "hs_draw": "Drawing",
    "hs_select": "Selecting and editing",
    "hs_furn": "Furniture",
    "hs_open": "Doors and windows",
    "hs_3d": "3D view",
    "hk_f1": "F1 | Show / close this help",
    "hk_esc": "Esc | Cancel the current wall or measurement, leave the Door / Window / furniture tool",
    "hk_zoom": "Ctrl + mouse wheel | Zoom in / out",
    "hk_scroll": "Mouse wheel | Scroll up / down",
    "hk_hscroll": "Shift + mouse wheel | Scroll left / right",
    "hk_pan": "Middle mouse + drag | Move the view",
    "hk_wall": "Wall: click, click | Start and end of a wall (always straight, snaps to grid)",
    "hk_m": "M | Measuring tool",
    "hk_measure_shift": "Shift (measuring) | Keep the measurement horizontal / vertical",
    "hk_click": "Click | Select an item",
    "hk_ctrl_click": "Ctrl + click | Add to / remove from selection",
    "hk_shift_click": "Shift + click | Remove from selection",
    "hk_box": "Drag on empty area | Select several items",
    "hk_drag_edit": "Drag (Edit mode) | Move, or resize with the handles",
    "hk_dbl": "Double-click | Properties (wall, door, window, furniture)",
    "hk_del": "Del | Delete selected",
    "hk_place": "Click in panel, click in plan | Place furniture (Stack on: lands on top of what's below)",
    "hk_rl": "R / L | Rotate selected furniture clockwise / counter-clockwise",
    "hk_ctrl_d": "Ctrl + D | Copy selected furniture on top of itself",
    "hk_open_click": "Door / Window + click on wall | Add a door or window",
    "hk_open_drag": "Drag (Edit mode) | Move a door or window along its wall",
    "hk_open_rl": "R / L | Change the swing of the selected door",
    "hk3_rot": "Left mouse + drag, arrow keys | Rotate the view",
    "hk3_pan": "Right / middle mouse + drag, Shift + drag | Move the view",
    "hk3_zoom": "Mouse wheel, + / - | Zoom",
    "walk_mode": "Walk mode",
    "hk3_wasd": "W / A / S / D | Move forward / left / back / right",
    "hk3_qe": "Q / E | Move down / up",
    "hk3_shift": "Shift + W A S D Q E | Move faster",
    "hk3_walk": "🚶 Walk mode | Eye-level view: drag turns your head, wheel takes steps",
    "grid_size": "Grid",
    "furn_dims": "Dimensions",
    "furn_width": "Width",
    "furn_depth": "Depth",
    "apply_dims": "Apply width × depth",
    "dims_hint": "Type width and depth and press Enter: the drawing is resized to that size (or a rectangle is created if nothing is drawn yet).",
    "height_hint": "Height (3D) = how tall the piece is in the 3D view.",
    "cursor_pos": "Cursor",
    "selected_shape": "Selected shape",
    "storage": "Storage",
    "storage_shelf_lbl": "Storage shelf",
    "storage_box_lbl": "Box",
    "furn_type": "Type",
    "furn_type_solid": "Solid",
    "furn_type_shelf": "Shelf",
    "shelf_levels": "Shelf boards",
    "shelf_bottom": "Lowest board from floor",
    "shelf_hint": "Boards are spread evenly up to the top. Things put on the shelf go to the lowest free board they fit on; PageUp / PageDown moves them between boards.",
    "shelf_invalid": "Shelf: boards must be 2–30 and the lowest board must be below the height.",
    "hk_pg": "PageUp / PageDown | Move selected piece one shelf / stack place up or down",
    "shelf_view": "Shelf view",
    "view_other_side": "View from the other side",
    "add_to_shelf": "Put on shelf",
    "copy": "Copy",
    "properties": "Properties",
    "front_side": "front",
    "no_room": "No free space there.",
    "click_to_place": "click a board to place it (Esc = stop)",
    "top_view_board": "From above: the board at {z} cm (drag up/down to move a piece further back or to the front)",
    "top_view_all": "From above: everything in the shelf (select a piece to see its board only)",
    "shelf_view_help": "Drag a piece sideways or onto another board – it never goes through boards or other pieces. Choose an item above, press Add and click a board to put it there. Double-click a piece for its properties.",
    "hs_shelf": "Shelf view",
    "hk_sv_open": "Double-click a shelf (or something in it) | Open the shelf front view",
    "hk_sv_drag": "Drag in the front view | Move sideways / to another board",
    "hk_sv_add": "Add + click on a board | Put a library item on the shelf",
    "hk_sv_top": "Drag in the strip below | Move further back / to the front",
    "hk_sv_keys": "← / → (Shift: 5 cm), PageUp / PageDown | Move by 1 cm, move one board up / down",
    "hk_sv_copy": "Ctrl + D, Del | Copy next to it, delete",
    "hk_sv_esc": "Esc | Stop adding / close the shelf view",
    "collapse_all": "Collapse all",
    "expand_all": "Expand all",
    "splash_subtitle": "Floor plan & room designer",
    "splash_author": "Made by Germo",
    "splash_country": "Estonia",
    "splash_lang": "Loading languages…",
    "splash_lib": "Loading furniture library…",
    "splash_ui": "Building the interface…",
    "splash_ready": "Ready!",
}


def load_languages():
    """Read every lang/*.json file. Returns {code: {"name": str, "strings": dict}}.
    If the folder is missing it is created and seeded with en.json."""
    bundled = os.path.join(BUNDLE_DIR, "lang")
    if not os.path.isdir(LANG_DIR) and os.path.isdir(bundled) and \
            os.path.abspath(bundled) != os.path.abspath(LANG_DIR):
        # first start of a packaged build: copy the bundled language files
        # next to the program so users can edit / add translations
        try:
            shutil.copytree(bundled, LANG_DIR)
        except OSError:
            pass
    if not os.path.isdir(LANG_DIR):
        try:
            os.makedirs(LANG_DIR, exist_ok=True)
            data = {"_meta": {"code": "en", "name": "English", "author": "", "version": "15"}}
            data.update(FALLBACK_STRINGS)
            with open(os.path.join(LANG_DIR, "en.json"), "w", encoding="utf-8") as fp:
                json.dump(data, fp, indent=4, ensure_ascii=False)
        except OSError:
            pass
    langs = {}
    try:
        fnames = sorted(f for f in os.listdir(LANG_DIR) if f.lower().endswith(".json"))
    except OSError:
        fnames = []
    for fname in fnames:
        try:
            with open(os.path.join(LANG_DIR, fname), "r", encoding="utf-8") as fp:
                data = json.load(fp)
        except (OSError, json.JSONDecodeError) as e:
            print(f"[lang] skipping {fname}: {e}")
            continue
        if not isinstance(data, dict):
            continue
        meta = data.get("_meta") if isinstance(data.get("_meta"), dict) else {}
        code = str(meta.get("code") or os.path.splitext(fname)[0]).strip()
        name = str(meta.get("name") or code)
        strings = {k: v for k, v in data.items()
                   if not k.startswith("_") and isinstance(v, str)}
        langs[code] = {"name": name, "strings": strings}
    if "en" not in langs:
        langs["en"] = {"name": "English", "strings": dict(FALLBACK_STRINGS)}
    return langs

# ─────────────────────────────────────────────────────────────────────────────
#  Theme palettes (selectable from Settings). Colors are chosen so the dark
#  theme reads as a designed dark-slate UI, not flat/plain black, and so that
#  walls / text / handles stay clearly visible against the dark canvas.
# ─────────────────────────────────────────────────────────────────────────────
THEMES = {
    "light": {
        "app_bg":          "#eef1f7",
        "panel_bg":        "#ffffff",
        "toolbar_bg":      "#ffffff",
        "canvas_bg":       "#ffffff",
        "grid_line":       "#e8ebf2",
        "grid_line_major": "#d7dceb",
        "text":            "#1f2430",
        "text_muted":      "#68708a",
        "border":          "#dbe1ee",
        "accent":          "#2f6fed",
        "accent_soft":     "#e6edff",
        "handle":          "#2f6fed",
        "select":          "#2f6fed",
        "ink_black":       "#20242c",
        "ink_blue":        "#2f6fed",
        "ink_red":         "#d64545",
        "lib_bg":          "#f8faff",
        "lib_row_bg":      "#ffffff",
        "lib_cat_bg":      "#e6edff",
        "lib_cat_fg":      "#28407a",
        "ghost":           "#c3c9d6",
        "measure":         "#c9820d",
        "room_label":      "#28407a",
        "room_palette": ["#e6f0ff", "#ffe9e0", "#e8f8ec", "#fff6db",
                         "#f2e8ff", "#e0f7f5", "#ffe8f1", "#f0f0da"],
    },
    "dark": {
        "app_bg":          "#171a21",
        "panel_bg":        "#1d212b",
        "toolbar_bg":      "#20242f",
        "canvas_bg":       "#12141a",
        "grid_line":       "#242938",
        "grid_line_major": "#2f3547",
        "text":            "#e8eaf0",
        "text_muted":      "#8b93a7",
        "border":          "#2c3140",
        "accent":          "#5b9bff",
        "accent_soft":     "#233150",
        "handle":          "#5b9bff",
        "select":          "#7db2ff",
        "ink_black":       "#eef0f5",
        "ink_blue":        "#6fa8ff",
        "ink_red":         "#ff7a7a",
        "lib_bg":          "#1d212b",
        "lib_row_bg":      "#252a37",
        "lib_cat_bg":      "#28324a",
        "lib_cat_fg":      "#a8c4ff",
        "ghost":           "#454b5c",
        "measure":         "#ffbe55",
        "room_label":      "#c7d6ff",
        "room_palette": ["#1c2b46", "#3a2620", "#1d3328", "#3a3116",
                         "#2a2148", "#173634", "#3a1f2c", "#2c2c1e"],
    },
}

# World-space constants (zoom-independent)
WORLD_GRID_PX = 20      # pixels per grid cell at zoom=1
WORLD_GRID_CM = 20      # cm per grid cell (default; user can change)
CANVAS_W      = 3000    # world-space canvas size
CANVAS_H      = 3000
HANDLE        = 6       # handle half-size in SCREEN pixels (fixed, not zoomed)

# The furniture library lives in JSON files inside this folder (next to the
# script), grouped by category e.g. library/living_room.json, library/kitchen.json.
# On first run the folder doesn't exist yet, so it gets created and seeded from
# the FURNITURE_DEFS table below (which becomes just the default/seed data,
# not the live source of truth - App.furniture_defs, loaded from disk, is).
LIBRARY_DIR = os.path.join(APP_DIR, "library")

# Category list (order, names, user-created categories). Files whose name
# starts with "_" are never read as furniture files.
CATEGORIES_FILE = os.path.join(LIBRARY_DIR, "_categories.json")
DEFAULT_CATEGORIES = ["doors_windows", "living_room", "dining_room", "bedroom", "kitchen",
                      "bathroom", "stairs", "custom"]

FURNITURE_DEFS = [
    ("sofa_3",     "sofa_3_lbl", "living_room",    240, 100, "sofa"),
    ("sofa_2",     "sofa_2_lbl", "living_room",    160, 100, "sofa"),
    ("armchair",   "armchair_lbl", "living_room",  100, 100, "armchair"),
    ("coffee_tbl", "coffee_tbl_lbl", "living_room",120,  60, "coffee_table"),
    ("tv_stand",   "tv_stand_lbl", "living_room",  160,  40, "tv_stand"),
    ("tv",         "tv_lbl", "living_room",        140,  10, "tv"),
    ("table_rect", "table_rect_lbl", "dining_room",120,  80, "rect_table"),
    ("table_round","table_round_lbl", "dining_room",80,  80, "round_table"),
    ("chair",      "chair_lbl", "dining_room",     40,  40, "chair"),
    ("bed_double", "bed_double_lbl", "bedroom",    160, 200, "bed_double"),
    ("bed_single", "bed_single_lbl", "bedroom",     80, 200, "bed_single"),
    ("wardrobe",   "wardrobe_lbl", "bedroom",      200,  60, "wardrobe"),
    ("desk",       "desk_lbl", "bedroom",          120,  60, "desk"),
    ("fridge",     "fridge_lbl", "kitchen",         60,  60, "fridge"),
    ("stove",      "stove_lbl", "kitchen",         60,  60, "stove"),
    ("sink_k",     "sink_k_lbl", "kitchen",         60,  40, "sink_kitchen"),
    ("dishwasher", "dishwasher_lbl", "kitchen",     60,  60, "dishwasher"),
    ("kitchen_cnt","kitchen_cnt_lbl", "kitchen",   160,  60, "counter"),
    ("bath",       "bath_lbl", "bathroom",         160,  80, "bathtub"),
    ("shower",     "shower_lbl", "bathroom",        80,  80, "shower"),
    ("toilet",     "toilet_lbl", "bathroom",        40,  60, "toilet"),
    ("sink_b",     "sink_b_lbl", "bathroom",        50,  40, "sink_bath"),
    ("wash_mach",  "wash_mach_lbl", "bathroom",     60,  60, "washing_machine"),
    ("stairs",        "stairs_lbl", "stairs",      100, 240, "stairs"),
    ("spiral_stairs", "spiral_stairs_lbl", "stairs",140, 140, "spiral_stairs"),
    ("ladder",        "ladder_lbl", "stairs",       50, 200, "ladder"),
    ("door",          "door_lbl", "doors_windows",  90,  90, "opening_door"),
    ("window",        "window_lbl", "doors_windows",120,  20, "opening_window"),
]


# ─────────────────────────────────────────────────────────────────────────────
#  RotatedDraw
# ─────────────────────────────────────────────────────────────────────────────

class RotatedDraw:
    def __init__(self, canvas, cx, cy, W, H, angle_deg):
        self._c   = canvas
        self._cx  = cx; self._cy = cy
        self._W   = W;  self._H  = H
        self._rad = radians(angle_deg)

    def _p(self, lx, ly):
        cx_pt = self._cx - self._W/2 + lx
        cy_pt = self._cy - self._H/2 + ly
        dx, dy = cx_pt - self._cx, cy_pt - self._cy
        ca, sa = cos(self._rad), sin(self._rad)
        return (self._cx + dx*ca - dy*sa, self._cy + dx*sa + dy*ca)

    def _rr(self, lx1, ly1, lx2, ly2):
        pts = [self._p(lx1,ly1), self._p(lx2,ly1),
               self._p(lx2,ly2), self._p(lx1,ly2)]
        return [c for pt in pts for c in pt]

    def create_rectangle(self, lx1, ly1, lx2, ly2, **kw):
        kw.pop("dash", None)
        fill=kw.pop("fill",""); outline=kw.pop("outline","black"); width=kw.pop("width",1)
        return self._c.create_polygon(*self._rr(lx1,ly1,lx2,ly2),
                                      fill=fill, outline=outline, width=width, smooth=False)

    def create_oval(self, lx1, ly1, lx2, ly2, **kw):
        lcx,lcy=(lx1+lx2)/2,(ly1+ly2)/2; rx,ry=abs(lx2-lx1)/2,abs(ly2-ly1)/2
        pts=[]
        for i in range(36):
            a=i*10*pi/180
            pts.extend(self._p(lcx+rx*cos(a), lcy+ry*sin(a)))
        fill=kw.pop("fill",""); outline=kw.pop("outline","black"); width=kw.pop("width",1)
        kw.pop("dash",None)
        return self._c.create_polygon(*pts, fill=fill, outline=outline, width=width, smooth=True)

    def create_line(self, lx1, ly1, lx2, ly2, **kw):
        kw.pop("dash",None)
        return self._c.create_line(*self._p(lx1,ly1), *self._p(lx2,ly2), **kw)

    def create_polygon(self, flat_pts, **kw):
        """flat_pts: [lx1,ly1,lx2,ly2,...] local (unrotated) coords."""
        kw.pop("dash", None)
        fill=kw.pop("fill",""); outline=kw.pop("outline","black"); width=kw.pop("width",1)
        out = []
        for i in range(0, len(flat_pts)-1, 2):
            out.extend(self._p(flat_pts[i], flat_pts[i+1]))
        return self._c.create_polygon(*out, fill=fill, outline=outline, width=width, smooth=False)

    def create_arc(self, lx1, ly1, lx2, ly2, **kw):
        start=kw.pop("start",0); extent=kw.pop("extent",90)
        outline=kw.pop("outline","black"); width=kw.pop("width",1)
        kw.pop("style",None); kw.pop("dash",None)
        lcx,lcy=(lx1+lx2)/2,(ly1+ly2)/2; rx,ry=abs(lx2-lx1)/2,abs(ly2-ly1)/2
        steps=max(12,int(abs(extent)//5)); pts=[]
        for i in range(steps+1):
            a=radians(start+extent*i/steps)
            pts.extend(self._p(lcx+rx*cos(a), lcy-ry*sin(a)))
        if len(pts)>=4:
            return self._c.create_line(*pts, fill=outline, width=width, smooth=True)
        return None


# ─────────────────────────────────────────────────────────────────────────────
#  Room auto-detection
#  Turns the current set of wall segments into a planar graph (splitting walls
#  at T-junctions / crossings, merging nearby endpoints) and traces its closed
#  faces to find enclosed rooms - this is how "hand drawn" walls that roughly
#  meet up get estimated into rooms, the way a real CAD tool would.
# ─────────────────────────────────────────────────────────────────────────────

_ROOM_TOL = 3.0  # world units (cm) - endpoints closer than this count as the same point


def _room_cluster_points(points, tol=_ROOM_TOL):
    """Merge near-duplicate points (hand-drawn walls rarely share exact pixels).
    Returns (cluster centers, list mapping each input point -> cluster index)."""
    clusters = []  # list of [sumx, sumy, count]
    assigned = []
    for (x, y) in points:
        found = None
        for i, (cx, cy, _cnt) in enumerate(clusters):
            if hypot(x - cx, y - cy) <= tol:
                found = i
                break
        if found is None:
            clusters.append([x, y, 1])
            assigned.append(len(clusters) - 1)
        else:
            cx, cy, cnt = clusters[found]
            clusters[found] = [(cx * cnt + x) / (cnt + 1), (cy * cnt + y) / (cnt + 1), cnt + 1]
            assigned.append(found)
    centers = [(c[0], c[1]) for c in clusters]
    return centers, assigned


def _room_seg_intersect_params(p1, p2, p3, p4, eps=1e-9):
    """t,u,point for segments p1-p2 (t) / p3-p4 (u) if they meet within [0,1] on
    both (inclusive of endpoints); parallel/collinear pairs are ignored."""
    x1, y1 = p1; x2, y2 = p2; x3, y3 = p3; x4, y4 = p4
    dax, day = x2 - x1, y2 - y1
    dbx, dby = x4 - x3, y4 - y3
    denom = dax * dby - day * dbx
    if abs(denom) < eps:
        return None
    t = ((x3 - x1) * dby - (y3 - y1) * dbx) / denom
    u = ((x3 - x1) * day - (y3 - y1) * dax) / denom
    if -1e-6 <= t <= 1 + 1e-6 and -1e-6 <= u <= 1 + 1e-6:
        return (t, u, (x1 + t * dax, y1 + t * day))
    return None


def _room_split_segments(segments):
    """Split every segment at points where another segment's line crosses it,
    including T-junctions where one wall's endpoint lands mid-way along another."""
    n = len(segments)
    cut_params = [[] for _ in range(n)]
    for i in range(n):
        x1, y1, x2, y2 = segments[i]
        if x1 == x2 and y1 == y2:
            continue
        for j in range(n):
            if i == j:
                continue
            x3, y3, x4, y4 = segments[j]
            res = _room_seg_intersect_params((x1, y1), (x2, y2), (x3, y3), (x4, y4))
            if res is None:
                continue
            t, _u, (ix, iy) = res
            # only cut segment i if the point is genuinely interior to it
            if hypot(ix - x1, iy - y1) > _ROOM_TOL and hypot(ix - x2, iy - y2) > _ROOM_TOL:
                cut_params[i].append(t)
    new_segments = []
    for i, (x1, y1, x2, y2) in enumerate(segments):
        ts = sorted(set([0.0] + cut_params[i] + [1.0]))
        for k in range(len(ts) - 1):
            ta, tb = ts[k], ts[k + 1]
            if tb - ta < 1e-4:
                continue
            new_segments.append((x1 + ta * (x2 - x1), y1 + ta * (y2 - y1),
                                  x1 + tb * (x2 - x1), y1 + tb * (y2 - y1)))
    return new_segments


def _room_build_graph(wall_segments):
    split = _room_split_segments(wall_segments)
    all_pts = []
    for (x1, y1, x2, y2) in split:
        all_pts.append((x1, y1)); all_pts.append((x2, y2))
    centers, assigned = _room_cluster_points(all_pts)
    nodes = {i: c for i, c in enumerate(centers)}
    edges = set()
    for k in range(len(split)):
        a, b = assigned[2 * k], assigned[2 * k + 1]
        if a != b:
            edges.add((min(a, b), max(a, b)))
    return nodes, edges


def _room_trace_faces(nodes, edges):
    """Trace closed faces of the planar graph by always taking the next edge
    clockwise around each vertex (the standard 'walk the wall' rule used to
    extract polygons from a line network)."""
    adjacency = {}
    for (a, b) in edges:
        adjacency.setdefault(a, []).append(b)
        adjacency.setdefault(b, []).append(a)

    def angle(u, v):
        ux, uy = nodes[u]; vx, vy = nodes[v]
        return atan2(vy - uy, vx - ux)

    for u in adjacency:
        adjacency[u].sort(key=lambda v: angle(u, v))

    visited = set()
    faces = []
    max_steps = 4 * len(edges) + 10
    for u in list(adjacency.keys()):
        for v in adjacency[u]:
            if (u, v) in visited:
                continue
            face = []
            cur_from, cur_to = u, v
            steps = 0
            while True:
                visited.add((cur_from, cur_to))
                face.append(cur_from)
                neighbors = adjacency[cur_to]
                idx = neighbors.index(cur_from)
                nxt = neighbors[(idx - 1) % len(neighbors)]
                cur_from, cur_to = cur_to, nxt
                steps += 1
                if (cur_from, cur_to) == (u, v) or steps > max_steps:
                    break
            if 2 < len(face) <= max_steps:
                faces.append(face)
    return faces


def _room_shoelace(pts):
    a = 0.0
    n = len(pts)
    for i in range(n):
        x1, y1 = pts[i]; x2, y2 = pts[(i + 1) % n]
        a += x1 * y2 - x2 * y1
    return a / 2.0


def _room_centroid(pts):
    a = _room_shoelace(pts)
    if abs(a) < 1e-9:
        xs = [p[0] for p in pts]; ys = [p[1] for p in pts]
        return sum(xs) / len(xs), sum(ys) / len(ys)
    cx = cy = 0.0
    n = len(pts)
    for i in range(n):
        x1, y1 = pts[i]; x2, y2 = pts[(i + 1) % n]
        cross = x1 * y2 - x2 * y1
        cx += (x1 + x2) * cross
        cy += (y1 + y2) * cross
    return cx / (6 * a), cy / (6 * a)


def compute_rooms(wall_segments, min_area=2500):
    """wall_segments: list of (x1,y1,x2,y2) in world cm. Returns a list of
    {'points','area','centroid'} for each enclosed room found (area in cm^2).
    min_area=2500cm^2 (0.25 m^2) filters out slivers from stray crossings."""
    if len(wall_segments) < 3:
        return []
    nodes, edges = _room_build_graph(wall_segments)
    if not edges:
        return []
    faces = _room_trace_faces(nodes, edges)
    rooms = []
    for face in faces:
        pts = [nodes[i] for i in face]
        area = _room_shoelace(pts)
        if area <= min_area:
            continue  # skip the outer/unbounded face (<=0) and tiny slivers
        rooms.append({"points": pts, "area": area, "centroid": _room_centroid(pts)})
    return rooms


# ─────────────────────────────────────────────────────────────────────────────
#  3D: building geometry, a small software renderer for Tk Canvas, OBJ export
#
#  Coordinates: the 2D plan uses x right / y down in cm. 3D "internal" space
#  is X = x, Y = -y, Z = up (cm), a right-handed system, so the model is not
#  mirrored. Every surface is a planar polygon ("face"); the viewer sorts the
#  visible faces far-to-near (painter's algorithm) and draws them as Canvas
#  polygons. No external libraries needed.
# ─────────────────────────────────────────────────────────────────────────────

SLAB_THICKNESS         = 20    # cm between floors (floor slab)
DEFAULT_WALL_HEIGHT    = 260   # cm
DEFAULT_WALL_THICKNESS = 15    # cm
DOOR_DEFAULTS   = {"width": 90,  "height": 210, "sill": 0}
WINDOW_DEFAULTS = {"width": 120, "height": 120, "sill": 90}

# Colours used by the 3D view (per theme)
THEME_3D = {
    "light": {"bg": "#eef2f8", "ground": "#dfe6d8", "wall": "#f1ede6",
              "wall_top": "#6e7480", "glass": "#9cc8ee", "door": "#b08968",
              "slab": "#cfcac0"},
    "dark":  {"bg": "#12141a", "ground": "#1f242e", "wall": "#d4d6dc",
              "wall_top": "#4b5260", "glass": "#5d8fc4", "door": "#9a7556",
              "slab": "#5a5f6a"},
}

# Built-in furniture in 3D: draw_fn -> (height cm, elevation cm, parts)
# Each part is (shape, lx0, ly0, lx1, ly1, z0, z1, colour) where lx/ly are
# fractions of the piece's footprint in its own (unrotated) frame - the same
# frame the 2D _furn_* drawings use, "back" side at ly=0 - and z0/z1 are
# fractions of the piece's height. shape is "box" or "cyl" (ellipse prism).
def _legs(t, z1, color):
    return [("box", 0, 0, t, t, 0, z1, color), ("box", 1 - t, 0, 1, t, 0, z1, color),
            ("box", 0, 1 - t, t, 1, 0, z1, color), ("box", 1 - t, 1 - t, 1, 1, 0, z1, color)]

FURN_3D = {
    "sofa": (85, 0, [("box", 0, 0, 1, 0.25, 0, 1, "#90aac8"),
                     ("box", 0.06, 0.25, 0.94, 1, 0, 0.5, "#d0e4f8"),
                     ("box", 0, 0.25, 0.06, 1, 0, 0.7, "#90aac8"),
                     ("box", 0.94, 0.25, 1, 1, 0, 0.7, "#90aac8")]),
    "armchair": (85, 0, [("box", 0, 0, 1, 0.28, 0, 1, "#b090d0"),
                         ("box", 0.12, 0.28, 0.88, 1, 0, 0.5, "#e0d0f8"),
                         ("box", 0, 0.28, 0.12, 1, 0, 0.7, "#b090d0"),
                         ("box", 0.88, 0.28, 1, 1, 0, 0.7, "#b090d0")]),
    "coffee_table": (45, 0, [("box", 0, 0, 1, 1, 0.85, 1, "#f5deb3")] + _legs(0.08, 0.85, "#8b6914")),
    "tv_stand": (50, 0, [("box", 0, 0, 1, 1, 0, 1, "#555555")]),
    "tv": (65, 50, [("box", 0, 0, 1, 1, 0, 1, "#161616")]),
    "rect_table": (75, 0, [("box", 0, 0, 1, 1, 0.94, 1, "#faebd7")] + _legs(0.08, 0.94, "#8b5e3c")),
    "round_table": (75, 0, [("cyl", 0, 0, 1, 1, 0.94, 1, "#faebd7"),
                            ("cyl", 0.44, 0.44, 0.56, 0.56, 0, 0.94, "#8b5e3c")]),
    "chair": (90, 0, [("box", 0, 0, 1, 0.2, 0, 1, "#c8a060"),
                      ("box", 0, 0.2, 1, 1, 0.42, 0.5, "#e8c888")] + _legs(0.1, 0.42, "#6b4020")),
    "bed_double": (95, 0, [("box", 0, 0.06, 1, 1, 0, 0.35, "#deb887"),
                           ("box", 0.02, 0.08, 0.98, 0.99, 0.35, 0.55, "#f5f5f5"),
                           ("box", 0, 0, 1, 0.06, 0, 1, "#a0522d")]),
    "bed_single": (95, 0, [("box", 0, 0.06, 1, 1, 0, 0.35, "#deb887"),
                           ("box", 0.04, 0.08, 0.96, 0.99, 0.35, 0.55, "#f5f5f5"),
                           ("box", 0, 0, 1, 0.06, 0, 1, "#a0522d")]),
    "wardrobe": (200, 0, [("box", 0, 0, 1, 1, 0, 1, "#d2b48c")]),
    "desk": (75, 0, [("box", 0, 0, 1, 1, 0.95, 1, "#e8d5b0"),
                     ("box", 0, 0, 0.05, 1, 0, 0.95, "#c8b590"),
                     ("box", 0.95, 0, 1, 1, 0, 0.95, "#c8b590")]),
    "fridge": (180, 0, [("box", 0, 0, 1, 1, 0, 1, "#e0e8f0")]),
    "stove": (90, 0, [("box", 0, 0, 1, 1, 0, 0.97, "#c0c0c0"),
                      ("box", 0.03, 0.03, 0.97, 0.97, 0.97, 1, "#2a2a35")]),
    "sink_kitchen": (90, 0, [("box", 0, 0, 1, 1, 0, 1, "#d0d8e0")]),
    "dishwasher": (85, 0, [("box", 0, 0, 1, 1, 0, 1, "#d8e0e8")]),
    "counter": (90, 0, [("box", 0, 0, 1, 1, 0, 0.95, "#e8ddd0"),
                        ("box", 0, 0, 1, 1, 0.95, 1, "#b8a890")]),
    "bathtub": (55, 0, [("box", 0, 0, 1, 1, 0, 1, "#e8f0f8")]),
    "shower": (200, 0, [("box", 0, 0, 1, 1, 0, 0.03, "#e8f4f8")]),
    "toilet": (80, 0, [("box", 0, 0, 1, 0.3, 0, 1, "#e0e8f0"),
                       ("cyl", 0.05, 0.25, 0.95, 1, 0, 0.5, "#f0f4f8")]),
    "sink_bath": (85, 0, [("box", 0, 0, 1, 1, 0.8, 1, "#d8e4ee"),
                          ("cyl", 0.35, 0.2, 0.65, 0.6, 0, 0.8, "#d8e4ee")]),
    "washing_machine": (85, 0, [("box", 0, 0, 1, 1, 0, 1, "#dce4ec")]),
    "door": (0, 0, []),            # old door symbol (converted to wall openings)
    "opening_door": (0, 0, []),    # library entries that start the Door tool
    "opening_window": (0, 0, []),  # ... and the Window tool
}
CUSTOM_FURN_HEIGHT = 75
SHELF_BOARD = 3      # shelf board thickness (cm)
SHELF_POST = 5       # shelf corner post size (cm)


def _hex6(c):
    """Normalise '#abc' / '#aabbcc' to '#aabbcc' (anything else -> grey)."""
    if isinstance(c, str) and c.startswith("#"):
        h = c[1:]
        if len(h) == 3:
            h = "".join(ch * 2 for ch in h)
        if len(h) == 6:
            try:
                int(h, 16)
                return "#" + h.lower()
            except ValueError:
                pass
    return "#bbbbbb"


def _shade(color, k):
    h = _hex6(color)[1:]
    r, g, b = (int(h[i:i + 2], 16) for i in (0, 2, 4))
    r, g, b = (max(0, min(255, int(v * k))) for v in (r, g, b))
    return f"#{r:02x}{g:02x}{b:02x}"


def _newell_normal(pts):
    nx = ny = nz = 0.0
    n = len(pts)
    for i in range(n):
        x1, y1, z1 = pts[i]; x2, y2, z2 = pts[(i + 1) % n]
        nx += (y1 - y2) * (z1 + z2)
        ny += (z1 - z2) * (x1 + x2)
        nz += (x1 - x2) * (y1 + y2)
    ln = sqrt(nx * nx + ny * ny + nz * nz) or 1.0
    return (nx / ln, ny / ln, nz / ln)


def _face(pts, color, level, phase=1, two_sided=False, glass=False, edge=True):
    return {"pts": pts, "color": _hex6(color), "normal": _newell_normal(pts),
            "level": level, "phase": phase, "two": two_sided, "glass": glass,
            "edge": edge}


def _prism(poly, z0, z1, color, level, top_color=None, caps=None, phase=1,
           edge=True, bottom=True):
    """Extrude a 2D polygon (internal X/Y coords) from z0 to z1. caps[i] = False
    skips the side face of edge i (poly[i] -> poly[i+1])."""
    n = len(poly)
    if n < 3 or z1 - z0 <= 0.01:
        return []
    area = 0.0
    for i in range(n):
        x1, y1 = poly[i]; x2, y2 = poly[(i + 1) % n]
        area += x1 * y2 - x2 * y1
    ccw = area > 0
    faces = []
    top = [(x, y, z1) for (x, y) in poly]
    bot = [(x, y, z0) for (x, y) in poly]
    if not ccw:
        top.reverse()
    else:
        bot.reverse()
    faces.append(_face(top, top_color or color, level, phase, edge=edge))
    if bottom:
        faces.append(_face(bot, color, level, phase, edge=edge))
    for i in range(n):
        if caps is not None and not caps[i]:
            continue
        (ax, ay), (bx, by) = poly[i], poly[(i + 1) % n]
        if ccw:
            q = [(ax, ay, z0), (bx, by, z0), (bx, by, z1), (ax, ay, z1)]
        else:
            q = [(bx, by, z0), (ax, ay, z0), (ax, ay, z1), (bx, by, z1)]
        faces.append(_face(q, color, level, phase, edge=edge))
    return faces


def _ellipse_pts(x0, y0, x1, y1, n=16):
    cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
    rx, ry = abs(x1 - x0) / 2, abs(y1 - y0) / 2
    return [(cx + rx * cos(2 * pi * i / n), cy + ry * sin(2 * pi * i / n)) for i in range(n)]


def write_obj(path, faces):
    """Write faces as Wavefront OBJ (+ .mtl next to it). Units: metres, Y up."""
    base = os.path.splitext(path)[0]
    mtl_path = base + ".mtl"
    mats = {}
    for f in faces:
        key = ("glass_" if f["glass"] else "c_") + f["color"][1:]
        mats.setdefault(key, f)
    with open(mtl_path, "w", encoding="utf-8") as fp:
        fp.write("# MyCAD materials\n")
        for name, f in mats.items():
            h = f["color"][1:]
            r, g, b = (int(h[i:i + 2], 16) / 255.0 for i in (0, 2, 4))
            fp.write(f"\nnewmtl {name}\nKd {r:.4f} {g:.4f} {b:.4f}\nKa 0 0 0\n"
                     f"d {0.35 if f['glass'] else 1.0}\nillum 1\n")
    with open(path, "w", encoding="utf-8") as fp:
        fp.write("# MyCAD floor plan export (units: metres, Y up)\n")
        fp.write(f"mtllib {os.path.basename(mtl_path)}\n")
        vi = 1
        cur = None
        for f in faces:
            key = ("glass_" if f["glass"] else "c_") + f["color"][1:]
            if key != cur:
                fp.write(f"usemtl {key}\n"); cur = key
            idx = []
            # internal (X, Y, Z-up) -> OBJ (X, Z, -Y), a proper rotation
            for (x, y, z) in f["pts"]:
                fp.write(f"v {x / 100:.4f} {z / 100:.4f} {-y / 100:.4f}\n")
                idx.append(str(vi)); vi += 1
            fp.write("f " + " ".join(idx) + "\n")
            if f["two"]:   # back side for double-sided surfaces (glass, ...)
                fp.write("f " + " ".join(reversed(idx)) + "\n")
    return mtl_path


class View3D:
    """Separate window with an orbit camera around the building."""

    NEAR = 5.0

    def __init__(self, app):
        self.app = app
        self.win = tk.Toplevel(app.root)
        self.win.title(app.get_text("view_3d"))
        self.win.geometry("1000x700")
        self.win.configure(bg=app.C("app_bg"))
        self.faces = []
        self.center = (0, 0, 0)
        self.yaw, self.pitch, self.dist = radians(-60), radians(35), 1500.0
        self.target = [0.0, 0.0, 0.0]
        self._pending = False
        self._drag = None
        self.walk = False             # walk mode: first-person camera at eye height
        self._saved_orbit = None
        self._keys = set()            # movement keys currently held down
        self._release_jobs = {}
        self._move_job = None
        self._last_t = None

        bar = ttk.Frame(self.win, padding=(6, 4)); bar.pack(fill="x")
        self.all_floors_var = tk.BooleanVar(value=True)
        self.furn_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(bar, text=app.get_text("show_all_floors"), variable=self.all_floors_var,
                        command=self.rebuild).pack(side="left", padx=2)
        ttk.Checkbutton(bar, text=app.get_text("furniture"), variable=self.furn_var,
                        command=self.rebuild).pack(side="left", padx=2)
        self.walk_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(bar, text=f"🚶 {app.get_text('walk_mode')}", variable=self.walk_var,
                        style="Toolbutton", command=self._toggle_walk).pack(side="left", padx=2)
        ttk.Separator(bar, orient="vertical").pack(side="left", fill="y", padx=6)
        ttk.Button(bar, text=f"⟲ {app.get_text('reset_view')}",
                   command=lambda: self.fit(reset_angles=True)).pack(side="left", padx=2)
        ttk.Button(bar, text=f"🔄 {app.get_text('refresh')}", command=self.rebuild).pack(side="left", padx=2)
        ttk.Button(bar, text=f"📤 {app.get_text('export_obj')}", command=app.export_obj).pack(side="left", padx=2)
        ttk.Label(bar, text=app.get_text("view3d_help"), foreground=app.C("text_muted"),
                  font=("TkDefaultFont", 8)).pack(side="right", padx=4)

        self.canvas = tk.Canvas(self.win, bg=self._col("bg"), highlightthickness=0)
        self.canvas.pack(fill="both", expand=True)
        c = self.canvas
        c.bind("<Configure>", lambda e: self.request_draw())
        c.bind("<ButtonPress-1>", lambda e: self._start(e, "pan" if e.state & 0x1 else "rot"))
        c.bind("<B1-Motion>", self._move)
        for b in ("2", "3"):
            c.bind(f"<ButtonPress-{b}>", lambda e: self._start(e, "pan"))
            c.bind(f"<B{b}-Motion>", self._move)
        c.bind("<MouseWheel>", lambda e: self._zoom(1 if e.delta > 0 else -1))
        c.bind("<Button-4>", lambda e: self._zoom(1))
        c.bind("<Button-5>", lambda e: self._zoom(-1))
        self.win.bind("<Left>",  lambda e: self._orbit(-0.08, 0))
        self.win.bind("<Right>", lambda e: self._orbit(0.08, 0))
        self.win.bind("<Up>",    lambda e: self._orbit(0, 0.05))
        self.win.bind("<Down>",  lambda e: self._orbit(0, -0.05))
        self.win.bind("<F1>", lambda e: app.toggle_help())
        self.win.bind("<plus>",  lambda e: self._zoom(1))
        self.win.bind("<minus>", lambda e: self._zoom(-1))
        self.win.bind("<KeyPress>", self._key_down)
        self.win.bind("<KeyRelease>", self._key_up)
        self.win.bind("<FocusOut>", lambda e: self._keys.clear())
        self.win.protocol("WM_DELETE_WINDOW", self.close)
        self.rebuild(fit=True)
        self.canvas.focus_set()

    def _col(self, key):
        return THEME_3D.get(self.app.theme, THEME_3D["light"])[key]

    def close(self):
        self.app.view3d = None
        self.win.destroy()

    def exists(self):
        try:
            return bool(self.win.winfo_exists())
        except tk.TclError:
            return False

    # ── scene ────────────────────────────────────────────────────────────────
    def rebuild(self, fit=False):
        only = None if self.all_floors_var.get() else self.app.current_floor
        self.faces = self.app.build_3d_faces(only_floor=only, furniture=self.furn_var.get(),
                                             subdivide=True, with_ground=True)
        light = (-0.45, 0.35, 0.82)
        ln = sqrt(sum(v * v for v in light)); light = tuple(v / ln for v in light)
        for f in self.faces:
            nx, ny, nz = f["normal"]
            k = 0.74 + 0.30 * max(0.0, nx * light[0] + ny * light[1] + nz * light[2])
            f["fill"] = _shade(f["color"], k)
            f["outline"] = _shade(f["color"], min(k, 1.0) * 0.72) if f["edge"] else f["fill"]
        if fit:
            self.fit(reset_angles=False)
        else:
            self.request_draw()

    def fit(self, reset_angles=False):
        pts = [p for f in self.faces if not f.get("ground") for p in f["pts"]]
        if not pts:
            pts = [(0, 0, 0), (500, -500, 260)]
        xs = [p[0] for p in pts]; ys = [p[1] for p in pts]; zs = [p[2] for p in pts]
        self.target = [(min(xs) + max(xs)) / 2, (min(ys) + max(ys)) / 2, (min(zs) + max(zs)) / 3]
        ext = max(max(xs) - min(xs), max(ys) - min(ys), max(zs) - min(zs), 300)
        self.dist = ext * 1.5
        if reset_angles:
            self.yaw, self.pitch = radians(-60), radians(35)
        if self.walk:
            self.walk = False
            self.walk_var.set(False)
        self.request_draw()

    # ── WASD movement / walk mode ────────────────────────────────────────────
    MOVE_KEYS = ("w", "a", "s", "d", "q", "e")

    def _key_down(self, e):
        k = e.keysym.lower()
        if k not in self.MOVE_KEYS and not k.startswith("shift"):
            return
        job = self._release_jobs.pop(k, None)     # key auto-repeat: ignore the fake release
        if job:
            self.win.after_cancel(job)
        self._keys.add(k)
        if self._move_job is None and any(x in self._keys for x in self.MOVE_KEYS):
            self._last_t = time.perf_counter()
            self._move_job = self.win.after(16, self._move_tick)

    def _key_up(self, e):
        k = e.keysym.lower()
        if k in self._keys:
            # released for real only if no new press follows right away
            self._release_jobs[k] = self.win.after(40, lambda: (self._keys.discard(k),
                                                                self._release_jobs.pop(k, None)))

    def _move_tick(self):
        self._move_job = None
        if not self.exists() or not any(x in self._keys for x in self.MOVE_KEYS):
            return
        now = time.perf_counter()
        dt = min(0.1, now - (self._last_t or now)); self._last_t = now
        fast = any(k.startswith("shift") for k in self._keys)
        if self.walk:
            speed = 450.0 if fast else 160.0                     # cm per second
        else:
            speed = max(150.0, self.dist * 0.6) * (2.5 if fast else 1.0)
        # forward / right on the ground plane, relative to where the camera looks
        fx, fy = -cos(self.yaw), -sin(self.yaw)
        rx, ry = fy, -fx
        fwd = ("w" in self._keys) - ("s" in self._keys)
        side = ("d" in self._keys) - ("a" in self._keys)
        up = ("e" in self._keys) - ("q" in self._keys)
        step = speed * dt
        self.target[0] += (fx * fwd + rx * side) * step
        self.target[1] += (fy * fwd + ry * side) * step
        self.target[2] += up * step
        self.draw()
        self._move_job = self.win.after(16, self._move_tick)

    def _toggle_walk(self):
        if self.walk_var.get() and not self.walk:
            self._saved_orbit = (self.yaw, self.pitch, self.dist, list(self.target))
            elevs, _top = self.app._floor_elevations()
            fl = self.app.current_floor if self.app.current_floor < len(elevs) else 0
            # start in the middle of a room on the active floor: the room the
            # orbit camera was looking at, or else the biggest one
            walls = self.app.floors[fl]["walls"]
            try:
                rooms = compute_rooms([(w["x1"], w["y1"], w["x2"], w["y2"]) for w in walls])
            except Exception:
                rooms = []
            px, py = self.target[0], -self.target[1]

            def contains(pts):
                inside, j = False, len(pts) - 1
                for i in range(len(pts)):
                    (xi, yi), (xj, yj) = pts[i], pts[j]
                    if (yi > py) != (yj > py) and px < (xj - xi) * (py - yi) / ((yj - yi) or 1e-9) + xi:
                        inside = not inside
                    j = i
                return inside
            if rooms:
                room = next((r for r in rooms if contains(r["points"])),
                            max(rooms, key=lambda r: r["area"]))
                self.target[0], self.target[1] = room["centroid"][0], -room["centroid"][1]
            self.target[2] = elevs[fl] + 165.0
            self.dist, self.pitch = 1.0, 0.0
            self.walk = True
        elif not self.walk_var.get() and self.walk:
            self.walk = False
            if self._saved_orbit:
                self.yaw, self.pitch, self.dist, self.target = (self._saved_orbit[0], self._saved_orbit[1],
                                                                self._saved_orbit[2], list(self._saved_orbit[3]))
        self.canvas.focus_set()
        self.request_draw()

    # ── interaction ──────────────────────────────────────────────────────────
    def _start(self, e, mode):
        self._drag = (mode, e.x, e.y)
        self.canvas.focus_set()

    def _move(self, e):
        if not self._drag:
            return
        mode, x0, y0 = self._drag
        dx, dy = e.x - x0, e.y - y0
        self._drag = (mode, e.x, e.y)
        if mode == "rot":
            self._orbit(-dx * 0.008, dy * 0.006)
        else:
            r, u, _f, _c = self._basis()
            s = 0.6 if self.walk else self.dist / max(200.0, self._focal())
            for i in range(3):
                self.target[i] += (-dx * r[i] + dy * u[i]) * s
            self.request_draw()

    def _orbit(self, dyaw, dpitch):
        self.yaw += dyaw
        lo, hi = (radians(-80), radians(80)) if self.walk else (radians(3), radians(89))
        self.pitch = max(lo, min(hi, self.pitch + dpitch))
        self.request_draw()

    def _zoom(self, steps):
        if self.walk:            # in walk mode the wheel takes steps forward / back
            self.target[0] += -cos(self.yaw) * 40 * steps
            self.target[1] += -sin(self.yaw) * 40 * steps
            self.request_draw()
            return
        self.dist = max(50.0, min(200000.0, self.dist * (0.88 ** steps)))
        self.request_draw()

    # ── camera / drawing ─────────────────────────────────────────────────────
    def _focal(self):
        h = max(100, self.canvas.winfo_height())
        return 0.5 * h / tan(radians(50) / 2)

    def _basis(self):
        cp, sp = cos(self.pitch), sin(self.pitch)
        cy_, sy_ = cos(self.yaw), sin(self.yaw)
        cam = (self.target[0] + self.dist * cp * cy_,
               self.target[1] + self.dist * cp * sy_,
               self.target[2] + self.dist * sp)
        f = (-cp * cy_, -cp * sy_, -sp)                    # forward
        r = (f[1], -f[0], 0.0)                              # forward x up(0,0,1)
        rl = sqrt(r[0] ** 2 + r[1] ** 2) or 1.0
        r = (r[0] / rl, r[1] / rl, 0.0)
        u = (r[1] * f[2] - r[2] * f[1], r[2] * f[0] - r[0] * f[2], r[0] * f[1] - r[1] * f[0])
        return r, u, f, cam

    def request_draw(self):
        if not self._pending:
            self._pending = True
            self.win.after_idle(self.draw)

    def draw(self):
        self._pending = False
        if not self.exists():
            return
        c = self.canvas
        c.configure(bg=self._col("bg"))
        c.delete("all")
        W = max(10, c.winfo_width()); H = max(10, c.winfo_height())
        cx, cy = W / 2, H / 2
        foc = self._focal()
        r, u, f, cam = self._basis()
        near = self.NEAR
        items = []
        for face in self.faces:
            p0 = face["pts"][0]
            if not face["two"]:
                n = face["normal"]
                if (n[0] * (cam[0] - p0[0]) + n[1] * (cam[1] - p0[1]) + n[2] * (cam[2] - p0[2])) <= 0:
                    continue
            cs = []
            for (x, y, z) in face["pts"]:
                vx, vy, vz = x - cam[0], y - cam[1], z - cam[2]
                cs.append((vx * r[0] + vy * r[1] + vz * r[2],
                           vx * u[0] + vy * u[1] + vz * u[2],
                           vx * f[0] + vy * f[1] + vz * f[2]))
            if min(p[2] for p in cs) < near:
                cs = self._clip_near(cs, near)
                if len(cs) < 3:
                    continue
            depth = sum(p[2] for p in cs) / len(cs)
            coords = []
            for (x, y, z) in cs:
                coords.append(cx + foc * x / z); coords.append(cy - foc * y / z)
            items.append((face["level"], face["phase"], -depth, coords, face))
        items.sort(key=lambda t: (t[0], t[1], t[2]))
        for (_l, _p, _d, coords, face) in items:
            kw = {"fill": face["fill"], "outline": face["outline"], "width": 1}
            if face["glass"]:
                kw["stipple"] = "gray50"
            try:
                c.create_polygon(coords, **kw)
            except tk.TclError:
                kw.pop("stipple", None)
                c.create_polygon(coords, **kw)

    @staticmethod
    def _clip_near(pts, near):
        out = []
        n = len(pts)
        for i in range(n):
            a = pts[i]; b = pts[(i + 1) % n]
            ain, bin_ = a[2] >= near, b[2] >= near
            if ain:
                out.append(a)
            if ain != bin_:
                t = (near - a[2]) / (b[2] - a[2])
                out.append((a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t, near))
        return out


class ShelfView:
    """Front view of one shelf unit: boards, posts and everything standing on
    them, drawn to scale. Things can be dragged sideways / between boards,
    added from the library, copied and deleted. A strip below shows the
    selected board from above so the depth position can be changed too."""

    FRONT_H = 430
    TOP_H = 150
    WIDTH = 760

    def __init__(self, app, shelf, select=None):
        self.app = app
        self.shelf = shelf
        self.sel = select
        self.flip = False
        self.drag = None
        self.add_fid = None
        self.hits = []          # front view: (item, x0, y0, x1, y1) in draw order
        self.top_hits = []
        self.geo = {}

        t = app.get_text
        self.win = tk.Toplevel(app.root)
        self.win.title(f"{t('shelf_view')} – {self._name(shelf)}")
        self.win.configure(bg=app.C("app_bg"))
        self.win.transient(app.root)
        frm = ttk.Frame(self.win, padding=10); frm.pack(fill="both", expand=True)

        bar = ttk.Frame(frm); bar.pack(fill="x", pady=(0, 6))
        self.flip_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(bar, text=f"⇄ {t('view_other_side')}", variable=self.flip_var, style="Toolbutton",
                        command=self._toggle_flip).pack(side="left", padx=(0, 8))
        ttk.Separator(bar, orient="vertical").pack(side="left", fill="y", padx=4)
        ttk.Label(bar, text=f"{t('add_to_shelf')}:").pack(side="left", padx=(4, 4))
        self.lib = self._library_choices()
        # default: something from the "storage" category (a box), else the first item
        storage = [k for k, fid in self.lib.items()
                   if (app._furn_def(fid) or {}).get("category") == "storage"]
        self.add_var = tk.StringVar(value=(storage or list(self.lib) or [""])[0])
        cb = ttk.Combobox(bar, textvariable=self.add_var, values=list(self.lib.keys()),
                          state="readonly", width=22)
        cb.pack(side="left")
        self.add_btn = ttk.Button(bar, text=f"➕ {t('add')}", command=self._start_add)
        self.add_btn.pack(side="left", padx=4)
        ttk.Separator(bar, orient="vertical").pack(side="left", fill="y", padx=4)
        ttk.Button(bar, text=f"📄 {t('copy')}", command=self._copy).pack(side="left", padx=2)
        ttk.Button(bar, text=f"🗑 {t('delete')}", command=self._delete).pack(side="left", padx=2)
        ttk.Button(bar, text=f"⚙ {t('properties')}", command=self._props).pack(side="left", padx=2)
        ttk.Button(bar, text=t("close"), command=self.close).pack(side="right")

        self.front = tk.Canvas(frm, width=self.WIDTH, height=self.FRONT_H, bg="white",
                               highlightthickness=1, highlightbackground=app.C("border"))
        self.front.pack()
        self.top_lbl = ttk.Label(frm, text="", foreground=app.C("text_muted"), font=("TkDefaultFont", 9))
        self.top_lbl.pack(anchor="w", pady=(6, 2))
        self.top = tk.Canvas(frm, width=self.WIDTH, height=self.TOP_H, bg="white",
                             highlightthickness=1, highlightbackground=app.C("border"))
        self.top.pack()
        self.status = tk.StringVar()
        ttk.Label(frm, textvariable=self.status, font=("TkDefaultFont", 9)).pack(anchor="w", pady=(6, 0))
        ttk.Label(frm, text=t("shelf_view_help"), foreground=app.C("text_muted"),
                  font=("TkDefaultFont", 8), wraplength=self.WIDTH, justify="left").pack(anchor="w")

        f = self.front
        f.bind("<ButtonPress-1>", self._press)
        f.bind("<B1-Motion>", self._motion_drag)
        f.bind("<ButtonRelease-1>", self._release)
        f.bind("<Motion>", self._hover)
        f.bind("<Double-Button-1>", lambda e: self._props())
        self.top.bind("<ButtonPress-1>", self._top_press)
        self.top.bind("<B1-Motion>", self._top_drag)
        self.top.bind("<ButtonRelease-1>", self._top_release)
        w = self.win
        w.bind("<Delete>", lambda e: self._delete())
        w.bind("<Control-d>", lambda e: self._copy())
        w.bind("<Control-D>", lambda e: self._copy())
        w.bind("<Escape>", lambda e: self._escape())
        w.bind("<Left>", lambda e: self._nudge(-5 if e.state & 1 else -1))
        w.bind("<Right>", lambda e: self._nudge(5 if e.state & 1 else 1))
        w.bind("<Prior>", lambda e: self._level(+1))
        w.bind("<Next>", lambda e: self._level(-1))
        w.bind("<F1>", lambda e: app.toggle_help())
        w.bind("<FocusIn>", lambda e: self.refresh() if e.widget is w else None)
        w.protocol("WM_DELETE_WINDOW", self.close)
        self.refresh()
        self.front.focus_set()

    # ── helpers ──────────────────────────────────────────────────────────────
    def exists(self):
        try:
            return bool(self.win.winfo_exists())
        except tk.TclError:
            return False

    def close(self):
        self.app.shelf_view = None
        self.win.destroy()

    def _name(self, it):
        e = self.app._furn_def(it["fid"]) or {}
        return self.app.get_text(e.get("label_key", it["fid"]))

    def _color(self, it):
        e = self.app._furn_def(it["fid"]) or {}
        if e.get("draw_fn") == "custom_shape":
            return _hex6(e.get("fill") or "#e0d3ae")
        parts = FURN_3D.get(e.get("draw_fn", ""), (0, 0, []))[2]
        return _hex6(parts[0][7]) if parts else "#cfcfcf"

    def _library_choices(self):
        out = {}
        skip = self.app.NON_STACKING
        for e in self.app.furniture_defs:
            if e.get("draw_fn") in skip or isinstance(e.get("shelf"), dict):
                continue
            name = self.app.get_text(e.get("label_key", e["fid"]))
            label = f"{name} ({e['width']:g}×{e['height']:g})"
            out[label] = e["fid"]
        return dict(sorted(out.items(), key=lambda kv: kv[0].lower()))

    def _frame(self):
        S = self.shelf
        cx, cy = (S["x1"] + S["x2"]) / 2, (S["y1"] + S["y2"]) / 2
        W, H = abs(S["x2"] - S["x1"]), abs(S["y2"] - S["y1"])
        ang = S.get("angle", 0)
        if (ang // 90) % 2 == 1:
            W, H = H, W
        return cx, cy, W, H, cos(radians(ang)), sin(radians(ang))

    def to_local(self, wx, wy):
        cx, cy, W, H, ca, sa = self._frame()
        dx, dy = wx - cx, wy - cy
        return (dx * ca + dy * sa + W / 2, -dx * sa + dy * ca + H / 2)

    def to_world(self, lx, ly):
        cx, cy, W, H, ca, sa = self._frame()
        dx, dy = lx - W / 2, ly - H / 2
        return (cx + dx * ca - dy * sa, cy + dx * sa + dy * ca)

    def lbox(self, it):
        pts = [self.to_local(x, y) for x in (it["x1"], it["x2"]) for y in (it["y1"], it["y2"])]
        xs = [p[0] for p in pts]; ys = [p[1] for p in pts]
        return min(xs), min(ys), max(xs), max(ys)

    def u_range(self, lx0, lx1):
        W = self._frame()[2]
        return (W - lx1, W - lx0) if self.flip else (lx0, lx1)

    def lx_from_u(self, u):
        W = self._frame()[2]
        return W - u if self.flip else u

    def depth_of(self, ly0, ly1):
        """distance range from the front edge (front = the side you look from)"""
        H = self._frame()[3]
        return (ly0, ly1) if self.flip else (H - ly1, H - ly0)

    def items(self):
        S = self.shelf
        out = []
        for it in self.app.furniture:
            if it is S or not self.app._stackable(it) or self.app._shelf_of(it):
                continue
            if self.app._furn_overlap(it, S):
                out.append(it)
        return out

    def _move_item(self, it, lcx, lcy):
        """Move a piece so that its centre is at local (lcx, lcy)."""
        wx, wy = self.to_world(lcx, lcy)
        ox, oy = (it["x1"] + it["x2"]) / 2, (it["y1"] + it["y2"]) / 2
        for k in ("x1", "x2"):
            it[k] += wx - ox
        for k in ("y1", "y2"):
            it[k] += wy - oy

    # ── placing with collision checks ────────────────────────────────────────
    def _blocked(self, it, z, h, others):
        a = self.lbox(it)
        for o in others:
            if o is it:
                continue
            oz, oh = self.app._furn_z(o)
            if not (z < oz + oh - 0.5 and oz < z + h - 0.5):
                continue
            b = self.lbox(o)
            if a[0] < b[2] - 0.5 and b[0] < a[2] - 0.5 and a[1] < b[3] - 0.5 and b[1] < a[3] - 0.5:
                return o
        return None

    def _try_place(self, it, lcx, lcy, zwant, search=False):
        """Put `it` near local (lcx, lcy) on the surface closest to height
        zwant. Slides sideways out of the way of other things if needed.
        With search=True it tries every board, lowest first after the wanted one."""
        app = self.app
        _cx, _cy, W, H, _ca, _sa = self._frame()
        orig = (it["x1"], it["y1"], it["x2"], it["y2"], it.get("z_elev"), it.get("stack"))
        h = app._furn_z(it)[1]
        others = [o for o in self.items() if o is not it] + [self.shelf]
        b = self.lbox(it); w, d = b[2] - b[0], b[3] - b[1]
        lcx = min(max(lcx, w / 2), max(w / 2, W - w / 2))
        lcy = min(max(lcy, d / 2), max(d / 2, H - d / 2))
        self._move_item(it, lcx, lcy)
        surfaces = sorted({round(s, 2) for s, room in app._surfaces(it, others)
                           if room is None or h <= room + 0.5})
        if not surfaces:
            self._restore(it, orig); return False
        order = sorted(surfaces, key=lambda s: (abs(s - zwant), s))
        if search:
            order = sorted(surfaces, key=lambda s: (s < zwant - 0.5, abs(s - zwant)))
        inner = [o for o in others if o is not self.shelf]
        for s in order:
            xs = [lcx]
            if self._blocked_at(it, lcx, lcy, s, h, inner):
                # candidate positions: right next to each blocking piece
                for o in inner:
                    ob = self.lbox(o)
                    xs += [ob[0] - w / 2 - 0.1, ob[2] + w / 2 + 0.1]
                xs = sorted({x for x in xs if w / 2 - 0.01 <= x <= W - w / 2 + 0.01},
                            key=lambda x: (abs(x - lcx) if not search else x))
            for x in xs:
                if not self._blocked_at(it, x, lcy, s, h, inner):
                    self._move_item(it, x, lcy)
                    it["z_elev"] = s
                    it["stack"] = True
                    it.pop("_new", None)
                    return True
        self._restore(it, orig)
        return False

    def _blocked_at(self, it, lcx, lcy, z, h, others):
        self._move_item(it, lcx, lcy)
        return self._blocked(it, z, h, others) is not None

    def _restore(self, it, orig):
        it["x1"], it["y1"], it["x2"], it["y2"] = orig[:4]
        if orig[4] is None:
            it.pop("z_elev", None)
        else:
            it["z_elev"] = orig[4]
        if orig[5] is None:
            it.pop("stack", None)
        else:
            it["stack"] = orig[5]

    def _commit(self, select=None):
        app = self.app
        app._apply_gravity()
        app._redraw_all()
        if select is not None and select in app.furniture:
            self.sel = select
            app.select_single(select)
        self.refresh()

    # ── drawing ──────────────────────────────────────────────────────────────
    def refresh(self):
        if not self.exists():
            return
        if self.shelf not in self.app.furniture:
            self.close(); return
        if self.sel is not None and self.sel not in self.app.furniture:
            self.sel = None
        self.draw_front()
        self.draw_top()
        self._status()

    def _scale(self):
        app = self.app
        _cx, _cy, W, H, _ca, _sa = self._frame()
        z0, h = app._furn_z(self.shelf)
        top = max([z0 + h] + [sum(app._furn_z(o)) for o in self.items()]) + 15
        cw, ch = self.WIDTH, self.FRONT_H
        sc = min((cw - 150) / max(W, 1), (ch - 50) / max(top, 1))
        ox = max(60, (cw - W * sc) / 2)
        return sc, ox, ch - 28, top

    def fx(self, u):
        return self.geo["ox"] + u * self.geo["sc"]

    def fz(self, z):
        return self.geo["floor"] - z * self.geo["sc"]

    def draw_front(self):
        app = self.app
        c = self.front
        c.delete("all")
        _cx, _cy, W, H, _ca, _sa = self._frame()
        sc, ox, floor, top = self._scale()
        self.geo = {"sc": sc, "ox": ox, "floor": floor}
        z0, h = app._furn_z(self.shelf)
        sh = app._shelf_of(self.shelf) or {}
        post = min(float(sh.get("post", SHELF_POST)), W / 3)
        board = float(sh.get("board", SHELF_BOARD))
        fill = self._color(self.shelf)
        dark = app._darken_hex(fill, 0.65)
        ink = "#2f6fed"
        # rulers
        lab = next((v for v in (5, 10, 20, 25, 50, 100, 200) if v * sc >= 28), 500)
        z = 0
        while z <= top:
            y = self.fz(z)
            c.create_line(ox - 8, y, ox - 3, y, fill="#9aa3b5")
            c.create_text(ox - 10, y, text=f"{z:g}", anchor="e", fill="#68708a", font=("TkDefaultFont", 7))
            z += lab
        c.create_text(ox - 10, 8, text="cm", anchor="e", fill="#68708a", font=("TkDefaultFont", 7))
        c.create_line(ox - 40, floor, ox + W * sc + 70, floor, fill="#68708a", width=2)
        labx = next((v for v in (5, 10, 20, 25, 50, 100, 200) if v * sc >= 32), 500)
        u = 0
        while u <= W + 0.01:
            x = self.fx(u)
            c.create_line(x, floor + 2, x, floor + 7, fill="#9aa3b5")
            c.create_text(x, floor + 9, text=f"{u:g}", anchor="n", fill="#68708a", font=("TkDefaultFont", 7))
            u += labx
        # shelf: posts + boards (back first, then contents, then front posts)
        for ux in (0, W - post):
            c.create_rectangle(self.fx(ux), self.fz(z0 + h), self.fx(ux + post), self.fz(z0),
                               fill=_shade(dark, 1.25), outline=dark)
        levels = app._shelf_levels(self.shelf) if sh else []
        for (t, room) in levels:
            c.create_rectangle(self.fx(0), self.fz(z0 + t), self.fx(W), self.fz(z0 + t - board),
                               fill=fill, outline=dark)
            txt = f"↕ {room:g} cm" if room is not None else "↑"
            c.create_text(self.fx(W) + 8, self.fz(z0 + t) - 2, text=txt, anchor="sw",
                          fill="#68708a", font=("TkDefaultFont", 8))
        # contents, farthest first; things further back are drawn paler
        self.hits = []
        its = self.items()

        def depth_key(o):
            b = self.lbox(o)
            return -self.depth_of(b[1], b[3])[0]
        for o in sorted(its, key=depth_key):
            b = self.lbox(o)
            u0, u1 = self.u_range(b[0], b[2])
            dz, hh = app._furn_z(o)
            dfront = self.depth_of(b[1], b[3])[0]
            col = self._color(o)
            if dfront > 2:
                col = _shade(col, 1.0)
                col = self._mix(col, "#ffffff", min(0.6, dfront / max(H, 1) * 0.9))
            sel = o is self.sel
            x0, y0, x1, y1 = self.fx(u0), self.fz(dz + hh), self.fx(u1), self.fz(dz)
            c.create_rectangle(x0, y0, x1, y1, fill=col, outline=ink if sel else app._darken_hex(col, 0.6),
                               width=3 if sel else 1)
            if x1 - x0 > 30 and y1 - y0 > 12:
                c.create_text((x0 + x1) / 2, (y0 + y1) / 2, text=self._name(o), fill="#222222",
                              font=("TkDefaultFont", 8), width=max(20, x1 - x0 - 4))
            self.hits.append((o, x0, y0, x1, y1))
        if self.sel is not None and self.sel in its:
            b = self.lbox(self.sel)
            u0, u1 = self.u_range(b[0], b[2])
            dz, hh = app._furn_z(self.sel)
            c.create_text(self.fx(u0), self.fz(dz + hh) - 2, anchor="sw", fill=ink,
                          font=("TkDefaultFont", 8, "bold"),
                          text=f"{b[2]-b[0]:g} × {hh:g} cm   ↔ {u0:g} cm   ↑ {dz:g} cm")

    @staticmethod
    def _mix(a, b, t):
        a, b = _hex6(a)[1:], _hex6(b)[1:]
        ca = [int(a[i:i + 2], 16) for i in (0, 2, 4)]; cb = [int(b[i:i + 2], 16) for i in (0, 2, 4)]
        return "#" + "".join(f"{int(x + (y - x) * t):02x}" for x, y in zip(ca, cb))

    def _active_band(self):
        """(z_from, z_to) of the board the selected piece stands on."""
        app = self.app
        if self.sel is None or not app._shelf_of(self.shelf):
            return None
        z0, _h = app._furn_z(self.shelf)
        sz = app._furn_z(self.sel)[0]
        levels = [z0 + t for (t, _r) in app._shelf_levels(self.shelf)]
        below = [l for l in levels if l <= sz + 0.5]
        if not below:
            return None
        lo = below[-1]
        above = [l for l in levels if l > lo + 0.5]
        return (lo, above[0] if above else 1e9)

    def draw_top(self):
        app = self.app
        c = self.top
        c.delete("all")
        _cx, _cy, W, H, _ca, _sa = self._frame()
        sc = self.geo["sc"]
        sd = min(sc, (self.TOP_H - 26) / max(H, 1))
        self.geo["sd"] = sd
        ybase = self.TOP_H - 14            # front edge of the shelf
        self.geo["ybase"] = ybase
        fill = self._color(self.shelf)
        c.create_rectangle(self.fx(0), ybase - H * sd, self.fx(W), ybase, fill=self._mix(fill, "#ffffff", 0.5),
                           outline=app._darken_hex(fill, 0.6))
        c.create_text(self.fx(W) + 8, ybase, text=app.get_text("front_side"), anchor="sw",
                      fill="#68708a", font=("TkDefaultFont", 8))
        c.create_line(self.fx(0), ybase + 1, self.fx(W), ybase + 1, fill="#2f6fed", width=2)
        band = self._active_band()
        self.top_hits = []
        for o in self.items():
            dz = app._furn_z(o)[0]
            if band and not (band[0] - 0.5 <= dz < band[1] - 0.5):
                continue
            b = self.lbox(o)
            u0, u1 = self.u_range(b[0], b[2])
            d0, d1 = self.depth_of(b[1], b[3])
            sel = o is self.sel
            x0, x1 = self.fx(u0), self.fx(u1)
            y0, y1 = ybase - d1 * sd, ybase - d0 * sd
            c.create_rectangle(x0, y0, x1, y1, fill=self._color(o),
                               outline="#2f6fed" if sel else app._darken_hex(self._color(o), 0.6),
                               width=3 if sel else 1)
            self.top_hits.append((o, x0, y0, x1, y1))
        if band:
            txt = app.get_text("top_view_board").format(z=f"{band[0]:g}")
        else:
            txt = app.get_text("top_view_all")
        self.top_lbl.configure(text=f"⬒ {txt}")

    def _status(self, extra=""):
        app = self.app
        _cx, _cy, W, H, _ca, _sa = self._frame()
        z0, h = app._furn_z(self.shelf)
        s = f"{self._name(self.shelf)}: {W:g} × {H:g} × {h:g} cm   ·   {len(self.items())} {app.get_text('items_count')}"
        if self.add_fid:
            s += f"   ·   ➕ {app.get_text('click_to_place')}"
        if extra:
            s += f"   ·   {extra}"
        self.status.set(s)

    # ── front view interaction ───────────────────────────────────────────────
    def _hit(self, x, y):
        for (o, x0, y0, x1, y1) in reversed(self.hits):
            if x0 <= x <= x1 and y0 <= y <= y1:
                return o
        return None

    def _ev_uz(self, e):
        return ((e.x - self.geo["ox"]) / self.geo["sc"], (self.geo["floor"] - e.y) / self.geo["sc"])

    def _press(self, e):
        self.front.focus_set()
        u, z = self._ev_uz(e)
        if self.add_fid:
            self._place_new(u, z)
            return
        o = self._hit(e.x, e.y)
        self.sel = o
        if o is not None:
            self.app.select_single(o)
            b = self.lbox(o)
            u0, _u1 = self.u_range(b[0], b[2])
            dz = self.app._furn_z(o)[0]
            self.drag = {"item": o, "du": u - u0, "dz": z - dz, "moved": False}
        self.draw_front(); self.draw_top(); self._status()

    def _motion_drag(self, e):
        if not self.drag:
            return
        o = self.drag["item"]
        u, z = self._ev_uz(e)
        b = self.lbox(o)
        w = b[2] - b[0]
        hh = self.app._furn_z(o)[1]
        u0 = round(u - self.drag["du"])
        zb = z - self.drag["dz"]
        self.drag.update(moved=True, u0=u0, zb=zb)
        self.front.delete("ghost")
        self.front.create_rectangle(self.fx(u0), self.fz(zb + hh), self.fx(u0 + w), self.fz(zb),
                                    outline="#2f6fed", dash=(4, 3), width=2, tags="ghost")
        self._status(f"↔ {u0:g} cm")

    def _release(self, e):
        d, self.drag = self.drag, None
        self.front.delete("ghost")
        if not d or not d.get("moved"):
            return
        o = d["item"]
        b = self.lbox(o)
        w = b[2] - b[0]
        lcx = self.lx_from_u(d["u0"] + w / 2)
        if not self._try_place(o, lcx, (b[1] + b[3]) / 2, d["zb"]):
            self._status(self.app.get_text("no_room"))
            self.refresh(); return
        self._commit(select=o)

    def _hover(self, e):
        if not self.add_fid:
            return
        u, z = self._ev_uz(e)
        e2 = self.app._furn_def(self.add_fid) or {}
        w = float(e2.get("width", 40))
        hh = float(e2.get("z_height") or self.app._furn_3d_defaults({"fid": self.add_fid})[0] or 30)
        self.front.delete("ghost")
        self.front.create_rectangle(self.fx(u - w / 2), self.fz(z + hh), self.fx(u + w / 2), self.fz(z),
                                    outline="#2f6fed", dash=(4, 3), width=2, tags="ghost")

    # ── commands ─────────────────────────────────────────────────────────────
    def _start_add(self):
        fid = self.lib.get(self.add_var.get())
        if not fid:
            return
        self.add_fid = fid
        self.front.configure(cursor="crosshair")
        self._status()

    def _escape(self):
        if self.add_fid:
            self.add_fid = None
            self.front.configure(cursor="")
            self.front.delete("ghost")
            self._status()
        else:
            self.close()

    def _new_item(self, fid):
        """Create a library piece aligned with the shelf (same rotation)."""
        e = self.app._furn_def(fid) or {}
        w, d = float(e.get("width", 40)), float(e.get("height", 40))
        pts = [self.to_world(lx, ly) for lx in (0, w) for ly in (0, d)]
        xs = [p[0] for p in pts]; ys = [p[1] for p in pts]
        return self.app.add_furniture(fid, min(xs), min(ys), max(xs), max(ys),
                                      angle=self.shelf.get("angle", 0), draw=False)

    def _place_new(self, u, z):
        it = self._new_item(self.add_fid)
        if it is None:
            return
        H = self._frame()[3]
        b = self.lbox(it); d = b[3] - b[1]
        lcy = d / 2 + 1 if self.flip else H - d / 2 - 1        # against the front edge
        if not self._try_place(it, self.lx_from_u(u), lcy, z):
            self.app.furniture.remove(it)
            self._status(self.app.get_text("no_room"))
            return
        self._commit(select=it)

    def _copy(self):
        o = self.sel
        if o is None or o not in self.app.furniture:
            return
        it = self.app._copy_furniture(o)
        if it is None:
            return
        b = self.lbox(o)
        dz = self.app._furn_z(o)[0]
        # right next to the original if there is room, otherwise the next free spot
        if not self._try_place(it, b[2] + (b[2] - b[0]) / 2 + 0.1, (b[1] + b[3]) / 2, dz) and \
           not self._try_place(it, 0, (b[1] + b[3]) / 2, dz, search=True):
            self.app.furniture.remove(it)
            self._status(self.app.get_text("no_room"))
            return
        self._commit(select=it)

    def _delete(self):
        o = self.sel
        if o is None or o not in self.app.furniture:
            return
        self.app.select_single(o)
        self.app.delete_selected()
        self.sel = None
        self.refresh()

    def _props(self):
        o = self.sel if self.sel is not None else self.shelf
        if o in self.app.furniture:
            self.app._open_furn_props(o)

    def _nudge(self, du):
        o = self.sel
        if o is None:
            return
        b = self.lbox(o)
        step = -du if self.flip else du
        if self._try_place(o, (b[0] + b[2]) / 2 + step, (b[1] + b[3]) / 2, self.app._furn_z(o)[0]):
            self._commit(select=o)

    def _level(self, direction):
        if self.sel is None:
            return
        self.app.select_single(self.sel)
        self.app._move_level(direction)
        self.refresh()

    def _toggle_flip(self):
        self.flip = self.flip_var.get()
        self.refresh()

    # ── top strip: change depth ──────────────────────────────────────────────
    def _top_press(self, e):
        for (o, x0, y0, x1, y1) in reversed(self.top_hits):
            if x0 <= e.x <= x1 and y0 <= e.y <= y1:
                self.sel = o
                self.app.select_single(o)
                self.drag = {"item": o, "y": e.y, "moved": False}
                break
        self.draw_front(); self.draw_top(); self._status()

    def _top_drag(self, e):
        if not self.drag or "y" not in self.drag:
            return
        self.drag["moved"] = True
        self.drag["dy"] = e.y - self.drag["y"]
        o = self.drag["item"]
        b = self.lbox(o)
        u0, u1 = self.u_range(b[0], b[2])
        d0, d1 = self.depth_of(b[1], b[3])
        sd, yb = self.geo["sd"], self.geo["ybase"]
        self.top.delete("ghost")
        self.top.create_rectangle(self.fx(u0), yb - d1 * sd + self.drag["dy"], self.fx(u1),
                                  yb - d0 * sd + self.drag["dy"], outline="#2f6fed", dash=(4, 3),
                                  width=2, tags="ghost")

    def _top_release(self, e):
        d, self.drag = self.drag, None
        self.top.delete("ghost")
        if not d or not d.get("moved"):
            return
        o = d["item"]
        b = self.lbox(o)
        ddepth = -d["dy"] / self.geo["sd"]          # up in the strip = further back
        dly = ddepth if self.flip else -ddepth
        if not self._try_place(o, (b[0] + b[2]) / 2, round((b[1] + b[3]) / 2 + dly), self.app._furn_z(o)[0]):
            self._status(self.app.get_text("no_room"))
            self.refresh(); return
        self._commit(select=o)


# ─────────────────────────────────────────────────────────────────────────────
#  Splash screen
# ─────────────────────────────────────────────────────────────────────────────
SPLASH_VERSION = "V15"
EST_BLUE, EST_BLACK, EST_WHITE = "#0072ce", "#000000", "#ffffff"   # Estonian flag


class Splash:
    """Borderless start-up window: logo, name, author and a progress bar that
    follows the real loading steps. The floor-plan logo draws itself as the
    progress bar fills."""

    W, H = 600, 360
    BG_TOP, BG_BOTTOM = "#0c1524", "#17263f"
    ACCENT = "#3b8cff"
    MIN_TIME = 1.8          # seconds the splash stays up at least

    def __init__(self, root, texts):
        self.root = root
        self.t = texts
        self.t0 = time.perf_counter()
        self.frac = 0.0
        self.win = tk.Toplevel(root)
        self.win.overrideredirect(True)
        self.win.configure(bg=self.BG_TOP)
        try:
            self.win.attributes("-topmost", True)
        except tk.TclError:
            pass
        sw, sh = self.win.winfo_screenwidth(), self.win.winfo_screenheight()
        self.win.geometry(f"{self.W}x{self.H}+{(sw - self.W) // 2}+{(sh - self.H) // 2}")
        self.c = tk.Canvas(self.win, width=self.W, height=self.H, highlightthickness=0, bd=0, bg=self.BG_TOP)
        self.c.pack()
        self.font = self._pick_font()
        self._draw_static()
        self._logo_segments = self._logo()
        self._alpha(0.0)
        self.win.update()
        for i in range(1, 11):                     # fade in
            self._alpha(i / 10)
            self.win.update()
            time.sleep(0.015)

    # ── helpers ──────────────────────────────────────────────────────────────
    def _pick_font(self):
        try:
            from tkinter import font as tkfont
            fams = set(tkfont.families(self.root))
        except tk.TclError:
            fams = set()
        for f in ("Segoe UI", "Helvetica Neue", "Inter", "DejaVu Sans", "Liberation Sans", "Arial"):
            if f in fams:
                return f
        return "TkDefaultFont"

    def _alpha(self, a):
        try:
            self.win.attributes("-alpha", a)
        except tk.TclError:
            pass

    @staticmethod
    def _mix(a, b, t):
        a, b = a.lstrip("#"), b.lstrip("#")
        ca = [int(a[i:i + 2], 16) for i in (0, 2, 4)]; cb = [int(b[i:i + 2], 16) for i in (0, 2, 4)]
        return "#" + "".join(f"{int(x + (y - x) * t):02x}" for x, y in zip(ca, cb))

    # ── drawing ──────────────────────────────────────────────────────────────
    def _draw_static(self):
        c, W, H, f = self.c, self.W, self.H, self.font
        for y in range(0, H, 2):                   # vertical gradient background
            col = self._mix(self.BG_TOP, self.BG_BOTTOM, y / H)
            c.create_rectangle(0, y, W, y + 2, fill=col, outline=col)
        # faint blueprint grid on the right half
        for x in range(300, W, 20):
            c.create_line(x, 0, x, H, fill="#1b2c47")
        for y in range(0, H, 20):
            c.create_line(300, y, W, y, fill="#1b2c47")
        # Estonian tricolour along the top edge
        for i, col in enumerate((EST_BLUE, EST_BLACK, EST_WHITE)):
            c.create_rectangle(0, i * 3, W, i * 3 + 3, fill=col, outline=col)
        c.create_rectangle(0, 0, W - 1, H - 1, outline="#2a3c5c")

        # name + subtitle
        c.create_text(48, 118, text="My", anchor="sw", fill="#ffffff", font=(f, 40, "bold"))
        my_w = c.bbox(c.find_all()[-1])[2] - 48
        c.create_text(48 + my_w, 118, text="CAD", anchor="sw", fill=self.ACCENT, font=(f, 40, "bold"))
        c.create_text(50, 128, text=self.t["subtitle"], anchor="nw", fill="#9fb0cc", font=(f, 11))
        c.create_text(50, 152, text=SPLASH_VERSION, anchor="nw", fill="#5f7394", font=(f, 9, "bold"))

        # author + small flag
        fx, fy = 50, H - 64
        for i, col in enumerate((EST_BLUE, EST_BLACK, EST_WHITE)):
            c.create_rectangle(fx, fy + i * 6, fx + 27, fy + i * 6 + 6, fill=col, outline="")
        c.create_rectangle(fx, fy, fx + 27, fy + 18, outline="#3a4d6e")
        c.create_text(fx + 38, fy - 1, text=self.t["author"], anchor="nw", fill="#e6ecf5", font=(f, 11, "bold"))
        c.create_text(fx + 38, fy + 17, text=self.t["country"], anchor="nw", fill="#8293b0", font=(f, 9))
        c.create_text(W - 20, H - 14, text=f"© {time.strftime('%Y')} Germo", anchor="se",
                      fill="#5f7394", font=(f, 8))

        # progress bar
        self.bx0, self.bx1, self.by = 50, 290, 212
        c.create_rectangle(self.bx0, self.by, self.bx1, self.by + 5, fill="#22324d", outline="")
        self.bar = c.create_rectangle(self.bx0, self.by, self.bx0, self.by + 5, fill=self.ACCENT, outline="")
        self.status = c.create_text(50, self.by + 14, text="", anchor="nw", fill="#8293b0", font=(f, 9))
        self.pct = c.create_text(self.bx1, self.by + 14, text="0%", anchor="ne", fill="#5f7394", font=(f, 9))

    def _logo(self):
        """Line segments of a little floor plan; they appear one by one."""
        ox, oy, s = 345, 70, 2.1           # origin and scale (plan units -> px)
        P = lambda x, y: (ox + x * s, oy + y * s)
        walls = [((0, 0), (100, 0)), ((100, 0), (100, 100)), ((100, 100), (0, 100)), ((0, 100), (0, 0)),
                 ((55, 0), (55, 60)), ((55, 60), (100, 60)), ((0, 55), (35, 55))]
        segs = [("wall", P(*a), P(*b)) for a, b in walls]
        # door: gap + swing arc in the inner wall
        segs.append(("door", P(55, 72), P(55, 92)))
        # window on the right wall
        segs.append(("window", P(100, 20), P(100, 42)))
        # a sofa and a table
        segs.append(("furn", P(8, 70), P(30, 92)))
        segs.append(("furn", P(65, 12), P(90, 38)))
        # dimension line under the plan
        segs.append(("dim", P(0, 112), P(100, 112)))
        return segs

    def _draw_logo(self, frac):
        c = self.c
        c.delete("logo")
        n = len(self._logo_segments)
        shown = frac * n
        for i, (kind, a, b) in enumerate(self._logo_segments):
            if i >= shown:
                break
            part = min(1.0, shown - i)            # the segment being drawn grows
            bx = a[0] + (b[0] - a[0]) * part; by = a[1] + (b[1] - a[1]) * part
            if kind == "wall":
                c.create_line(a[0], a[1], bx, by, fill="#e9eef7", width=5, capstyle="projecting", tags="logo")
            elif kind == "door":
                c.create_line(a[0], a[1], b[0], b[1], fill=self.BG_BOTTOM, width=7, tags="logo")
                if part >= 1:
                    r = b[1] - a[1]
                    c.create_arc(a[0] - r, a[1] - r, a[0] + r, a[1] + r, start=270, extent=90,
                                 style="arc", outline="#7f93b5", dash=(3, 3), tags="logo")
                    c.create_line(a[0], a[1], a[0] + r, a[1], fill="#e9eef7", width=2, tags="logo")
            elif kind == "window":
                c.create_line(a[0], a[1], b[0], b[1], fill=self.ACCENT, width=7, tags="logo")
                c.create_line(a[0], a[1], b[0], b[1], fill="#cfe4ff", width=1, tags="logo")
            elif kind == "furn":
                col = self._mix("#17263f", self.ACCENT, 0.45 * part)
                c.create_rectangle(a[0], a[1], b[0], b[1], fill=col, outline="#6fa6ff", tags="logo")
            elif kind == "dim":
                c.create_line(a[0], a[1], bx, by, fill="#6f83a6", arrow="both" if part >= 1 else "first",
                              arrowshape=(6, 7, 3), tags="logo")
                if part >= 1:
                    c.create_text((a[0] + b[0]) / 2, a[1] - 3, text="5.00 m", anchor="s",
                                  fill="#9fb0cc", font=(self.font, 8), tags="logo")

    def _set(self, frac, text=None):
        self.frac = frac
        x = self.bx0 + (self.bx1 - self.bx0) * frac
        self.c.coords(self.bar, self.bx0, self.by, x, self.by + 5)
        self.c.itemconfigure(self.pct, text=f"{int(frac * 100)}%")
        if text is not None:
            self.c.itemconfigure(self.status, text=text)
        self._draw_logo(frac)
        self.win.update()

    # ── public ───────────────────────────────────────────────────────────────
    def step(self, key, target):
        """Show a loading step and glide the bar to `target` (0..1)."""
        text = self.t.get(key, key)
        start = self.frac
        n = 14
        for i in range(1, n + 1):
            e = 1 - (1 - i / n) ** 3                # ease-out
            self._set(start + (target - start) * e, text)
            time.sleep(0.012)

    def finish(self):
        self.step("ready", 1.0)
        left = self.MIN_TIME - (time.perf_counter() - self.t0)
        if left > 0:
            end = time.perf_counter() + left
            while time.perf_counter() < end:
                self.win.update()
                time.sleep(0.02)
        for i in range(10, -1, -1):                 # fade out
            self._alpha(i / 10)
            self.win.update()
            time.sleep(0.015)
        self.win.destroy()


def splash_texts():
    """Splash texts in the language from config.json (before the app exists)."""
    lang = DEFAULT_LANGUAGE
    try:
        with open(CONFIG_PATH, "r", encoding="utf-8") as fp:
            lang = json.load(fp).get("language", lang)
    except (OSError, ValueError):
        pass
    langs = load_languages()
    strings = dict(FALLBACK_STRINGS)
    strings.update(langs.get("en", {}).get("strings", {}))
    strings.update(langs.get(lang, {}).get("strings", {}))
    return {k: strings.get("splash_" + k, k) for k in
            ("subtitle", "author", "country", "lang", "lib", "ui", "ready")}


# ─────────────────────────────────────────────────────────────────────────────
#  App
# ─────────────────────────────────────────────────────────────────────────────

class App:
    def __init__(self, root, splash=None):
        self.root = root
        step = splash.step if splash else (lambda key, frac: None)
        step("lang", 0.15)
        self._load_settings()
        self.root.title(self.get_text("title"))
        step("lib", 0.40)
        self._init_state()
        step("ui", 0.70)
        self._apply_ttk_style()

        # Layout containers to allow dynamic ordering / clearing
        self.toolbar_container = ttk.Frame(self.root)
        self.toolbar_container.pack(fill="x", padx=5, pady=4)

        self.floor_row_container = ttk.Frame(self.root)
        self.floor_row_container.pack(fill="x", padx=5, pady=(0,4))

        self.main_pane = ttk.Frame(self.root)
        self.main_pane.pack(fill="both", expand=True)

        self._build_floor_row_container()
        self._build_toolbar()
        self._build_main_area()
        self.draw_grid()

    # ═══════════════════════════════════════════════════════════════════════════
    #  Settings and Translation Handlers
    # ═══════════════════════════════════════════════════════════════════════════

    def _load_settings(self):
        self.languages = load_languages()
        self.language = DEFAULT_LANGUAGE
        self.units = "metric"
        self.theme = "light"
        self.auto_stack = True
        self.seeded = []
        self.collapsed_cats = set()
        self.default_wall_height = DEFAULT_WALL_HEIGHT
        self.default_wall_thickness = DEFAULT_WALL_THICKNESS
        if os.path.exists(CONFIG_PATH):
            try:
                with open(CONFIG_PATH, "r", encoding="utf-8") as f:
                    cfg = json.load(f)
                    self.language = cfg.get("language", DEFAULT_LANGUAGE)
                    self.units = cfg.get("units", "metric")
                    self.theme = cfg.get("theme", "light")
                    self.auto_stack = bool(cfg.get("auto_stack", True))
                    self.seeded = list(cfg.get("seeded", []))
                    self.collapsed_cats = set(cfg.get("collapsed_cats", []))
                    self.default_wall_height = float(cfg.get("wall_height", DEFAULT_WALL_HEIGHT))
                    self.default_wall_thickness = float(cfg.get("wall_thickness", DEFAULT_WALL_THICKNESS))
            except Exception:
                pass
        # Fallback security if loading returns empty or invalid values
        self.language = self._valid_language(self.language)
        if self.units not in ("metric", "imperial"):
            self.units = "metric"
        if self.theme not in ("light", "dark"):
            self.theme = "light"

    def _save_settings(self):
        try:
            with open(CONFIG_PATH, "w", encoding="utf-8") as f:
                json.dump({"language": self.language, "units": self.units,
                           "theme": self.theme,
                           "auto_stack": self.auto_stack,
                           "seeded": self.seeded,
                           "collapsed_cats": sorted(self.collapsed_cats),
                           "wall_height": self.default_wall_height,
                           "wall_thickness": self.default_wall_thickness}, f, indent=4)
        except Exception:
            pass

    # ═══════════════════════════════════════════════════════════════════════════
    #  Theme helpers
    # ═══════════════════════════════════════════════════════════════════════════

    def C(self, key):
        """Look up a color for the currently active theme."""
        return THEMES.get(self.theme, THEMES["light"])[key]

    def _ink(self, name):
        """Resolve a logical pen color ('black'/'blue'/'red', as stored on
        walls/freehand strokes) to an actual hex color for the current theme,
        so 'black' ink stays visible instead of vanishing on a dark canvas."""
        mapping = {"black": self.C("ink_black"), "blue": self.C("ink_blue"), "red": self.C("ink_red")}
        return mapping.get(name, name)

    def _menu_kwargs(self):
        return dict(bg=self.C("toolbar_bg"), fg=self.C("text"),
                    activebackground=self.C("accent_soft"), activeforeground=self.C("text"),
                    disabledforeground=self.C("text_muted"), relief="flat", bd=0)

    def _apply_ttk_style(self):
        style = ttk.Style()
        try:
            style.theme_use("clam")
        except tk.TclError:
            pass
        bg      = self.C("app_bg");     panel  = self.C("panel_bg")
        tbg     = self.C("toolbar_bg"); text   = self.C("text")
        muted   = self.C("text_muted"); border = self.C("border")
        accent  = self.C("accent");     soft   = self.C("accent_soft")

        style.configure(".", background=bg, foreground=text,
                         fieldbackground=tbg, bordercolor=border,
                         lightcolor=tbg, darkcolor=border,
                         troughcolor=bg, focuscolor=accent)
        style.configure("TFrame", background=bg)
        style.configure("TLabel", background=bg, foreground=text)
        style.configure("TButton", background=tbg, foreground=text,
                         bordercolor=border, padding=4)
        style.map("TButton", background=[("active", soft), ("pressed", soft)])
        style.configure("TMenubutton", background=tbg, foreground=text,
                         bordercolor=border, padding=4)
        style.map("TMenubutton", background=[("active", soft)])
        style.configure("TCheckbutton", background=bg, foreground=text)
        style.map("TCheckbutton", background=[("active", bg)])
        style.configure("TRadiobutton", background=bg, foreground=text)
        style.map("TRadiobutton", background=[("active", bg)])
        style.configure("Toolbutton", background=tbg, foreground=text,
                         bordercolor=border, padding=4)
        style.map("Toolbutton",
                   background=[("selected", soft), ("active", soft)],
                   foreground=[("selected", accent)])
        style.configure("TSeparator", background=border)
        style.configure("TEntry", fieldbackground=tbg, foreground=text,
                         bordercolor=border, insertcolor=text)
        style.configure("TScrollbar", background=tbg, troughcolor=bg,
                         bordercolor=border, arrowcolor=text)
        self.root.configure(bg=bg)

    def _change_theme(self):
        self.theme = self.theme_var.get()
        self._save_settings()
        self._apply_ttk_style()
        self._build_floor_row_container()
        self._build_toolbar()
        self._build_main_area()
        self._redraw_all()
        if self.view3d and self.view3d.exists():
            self.view3d.close(); self.open_3d_view()

    def _valid_language(self, code):
        """Return code if a language file for it exists, otherwise the
        default language (or English, which always exists)."""
        if code in self.languages:
            return code
        if DEFAULT_LANGUAGE in self.languages:
            return DEFAULT_LANGUAGE
        return "en"

    def get_text(self, key, default=""):
        # 1) active language file, 2) English file, 3) built-in English
        lang = self.languages.get(self.language) or {}
        val = lang.get("strings", {}).get(key)
        if val is not None:
            return val
        val_en = self.languages.get("en", {}).get("strings", {}).get(key)
        if val_en is not None:
            return val_en
        val_fb = FALLBACK_STRINGS.get(key)
        if val_fb is not None:
            return val_fb
        return default if default else key

    def _reload_languages(self):
        """Re-read lang/*.json without restarting - handy while translating."""
        self.languages = load_languages()
        self.language = self._valid_language(self.language)
        self.lang_var.set(self.language)
        self._change_language()

    # ═══════════════════════════════════════════════════════════════════════════
    #  State Initializer
    # ═══════════════════════════════════════════════════════════════════════════

    def _init_state(self):
        self.zoom         = 1.0
        self.lang_var     = tk.StringVar(value=self.language)
        self.unit_var     = tk.StringVar(value=self.units)
        self.theme_var    = tk.StringVar(value=self.theme)
        self.grid_val_var = tk.IntVar(value=20 if self.units == "metric" else 12)

        self.furniture_defs = []
        self._load_furniture_library()
        # doors & windows in the library start the Door/Window tools (older
        # libraries had "door" as a plain furniture symbol - migrate it)
        old_door = self._furn_def("door")
        if old_door is not None and old_door.get("draw_fn") != "opening_door":
            self._delete_furniture_entry("door")
        self._ensure_builtin_item("door", "door_lbl", "doors_windows", 90, 90, "opening_door")
        self._ensure_builtin_item("window", "window_lbl", "doors_windows", 120, 20, "opening_window")
        self._seed_storage_items()
        self.categories = []
        self._load_categories()

        # Floors and elements
        self.floors      = [self._new_floor_data()]
        self.current_floor = 0
        self.walls       = self.floors[0]["walls"]
        self.furniture   = self.floors[0]["furniture"]
        self.freehand    = self.floors[0]["freehand"]
        self.measurements = self.floors[0]["measurements"]
        self._ghost_ids  = []         
        self.selected    = None       
        self.multi_sel   = []         
        self.drag_handle = None
        self.start       = None
        self.preview     = None
        self._pending_fid = self._pending_dfw = self._pending_dfh = None
        self._rb_start   = None       
        self._rb_rect    = None       
        self._mdrag_start_wx = None
        self._mdrag_start_wy = None
        self._mdrag_origins  = []     
        self._fh_points  = None       
        self.furniture_dimmed = False 

        # Measuring tool
        self.measure_start   = None
        self._measure_preview = None
        self._measure_preview_text = None

        # Auto room detection (cache of the last computed rooms for the
        # current floor + the canvas item ids currently drawn for them)
        self.rooms = []
        self._room_canvas_ids = []

        # 3D view window (None while closed) + pending refresh timer
        self.view3d = None
        self._3d_after = None
        self.shelf_view = None

    @staticmethod
    def _new_floor_data():
        return {"walls": [], "furniture": [], "freehand": [], "measurements": []}

    # ═══════════════════════════════════════════════════════════════════════════
    #  Furniture library (external JSON, grouped by category)
    # ═══════════════════════════════════════════════════════════════════════════

    def _seed_library_defaults(self):
        """Write the built-in furniture set (FURNITURE_DEFS) out to
        library/<category>.json files. Only used the first time the library
        folder is missing/empty, so the app has something to load."""
        by_cat = {}
        for (fid, label_key, cat, dw, dh, fn) in FURNITURE_DEFS:
            by_cat.setdefault(cat, []).append({
                "fid": fid, "label_key": label_key, "category": cat,
                "width": dw, "height": dh, "draw_fn": fn, "points": None})
        try:
            os.makedirs(LIBRARY_DIR, exist_ok=True)
            for cat, entries in by_cat.items():
                path = os.path.join(LIBRARY_DIR, f"{cat}.json")
                with open(path, "w", encoding="utf-8") as fp:
                    json.dump(entries, fp, indent=2, ensure_ascii=False)
        except OSError:
            pass

    def _load_furniture_library(self):
        if not os.path.isdir(LIBRARY_DIR):
            self._seed_library_defaults()
        defs = []
        try:
            fnames = sorted(f for f in os.listdir(LIBRARY_DIR)
                            if f.endswith(".json") and not f.startswith("_"))
        except OSError:
            fnames = []
        for fname in fnames:
            path = os.path.join(LIBRARY_DIR, fname)
            try:
                with open(path, "r", encoding="utf-8") as fp:
                    entries = json.load(fp)
                for e in entries:
                    if isinstance(e, dict) and "fid" in e and "width" in e and "height" in e:
                        e.setdefault("category", "custom")
                        e.setdefault("draw_fn", "")
                        e.setdefault("points", None)
                        e.setdefault("shape", None)
                        e.setdefault("label_key", e["fid"])
                        defs.append(e)
            except (OSError, json.JSONDecodeError):
                continue
        if not defs:
            # folder existed but was empty/unreadable - reseed from built-ins
            self._seed_library_defaults()
            defs = [{"fid": f, "label_key": lb, "category": cat,
                     "width": dw, "height": dh, "draw_fn": fn, "points": None}
                    for (f, lb, cat, dw, dh, fn) in FURNITURE_DEFS]
        self.furniture_defs = defs

    def _furn_def(self, fid):
        for e in self.furniture_defs:
            if e.get("fid") == fid:
                return e
        return None

    def _seed_storage_items(self):
        """Add a ready-made storage shelf and box (category "storage") once.
        If the user deletes them later they are not added again."""
        if "storage" in self.seeded:
            return
        rect = lambda w, d: [{"type": "polygon", "points": [[0, 0], [w, 0], [w, d], [0, d]]}]
        items = [
            {"fid": "storage_shelf", "label_key": "storage_shelf_lbl", "category": "storage",
             "width": 120, "height": 50, "draw_fn": "custom_shape", "shape": rect(120, 50),
             "fill": "#a9bccf", "outline": "#5d7186", "z_height": 200,
             "shelf": {"levels": 5, "bottom": 10, "board": SHELF_BOARD, "post": SHELF_POST}},
            {"fid": "storage_box", "label_key": "storage_box_lbl", "category": "storage",
             "width": 60, "height": 40, "draw_fn": "custom_shape", "shape": rect(60, 40),
             "fill": "#c8a26a", "outline": "#7a5a2a", "z_height": 30},
        ]
        for e in items:
            if self._furn_def(e["fid"]) is None:
                self._save_custom_furniture(e)
        self.seeded.append("storage")
        self._save_settings()

    def _ensure_builtin_item(self, fid, label_key, category, width, height, draw_fn):
        """Add a built-in furniture item that didn't exist yet in an already-
        seeded library folder (e.g. the app added a new default piece after
        the user's library was first created). No-op if it's already there."""
        if self._furn_def(fid) is not None:
            return
        entry = {"fid": fid, "label_key": label_key, "category": category,
                 "width": width, "height": height, "draw_fn": draw_fn,
                 "points": None, "shape": None}
        self._save_custom_furniture(entry)

    def _save_custom_furniture(self, entry):
        """Append a newly-created custom furniture entry to its category's
        JSON file in the library folder (creating the file if needed)."""
        cat = entry.get("category") or "custom"
        safe_name = re.sub(r'[^a-zA-Z0-9_]+', '_', cat).strip('_').lower() or "custom"
        path = os.path.join(LIBRARY_DIR, f"{safe_name}.json")
        try:
            os.makedirs(LIBRARY_DIR, exist_ok=True)
            existing = []
            if os.path.exists(path):
                try:
                    with open(path, "r", encoding="utf-8") as fp:
                        existing = json.load(fp)
                    if not isinstance(existing, list):
                        existing = []
                except (OSError, json.JSONDecodeError):
                    existing = []
            existing.append(entry)
            with open(path, "w", encoding="utf-8") as fp:
                json.dump(existing, fp, indent=2, ensure_ascii=False)
        except OSError as e:
            messagebox.showerror(self.get_text("error_title"), str(e))
            return False
        self.furniture_defs.append(entry)
        return True

    def _delete_furniture_entry(self, fid):
        """Remove a furniture entry from memory and from whichever library
        JSON file on disk currently holds it."""
        self.furniture_defs = [e for e in self.furniture_defs if e.get("fid") != fid]
        try:
            fnames = [f for f in os.listdir(LIBRARY_DIR)
                      if f.endswith(".json") and not f.startswith("_")]
        except OSError:
            fnames = []
        for fname in fnames:
            path = os.path.join(LIBRARY_DIR, fname)
            try:
                with open(path, "r", encoding="utf-8") as fp:
                    entries = json.load(fp)
                if not isinstance(entries, list):
                    continue
            except (OSError, json.JSONDecodeError):
                continue
            new_entries = [e for e in entries if e.get("fid") != fid]
            if len(new_entries) != len(entries):
                try:
                    with open(path, "w", encoding="utf-8") as fp:
                        json.dump(new_entries, fp, indent=2, ensure_ascii=False)
                except OSError:
                    pass
                break

    # ═══════════════════════════════════════════════════════════════════════════
    #  Furniture categories (library/_categories.json)
    #  Each category: {"id": "kitchen", "label_key": "kitchen"} for built-ins
    #  (translated through the lang files) or {"id": "garden",
    #  "names": {"et": "Aed", "en": "Garden"}} for user-created ones.
    #  "names" always wins over "label_key" for the languages it contains.
    # ═══════════════════════════════════════════════════════════════════════════

    def _load_categories(self):
        cats = []
        if os.path.exists(CATEGORIES_FILE):
            try:
                with open(CATEGORIES_FILE, "r", encoding="utf-8") as fp:
                    data = json.load(fp)
                if isinstance(data, list):
                    cats = [c for c in data if isinstance(c, dict) and c.get("id")]
            except (OSError, json.JSONDecodeError):
                cats = []
        changed = not cats
        if not cats:
            cats = [{"id": cid, "label_key": ("custom_cat" if cid == "custom" else cid)}
                    for cid in DEFAULT_CATEGORIES]
        # any category used by a furniture piece but not listed (e.g. typed
        # by hand in an older version) is added to the end of the list
        known = {c["id"] for c in cats}
        if "doors_windows" not in known:
            cats.insert(0, {"id": "doors_windows", "label_key": "doors_windows"})
            known.add("doors_windows")
            changed = True
        for e in self.furniture_defs:
            cid = e.get("category") or "custom"
            if cid not in known:
                cats.append({"id": cid, "label_key": cid})
                known.add(cid)
                changed = True
        self.categories = cats
        if changed:
            self._save_categories()

    def _save_categories(self):
        try:
            os.makedirs(LIBRARY_DIR, exist_ok=True)
            with open(CATEGORIES_FILE, "w", encoding="utf-8") as fp:
                json.dump(self.categories, fp, indent=2, ensure_ascii=False)
        except OSError as e:
            messagebox.showerror(self.get_text("error_title"), str(e))

    def _category(self, cid):
        for c in self.categories:
            if c["id"] == cid:
                return c
        return None

    def _cat_name(self, cid):
        """Display name of a category in the current language."""
        c = self._category(cid)
        if c is None:
            return self.get_text(cid)
        names = c.get("names") or {}
        if names.get(self.language):
            return names[self.language]
        if c.get("label_key"):
            txt = self.get_text(c["label_key"])
            if txt != c["label_key"] or not names:
                return txt
        for code in ("en", DEFAULT_LANGUAGE):
            if names.get(code):
                return names[code]
        return next(iter(names.values()), cid)

    def _cat_order(self, cid):
        for i, c in enumerate(self.categories):
            if c["id"] == cid:
                return i
        return len(self.categories)

    def _cat_item_count(self, cid):
        return sum(1 for e in self.furniture_defs if (e.get("category") or "custom") == cid)

    @staticmethod
    def _slugify(text):
        t = unicodedata.normalize("NFKD", text)
        t = "".join(ch for ch in t if not unicodedata.combining(ch))
        return re.sub(r'[^a-z0-9]+', '_', t.lower()).strip('_')

    def _add_category(self, name):
        """Create a new category from a display name in the current language.
        Returns the new id, or None if the name is empty or already taken."""
        name = name.strip()
        if not name:
            return None
        if any(self._cat_name(c["id"]).casefold() == name.casefold() for c in self.categories):
            return None
        base = self._slugify(name) or "category"
        taken = {c["id"].lower() for c in self.categories} | \
                {self._slugify(c["id"]) for c in self.categories}
        cid, n = base, 2
        while cid in taken:
            cid = f"{base}_{n}"; n += 1
        self.categories.append({"id": cid, "names": {self.language: name}})
        self._save_categories()
        return cid

    def _rename_category(self, cid, name):
        name = name.strip()
        c = self._category(cid)
        if c is None or not name:
            return False
        if any(o["id"] != cid and self._cat_name(o["id"]).casefold() == name.casefold()
               for o in self.categories):
            return False
        c.setdefault("names", {})[self.language] = name
        self._save_categories()
        return True

    def _delete_category(self, cid):
        if self._cat_item_count(cid) > 0:
            return False
        self.categories = [c for c in self.categories if c["id"] != cid]
        self._save_categories()
        return True

    def _move_category(self, cid, delta):
        i = self._cat_order(cid)
        j = i + delta
        if 0 <= i < len(self.categories) and 0 <= j < len(self.categories):
            self.categories[i], self.categories[j] = self.categories[j], self.categories[i]
            self._save_categories()
            return True
        return False

    def _ask_string(self, parent, title, prompt, initial=""):
        """Small themed text-input dialog. Returns the text or None."""
        dlg = tk.Toplevel(parent)
        dlg.configure(bg=self.C("app_bg"))
        dlg.title(title)
        dlg.resizable(False, False)
        dlg.transient(parent)
        frm = ttk.Frame(dlg, padding=12); frm.pack()
        ttk.Label(frm, text=prompt).grid(row=0, column=0, sticky="w", pady=(0,4))
        var = tk.StringVar(value=initial)
        ent = ttk.Entry(frm, textvariable=var, width=28)
        ent.grid(row=1, column=0, sticky="we")
        result = {"value": None}

        def ok(_e=None):
            result["value"] = var.get()
            dlg.destroy()

        btns = ttk.Frame(frm); btns.grid(row=2, column=0, sticky="e", pady=(10,0))
        ttk.Button(btns, text=self.get_text("ok"), command=ok).pack(side="left", padx=2)
        ttk.Button(btns, text=self.get_text("cancel"), command=dlg.destroy).pack(side="left", padx=2)
        dlg.bind("<Return>", ok)
        dlg.bind("<Escape>", lambda e: dlg.destroy())
        ent.focus_set(); ent.select_range(0, "end")
        dlg.grab_set()
        dlg.wait_window()
        try:
            parent.grab_set()   # give the modal grab back to the calling dialog
        except tk.TclError:
            pass
        return result["value"]

    def _prompt_new_category(self, parent):
        """Ask for a name and create the category. Returns the new id or None."""
        while True:
            name = self._ask_string(parent, self.get_text("new_category"),
                                    f"{self.get_text('category_name')}:")
            if name is None:
                return None
            if not name.strip():
                messagebox.showwarning(self.get_text("error_title"),
                                       self.get_text("category_name_required"), parent=parent)
                continue
            cid = self._add_category(name)
            if cid is None:
                messagebox.showwarning(self.get_text("error_title"),
                                       self.get_text("category_exists"), parent=parent)
                continue
            self._populate_library()
            return cid

    def _open_category_manager(self, parent=None, on_close=None):
        parent = parent or self.root
        dlg = tk.Toplevel(parent)
        dlg.configure(bg=self.C("app_bg"))
        dlg.title(self.get_text("categories"))
        dlg.resizable(False, False)
        dlg.transient(parent)
        frm = ttk.Frame(dlg, padding=12); frm.pack()

        wrap = ttk.Frame(frm); wrap.grid(row=0, column=0, sticky="ns")
        sb = ttk.Scrollbar(wrap, orient="vertical")
        lb = tk.Listbox(wrap, width=30, height=14, yscrollcommand=sb.set,
                        bg=self.C("lib_row_bg"), fg=self.C("text"),
                        selectbackground=self.C("accent"), selectforeground="white",
                        highlightthickness=1, highlightbackground=self.C("border"),
                        bd=0, activestyle="none", exportselection=False)
        sb.config(command=lb.yview)
        lb.pack(side="left", fill="both"); sb.pack(side="right", fill="y")

        def refresh(select_id=None):
            lb.delete(0, "end")
            for c in self.categories:
                n = self._cat_item_count(c["id"])
                lb.insert("end", f"{self._cat_name(c['id'])}  ({n} {self.get_text('items_count')})")
            if select_id is not None:
                i = self._cat_order(select_id)
                if i < len(self.categories):
                    lb.selection_set(i); lb.see(i)

        def sel_id():
            s = lb.curselection()
            if not s or s[0] >= len(self.categories):
                return None
            return self.categories[s[0]]["id"]

        def changed(select_id=None):
            refresh(select_id)
            self._populate_library()

        def do_add():
            cid = self._prompt_new_category(dlg)
            if cid:
                changed(cid)

        def do_rename():
            cid = sel_id()
            if cid is None:
                return
            while True:
                name = self._ask_string(dlg, self.get_text("rename"),
                                        f"{self.get_text('category_name')}:", self._cat_name(cid))
                if name is None:
                    return
                if self._rename_category(cid, name):
                    changed(cid); return
                messagebox.showwarning(self.get_text("error_title"),
                                       self.get_text("category_exists") if name.strip()
                                       else self.get_text("category_name_required"), parent=dlg)

        def do_delete():
            cid = sel_id()
            if cid is None:
                return
            if self._cat_item_count(cid) > 0:
                messagebox.showinfo(self.get_text("categories"),
                                    self.get_text("category_not_empty"), parent=dlg)
                return
            if messagebox.askyesno(self.get_text("confirm_title"),
                                   self.get_text("confirm_delete_category"), parent=dlg):
                self._delete_category(cid)
                changed()

        def do_move(delta):
            cid = sel_id()
            if cid is not None and self._move_category(cid, delta):
                changed(cid)

        btns = ttk.Frame(frm); btns.grid(row=0, column=1, sticky="n", padx=(10,0))
        for txt, cmd in [(f"+ {self.get_text('add')}", do_add),
                         (f"✎ {self.get_text('rename')}", do_rename),
                         (f"🗑 {self.get_text('delete')}", do_delete),
                         ("▲", lambda: do_move(-1)),
                         ("▼", lambda: do_move(1))]:
            ttk.Button(btns, text=txt, command=cmd).pack(fill="x", pady=2)

        def close():
            dlg.destroy()
            if on_close:
                on_close()
            if parent is not self.root:
                try:
                    parent.grab_set()
                except tk.TclError:
                    pass

        ttk.Button(frm, text=self.get_text("close"), command=close).grid(
            row=1, column=0, columnspan=2, sticky="e", pady=(10,0))
        dlg.protocol("WM_DELETE_WINDOW", close)
        dlg.bind("<Escape>", lambda e: close())
        lb.bind("<Double-Button-1>", lambda e: do_rename())
        refresh()
        dlg.grab_set()

    @staticmethod
    def _darken_hex(hex_color, factor=0.6):
        """Return a darker shade of a #rrggbb color, used to auto-derive an
        outline color from a chosen fill color."""
        h = (hex_color or "").lstrip('#')
        if len(h) != 6:
            return "#8a7452"
        try:
            r, g, b = int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)
        except ValueError:
            return "#8a7452"
        r, g, b = int(r * factor), int(g * factor), int(b * factor)
        return f"#{r:02x}{g:02x}{b:02x}"

    # ═══════════════════════════════════════════════════════════════════════════
    #  Coordinate & Unit conversion helpers
    # ═══════════════════════════════════════════════════════════════════════════

    def w2c(self, v):
        return v * self.zoom

    def c2w(self, v):
        return v / self.zoom

    def grid_step(self):
        val = self.grid_val_var.get()
        if self.units == "metric":
            # 1 pixel is 1 cm internally, so grid step in px = value in cm
            return val
        else:
            # 1 inch is approx 2.54 cm. (1 pixel is 1 cm internally, so 1 inch = 2.54 pixels)
            return val * 2.54

    def snap_world(self, world_v):
        step = self.grid_step()
        return round(world_v / step) * step

    def event_world(self, event):
        cx = self.canvas.canvasx(event.x)
        cy = self.canvas.canvasy(event.y)
        return self.c2w(cx), self.c2w(cy)

    def format_length(self, world_px):
        # 1 pixel is 1 cm in coordinates
        cm = world_px
        if self.units == "metric":
            meters = cm / 100.0
            return f"{meters:.2f} m"
        else:
            # Convert cm to inches, then to feet
            inches = cm * 0.393701
            feet = inches / 12.0
            return f"{feet:.2f} ft"

    def wall_text(self, wx1, wy1, wx2, wy2):
        d = sqrt((wx2-wx1)**2 + (wy2-wy1)**2)
        return self.format_length(d)

    def furn_size_text(self, item):
        w = abs(item["x2"]-item["x1"]); h = abs(item["y2"]-item["y1"])
        angle = item["angle"]
        txt = f"{self.format_length(w)} × {self.format_length(h)}  {angle}°"
        z = item.get("z_elev", 0) or 0
        if z > 0.5:
            txt += f"  ↑{self.format_length(z)}"
        return txt

    def format_area(self, world_area_cm2):
        # 1 world unit is 1 cm, so area is already in cm^2
        if self.units == "metric":
            return f"{world_area_cm2/10000.0:.2f} m²"
        else:
            return f"{world_area_cm2/929.0304:.1f} ft²"

    # ═══════════════════════════════════════════════════════════════════════════
    #  UI Layout and Renderers
    # ═══════════════════════════════════════════════════════════════════════════

    def _build_toolbar(self):
        top = self.toolbar_container
        for w in top.winfo_children():
            w.destroy()

        # ── File Menu ────────────────────────────────────────────────────────
        file_menu = tk.Menu(self.root, tearoff=0, **self._menu_kwargs())
        file_menu.add_command(label=f"💾 {self.get_text('save_proj')}", command=self.save_json)
        file_menu.add_command(label=f"📂 {self.get_text('load_proj')}", command=self.load_json)
        file_menu.add_separator()
        file_menu.add_command(label=f"📤 {self.get_text('export_obj')}", command=self.export_obj)
        ttk.Menubutton(top, text=f"📁 {self.get_text('file')}", menu=file_menu).pack(side="left", padx=(0,4))

        # ── Settings Menu ─────────────────────────────────────────────────────
        settings_menu = tk.Menu(self.root, tearoff=0, **self._menu_kwargs())
        
        lang_menu = tk.Menu(settings_menu, tearoff=0, **self._menu_kwargs())
        for code, info in sorted(self.languages.items(), key=lambda kv: kv[1]["name"].lower()):
            lang_menu.add_radiobutton(label=info["name"], variable=self.lang_var, value=code,
                                      command=self._change_language)
        lang_menu.add_separator()
        lang_menu.add_command(label=f"🔄 {self.get_text('reload_languages')}",
                              command=self._reload_languages)
        settings_menu.add_cascade(label=self.get_text("language"), menu=lang_menu)
        
        unit_menu = tk.Menu(settings_menu, tearoff=0, **self._menu_kwargs())
        unit_menu.add_radiobutton(label=f"{self.get_text('metric')} (m/cm)", variable=self.unit_var, value="metric", command=self._change_units)
        unit_menu.add_radiobutton(label=f"{self.get_text('imperial')} (ft/in)", variable=self.unit_var, value="imperial", command=self._change_units)
        settings_menu.add_cascade(label=self.get_text("units"), menu=unit_menu)

        theme_menu = tk.Menu(settings_menu, tearoff=0, **self._menu_kwargs())
        theme_menu.add_radiobutton(label=f"☀ {self.get_text('theme_light')}", variable=self.theme_var,
                                    value="light", command=self._change_theme)
        theme_menu.add_radiobutton(label=f"🌙 {self.get_text('theme_dark')}", variable=self.theme_var,
                                    value="dark", command=self._change_theme)
        settings_menu.add_cascade(label=self.get_text("theme"), menu=theme_menu)
        settings_menu.add_separator()
        settings_menu.add_command(label=f"🧱 {self.get_text('wall_defaults')}",
                                  command=self._open_wall_defaults)
        
        ttk.Menubutton(top, text=f"⚙ {self.get_text('settings')}", menu=settings_menu).pack(side="left", padx=(0,4))

        ttk.Separator(top, orient="vertical").pack(side="left", fill="y", padx=6)

        # ── Tool selection Mode ───────────────────────────────────────────────
        self.mode = tk.StringVar(value="select")
        self.mode.trace_add("write", lambda *a: self._on_mode_change())
        for text_key, val in [("select", "select"), ("wall", "draw_wall"),
                              ("freehand", "draw_free"), ("edit", "edit"),
                              ("measure", "measure"), ("door_tool", "place_door"),
                              ("window_tool", "place_window")]:
            symbols = {"select": "🖱 ", "draw_wall": "🧱 ", "draw_free": "✏ ", "edit": "✥ ", "measure": "📐 ",
                       "place_door": "🚪 ", "place_window": "🪟 "}
            display_text = symbols.get(val, "") + self.get_text(text_key)
            ttk.Radiobutton(top, text=display_text, variable=self.mode, value=val,
                            style="Toolbutton").pack(side="left", padx=1)

        ttk.Separator(top, orient="vertical").pack(side="left", fill="y", padx=6)

        ttk.Button(top, text=f"🧊 {self.get_text('view_3d')}", command=self.open_3d_view).pack(side="left", padx=2)

        ttk.Separator(top, orient="vertical").pack(side="left", fill="y", padx=6)

        # ── Rotate buttons ────────────────────────────────────────────────────
        ttk.Button(top, text="↺ L", width=4, command=self._rotate_ccw).pack(side="left")
        ttk.Button(top, text="R ↻", width=4, command=self._rotate_cw).pack(side="left")

        ttk.Separator(top, orient="vertical").pack(side="left", fill="y", padx=6)

        # ── Furniture dimming checkbox ────────────────────────────────────────
        self.furn_dim_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(top, text=f"🙈 {self.get_text('hide_furn')}", variable=self.furn_dim_var,
                        style="Toolbutton",
                        command=self._toggle_furniture_dim).pack(side="left", padx=2)
        self.stack_var = tk.BooleanVar(value=self.auto_stack)
        ttk.Checkbutton(top, text=f"📦 {self.get_text('auto_stack')}", variable=self.stack_var,
                        style="Toolbutton", command=self._toggle_auto_stack).pack(side="left", padx=2)

        ttk.Separator(top, orient="vertical").pack(side="left", fill="y", padx=6)

        # ── Style properties ──────────────────────────────────────────────────
        self.thickness = tk.IntVar(value=4)
        self.color = tk.StringVar(value="black")

        self.style_menubtn = ttk.Menubutton(top, text=f"🎨 {self.get_text('style')}", menu=self._build_style_menu())
        self.style_menubtn.pack(side="left", padx=4)
        self._update_style_label()

        ttk.Separator(top, orient="vertical").pack(side="left", fill="y", padx=6)

        # ── Room dimensions popup trigger ────────────────────────────────────
        self.room_w_var = tk.StringVar(value="4")
        self.room_h_var = tk.StringVar(value="3")
        ttk.Button(top, text=f"🏠 {self.get_text('add_room')}", command=self._open_room_dialog).pack(side="left", padx=2)

        # ── Auto room detection toggle ────────────────────────────────────────
        self.auto_rooms_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(top, text=f"🏷 {self.get_text('auto_rooms')}", variable=self.auto_rooms_var,
                        style="Toolbutton",
                        command=self._recompute_and_draw_rooms).pack(side="left", padx=2)

        # ── Clear measurements ──────────────────────────────────────────────
        ttk.Button(top, text=f"📐✕ {self.get_text('clear_measure')}",
                   command=self._clear_measurements).pack(side="left", padx=2)

        ttk.Separator(top, orient="vertical").pack(side="left", fill="y", padx=6)

        # ── Grid value selection ─────────────────────────────────────────────
        grid_menu = tk.Menu(self.root, tearoff=0, **self._menu_kwargs())
        options = (20, 10, 5, 1) if self.units == "metric" else (12, 6, 3, 1)
        unit_suffix = "cm" if self.units == "metric" else "in"
        for val in options:
            grid_menu.add_radiobutton(label=f"{val} {unit_suffix}", variable=self.grid_val_var,
                                       value=val, command=self._on_grid_change)
        self.grid_menubtn = ttk.Menubutton(
            top, text=f"⊞ {self.get_text('grid')}: {self.grid_val_var.get()} {unit_suffix}", menu=grid_menu)
        self.grid_menubtn.pack(side="left", padx=4)

        ttk.Separator(top, orient="vertical").pack(side="left", fill="y", padx=6)

        # ── Zooming utilities ───────────────────────────────────────────────
        ttk.Label(top, text="🔍").pack(side="left")
        ttk.Button(top, text="−", width=2, command=self._zoom_out).pack(side="left")
        self.zoom_label = ttk.Label(top, text=f"{int(self.zoom*100)}%", width=5, anchor="center")
        self.zoom_label.pack(side="left")
        ttk.Button(top, text="+", width=2, command=self._zoom_in).pack(side="left")
        ttk.Button(top, text="⟲", width=2, command=self._zoom_reset).pack(side="left", padx=(0,4))

        ttk.Separator(top, orient="vertical").pack(side="left", fill="y", padx=6)

        # ── Shortcuts / Help Menu ────────────────────────────────────────────
        help_menu = tk.Menu(self.root, tearoff=0, **self._menu_kwargs())
        help_menu.add_command(label=f"⌨ {self.get_text('help_title')}", accelerator="F1",
                              command=self.toggle_help)
        # packed before everything else so it stays visible even when the
        # toolbar is wider than the window
        ttk.Menubutton(top, text=f"❓ {self.get_text('help')}", menu=help_menu).pack(
            side="right", padx=4, before=top.winfo_children()[0])

    def _build_style_menu(self):
        style_menu = tk.Menu(self.root, tearoff=0, **self._menu_kwargs())
        style_menu.add_command(label=self.get_text("line_width"), state="disabled")
        style_menu.add_radiobutton(label=self.get_text("line_wall"), variable=self.thickness,
                                    value=4, command=self._update_style_label)
        style_menu.add_radiobutton(label=self.get_text("line_furn"), variable=self.thickness,
                                    value=2, command=self._update_style_label)
        style_menu.add_separator()
        style_menu.add_command(label=self.get_text("color"), state="disabled")
        style_menu.add_radiobutton(label=f"⚫ {self.get_text('black')}",   variable=self.color,
                                    value="black", command=self._update_style_label)
        style_menu.add_radiobutton(label=f"🔵 {self.get_text('blue')}", variable=self.color,
                                    value="blue", command=self._update_style_label)
        style_menu.add_radiobutton(label=f"🔴 {self.get_text('red')}", variable=self.color,
                                    value="red", command=self._update_style_label)
        return style_menu

    def _on_mode_change(self):
        if self.preview:
            self.canvas.delete(self.preview); self.preview = None
        if self.mode.get() != "place_furn":
            self.root.config(cursor="")

    def _update_style_label(self):
        color_names = {
            "black": f"⚫ {self.get_text('black')}", 
            "blue": f"🔵 {self.get_text('blue')}", 
            "red": f"🔴 {self.get_text('red')}"
        }
        cname = color_names.get(self.color.get(), self.color.get())
        self.style_menubtn.config(text=f"🎨 {self.thickness.get()}px, {cname}")

    def _change_language(self):
        self.language = self.lang_var.get()
        self._save_settings()
        self.root.title(self.get_text("title"))
        self._build_floor_row_container()
        self._build_toolbar()
        self._populate_library()
        self._redraw_all()
        if self.view3d and self.view3d.exists():
            self.view3d.close(); self.open_3d_view()

    def _change_units(self):
        old_units = self.units
        self.units = self.unit_var.get()
        self._save_settings()
        if old_units != self.units:
            self.grid_val_var.set(20 if self.units == "metric" else 12)
        self._build_floor_row_container()
        self._build_toolbar()
        self._populate_library()
        self._redraw_all()

    # (keys, description) per line: "KEYS | description" in the lang files
    HELP_SECTIONS = [
        ("hs_general", ["hk_f1", "hk_esc"]),
        ("hs_view",    ["hk_zoom", "hk_scroll", "hk_hscroll", "hk_pan"]),
        ("hs_draw",    ["hk_wall", "hk_m", "hk_measure_shift"]),
        ("hs_select",  ["hk_click", "hk_ctrl_click", "hk_shift_click", "hk_box",
                        "hk_drag_edit", "hk_dbl", "hk_del"]),
        ("hs_furn",    ["hk_place", "hk_rl", "hk_ctrl_d", "hk_pg"]),
        ("hs_shelf",   ["hk_sv_open", "hk_sv_drag", "hk_sv_add", "hk_sv_top", "hk_sv_keys",
                        "hk_sv_copy", "hk_sv_esc"]),
        ("hs_open",    ["hk_open_click", "hk_open_drag", "hk_open_rl"]),
        ("hs_3d",      ["hk3_rot", "hk3_pan", "hk3_zoom", "hk3_wasd", "hk3_qe",
                        "hk3_shift", "hk3_walk"]),
    ]

    def toggle_help(self):
        """F1: show the keyboard shortcut window, or close it if it is open."""
        win = getattr(self, "_help_win", None)
        if win is not None:
            try:
                if win.winfo_exists():
                    win.destroy(); self._help_win = None
                    return
            except tk.TclError:
                pass
        win = tk.Toplevel(self.root)
        self._help_win = win
        win.title(self.get_text("help_title"))
        win.configure(bg=self.C("app_bg"))
        win.geometry("720x760")
        frm = ttk.Frame(win, padding=(12, 10, 12, 8)); frm.pack(fill="both", expand=True)
        sb = ttk.Scrollbar(frm, orient="vertical")
        txt = tk.Text(frm, wrap="word", yscrollcommand=sb.set, bd=0, highlightthickness=0,
                      bg=self.C("panel_bg"), fg=self.C("text"), padx=14, pady=10,
                      font=("TkDefaultFont", 10), cursor="arrow", tabs=("290",),
                      spacing1=2, spacing3=2)
        sb.config(command=txt.yview)
        sb.pack(side="right", fill="y"); txt.pack(side="left", fill="both", expand=True)
        txt.tag_configure("title", font=("TkDefaultFont", 14, "bold"), spacing3=6)
        txt.tag_configure("h", font=("TkDefaultFont", 11, "bold"), foreground=self.C("accent"),
                          spacing1=12, spacing3=4)
        txt.tag_configure("key", font=("TkFixedFont", 10, "bold"), lmargin1=8, lmargin2=298)
        txt.tag_configure("desc", lmargin2=298)
        txt.insert("end", f"⌨ {self.get_text('help_title')}\n", "title")
        for sec_key, items in self.HELP_SECTIONS:
            txt.insert("end", self.get_text(sec_key) + "\n", "h")
            for k in items:
                line = self.get_text(k)
                keys, _sep, desc = line.partition("|")
                txt.insert("end", keys.strip(), "key")
                txt.insert("end", "\t" + desc.strip() + "\n", "desc")
        txt.configure(state="disabled")
        bottom = ttk.Frame(win, padding=(12, 0, 12, 10)); bottom.pack(fill="x")
        ttk.Label(bottom, text=self.get_text("help_more"), foreground=self.C("text_muted"),
                  font=("TkDefaultFont", 8)).pack(side="left")
        ttk.Button(bottom, text=self.get_text("close"), command=self.toggle_help).pack(side="right")
        win.bind("<Escape>", lambda e: self.toggle_help())
        win.bind("<F1>", lambda e: self.toggle_help())
        win.protocol("WM_DELETE_WINDOW", self.toggle_help)
        win.focus_set()

    def _open_room_dialog(self):
        dlg = tk.Toplevel(self.root)
        dlg.configure(bg=self.C("app_bg"))
        dlg.title(self.get_text("add_room"))
        dlg.resizable(False, False)
        dlg.transient(self.root)
        dlg.grab_set()

        frm = ttk.Frame(dlg, padding=12)
        frm.pack()

        unit_lbl = "m" if self.units == "metric" else "ft"

        ttk.Label(frm, text=f"{self.get_text('width')} ({unit_lbl}):").grid(row=0, column=0, sticky="w", pady=4, padx=(0,8))
        w_entry = ttk.Entry(frm, width=8, textvariable=self.room_w_var)
        w_entry.grid(row=0, column=1)

        ttk.Label(frm, text=f"{self.get_text('height')} ({unit_lbl}):").grid(row=1, column=0, sticky="w", pady=4, padx=(0,8))
        h_entry = ttk.Entry(frm, width=8, textvariable=self.room_h_var)
        h_entry.grid(row=1, column=1)

        def do_create():
            self.create_room()
            dlg.destroy()

        ttk.Button(frm, text=f"🏠 {self.get_text('create_room')}", command=do_create).grid(
            row=2, column=0, columnspan=2, pady=(10,0))

        dlg.bind("<Return>", lambda e: do_create())
        dlg.bind("<Escape>", lambda e: dlg.destroy())
        w_entry.focus_set()
        w_entry.select_range(0, "end")

    def _open_furniture_creator(self):
        """Dialog for drawing your own furniture. All shape coordinates are kept
        in centimetres; the canvas shows them at the chosen zoom, with rulers,
        a selectable snap grid (1 / 5 / 10 cm) and live dimensions."""
        DEFAULT_FILL = "#e0d3ae"
        AREA = 500           # drawing area 0..500 cm in both directions
        MARGIN = 20          # extra space shown left/above the 0 line (cm)
        ZOOMS = [0.5, 0.75, 1, 1.5, 2, 3, 4, 6, 8]    # pixels per cm
        VIEW_W, VIEW_H = 560, 440
        RULER = 26
        ink = "#2f6fed"

        dlg = tk.Toplevel(self.root)
        dlg.configure(bg=self.C("app_bg"))
        dlg.title(self.get_text("new_furniture"))
        dlg.resizable(False, False)
        dlg.transient(self.root)
        dlg.grab_set()

        frm = ttk.Frame(dlg, padding=12)
        frm.pack()

        # ── Name + category + colour ─────────────────────────────────────────
        top_row = ttk.Frame(frm); top_row.grid(row=0, column=0, columnspan=2, sticky="w", pady=(0,6))
        ttk.Label(top_row, text=f"{self.get_text('furn_name')}:").grid(row=0, column=0, sticky="w", padx=(0,4))
        name_var = tk.StringVar()
        name_entry = ttk.Entry(top_row, textvariable=name_var, width=18)
        name_entry.grid(row=0, column=1, padx=(0,10))

        disp_to_key = {}

        def refresh_categories(select_id=None):
            current = disp_to_key.get(cat_var.get())
            disp_to_key.clear()
            for c in self.categories:
                if c["id"] == "doors_windows":   # doors/windows are tools, not drawn furniture
                    continue
                disp_to_key[self._cat_name(c["id"])] = c["id"]
            values = list(disp_to_key.keys())
            cat_combo.configure(values=values)
            want = select_id or current or "custom"
            if want and self._category(want) and want != "doors_windows":
                cat_var.set(self._cat_name(want))
            elif values:
                cat_var.set(values[0])

        def quick_add_category():
            cid = self._prompt_new_category(dlg)
            if cid:
                refresh_categories(cid)
                refresh_list()

        ttk.Label(top_row, text=f"{self.get_text('furn_category')}:").grid(row=0, column=2, sticky="w", padx=(0,4))
        cat_var = tk.StringVar()
        cat_combo = ttk.Combobox(top_row, textvariable=cat_var, state="readonly", width=16)
        cat_combo.grid(row=0, column=3)
        refresh_categories()
        cat_btns = ttk.Frame(top_row); cat_btns.grid(row=0, column=4, padx=(4,0))
        ttk.Button(cat_btns, text="+", width=3, command=quick_add_category).pack(side="left", padx=1)
        ttk.Button(cat_btns, text="⚙", width=3,
                   command=lambda: self._open_category_manager(
                       dlg, on_close=lambda: (refresh_categories(), refresh_list()))
                   ).pack(side="left", padx=1)

        fill_color = {"value": DEFAULT_FILL}

        def pick_color():
            _, hexval = colorchooser.askcolor(color=fill_color["value"],
                                              title=self.get_text("furn_colour"), parent=dlg)
            if hexval:
                fill_color["value"] = hexval
                color_btn.configure(bg=hexval)
                redraw()

        ttk.Label(top_row, text=f"{self.get_text('furn_colour')}:").grid(row=0, column=5, sticky="w", padx=(14,4))
        color_btn = tk.Button(top_row, text="   ", bg=DEFAULT_FILL, width=3, relief="raised", command=pick_color)
        color_btn.grid(row=0, column=6)

        # ── Tools + grid size + zoom ─────────────────────────────────────────
        tool_var = tk.StringVar(value="rect")
        tool_row = ttk.Frame(frm); tool_row.grid(row=1, column=0, columnspan=2, sticky="w", pady=(0,4))
        for key, val in [("furn_tool_rect","rect"), ("furn_tool_circle","circle"),
                         ("furn_tool_triangle","triangle"), ("furn_tool_polygon","polygon"),
                         ("furn_tool_select","select")]:
            ttk.Radiobutton(tool_row, text=self.get_text(key), variable=tool_var, value=val,
                            style="Toolbutton").pack(side="left", padx=1)
        ttk.Separator(tool_row, orient="vertical").pack(side="left", fill="y", padx=8)
        ttk.Label(tool_row, text=f"{self.get_text('grid_size')}:").pack(side="left", padx=(0,4))
        step_var = tk.StringVar(value="10 cm")
        step_combo = ttk.Combobox(tool_row, textvariable=step_var, state="readonly", width=6,
                                  values=["1 cm", "5 cm", "10 cm"])
        step_combo.pack(side="left")
        ttk.Separator(tool_row, orient="vertical").pack(side="left", fill="y", padx=8)
        ttk.Label(tool_row, text="🔍").pack(side="left")
        zoom_i = {"i": ZOOMS.index(2)}
        zoom_lbl = ttk.Label(tool_row, width=6, anchor="center")

        def step_cm():
            try:
                return float(step_var.get().split()[0])
            except (ValueError, IndexError):
                return 10.0

        # ── Drawing area with rulers ─────────────────────────────────────────
        area = ttk.Frame(frm); area.grid(row=2, column=0, sticky="nw")
        ruler_bg, ruler_fg = self.C("toolbar_bg"), self.C("text_muted")
        corner = tk.Canvas(area, width=RULER, height=RULER, bg=ruler_bg, highlightthickness=0)
        corner.grid(row=0, column=0)
        corner.create_text(RULER/2, RULER/2, text="cm", fill=ruler_fg, font=("TkDefaultFont", 7))
        top_ruler = tk.Canvas(area, width=VIEW_W, height=RULER, bg=ruler_bg, highlightthickness=0)
        top_ruler.grid(row=0, column=1, sticky="w")
        left_ruler = tk.Canvas(area, width=RULER, height=VIEW_H, bg=ruler_bg, highlightthickness=0)
        left_ruler.grid(row=1, column=0, sticky="n")
        draw_canvas = tk.Canvas(area, width=VIEW_W, height=VIEW_H, bg="white", highlightthickness=0)
        draw_canvas.grid(row=1, column=1)
        vbar = ttk.Scrollbar(area, orient="vertical", command=draw_canvas.yview)
        vbar.grid(row=1, column=2, sticky="ns")
        hbar = ttk.Scrollbar(area, orient="horizontal", command=draw_canvas.xview)
        hbar.grid(row=2, column=1, sticky="ew")
        status_var = tk.StringVar(value="")
        ttk.Label(area, textvariable=status_var, foreground=self.C("text_muted"),
                  font=("TkDefaultFont", 9)).grid(row=3, column=1, sticky="w", pady=(2,0))

        def ppc():
            return ZOOMS[zoom_i["i"]]

        def to_px(v):
            return (v + MARGIN) * ppc()

        def ev_cm(e):
            return (draw_canvas.canvasx(e.x) / ppc() - MARGIN,
                    draw_canvas.canvasy(e.y) / ppc() - MARGIN)

        def snap(v):
            s = step_cm()
            return min(AREA, max(0.0, round(v / s) * s))

        def fmt(v):
            return f"{v:.1f}".rstrip("0").rstrip(".")

        def nice_steps(min_px):
            """(minor, label) spacing in cm so that labels are >= min_px apart."""
            for lab in (1, 2, 5, 10, 20, 50, 100, 200, 500):
                if lab * ppc() >= min_px:
                    break
            minor = {1: 1, 2: 1, 5: 1, 10: 2, 20: 5, 50: 10, 100: 10, 200: 50, 500: 100}[lab]
            if minor * ppc() < 4:
                minor = lab
            return minor, lab

        def draw_rulers(*_):
            top_ruler.delete("all"); left_ruler.delete("all")
            minor, lab = nice_steps(42)
            x0 = draw_canvas.canvasx(0) / ppc() - MARGIN
            x1 = draw_canvas.canvasx(VIEW_W) / ppc() - MARGIN
            y0 = draw_canvas.canvasy(0) / ppc() - MARGIN
            y1 = draw_canvas.canvasy(VIEW_H) / ppc() - MARGIN
            for ruler, a, b, horiz in ((top_ruler, x0, x1, True), (left_ruler, y0, y1, False)):
                v = (int(a // minor)) * minor
                while v <= b:
                    if v >= 0 or v == 0:
                        p = (v - a) * ppc()
                        is_lab = abs(v / lab - round(v / lab)) < 1e-6
                        ln = 12 if is_lab else 5
                        if horiz:
                            ruler.create_line(p, RULER, p, RULER - ln, fill=ruler_fg)
                            if is_lab and v >= 0:
                                ruler.create_text(p + 2, 2, text=fmt(v), anchor="nw",
                                                  fill=self.C("text"), font=("TkDefaultFont", 7))
                        else:
                            ruler.create_line(RULER, p, RULER - ln, p, fill=ruler_fg)
                            if is_lab and v >= 0:
                                ruler.create_text(2, p + 2, text=fmt(v), anchor="nw",
                                                  fill=self.C("text"), font=("TkDefaultFont", 7))
                    v += minor
            top_ruler.create_line(0, RULER - 1, VIEW_W, RULER - 1, fill=self.C("border"))
            left_ruler.create_line(RULER - 1, 0, RULER - 1, VIEW_H, fill=self.C("border"))
            draw_cursor_marks()

        cursor = {"x": None, "y": None}

        def draw_cursor_marks():
            top_ruler.delete("cur"); left_ruler.delete("cur")
            if cursor["x"] is None:
                return
            px = to_px(cursor["x"]) - draw_canvas.canvasx(0)
            py = to_px(cursor["y"]) - draw_canvas.canvasy(0)
            top_ruler.create_line(px, 0, px, RULER, fill="#d64545", width=1, tags="cur")
            left_ruler.create_line(0, py, RULER, py, fill="#d64545", width=1, tags="cur")

        def xscroll(*a):
            hbar.set(*a); draw_rulers()

        def yscroll(*a):
            vbar.set(*a); draw_rulers()

        draw_canvas.configure(xscrollcommand=xscroll, yscrollcommand=yscroll)

        def draw_grid():
            draw_canvas.delete("grid")
            s = step_cm()
            minor = s
            while minor * ppc() < 6 and minor < 100:
                minor = {1: 5, 5: 10, 10: 50, 50: 100}.get(minor, minor * 2)
            major = {1: 10, 5: 50, 10: 50, 50: 100}.get(minor, 500)
            end = to_px(AREA)
            v = 0.0
            while v <= AREA + 0.001:
                is_major = abs(v / major - round(v / major)) < 1e-6
                col = "#c4c9d4" if is_major else "#eceef3"
                p = to_px(v)
                draw_canvas.create_line(p, to_px(0), p, end, fill=col, tags="grid")
                draw_canvas.create_line(to_px(0), p, end, p, fill=col, tags="grid")
                v += minor
            draw_canvas.create_rectangle(to_px(0), to_px(0), end, end, outline="#9aa3b5", tags="grid")
            draw_canvas.tag_lower("grid")

        def apply_zoom(new_i, anchor=None):
            new_i = max(0, min(len(ZOOMS) - 1, new_i))
            if new_i == zoom_i["i"]:
                return
            # keep the point under the mouse (or the view centre) where it is
            if anchor is None:
                ax, ay = VIEW_W / 2, VIEW_H / 2
            else:
                ax, ay = anchor
            cmx = draw_canvas.canvasx(ax) / ppc() - MARGIN
            cmy = draw_canvas.canvasy(ay) / ppc() - MARGIN
            zoom_i["i"] = new_i
            total = (AREA + 2 * MARGIN) * ppc()
            draw_canvas.configure(scrollregion=(0, 0, total, total))
            draw_canvas.xview_moveto(max(0.0, (to_px(cmx) - ax) / total))
            draw_canvas.yview_moveto(max(0.0, (to_px(cmy) - ay) / total))
            zoom_lbl.configure(text=f"{int(ppc() * 50)}%")
            draw_grid(); redraw(); draw_rulers()

        ttk.Button(tool_row, text="−", width=2, command=lambda: apply_zoom(zoom_i["i"] - 1)).pack(side="left")
        zoom_lbl.pack(side="left")
        ttk.Button(tool_row, text="+", width=2, command=lambda: apply_zoom(zoom_i["i"] + 1)).pack(side="left")

        # ── Right side: dimensions + existing furniture ──────────────────────
        side = ttk.Frame(frm); side.grid(row=2, column=1, sticky="n", padx=(12,0))
        dims = tk.LabelFrame(side, text=f" 📏 {self.get_text('furn_dims')} ", bg=self.C("app_bg"),
                             fg=self.C("text"), font=("TkDefaultFont", 10, "bold"), padx=8, pady=6)
        dims.pack(fill="x")
        big = ("TkDefaultFont", 11)
        w_var, d_var = tk.StringVar(), tk.StringVar()
        h3d_var = tk.StringVar(value=fmt(CUSTOM_FURN_HEIGHT))
        rows = [(self.get_text("furn_width"), w_var), (self.get_text("furn_depth"), d_var),
                (self.get_text("height_3d"), h3d_var)]
        dim_entries = []
        for i, (lbl, var) in enumerate(rows):
            tk.Label(dims, text=f"{lbl}:", bg=self.C("app_bg"), fg=self.C("text"),
                     font=big).grid(row=i, column=0, sticky="w", pady=3)
            ent = tk.Entry(dims, textvariable=var, width=7, font=big, justify="right",
                           bg=self.C("panel_bg"), fg=self.C("text"), insertbackground=self.C("text"),
                           relief="solid", bd=1)
            ent.grid(row=i, column=1, padx=(8,4), pady=3)
            tk.Label(dims, text="cm", bg=self.C("app_bg"), fg=self.C("text_muted"),
                     font=big).grid(row=i, column=2, sticky="w")
            dim_entries.append(ent)
        ttk.Button(dims, text=f"↔ {self.get_text('apply_dims')}",
                   command=lambda: apply_dims()).grid(row=3, column=0, columnspan=3, sticky="ew", pady=(6,2))
        tk.Label(dims, text=self.get_text("dims_hint"), bg=self.C("app_bg"), fg=self.C("text_muted"),
                 font=("TkDefaultFont", 8), wraplength=190, justify="left").grid(
                     row=4, column=0, columnspan=3, sticky="w")
        tk.Label(dims, text=f"↕ {self.get_text('height_hint')}", bg=self.C("app_bg"),
                 fg=self.C("text_muted"), font=("TkDefaultFont", 8), wraplength=190,
                 justify="left").grid(row=5, column=0, columnspan=3, sticky="w", pady=(4,0))

        # furniture type: solid block, or a shelf unit you can put things in
        type_var = tk.StringVar(value="solid")
        type_row = tk.Frame(dims, bg=self.C("app_bg"))
        type_row.grid(row=6, column=0, columnspan=3, sticky="w", pady=(10,2))
        tk.Label(type_row, text=f"{self.get_text('furn_type')}:", bg=self.C("app_bg"), fg=self.C("text"),
                 font=big).pack(side="left", padx=(0,6))
        shelf_box = tk.Frame(dims, bg=self.C("app_bg"))
        lv_var = tk.StringVar(value="5"); bot_var = tk.StringVar(value="10")
        for i, (lbl, var, unit) in enumerate([(self.get_text("shelf_levels"), lv_var, self.get_text("items_count")),
                                              (self.get_text("shelf_bottom"), bot_var, "cm")]):
            tk.Label(shelf_box, text=f"{lbl}:", bg=self.C("app_bg"), fg=self.C("text"),
                     font=("TkDefaultFont", 10)).grid(row=i, column=0, sticky="w", pady=2)
            e = tk.Entry(shelf_box, textvariable=var, width=5, font=("TkDefaultFont", 10), justify="right",
                         bg=self.C("panel_bg"), fg=self.C("text"), insertbackground=self.C("text"),
                         relief="solid", bd=1)
            e.grid(row=i, column=1, padx=(6,4), pady=2)
            tk.Label(shelf_box, text=unit, bg=self.C("app_bg"), fg=self.C("text_muted"),
                     font=("TkDefaultFont", 10)).grid(row=i, column=2, sticky="w")
        tk.Label(shelf_box, text=self.get_text("shelf_hint"), bg=self.C("app_bg"), fg=self.C("text_muted"),
                 font=("TkDefaultFont", 8), wraplength=190, justify="left").grid(
                     row=2, column=0, columnspan=3, sticky="w", pady=(2,0))

        def on_type():
            if type_var.get() == "shelf":
                shelf_box.grid(row=7, column=0, columnspan=3, sticky="w")
                if h3d_var.get().strip() in ("", fmt(CUSTOM_FURN_HEIGHT)):
                    h3d_var.set("200")
            else:
                shelf_box.grid_remove()
            redraw()

        for val, key in (("solid", "furn_type_solid"), ("shelf", "furn_type_shelf")):
            tk.Radiobutton(type_row, text=self.get_text(key), variable=type_var, value=val, command=on_type,
                           bg=self.C("app_bg"), fg=self.C("text"), selectcolor=self.C("panel_bg"),
                           activebackground=self.C("app_bg"), activeforeground=self.C("text"),
                           font=("TkDefaultFont", 10)).pack(side="left")

        mgmt_frame = ttk.Frame(side)
        mgmt_frame.pack(fill="both", pady=(10,0))
        ttk.Label(mgmt_frame, text=self.get_text("furn_library_list"),
                  font=("TkDefaultFont",8,"bold")).pack(anchor="w")
        list_wrap = ttk.Frame(mgmt_frame); list_wrap.pack(fill="both", expand=True, pady=(2,4))
        list_scroll = ttk.Scrollbar(list_wrap, orient="vertical")
        listbox = tk.Listbox(list_wrap, width=30, height=9, yscrollcommand=list_scroll.set,
                             bg=self.C("lib_row_bg"), fg=self.C("text"),
                             selectbackground=self.C("accent"), selectforeground="white",
                             highlightthickness=1, highlightbackground=self.C("border"),
                             bd=0, font=("TkDefaultFont",8), activestyle="none")
        list_scroll.config(command=listbox.yview)
        listbox.pack(side="left", fill="both", expand=True)
        list_scroll.pack(side="right", fill="y")

        # ── Shape model (cm) ─────────────────────────────────────────────────
        #   {"type":"polygon", "pts":[(x,y),...]}  or  {"type":"oval","cx","cy","rx","ry"}
        state = {"elements": [], "poly_pts": [], "sel": None}
        drag = {"active": False, "x0": 0, "y0": 0, "move": None}

        def el_bbox(el):
            if el["type"] == "oval":
                return (el["cx"] - el["rx"], el["cy"] - el["ry"], el["cx"] + el["rx"], el["cy"] + el["ry"])
            xs = [p[0] for p in el["pts"]]; ys = [p[1] for p in el["pts"]]
            return (min(xs), min(ys), max(xs), max(ys))

        def all_bbox():
            if not state["elements"]:
                return None
            bbs = [el_bbox(el) for el in state["elements"]]
            return (min(b[0] for b in bbs), min(b[1] for b in bbs),
                    max(b[2] for b in bbs), max(b[3] for b in bbs))

        def point_in_polygon(px, py, pts):
            inside = False
            n = len(pts); j = n - 1
            for i in range(n):
                xi, yi = pts[i]; xj, yj = pts[j]
                if ((yi > py) != (yj > py)) and \
                   (px < (xj - xi) * (py - yi) / (yj - yi + 1e-12) + xi):
                    inside = not inside
                j = i
            return inside

        def hit_test(mx, my):
            for idx in range(len(state["elements"]) - 1, -1, -1):
                el = state["elements"][idx]
                if el["type"] == "oval":
                    dx = (mx - el["cx"]) / max(el["rx"], 0.1)
                    dy = (my - el["cy"]) / max(el["ry"], 0.1)
                    if dx*dx + dy*dy <= 1.0:
                        return idx
                elif point_in_polygon(mx, my, el["pts"]):
                    return idx
            return None

        def dim_line(xa, ya, xb, yb, text, horizontal):
            """Dimension line with end ticks and the value in the middle (cm coords)."""
            pa = (to_px(xa), to_px(ya)); pb = (to_px(xb), to_px(yb))
            draw_canvas.create_line(*pa, *pb, fill=ink, width=1, arrow="both",
                                    arrowshape=(6, 7, 3), tags="dim")
            if horizontal:
                for p in (pa, pb):
                    draw_canvas.create_line(p[0], p[1] - 5, p[0], p[1] + 5, fill=ink, tags="dim")
                draw_canvas.create_text((pa[0] + pb[0]) / 2, pa[1] - 2, text=text, anchor="s",
                                        fill=ink, font=("TkDefaultFont", 9, "bold"), tags="dim")
            else:
                for p in (pa, pb):
                    draw_canvas.create_line(p[0] - 5, p[1], p[0] + 5, p[1], fill=ink, tags="dim")
                draw_canvas.create_text(pa[0] - 3, (pa[1] + pb[1]) / 2, text=text, angle=90,
                                        anchor="s", fill=ink, font=("TkDefaultFont", 9, "bold"), tags="dim")

        def update_dim_fields():
            bb = all_bbox()
            focused = dlg.focus_get()
            if bb and focused not in dim_entries[:2]:
                w_var.set(fmt(bb[2] - bb[0])); d_var.set(fmt(bb[3] - bb[1]))
            elif not bb and focused not in dim_entries[:2]:
                w_var.set(""); d_var.set("")

        def redraw():
            draw_canvas.delete("shape"); draw_canvas.delete("dim")
            fc = fill_color["value"]
            for idx, el in enumerate(state["elements"]):
                selected = (idx == state["sel"])
                color = self.C("accent") if selected else self._darken_hex(fc)
                lw = 3 if selected else 2
                if el["type"] == "oval":
                    draw_canvas.create_oval(to_px(el["cx"] - el["rx"]), to_px(el["cy"] - el["ry"]),
                                            to_px(el["cx"] + el["rx"]), to_px(el["cy"] + el["ry"]),
                                            fill=fc, outline=color, width=lw, tags="shape")
                else:
                    flat = [to_px(v) for p in el["pts"] for v in p]
                    draw_canvas.create_polygon(*flat, fill=fc, outline=color, width=lw, tags="shape")
            pts = state["poly_pts"]
            for (px, py) in pts:
                draw_canvas.create_oval(to_px(px)-3, to_px(py)-3, to_px(px)+3, to_px(py)+3,
                                        fill=self.C("accent"), outline="", tags="shape")
            if len(pts) >= 2:
                flat = [to_px(v) for p in pts for v in p]
                draw_canvas.create_line(*flat, fill=self.C("accent"), width=2, tags="shape")
            # overall size of the piece
            bb = all_bbox()
            if bb and type_var.get() == "shelf":
                ps = SHELF_POST
                for (qx, qy) in ((bb[0], bb[1]), (bb[2] - ps, bb[1]), (bb[0], bb[3] - ps), (bb[2] - ps, bb[3] - ps)):
                    draw_canvas.create_rectangle(to_px(qx), to_px(qy), to_px(qx + ps), to_px(qy + ps),
                                                 fill="#555555", outline="", tags="shape")
            if bb:
                gap = 14 / ppc()
                dim_line(bb[0], bb[1] - gap, bb[2], bb[1] - gap, f"{fmt(bb[2]-bb[0])} cm", True)
                dim_line(bb[0] - gap, bb[1], bb[0] - gap, bb[3], f"{fmt(bb[3]-bb[1])} cm", False)
            update_dim_fields()
            show_selection_status()

        def show_selection_status(extra=""):
            parts = []
            if cursor["x"] is not None:
                parts.append(f"{self.get_text('cursor_pos')}: X {fmt(cursor['x'])}  Y {fmt(cursor['y'])} cm")
            i = state["sel"]
            if i is not None and i < len(state["elements"]):
                b = el_bbox(state["elements"][i])
                parts.append(f"{self.get_text('selected_shape')}: {fmt(b[2]-b[0])} × {fmt(b[3]-b[1])} cm")
            if extra:
                parts.append(extra)
            status_var.set("     ".join(parts))

        def live_label(x, y, text):
            draw_canvas.create_text(to_px(x) + 10, to_px(y) + 12, text=text, anchor="nw",
                                    fill="#d64545", font=("TkDefaultFont", 9, "bold"), tags="temp")

        def on_motion(e):
            mx, my = ev_cm(e)
            cursor["x"], cursor["y"] = snap(mx), snap(my)
            draw_cursor_marks()
            if tool_var.get() == "polygon" and state["poly_pts"]:
                draw_canvas.delete("temp")
                lx, ly = state["poly_pts"][-1]
                gx, gy = cursor["x"], cursor["y"]
                draw_canvas.create_line(to_px(lx), to_px(ly), to_px(gx), to_px(gy), fill=self.C("accent"),
                                        dash=(4, 3), width=2, tags="temp")
                live_label(gx, gy, f"{fmt(hypot(gx - lx, gy - ly))} cm")
            show_selection_status()

        def on_press(e):
            mx, my = ev_cm(e)
            tool = tool_var.get()
            draw_canvas.focus_set()
            if tool == "polygon":
                state["poly_pts"].append((snap(mx), snap(my)))
                redraw()
            elif tool == "select":
                state["sel"] = hit_test(mx, my)
                if state["sel"] is not None:
                    el = state["elements"][state["sel"]]
                    drag.update(active=True, x0=snap(mx), y0=snap(my),
                                move=dict(el) if el["type"] == "oval" else {"type": "polygon", "pts": list(el["pts"])})
                redraw()
            else:
                drag.update(active=True, x0=snap(mx), y0=snap(my), move=None)

        def on_drag(e):
            if not drag["active"]:
                return
            mx, my = ev_cm(e)
            gx, gy = snap(mx), snap(my)
            cursor["x"], cursor["y"] = gx, gy
            draw_cursor_marks()
            tool = tool_var.get()
            if tool == "select":
                i = state["sel"]
                if i is None or drag["move"] is None:
                    return
                dx, dy = gx - drag["x0"], gy - drag["y0"]
                orig = drag["move"]
                if orig["type"] == "oval":
                    state["elements"][i] = dict(orig, cx=orig["cx"] + dx, cy=orig["cy"] + dy)
                else:
                    state["elements"][i] = {"type": "polygon", "pts": [(x + dx, y + dy) for (x, y) in orig["pts"]]}
                redraw()
                return
            if tool not in ("rect", "circle", "triangle"):
                return
            draw_canvas.delete("temp")
            x0, y0 = drag["x0"], drag["y0"]
            x1, x2 = sorted((x0, gx)); y1, y2 = sorted((y0, gy))
            a, b, c, d = to_px(x1), to_px(y1), to_px(x2), to_px(y2)
            if tool == "rect":
                draw_canvas.create_rectangle(a, b, c, d, outline=self.C("accent"), dash=(4,3), width=2, tags="temp")
            elif tool == "circle":
                draw_canvas.create_oval(a, b, c, d, outline=self.C("accent"), dash=(4,3), width=2, tags="temp")
            else:
                draw_canvas.create_polygon((a + c) / 2, b, a, d, c, d, outline=self.C("accent"),
                                           fill="", dash=(4,3), width=2, tags="temp")
            prefix = "Ø " if tool == "circle" else ""
            live_label(gx, gy, f"{prefix}{fmt(x2 - x1)} × {fmt(y2 - y1)} cm")

        def on_release(e):
            if not drag["active"]:
                return
            drag["active"] = False
            draw_canvas.delete("temp")
            tool = tool_var.get()
            if tool == "select":
                drag["move"] = None
                return
            if tool not in ("rect", "circle", "triangle"):
                return
            mx, my = ev_cm(e)
            gx, gy = snap(mx), snap(my)
            x0, y0 = drag["x0"], drag["y0"]
            if abs(gx - x0) < 0.5 or abs(gy - y0) < 0.5:
                return  # zero size - likely an accidental click
            x1, x2 = sorted((x0, gx)); y1, y2 = sorted((y0, gy))
            if tool == "rect":
                el = {"type": "polygon", "pts": [(x1, y1), (x2, y1), (x2, y2), (x1, y2)]}
            elif tool == "circle":
                el = {"type": "oval", "cx": (x1 + x2) / 2, "cy": (y1 + y2) / 2,
                      "rx": (x2 - x1) / 2, "ry": (y2 - y1) / 2}
            else:
                el = {"type": "polygon", "pts": [((x1 + x2) / 2, y1), (x1, y2), (x2, y2)]}
            state["elements"].append(el)
            state["sel"] = len(state["elements"]) - 1
            redraw()

        def on_leave(_e):
            cursor["x"] = cursor["y"] = None
            draw_cursor_marks(); show_selection_status()

        def on_wheel(e):
            up = (e.delta > 0) if e.num not in (4, 5) else (e.num == 4)
            if e.state & 0x4:
                apply_zoom(zoom_i["i"] + (1 if up else -1), anchor=(e.x, e.y))
            elif e.state & 0x1:
                draw_canvas.xview_scroll(-2 if up else 2, "units")
            else:
                draw_canvas.yview_scroll(-2 if up else 2, "units")

        draw_canvas.bind("<ButtonPress-1>", on_press)
        draw_canvas.bind("<B1-Motion>", on_drag)
        draw_canvas.bind("<ButtonRelease-1>", on_release)
        draw_canvas.bind("<Motion>", on_motion)
        draw_canvas.bind("<Leave>", on_leave)
        draw_canvas.bind("<MouseWheel>", on_wheel)
        draw_canvas.bind("<Button-4>", on_wheel)
        draw_canvas.bind("<Button-5>", on_wheel)
        draw_canvas.bind("<Double-Button-1>", lambda e: finish_shape() if tool_var.get() == "polygon" else None)

        def finish_shape():
            if len(state["poly_pts"]) >= 3:
                state["elements"].append({"type": "polygon", "pts": list(state["poly_pts"])})
                state["poly_pts"] = []
                state["sel"] = len(state["elements"]) - 1
                draw_canvas.delete("temp")
                redraw()

        def undo_point():
            if state["poly_pts"]:
                state["poly_pts"].pop()
                draw_canvas.delete("temp")
                redraw()

        def clear_points():
            state["poly_pts"] = []
            draw_canvas.delete("temp")
            redraw()

        def rotate_selected(delta_deg):
            i = state["sel"]
            if i is None or i >= len(state["elements"]):
                return
            el = state["elements"][i]
            if el["type"] != "polygon":
                if abs(delta_deg) == 90:   # an ellipse turned by 90° just swaps its radii
                    el["rx"], el["ry"] = el["ry"], el["rx"]
                    redraw()
                return
            pts = el["pts"]
            cx = sum(p[0] for p in pts) / len(pts)
            cy = sum(p[1] for p in pts) / len(pts)
            rad = radians(delta_deg)
            ca, sa = cos(rad), sin(rad)
            el["pts"] = [(round(cx + (px-cx)*ca - (py-cy)*sa, 2),
                          round(cy + (px-cx)*sa + (py-cy)*ca, 2)) for (px, py) in pts]
            redraw()

        def delete_selected():
            i = state["sel"]
            if i is None or i >= len(state["elements"]):
                return
            del state["elements"][i]
            state["sel"] = None
            redraw()

        def clear_all():
            state["elements"] = []
            state["poly_pts"] = []
            state["sel"] = None
            draw_canvas.delete("temp")
            redraw()

        def apply_dims(_e=None):
            """Typed width / depth: scale the drawing to that size, or create a
            rectangle of that size when nothing has been drawn yet."""
            try:
                W = float(w_var.get().replace(",", "."))
                D = float(d_var.get().replace(",", "."))
                if W <= 0 or D <= 0:
                    raise ValueError
            except ValueError:
                messagebox.showwarning(self.get_text("error_title"), self.get_text("invalid_number"), parent=dlg)
                return
            W, D = min(W, AREA), min(D, AREA)
            bb = all_bbox()
            if not bb:
                state["elements"].append({"type": "polygon", "pts": [(0, 0), (W, 0), (W, D), (0, D)]})
                state["sel"] = 0
            else:
                ow, od = max(bb[2] - bb[0], 0.01), max(bb[3] - bb[1], 0.01)
                sx, sy = W / ow, D / od
                for el in state["elements"]:
                    if el["type"] == "oval":
                        el["cx"] = bb[0] + (el["cx"] - bb[0]) * sx
                        el["cy"] = bb[1] + (el["cy"] - bb[1]) * sy
                        el["rx"] *= sx; el["ry"] *= sy
                    else:
                        el["pts"] = [(bb[0] + (x - bb[0]) * sx, bb[1] + (y - bb[1]) * sy) for (x, y) in el["pts"]]
            draw_canvas.focus_set()
            redraw()

        for ent in dim_entries[:2]:
            ent.bind("<Return>", apply_dims)
            ent.bind("<KP_Enter>", apply_dims)
        step_combo.bind("<<ComboboxSelected>>", lambda e: (draw_grid(), draw_canvas.focus_set()))

        # ── Existing-furniture list: edit / delete / start a new piece ──────
        list_fids = []

        def refresh_list():
            listbox.delete(0, "end")
            list_fids.clear()
            ordered = sorted(self.furniture_defs, key=lambda e:
                             (self._cat_order(e.get("category") or "custom"),
                              self.get_text(e.get("label_key",e["fid"])).lower()))
            for e in ordered:
                cat = self._cat_name(e.get("category") or "custom")
                nm  = self.get_text(e.get("label_key", e["fid"]))
                lock = "" if e.get("draw_fn") == "custom_shape" else " 🔒"
                listbox.insert("end", f"{cat}: {nm}{lock}")
                list_fids.append(e["fid"])

        def selected_entry():
            sel = listbox.curselection()
            if not sel or sel[0] >= len(list_fids):
                return None
            return self._furn_def(list_fids[sel[0]])

        editing = {"fid": None}

        def start_new():
            editing["fid"] = None
            name_var.set("")
            h3d_var.set(fmt(CUSTOM_FURN_HEIGHT))
            type_var.set("solid"); lv_var.set("5"); bot_var.set("10"); on_type()
            clear_all()
            fill_color["value"] = DEFAULT_FILL
            color_btn.configure(bg=DEFAULT_FILL)
            save_btn.configure(text=f"💾 {self.get_text('save')}")
            name_entry.focus_set()

        def load_selected_for_edit():
            entry = selected_entry()
            if entry is None:
                return
            if entry.get("draw_fn") != "custom_shape":
                messagebox.showinfo(self.get_text("furn_library_list"), self.get_text("furn_builtin_readonly"),
                                    parent=dlg)
                return
            clear_all()
            name_var.set(self.get_text(entry.get("label_key", entry["fid"])))
            refresh_categories(entry.get("category") or "custom")
            fill_color["value"] = entry.get("fill") or DEFAULT_FILL
            color_btn.configure(bg=fill_color["value"])
            h3d_var.set(fmt(entry.get("z_height") or CUSTOM_FURN_HEIGHT))
            sh = entry.get("shelf")
            if isinstance(sh, dict):
                type_var.set("shelf"); lv_var.set(str(int(sh.get("levels", 5))))
                bot_var.set(fmt(float(sh.get("bottom", 10))))
            else:
                type_var.set("solid")
            on_type()
            shape = entry.get("shape") or \
                    ([{"type":"polygon","points":entry["points"]}] if entry.get("points") else [])
            for el in shape:
                if el.get("type") == "oval":
                    state["elements"].append({"type": "oval", "cx": el.get("cx", 0), "cy": el.get("cy", 0),
                                              "rx": el.get("rx", 0), "ry": el.get("ry", 0)})
                else:
                    state["elements"].append({"type": "polygon",
                                              "pts": [(p[0], p[1]) for p in el.get("points", [])]})
            editing["fid"] = entry["fid"]
            save_btn.configure(text=f"💾 {self.get_text('update')}")
            draw_canvas.xview_moveto(0); draw_canvas.yview_moveto(0)
            redraw()

        def delete_selected_from_list():
            entry = selected_entry()
            if entry is None:
                return
            if not messagebox.askyesno(self.get_text("confirm_title"), self.get_text("confirm_delete_furniture"),
                                       parent=dlg):
                return
            self._delete_furniture_entry(entry["fid"])
            if editing["fid"] == entry["fid"]:
                start_new()
            refresh_list()
            self._populate_library()
            self._redraw_all()

        refresh_list()
        listbox.bind("<Double-Button-1>", lambda e: load_selected_for_edit())
        mgmt_btns = ttk.Frame(mgmt_frame); mgmt_btns.pack(fill="x")
        ttk.Button(mgmt_btns, text=self.get_text("edit"), command=load_selected_for_edit).pack(side="left", padx=1)
        ttk.Button(mgmt_btns, text=self.get_text("delete"), command=delete_selected_from_list).pack(side="left", padx=1)
        ttk.Button(mgmt_btns, text=self.get_text("new_item"), command=start_new).pack(side="left", padx=1)

        # ── Shape buttons ────────────────────────────────────────────────────
        btn_row = ttk.Frame(frm); btn_row.grid(row=3, column=0, columnspan=2, sticky="w", pady=(6,2))
        ttk.Button(btn_row, text=self.get_text("undo_point"), command=undo_point).pack(side="left", padx=2)
        ttk.Button(btn_row, text=self.get_text("clear_shape"), command=clear_points).pack(side="left", padx=2)
        ttk.Button(btn_row, text=self.get_text("finish_shape"), command=finish_shape).pack(side="left", padx=2)
        ttk.Separator(btn_row, orient="vertical").pack(side="left", fill="y", padx=6)
        ttk.Button(btn_row, text=self.get_text("rotate_left"), command=lambda: rotate_selected(-15)).pack(side="left", padx=2)
        ttk.Button(btn_row, text=self.get_text("rotate_right"), command=lambda: rotate_selected(15)).pack(side="left", padx=2)
        ttk.Button(btn_row, text=self.get_text("delete_element"), command=delete_selected).pack(side="left", padx=2)
        ttk.Button(btn_row, text=self.get_text("clear_all"), command=clear_all).pack(side="left", padx=2)

        ttk.Label(frm, text=self.get_text("furn_draw_help"),
                  foreground=self.C("text_muted"), font=("TkDefaultFont",8)
                  ).grid(row=4, column=0, columnspan=2, sticky="w", pady=(2,4))

        def do_save():
            name = name_var.get().strip()
            if not name:
                messagebox.showwarning(self.get_text("error_title"), self.get_text("furn_name_required"), parent=dlg)
                return
            # a dangling in-progress polygon (points placed but not "Finished")
            # gets auto-committed as one more shape for convenience
            if len(state["poly_pts"]) >= 3:
                state["elements"].append({"type": "polygon", "pts": list(state["poly_pts"])})
                state["poly_pts"] = []
            if not state["elements"]:
                messagebox.showwarning(self.get_text("error_title"), self.get_text("furn_shape_required"), parent=dlg)
                return
            try:
                z_height = float(h3d_var.get().replace(",", "."))
                if z_height <= 0:
                    raise ValueError
            except ValueError:
                messagebox.showwarning(self.get_text("error_title"), self.get_text("invalid_number"), parent=dlg)
                dim_entries[2].focus_set()
                return

            shelf = None
            if type_var.get() == "shelf":
                try:
                    lv = int(float(lv_var.get().replace(",", ".")))
                    bot = float(bot_var.get().replace(",", "."))
                    if not (2 <= lv <= 30) or bot < 0 or bot >= z_height:
                        raise ValueError
                except ValueError:
                    messagebox.showwarning(self.get_text("error_title"), self.get_text("shelf_invalid"), parent=dlg)
                    return
                shelf = {"levels": lv, "bottom": bot, "board": SHELF_BOARD, "post": SHELF_POST}
            minx, miny, maxx, maxy = all_bbox()
            shape_json = []
            for el in state["elements"]:
                if el["type"] == "oval":
                    shape_json.append({
                        "type": "oval",
                        "cx": round(el["cx"] - minx, 1), "cy": round(el["cy"] - miny, 1),
                        "rx": round(el["rx"], 1),        "ry": round(el["ry"], 1),
                    })
                else:
                    shape_json.append({
                        "type": "polygon",
                        "points": [[round(px - minx, 1), round(py - miny, 1)] for (px, py) in el["pts"]],
                    })
            width  = max(1.0, round(maxx - minx, 1))
            height = max(1.0, round(maxy - miny, 1))

            category_key = disp_to_key.get(cat_var.get(), "custom")
            if self._category(category_key) is None:
                category_key = self._add_category(self.get_text("custom_cat")) or "custom"

            if editing["fid"]:
                fid = editing["fid"]
                self._delete_furniture_entry(fid)   # remove the old version, then re-add below
            else:
                slug = re.sub(r'[^a-z0-9]+', '_', name.lower()).strip('_') or "item"
                fid = f"custom_{slug}_{int(time.time()*1000) % 1000000}"

            entry = {"fid": fid, "label_key": name, "category": category_key, "z_height": z_height,
                     "width": width, "height": height, "draw_fn": "custom_shape",
                     "shape": shape_json, "fill": fill_color["value"],
                     "outline": self._darken_hex(fill_color["value"])}
            if shelf:
                entry["shelf"] = shelf

            if self._save_custom_furniture(entry):
                self._populate_library()
                self._redraw_all()
                refresh_list()
                start_new()

        bottom_row = ttk.Frame(frm); bottom_row.grid(row=5, column=0, columnspan=2, sticky="w", pady=(4,0))
        save_btn = ttk.Button(bottom_row, text=f"💾 {self.get_text('save')}", command=do_save)
        save_btn.pack(side="left", padx=(0,4))
        ttk.Button(bottom_row, text=self.get_text("cancel"), command=dlg.destroy).pack(side="left")

        def on_key_delete(e):
            if dlg.focus_get() is draw_canvas:
                delete_selected()

        dlg.bind("<Delete>", on_key_delete)
        dlg.bind("<Escape>", lambda e: dlg.destroy())

        # initial view: zoom 100% (2 px per cm), scrolled to the top-left corner
        total = (AREA + 2 * MARGIN) * ppc()
        draw_canvas.configure(scrollregion=(0, 0, total, total))
        zoom_lbl.configure(text=f"{int(ppc() * 50)}%")
        draw_grid()
        redraw()
        dlg.after_idle(draw_rulers)
        name_entry.focus_set()

    def _build_floor_row_container(self):
        for w in self.floor_row_container.winfo_children():
            w.destroy()
        ttk.Label(self.floor_row_container, text=f"🏢 {self.get_text('floor')}:").pack(side="left", padx=(0,4))
        self.floor_btns_frame = ttk.Frame(self.floor_row_container)
        self.floor_btns_frame.pack(side="left")
        ttk.Button(self.floor_row_container, text=f"+ {self.get_text('add_floor')}", command=self._add_floor).pack(side="left", padx=6)
        self.ghost_info_label = ttk.Label(self.floor_row_container, text="",
                                          foreground=self.C("text_muted"), font=("TkDefaultFont",8))
        self.ghost_info_label.pack(side="left", padx=8)
        self.floor_var = tk.IntVar(value=self.current_floor)
        self._rebuild_floor_buttons()

    def _build_main_area(self):
        pane = self.main_pane
        for w in pane.winfo_children():
            w.destroy()
        cf = ttk.Frame(pane); cf.pack(side="left", fill="both", expand=True)
        self.hbar = ttk.Scrollbar(cf, orient="horizontal")
        self.vbar = ttk.Scrollbar(cf, orient="vertical")
        self.hbar.pack(side="bottom", fill="x")
        self.vbar.pack(side="right",  fill="y")
        self.canvas = tk.Canvas(cf, bg=self.C("canvas_bg"), highlightthickness=0,
                                xscrollcommand=self.hbar.set,
                                yscrollcommand=self.vbar.set)
        self.canvas.pack(fill="both", expand=True)
        self.hbar.config(command=self.canvas.xview)
        self.vbar.config(command=self.canvas.yview)
        self._update_scroll_region()

        self.canvas.bind("<Button-1>",        self.click)
        self.canvas.bind("<Motion>",          self.motion)
        self.canvas.bind("<B1-Motion>",       self.drag)
        self.canvas.bind("<ButtonRelease-1>", self.release)
        self.canvas.bind("<Button-2>",        self._pan_start)
        self.canvas.bind("<B2-Motion>",       self._pan_move)
        self.canvas.bind("<MouseWheel>",      self._on_mousewheel)
        self.canvas.bind("<Shift-MouseWheel>",self._on_mousewheel_h)
        self.canvas.bind("<Button-4>",        self._on_mousewheel)
        self.canvas.bind("<Button-5>",        self._on_mousewheel)
        self.root.bind("<F1>", lambda e: self.toggle_help())
        self.root.bind("<Delete>", self.delete_selected)
        self.root.bind("<r>",      self._rotate_cw)
        self.root.bind("<R>",      self._rotate_cw)
        self.root.bind("<l>",      self._rotate_ccw)
        self.root.bind("<L>",      self._rotate_ccw)
        self.root.bind("<m>",      lambda e: self.mode.set("measure"))
        self.root.bind("<M>",      lambda e: self.mode.set("measure"))
        self.root.bind("<Escape>", self._cancel_current_draw)
        self.canvas.bind("<Double-Button-1>", self._on_double_click)
        self.root.bind("<Control-d>", self._duplicate_selected)
        self.root.bind("<Control-D>", self._duplicate_selected)
        self.root.bind("<Prior>", lambda e: self._move_level(+1))
        self.root.bind("<Next>",  lambda e: self._move_level(-1))

        # Side furniture selection panel
        panel = ttk.Frame(pane, width=210, relief="sunken", borderwidth=1)
        panel.pack(side="right", fill="y"); panel.pack_propagate(False)
        furn_header = tk.Frame(panel, bg=self.C("accent_soft"))
        furn_header.pack(fill="x")
        ttk.Label(furn_header, text=self.get_text("furniture"), font=("TkDefaultFont",10,"bold"),
                  background=self.C("accent_soft"), foreground=self.C("text")).pack(pady=(6,2))
        ttk.Label(furn_header, text=self.get_text("furn_help"),
                  font=("TkDefaultFont",7), foreground=self.C("text_muted"),
                  background=self.C("accent_soft")).pack(pady=(0,4))
        pf  = ttk.Frame(panel); pf.pack(fill="both", expand=True)
        psb = ttk.Scrollbar(pf, orient="vertical"); psb.pack(side="right", fill="y")
        self.lib_canvas = tk.Canvas(pf, bg=self.C("lib_bg"),
                                    yscrollcommand=psb.set, highlightthickness=0)
        self.lib_canvas.pack(side="left", fill="both", expand=True)
        psb.config(command=self.lib_canvas.yview)
        self.lib_canvas.bind("<MouseWheel>",
            lambda e: self.lib_canvas.yview_scroll(-1*(e.delta//120),"units"))
        self.lib_inner = ttk.Frame(self.lib_canvas)
        self.lib_canvas.create_window((0,0), window=self.lib_inner, anchor="nw")
        self.lib_inner.bind("<Configure>",
            lambda e: self.lib_canvas.configure(
                scrollregion=self.lib_canvas.bbox("all")))
        self._populate_library()

    def _populate_library(self):
        for w in self.lib_inner.winfo_children():
            w.destroy()

        # "+ New Furniture" tile, always first
        add_row = tk.Frame(self.lib_inner, bg=self.C("lib_row_bg"), cursor="hand2")
        add_row.pack(fill="x", padx=4, pady=(4,6))
        add_thumb = tk.Canvas(add_row, width=56, height=44, bg="white",
                              relief="solid", bd=1, highlightthickness=0)
        add_thumb.pack(side="left")
        add_thumb.create_text(28, 22, text="+", font=("TkDefaultFont", 20, "bold"),
                              fill=self.C("accent"))
        add_lbl = tk.Label(add_row, text=self.get_text("new_furniture"),
                           bg=self.C("lib_row_bg"), fg=self.C("text"),
                           font=("TkDefaultFont", 8, "bold"), wraplength=120, justify="left")
        add_lbl.pack(side="left", padx=4)
        for w in (add_row, add_thumb, add_lbl):
            w.bind("<ButtonPress-1>", lambda e: self._open_furniture_creator())

        # "Manage categories" link
        cat_lbl = tk.Label(self.lib_inner, text=f"📂 {self.get_text('manage_categories')}",
                           bg=self.C("lib_bg"), fg=self.C("accent"), cursor="hand2",
                           font=("TkDefaultFont", 8, "underline"))
        cat_lbl.pack(anchor="w", padx=6, pady=(0,2))
        cat_lbl.bind("<ButtonPress-1>", lambda e: self._open_category_manager())

        # sorted by the category order from the category manager so items stay
        # grouped together no matter which JSON file(s) they were loaded from
        sorted_defs = sorted(self.furniture_defs,
                             key=lambda e: self._cat_order(e.get("category") or "custom"))
        groups = []                      # [(category id, [entries])] in display order
        for entry in sorted_defs:
            ck = entry.get("category") or "custom"
            if not groups or groups[-1][0] != ck:
                groups.append((ck, []))
            groups[-1][1].append(entry)

        # "collapse all / expand all" links
        links = tk.Frame(self.lib_inner, bg=self.C("lib_bg"))
        links.pack(anchor="w", padx=6, pady=(0,4))
        for txt, collapse in ((f"⊟ {self.get_text('collapse_all')}", True),
                              (f"⊞ {self.get_text('expand_all')}", False)):
            l = tk.Label(links, text=txt, bg=self.C("lib_bg"), fg=self.C("accent"), cursor="hand2",
                         font=("TkDefaultFont", 8, "underline"))
            l.pack(side="left", padx=(0,10))
            l.bind("<ButtonPress-1>",
                   lambda e, c=collapse, ids=[g[0] for g in groups]: self._set_all_categories(ids, c))

        for cat_key, entries in groups:
            collapsed = cat_key in self.collapsed_cats
            arrow = "▶" if collapsed else "▼"
            hdr = tk.Label(self.lib_inner, text=f"{arrow}  {self._cat_name(cat_key)}  ({len(entries)})",
                           font=("TkDefaultFont",9,"bold"), anchor="w", cursor="hand2",
                           bg=self.C("lib_cat_bg"), fg=self.C("lib_cat_fg"), padx=6, pady=2)
            hdr.pack(fill="x", pady=(6,1), padx=2)
            hdr.bind("<ButtonPress-1>", lambda e, c=cat_key: self._toggle_category(c))
            if collapsed:
                continue
            for entry in entries:
                self._library_row(entry)

    def _toggle_category(self, cat_key):
        """Click on a category header in the furniture panel: hide / show its items."""
        if cat_key in self.collapsed_cats:
            self.collapsed_cats.discard(cat_key)
        else:
            self.collapsed_cats.add(cat_key)
        self._save_settings()
        self._repopulate_library_keep_scroll()

    def _set_all_categories(self, cat_ids, collapse):
        if collapse:
            self.collapsed_cats.update(cat_ids)
        else:
            self.collapsed_cats.difference_update(cat_ids)
        self._save_settings()
        self._repopulate_library_keep_scroll()

    def _repopulate_library_keep_scroll(self):
        try:
            top = self.lib_canvas.yview()[0]
        except tk.TclError:
            top = 0.0
        self._populate_library()
        self.lib_inner.update_idletasks()
        self.lib_canvas.configure(scrollregion=self.lib_canvas.bbox("all"))
        self.lib_canvas.yview_moveto(top)

    def _library_row(self, entry):
            fid, label_key = entry["fid"], entry.get("label_key", entry["fid"])
            dw, dh = entry["width"], entry["height"]
            translated_label = self.get_text(label_key)
            row = tk.Frame(self.lib_inner, bg=self.C("lib_row_bg"), cursor="hand2")
            row.pack(fill="x", padx=4, pady=2)
            # thumbnail stays on a fixed white card so every furniture icon's
            # (mostly light/pastel) colors always render with full contrast,
            # regardless of the active theme
            thumb = tk.Canvas(row, width=56, height=44, bg="white",
                              relief="solid", bd=1, highlightthickness=0)
            thumb.pack(side="left")
            self._draw_furniture_thumb(thumb, entry)
            lbl = tk.Label(row, text=translated_label, bg=self.C("lib_row_bg"), fg=self.C("text"),
                           font=("TkDefaultFont",8), wraplength=120, justify="left")
            lbl.pack(side="left", padx=4)
            for w in (row, thumb, lbl):
                w.bind("<ButtonPress-1>",
                       lambda e, f=fid, fw=dw, fh=dh: self._lib_pick(e,f,fw,fh))

    # ═══════════════════════════════════════════════════════════════════════════
    #  Floors
    # ═══════════════════════════════════════════════════════════════════════════

    def _rebuild_floor_buttons(self):
        for w in self.floor_btns_frame.winfo_children():
            w.destroy()
        for i in range(len(self.floors)):
            ttk.Radiobutton(self.floor_btns_frame, text=f"{self.get_text('floor')} {i+1}",
                            variable=self.floor_var, value=i,
                            style="Toolbutton",
                            command=lambda idx=i: self._switch_floor(idx)
                            ).pack(side="left", padx=1)
        if len(self.floors) > 1:
            self.ghost_info_label.config(text=self.get_text("ghost_info"))
        else:
            self.ghost_info_label.config(text="")

    def _add_floor(self):
        self.floors.append(self._new_floor_data())
        new_idx = len(self.floors) - 1
        self._rebuild_floor_buttons()
        self.floor_var.set(new_idx)
        self._switch_floor(new_idx)

    def _switch_floor(self, idx):
        if idx == self.current_floor:
            return
        self.deselect_all()
        self.current_floor = idx
        floor = self.floors[idx]
        self.walls        = floor["walls"]
        self.furniture     = floor["furniture"]
        self.freehand      = floor["freehand"]
        self.measurements  = floor["measurements"]
        self.floor_var.set(idx)
        self._redraw_all()

    def _draw_ghost_walls(self):
        self._ghost_ids = []
        if self.current_floor == 0:
            return
        below_walls = self.floors[self.current_floor - 1]["walls"]
        for w in below_walls:
            x1,y1 = self.w2c(w["x1"]), self.w2c(w["y1"])
            x2,y2 = self.w2c(w["x2"]), self.w2c(w["y2"])
            gid = self.canvas.create_line(
                x1,y1,x2,y2,
                fill=self.C("ghost"), width=w["width"], dash=(6,4), tags="ghost")
            self._ghost_ids.append(gid)

    # ═══════════════════════════════════════════════════════════════════════════
    #  Grid
    # ═══════════════════════════════════════════════════════════════════════════

    def draw_grid(self):
        self.canvas.delete("grid")
        step = self.w2c(self.grid_step())  
        cw   = self.w2c(CANVAS_W)
        ch   = self.w2c(CANVAS_H)
        minor, major = self.C("grid_line"), self.C("grid_line_major")
        i = 0; x = 0.0
        while x <= cw:
            color = major if i % 5 == 0 else minor
            self.canvas.create_line(x, 0, x, ch, fill=color, tags="grid")
            x += step; i += 1
        i = 0; y = 0.0
        while y <= ch:
            color = major if i % 5 == 0 else minor
            self.canvas.create_line(0, y, cw, y, fill=color, tags="grid")
            y += step; i += 1
        self.canvas.tag_lower("grid")

    def _update_scroll_region(self):
        self.canvas.configure(scrollregion=(0, 0,
                                            self.w2c(CANVAS_W),
                                            self.w2c(CANVAS_H)))

    # ═══════════════════════════════════════════════════════════════════════════
    #  Zooming
    # ═══════════════════════════════════════════════════════════════════════════

    ZOOM_STEPS = [0.25, 0.33, 0.5, 0.67, 0.75, 1.0, 1.25, 1.5, 2.0, 2.5, 3.0, 4.0]

    def _pan_start(self, e): self.canvas.scan_mark(e.x, e.y)
    def _pan_move(self, e):  self.canvas.scan_dragto(e.x, e.y, gain=1)

    def _on_mousewheel(self, e):
        # Windows/macOS send <MouseWheel> with delta; Linux sends Button-4/5
        up = (e.delta > 0) if e.num not in (4, 5) else (e.num == 4)
        if e.state & 0x4:
            if up: self._zoom_in()
            else:  self._zoom_out()
        elif e.state & 0x1:
            self.canvas.xview_scroll(-1 if up else 1, "units")
        else:
            self.canvas.yview_scroll(-1 if up else 1, "units")

    def _on_mousewheel_h(self, e):
        up = (e.delta > 0) if e.num not in (4, 5) else (e.num == 4)
        self.canvas.xview_scroll(-1 if up else 1, "units")

    def _zoom_index(self):
        return min(range(len(self.ZOOM_STEPS)),
                   key=lambda i: abs(self.ZOOM_STEPS[i]-self.zoom))

    def _zoom_in(self):
        i = self._zoom_index()
        if i < len(self.ZOOM_STEPS)-1:
            self._apply_zoom(self.ZOOM_STEPS[i+1])

    def _zoom_out(self):
        i = self._zoom_index()
        if i > 0:
            self._apply_zoom(self.ZOOM_STEPS[i-1])

    def _zoom_reset(self):
        self._apply_zoom(1.0)

    def _apply_zoom(self, new_zoom):
        if new_zoom == self.zoom: return
        hfrac = self.canvas.xview()[0]
        vfrac = self.canvas.yview()[0]

        self.zoom = new_zoom
        self.zoom_label.config(text=f"{int(new_zoom*100)}%")
        self._update_scroll_region()
        self._redraw_all()

        self.canvas.xview_moveto(hfrac)
        self.canvas.yview_moveto(vfrac)

    # ═══════════════════════════════════════════════════════════════════════════
    #  Grid configuration changes
    # ═══════════════════════════════════════════════════════════════════════════

    def _on_grid_change(self):
        unit_suffix = "cm" if self.units == "metric" else "in"
        self.grid_menubtn.config(text=f"⊞ {self.get_text('grid')}: {self.grid_val_var.get()} {unit_suffix}")
        self.draw_grid()
        self._refresh_labels()

    # ═══════════════════════════════════════════════════════════════════════════
    #  Dynamic Redrawing / Refreshing
    # ═══════════════════════════════════════════════════════════════════════════

    def _redraw_all(self):
        self.canvas.delete("all")
        self.draw_grid()
        self._draw_ghost_walls()
        self._recompute_and_draw_rooms()
        for w in self.walls:
            self._draw_wall_canvas(w)
        for item in self._furn_by_height():
            self._draw_furn_canvas(item)
        self._update_stack_labels()
        for item in self.freehand:
            self._draw_freehand_canvas(item)
        for m in self.measurements:
            self._draw_measure_canvas(m)
        if self.selected:
            self._show_handles(self.selected, True)
            if self.selected["kind"] in ("freehand", "measure", "opening"):
                self._highlight_item(self.selected, True)
        for item in self.multi_sel:
            self._highlight_item(item, True)
        self._schedule_3d_refresh()
        sv = getattr(self, "shelf_view", None)
        if sv and sv.exists() and not getattr(self, "_sv_pending", False):
            self._sv_pending = True
            def _sv_refresh():
                self._sv_pending = False
                if sv.exists():
                    sv.refresh()
            self.root.after_idle(_sv_refresh)

    def _refresh_labels(self):
        for w in self.walls:
            self.canvas.itemconfigure(w["text_id"],
                text=self.wall_text(w["x1"],w["y1"],w["x2"],w["y2"]))
        for item in self.furniture:
            self.canvas.itemconfigure(item["sz_text"],
                text=self.furn_size_text(item))

    # ═══════════════════════════════════════════════════════════════════════════
    #  Auto room detection
    # ═══════════════════════════════════════════════════════════════════════════

    def _recompute_rooms(self):
        wall_segs = [(w["x1"], w["y1"], w["x2"], w["y2"]) for w in self.walls]
        try:
            self.rooms = compute_rooms(wall_segs)
        except Exception:
            # geometry edge-cases should never crash the app - just skip
            # showing rooms for this redraw rather than raising
            self.rooms = []

    def _recompute_and_draw_rooms(self):
        auto_on = getattr(self, "auto_rooms_var", None)
        if auto_on is not None and auto_on.get():
            self._recompute_rooms()
        else:
            self.rooms = []
        self._draw_rooms()

    def _draw_rooms(self):
        for cid in self._room_canvas_ids:
            self.canvas.delete(cid)
        self._room_canvas_ids = []
        if not self.rooms:
            return
        palette = self.C("room_palette")
        for i, room in enumerate(self.rooms):
            coords = []
            for (wx, wy) in room["points"]:
                coords.append(self.w2c(wx)); coords.append(self.w2c(wy))
            fill = palette[i % len(palette)]
            pid = self.canvas.create_polygon(*coords, fill=fill, outline="", tags="room")
            self._room_canvas_ids.append(pid)
            cx, cy = self.w2c(room["centroid"][0]), self.w2c(room["centroid"][1])
            label = f"{self.get_text('room_lbl')} {i+1}\n{self.format_area(room['area'])}"
            tid = self.canvas.create_text(cx, cy, text=label, justify="center",
                        font=("TkDefaultFont", 9, "bold"), fill=self.C("room_label"), tags="room")
            self._room_canvas_ids.append(tid)
        # sit just above the grid, below walls/furniture/freehand (which are
        # always (re)drawn after this, whether via a full redraw or an
        # incremental update, so this keeps the stacking correct either way)
        self.canvas.tag_raise("room", "grid")

    # ═══════════════════════════════════════════════════════════════════════════
    #  Wall handling
    # ═══════════════════════════════════════════════════════════════════════════

    def _draw_wall_canvas(self, w):
        for key in ("line_id","text_id","h1_id","h2_id"):
            if w.get(key): self.canvas.delete(w[key])

        x1,y1,x2,y2 = self.w2c(w["x1"]),self.w2c(w["y1"]),self.w2c(w["x2"]),self.w2c(w["y2"])
        w["line_id"] = self.canvas.create_line(x1,y1,x2,y2, width=w["width"], fill=self._ink(w["color"]))
        for op in w.get("openings", []):
            self._draw_opening(op, highlight=(op is self.selected or op in self.multi_sel))
        mx,my = (x1+x2)/2, (y1+y2)/2
        w["text_id"] = self.canvas.create_text(mx,my-10,
            text=self.wall_text(w["x1"],w["y1"],w["x2"],w["y2"]),
            font=("TkDefaultFont",8), fill=self.C("text_muted"))
        w["h1_id"] = self.canvas.create_oval(x1-HANDLE,y1-HANDLE,x1+HANDLE,y1+HANDLE,
                                              fill=self.C("select"), outline="white", state="hidden", tags="handle")
        w["h2_id"] = self.canvas.create_oval(x2-HANDLE,y2-HANDLE,x2+HANDLE,y2+HANDLE,
                                              fill=self.C("select"), outline="white", state="hidden", tags="handle")

    def add_wall(self, wx1,wy1,wx2,wy2, color="black", width=4, draw=True,
                 height=None, thickness=None, openings=None):
        w = {"kind":"wall",
             "x1":wx1,"y1":wy1,"x2":wx2,"y2":wy2,
             "color":color,"width":width,
             "height": height if height else self.default_wall_height,
             "thickness": thickness if thickness else self.default_wall_thickness,
             "openings": [],
             "line_id":None,"text_id":None,"h1_id":None,"h2_id":None}
        self.walls.append(w)
        for o in (openings or []):
            self._new_opening(w, o.get("type", "door"), o.get("pos", 0),
                              o.get("width"), o.get("height"), o.get("sill"), o.get("orient", 0))
        if draw:
            self._draw_wall_canvas(w)
        return w

    def _refresh_wall(self, w):
        x1,y1,x2,y2 = self.w2c(w["x1"]),self.w2c(w["y1"]),self.w2c(w["x2"]),self.w2c(w["y2"])
        self.canvas.coords(w["line_id"], x1,y1,x2,y2)
        mx,my=(x1+x2)/2,(y1+y2)/2
        self.canvas.coords(w["text_id"], mx, my-10)
        self.canvas.itemconfigure(w["text_id"],
            text=self.wall_text(w["x1"],w["y1"],w["x2"],w["y2"]))
        self.canvas.coords(w["h1_id"], x1-HANDLE,y1-HANDLE,x1+HANDLE,y1+HANDLE)
        self.canvas.coords(w["h2_id"], x2-HANDLE,y2-HANDLE,x2+HANDLE,y2+HANDLE)
        if w.get("openings"):
            self._clamp_openings(w)
            self._draw_openings(w)

    # ═══════════════════════════════════════════════════════════════════════════
    #  Freehand strokes
    # ═══════════════════════════════════════════════════════════════════════════

    def _draw_freehand_canvas(self, item):
        if item.get("line_id"): self.canvas.delete(item["line_id"])
        coords = []
        for (wx,wy) in item["points"]:
            coords.append(self.w2c(wx)); coords.append(self.w2c(wy))
        if len(coords) < 4:
            item["line_id"] = None
            return
        item["line_id"] = self.canvas.create_line(
            *coords, fill=self._ink(item["color"]), width=item["width"],
            smooth=True, splinesteps=12, capstyle="round", joinstyle="round")

    def add_freehand(self, points, color="black", width=2, draw=True):
        item = {"kind":"freehand",
                "points":[tuple(p) for p in points],
                "color":color, "width":width, "line_id":None}
        self.freehand.append(item)
        if draw:
            self._draw_freehand_canvas(item)
        return item

    def _freehand_dist(self, item, px, py):
        pts = item["points"]
        best = 999999
        for i in range(len(pts)-1):
            x1,y1 = pts[i]; x2,y2 = pts[i+1]
            d = self.segdist(px,py,x1,y1,x2,y2)
            if d < best: best = d
        return best

    def _freehand_bbox(self, item):
        xs=[p[0] for p in item["points"]]; ys=[p[1] for p in item["points"]]
        return min(xs),min(ys),max(xs),max(ys)

    # ═══════════════════════════════════════════════════════════════════════════
    #  Measuring tool
    # ═══════════════════════════════════════════════════════════════════════════

    def add_measurement(self, x1, y1, x2, y2, draw=True):
        m = {"kind":"measure", "x1":x1, "y1":y1, "x2":x2, "y2":y2,
             "line_id":None, "text_id":None, "t1_id":None, "t2_id":None}
        self.measurements.append(m)
        if draw:
            self._draw_measure_canvas(m)
        return m

    def _draw_measure_canvas(self, m):
        for k in ("line_id","text_id","t1_id","t2_id"):
            if m.get(k):
                self.canvas.delete(m[k])
        x1,y1 = self.w2c(m["x1"]), self.w2c(m["y1"])
        x2,y2 = self.w2c(m["x2"]), self.w2c(m["y2"])
        col = self.C("measure")
        m["line_id"] = self.canvas.create_line(x1,y1,x2,y2, fill=col, width=2,
                                                 dash=(6,3), tags="measure")
        ang  = atan2(y2-y1, x2-x1)
        perp = ang + pi/2
        tl = 6
        m["t1_id"] = self.canvas.create_line(x1-tl*cos(perp), y1-tl*sin(perp),
                                              x1+tl*cos(perp), y1+tl*sin(perp),
                                              fill=col, width=2, tags="measure")
        m["t2_id"] = self.canvas.create_line(x2-tl*cos(perp), y2-tl*sin(perp),
                                              x2+tl*cos(perp), y2+tl*sin(perp),
                                              fill=col, width=2, tags="measure")
        mx,my = (x1+x2)/2, (y1+y2)/2
        dist = hypot(m["x2"]-m["x1"], m["y2"]-m["y1"])
        m["text_id"] = self.canvas.create_text(mx, my-12, text=f"📐 {self.format_length(dist)}",
                            font=("TkDefaultFont",8,"bold"), fill=col, tags="measure")

    def _clear_measurements(self):
        for m in self.measurements:
            for k in ("line_id","text_id","t1_id","t2_id"):
                if m.get(k):
                    self.canvas.delete(m[k])
        self.measurements.clear()
        if self.selected and self.selected.get("kind") == "measure":
            self.selected = None
        self.multi_sel = [it for it in self.multi_sel if it.get("kind") != "measure"]

    def _cancel_current_draw(self, event=None):
        """Escape - cancel an in-progress wall / measurement without placing it,
        and leave the Door / Window / furniture placing tools."""
        if self.mode.get() in ("place_door", "place_window", "place_furn"):
            self.mode.set("select")
        self.start = None
        self.measure_start = None
        self._fh_points = None
        if self.preview:
            self.canvas.delete(self.preview); self.preview = None
        if self._measure_preview:
            self.canvas.delete(self._measure_preview); self._measure_preview = None
        if self._measure_preview_text:
            self.canvas.delete(self._measure_preview_text); self._measure_preview_text = None

    # ═══════════════════════════════════════════════════════════════════════════
    #  Furniture rendering & properties
    # ═══════════════════════════════════════════════════════════════════════════

    def _render_furn_shape(self, proxy, x1, y1, x2, y2, entry):
        """Draw one furniture piece's footprint. Built-in pieces have a named
        draw_fn matching one of the hand-crafted _furn_* methods below; custom
        user-drawn pieces store their own shape(s) and use the generic
        _render_custom_shape_elements renderer, scaled to whatever size it's placed at."""
        draw_fn = entry.get("draw_fn") if entry else None
        if draw_fn == "custom_shape" and (entry.get("shape") or entry.get("points")):
            orig_w = entry.get("width") or 1
            orig_h = entry.get("height") or 1
            return self._render_custom_shape_elements(proxy, x1, y1, x2, y2, entry, orig_w, orig_h)
        method = getattr(self, f"_furn_{draw_fn}", None) if draw_fn else None
        if method:
            return method(proxy, x1, y1, x2, y2)
        return [proxy.create_rectangle(x1, y1, x2, y2, outline="#999", fill="#eee")]

    def _render_custom_shape_elements(self, c, x1, y1, x2, y2, entry, orig_w, orig_h):
        """Generic renderer for a user hand-drawn footprint - one or more
        polygon/oval elements, scaled from the size they were drawn at to
        however big the piece is placed. Also reads the older single-polygon
        'points' format from furniture saved before multi-shape support."""
        W, H = x2 - x1, y2 - y1
        sx = W / orig_w if orig_w else 1
        sy = H / orig_h if orig_h else 1
        fill = entry.get("fill") or "#e0d3ae"
        outline = entry.get("outline") or "#8a7452"
        shape = entry.get("shape")
        if not shape and entry.get("points"):
            shape = [{"type": "polygon", "points": entry["points"]}]
        if not shape:
            return [c.create_rectangle(x1, y1, x2, y2, fill=fill, outline=outline, width=1)]
        ids = []
        for el in shape:
            if el.get("type") == "oval":
                cx = x1 + el.get("cx", 0) * sx; cy = y1 + el.get("cy", 0) * sy
                rx = el.get("rx", 0) * sx;      ry = el.get("ry", 0) * sy
                ids.append(c.create_oval(cx-rx, cy-ry, cx+rx, cy+ry,
                                         fill=fill, outline=outline, width=1))
            else:
                flat = []
                for (px, py) in el.get("points", []):
                    flat.append(x1 + px*sx); flat.append(y1 + py*sy)
                if len(flat) >= 6:
                    ids.append(c.create_polygon(flat, fill=fill, outline=outline, width=1))
        if not ids:
            ids.append(c.create_rectangle(x1, y1, x2, y2, fill=fill, outline=outline, width=1))
        if isinstance(entry.get("shelf"), dict):
            # shelf symbol: corner posts + a cross, like on a real floor plan
            ps = max(2.0, entry["shelf"].get("post", SHELF_POST) * min(sx, sy))
            ids.append(c.create_line(x1, y1, x2, y2, fill=outline, width=1))
            ids.append(c.create_line(x1, y2, x2, y1, fill=outline, width=1))
            for (px, py) in ((x1, y1), (x2 - ps, y1), (x1, y2 - ps), (x2 - ps, y2 - ps)):
                ids.append(c.create_rectangle(px, py, px + ps, py + ps, fill=outline, outline=outline))
        return ids

    def _draw_furn_canvas(self, item):
        for cid in item.get("group", []): self.canvas.delete(cid)
        for hid in item.get("handles", {}).values(): self.canvas.delete(hid)
        for key in ("text","sz_text","rot_badge"):
            if item.get(key): self.canvas.delete(item[key])
        item["handles"] = {}

        x1,y1 = self.w2c(item["x1"]), self.w2c(item["y1"])
        x2,y2 = self.w2c(item["x2"]), self.w2c(item["y2"])
        cx,cy  = (x1+x2)/2, (y1+y2)/2
        W,H    = x2-x1, y2-y1
        angle  = item["angle"]

        sideways = (angle // 90) % 2 == 1
        W_local, H_local = (H, W) if sideways else (W, H)

        entry   = self._furn_def(item["fid"])
        proxy   = RotatedDraw(self.canvas, cx, cy, W_local, H_local, angle)
        item["group"] = self._render_furn_shape(proxy, 0, 0, W_local, H_local, entry)

        if self.furniture_dimmed:
            for cid in item["group"]:
                try:
                    self.canvas.itemconfigure(cid, fill="#999999", stipple="gray25")
                except tk.TclError:
                    pass
                try:
                    self.canvas.itemconfigure(cid, outline="#bbbbbb")
                except tk.TclError:
                    pass

        label_key = entry.get("label_key", item["fid"]) if entry else item["fid"]
        label = self.get_text(label_key)
        label_state = "hidden" if self.furniture_dimmed else "normal"
        # on-body label sits over the furniture's own (theme-independent, light
        # pastel) fill colors, so it keeps a fixed dark tone for readability
        item["text"]    = self.canvas.create_text(cx, cy, text=label,
                            font=("TkDefaultFont",7), fill="#333333", state=label_state)
        # size/rotation labels sit over the plain canvas background, so they
        # follow the active theme like any other canvas text
        item["sz_text"] = self.canvas.create_text(cx, y1-12,
                            text=self.furn_size_text(item),
                            font=("TkDefaultFont",7), fill=self.C("text_muted"), state=label_state)
        item["rot_badge"] = None
        if angle % 360 != 0:
            item["rot_badge"] = self.canvas.create_text(
                cx, y2+10, text=f"↻ {angle}°",
                font=("TkDefaultFont",7,"bold"), fill=self.C("accent"), state=label_state)

        item["handles"] = self._make_furn_handles(x1,y1,x2,y2)
        for cid in list(item["handles"].values())+[item["text"],item["sz_text"]]:
            self.canvas.tag_raise(cid)
        if item["rot_badge"]: self.canvas.tag_raise(item["rot_badge"])

    def _make_furn_handles(self, x1, y1, x2, y2):
        mx,my=(x1+x2)/2,(y1+y2)/2
        pts={"tl":(x1,y1),"tr":(x2,y1),"bl":(x1,y2),"br":(x2,y2),
             "tm":(mx,y1),"bm":(mx,y2),"ml":(x1,my),"mr":(x2,my)}
        hs={}
        for name,(hx,hy) in pts.items():
            hs[name]=self.canvas.create_rectangle(
                hx-HANDLE,hy-HANDLE,hx+HANDLE,hy+HANDLE,
                fill=self.C("handle"),outline="white",state="hidden",tags="handle")
        return hs

    def add_furniture(self, fid, wx1,wy1,wx2,wy2, angle=0, draw=True):
        entry = self._furn_def(fid)
        if entry is None: return None
        item = {"kind":"furniture","fid":fid,
                "x1":wx1,"y1":wy1,"x2":wx2,"y2":wy2,
                "angle":angle,
                "group":[],"text":None,"sz_text":None,"rot_badge":None,"handles":{}}
        self.furniture.append(item)
        if draw:
            self._draw_furn_canvas(item)
        return item

    # ═══════════════════════════════════════════════════════════════════════════
    #  Rotation
    # ═══════════════════════════════════════════════════════════════════════════

    def _rotate_cw(self,  e=None): self._rotate_selected(+90)
    def _rotate_ccw(self, e=None): self._rotate_selected(-90)

    def _rotate_selected(self, delta):
        if self.selected and self.selected["kind"] == "opening":
            op = self.selected
            if op["type"] == "door":
                seq = [0, 2, 3, 1]   # cycle through the 4 hinge/swing combinations
                i = seq.index(op["orient"] & 3)
                op["orient"] = seq[(i + (1 if delta > 0 else -1)) % 4]
                self._draw_opening(op, highlight=True)
                self._schedule_3d_refresh()
            return
        if not self.selected or self.selected["kind"] != "furniture": return
        item = self.selected
        item["angle"] = (item["angle"] + delta) % 360
        bbox = (item["x1"], item["y1"], item["x2"], item["y2"])
        # Rotate around the centre, then snap the top-left corner to the grid
        # so the piece lines up with the grid again. The unsnapped centre is
        # remembered while the piece is only being rotated, so four turns in a
        # row bring it back exactly where it started instead of drifting.
        pv = item.get("_pivot")
        if pv and pv[2] == bbox:
            cx, cy = pv[0], pv[1]
        else:
            cx = (item["x1"]+item["x2"])/2; cy = (item["y1"]+item["y2"])/2
        W  = abs(item["x2"]-item["x1"]); H  = abs(item["y2"]-item["y1"])
        item["x1"] = self.snap_world(cx - H/2); item["x2"] = item["x1"] + H
        item["y1"] = self.snap_world(cy - W/2); item["y2"] = item["y1"] + W
        item["_pivot"] = (cx, cy, (item["x1"], item["y1"], item["x2"], item["y2"]))
        self._draw_furn_canvas(item)
        for hid in item["handles"].values():
            self.canvas.itemconfigure(hid, state="normal")
        self._drag_x1=item["x1"]; self._drag_y1=item["y1"]
        self._drag_ox=(item["x1"]+item["x2"])/2
        self._drag_oy=(item["y1"]+item["y2"])/2
        if self._apply_gravity():
            self._redraw_all()
        self._schedule_3d_refresh()

    # ═══════════════════════════════════════════════════════════════════════════
    #  Hide / dim furniture
    # ═══════════════════════════════════════════════════════════════════════════

    def _toggle_furniture_dim(self):
        self.furniture_dimmed = self.furn_dim_var.get()
        if self.furniture_dimmed:
            if self.selected and self.selected["kind"] == "furniture":
                self.deselect_all()
            for it in list(self.multi_sel):
                if it["kind"] == "furniture":
                    self.multi_remove(it)
        self._redraw_all()

    # ═══════════════════════════════════════════════════════════════════════════
    #  Room creator
    # ═══════════════════════════════════════════════════════════════════════════

    def create_room(self):
        try: 
            w = float(self.room_w_var.get())
            h = float(self.room_h_var.get())
        except ValueError: 
            return
            
        # Convert user units to world coordinates (1 pixel = 1 cm)
        if self.units == "metric":
            pw = w * 100.0
            ph = h * 100.0
        else: # imperial to cm (1 ft = 30.48 cm)
            pw = w * 30.48
            ph = h * 30.48
            
        x,y = 200,200
        col,wid=self.color.get(),self.thickness.get()
        self.add_wall(x,y,     x+pw,y,      color=col,width=wid)
        self.add_wall(x+pw,y,  x+pw,y+ph,   color=col,width=wid)
        self.add_wall(x+pw,y+ph,x,y+ph,     color=col,width=wid)
        self.add_wall(x,y+ph,  x,y,          color=col,width=wid)
        self._recompute_and_draw_rooms()

    # ═══════════════════════════════════════════════════════════════════════════
    #  Furniture selection library pick
    # ═══════════════════════════════════════════════════════════════════════════

    def _lib_pick(self, event, fid, dfw, dfh):
        entry = self._furn_def(fid) or {}
        if entry.get("draw_fn") == "opening_door":
            self.mode.set("place_door"); return
        if entry.get("draw_fn") == "opening_window":
            self.mode.set("place_window"); return
        self.mode.set("place_furn")
        self._pending_fid=fid; self._pending_dfw=dfw; self._pending_dfh=dfh
        self.root.config(cursor="crosshair")

    # ═══════════════════════════════════════════════════════════════════════════
    #  Canvas Events
    # ═══════════════════════════════════════════════════════════════════════════

    def _hit_item(self, wx, wy):
        op = self._hit_opening(wx, wy)
        if op:
            return op
        if not self.furniture_dimmed:
            for furn in reversed(self._furn_by_height()):
                fx1,fy1=min(furn["x1"],furn["x2"]),min(furn["y1"],furn["y2"])
                fx2,fy2=max(furn["x1"],furn["x2"]),max(furn["y1"],furn["y2"])
                if fx1<=wx<=fx2 and fy1<=wy<=fy2:
                    return furn
        best=12; nearest=None
        for wall in self.walls:
            d=self.segdist(wx,wy,wall["x1"],wall["y1"],wall["x2"],wall["y2"])
            if d<best: best=d; nearest=wall
        for fh in self.freehand:
            d=self._freehand_dist(fh, wx, wy)
            if d<best: best=d; nearest=fh
        for meas in self.measurements:
            d=self.segdist(wx,wy,meas["x1"],meas["y1"],meas["x2"],meas["y2"])
            if d<best: best=d; nearest=meas
        return nearest

    def click(self, event):
        wx,wy = self.event_world(event)
        m     = self.mode.get()
        ctrl  = bool(event.state & 0x4)   
        shift = bool(event.state & 0x1)   

        if m == "place_furn":
            sx,sy = self.snap_world(wx), self.snap_world(wy)
            item = self.add_furniture(self._pending_fid,
                                      sx, sy,
                                      sx+self._pending_dfw, sy+self._pending_dfh)
            if self.preview: self.canvas.delete(self.preview); self.preview=None
            self.mode.set("edit"); self.root.config(cursor="")
            if item:
                self._stack_on_top([item])
                self.select_single(item)
            return

        if m in ("place_door", "place_window"):
            w = self._nearest_wall(wx, wy, 40)
            if w is not None:
                otype = "door" if m == "place_door" else "window"
                op = self._new_opening(w, otype, self._snap_along(self._project_on_wall(w, wx, wy)[0]))
                if self.preview: self.canvas.delete(self.preview); self.preview = None
                self.select_single(op)
                self._schedule_3d_refresh()
            return

        if m == "draw_wall":
            sx,sy = self.snap_world(wx), self.snap_world(wy)
            if self.start is None:
                self.start=(sx,sy)
            else:
                x1,y1=self.start
                if abs(sx-x1)>abs(sy-y1): sy=y1
                else: sx=x1
                self.add_wall(x1,y1,sx,sy,
                              color=self.color.get(),width=self.thickness.get())
                self.start=None
                if self.preview: self.canvas.delete(self.preview); self.preview=None
                self._recompute_and_draw_rooms()
            return

        if m == "measure":
            sx,sy = self.snap_world(wx), self.snap_world(wy)
            if self.measure_start is None:
                self.measure_start = (sx,sy)
            else:
                x1,y1 = self.measure_start
                if shift:
                    if abs(sx-x1) > abs(sy-y1): sy = y1
                    else: sx = x1
                self.add_measurement(x1,y1,sx,sy)
                self.measure_start = None
                if self._measure_preview:
                    self.canvas.delete(self._measure_preview); self._measure_preview = None
                if self._measure_preview_text:
                    self.canvas.delete(self._measure_preview_text); self._measure_preview_text = None
            return

        if m == "draw_free":
            self._fh_points = [(wx,wy)]
            return

        if m in ("select","edit"):
            allow_handles = (m == "edit") and not ctrl and not shift
            cx_ev = self.canvas.canvasx(event.x)
            cy_ev = self.canvas.canvasy(event.y)

            if allow_handles and not self.multi_sel:
                for wall in self.walls:
                    for hk in ("h1_id","h2_id"):
                        a,b,c,d = self.canvas.coords(wall[hk])
                        if a<=cx_ev<=c and b<=cy_ev<=d:
                            self.select_single(wall)
                            self.drag_handle = "h1" if hk=="h1_id" else "h2"
                            return
                for furn in self.furniture:
                    if self.furniture_dimmed: break
                    for hn,hid in furn["handles"].items():
                        a,b,c,d = self.canvas.coords(hid)
                        if a<=cx_ev<=c and b<=cy_ev<=d:
                            self.select_single(furn); self.drag_handle=hn; return

            hit = self._hit_item(wx, wy)

            if shift and hit:
                self.multi_remove(hit)
                return

            if ctrl and hit:
                if hit in self.multi_sel:
                    self.multi_remove(hit)
                else:
                    self.multi_add(hit)
                return

            if hit:
                if self.multi_sel:
                    if hit in self.multi_sel:
                        self.drag_handle = "multi_move"
                        self._mdrag_start_wx = wx
                        self._mdrag_start_wy = wy
                        self._setup_multi_drag()
                        return
                    else:
                        self.deselect_all()
                self.select_single(hit)
                if m=="edit" and hit["kind"] in ("furniture","freehand","opening"):
                    self.drag_handle="move"
                return

            if not ctrl and not shift:
                self.deselect_all()
            self._rb_start = (wx, wy)

    def motion(self, event):
        wx,wy = self.event_world(event)
        m     = self.mode.get()

        if m=="draw_wall" and self.start:
            sx,sy=self.snap_world(wx),self.snap_world(wy); x1,y1=self.start
            if abs(sx-x1)>abs(sy-y1): sy=y1
            else: sx=x1
            if self.preview: self.canvas.delete(self.preview)
            self.preview=self.canvas.create_line(
                self.w2c(x1),self.w2c(y1),self.w2c(sx),self.w2c(sy),
                dash=(4,4), fill=self._ink(self.color.get()), width=self.thickness.get())

        elif m=="measure" and self.measure_start:
            sx,sy=self.snap_world(wx),self.snap_world(wy); x1,y1=self.measure_start
            shift = bool(event.state & 0x1)
            if shift:
                if abs(sx-x1)>abs(sy-y1): sy=y1
                else: sx=x1
            if self._measure_preview: self.canvas.delete(self._measure_preview)
            if self._measure_preview_text: self.canvas.delete(self._measure_preview_text)
            cx1,cy1,cx2,cy2 = self.w2c(x1),self.w2c(y1),self.w2c(sx),self.w2c(sy)
            col = self.C("measure")
            self._measure_preview = self.canvas.create_line(
                cx1,cy1,cx2,cy2, dash=(4,4), fill=col, width=2)
            dist = hypot(sx-x1, sy-y1)
            self._measure_preview_text = self.canvas.create_text(
                (cx1+cx2)/2, (cy1+cy2)/2-12, text=f"📐 {self.format_length(dist)}",
                font=("TkDefaultFont",8,"bold"), fill=col)

        elif m in ("place_door", "place_window"):
            self._place_opening_preview(wx, wy)

        elif m=="place_furn":
            sx,sy=self.snap_world(wx),self.snap_world(wy)
            sx2,sy2=sx+self._pending_dfw,sy+self._pending_dfh
            if self.preview: self.canvas.delete(self.preview)
            self.preview=self.canvas.create_rectangle(
                self.w2c(sx),self.w2c(sy),self.w2c(sx2),self.w2c(sy2),
                outline=self.C("accent"),dash=(4,4),width=2)

    def drag(self, event):
        m = self.mode.get()
        wx,wy = self.event_world(event)

        if m == "draw_free" and self._fh_points is not None:
            self._fh_points.append((wx,wy))
            coords=[]
            for (px,py) in self._fh_points:
                coords.append(self.w2c(px)); coords.append(self.w2c(py))
            if self.preview: self.canvas.delete(self.preview)
            if len(coords) >= 4:
                self.preview=self.canvas.create_line(
                    *coords, fill=self._ink(self.color.get()), width=self.thickness.get(),
                    smooth=True, splinesteps=12, capstyle="round", joinstyle="round")
            return

        if self._rb_start is not None and self.drag_handle is None:
            rx1,ry1=self._rb_start
            if self._rb_rect: self.canvas.delete(self._rb_rect)
            # Tk has no alpha colours (#rrggbbaa is an error), so the light
            # see-through fill is done with a sparse stipple pattern instead
            coords = (self.w2c(rx1),self.w2c(ry1),self.w2c(wx),self.w2c(wy))
            try:
                self._rb_rect = self.canvas.create_rectangle(
                    *coords, outline=self.C("accent"), fill=self.C("accent"), stipple="gray12",
                    dash=(3,3), width=1, tags="rubberband")
            except tk.TclError:   # platforms without stipple support (macOS)
                self._rb_rect = self.canvas.create_rectangle(
                    *coords, outline=self.C("accent"), fill="", dash=(3,3), width=1, tags="rubberband")
            return

        if m != "edit" or not self.drag_handle: return
        sx,sy = self.snap_world(wx), self.snap_world(wy)
        if getattr(self, "_furn_moved", None) is None:
            if self.drag_handle == "multi_move":
                cand = [e[0] for e in self._mdrag_origins if e[0]["kind"] == "furniture"]
            elif self.selected and self.selected["kind"] == "furniture":
                cand = [self.selected]
            else:
                cand = []
            # remember where they started, so a click without a real move
            # (or a resize) doesn't reorder a stack
            self._furn_moved = {"handle": self.drag_handle,
                                "items": [(it, (it["x1"], it["y1"], it["x2"], it["y2"])) for it in cand]}

        if self.drag_handle == "multi_move":
            dx = sx - self.snap_world(self._mdrag_start_wx)
            dy = sy - self.snap_world(self._mdrag_start_wy)
            for entry in self._mdrag_origins:
                it, kind = entry[0], entry[1]
                if kind == "points":
                    orig_points = entry[2]
                    it["points"] = [(ox+dx,oy+dy) for ox,oy in orig_points]
                    self._draw_freehand_canvas(it)
                    self._highlight_item(it, True)
                else:  
                    ox1,oy1,ox2,oy2 = entry[2],entry[3],entry[4],entry[5]
                    it["x1"]=ox1+dx; it["y1"]=oy1+dy
                    it["x2"]=ox2+dx; it["y2"]=oy2+dy
                    if it["kind"]=="wall":
                        self._refresh_wall(it)
                    elif it["kind"]=="measure":
                        self._draw_measure_canvas(it)
                        self._highlight_item(it, True)
                    else:
                        self._draw_furn_canvas(it)
                        for hid in it["handles"].values():
                            self.canvas.itemconfigure(hid,state="normal")
                        self._highlight_item(it, True)
            return

        if not self.selected: return
        item = self.selected
        h    = self.drag_handle

        if item["kind"]=="opening":
            if h=="move":
                w = item["wall"]
                item["pos"] = self._snap_along(self._project_on_wall(w, wx, wy)[0])
                self._clamp_openings(w)
                self._draw_opening(item, highlight=True)
            return

        if item["kind"]=="wall":
            if h=="h1": item["x1"],item["y1"]=sx,sy
            else:       item["x2"],item["y2"]=sx,sy
            self._refresh_wall(item)

        elif item["kind"]=="furniture":
            if h=="move":
                dx=sx-self.snap_world(self._drag_ox)
                dy=sy-self.snap_world(self._drag_oy)
                W=item["x2"]-item["x1"]; H=item["y2"]-item["y1"]
                # snap the corner itself, so a piece that was off the grid
                # lines up again as soon as it is moved
                item["x1"]=self.snap_world(self._drag_x1+dx); item["y1"]=self.snap_world(self._drag_y1+dy)
                item["x2"]=item["x1"]+W;     item["y2"]=item["y1"]+H
            else:
                if "l" in h: item["x1"]=sx
                if "r" in h: item["x2"]=sx
                if "t" in h: item["y1"]=sy
                if "b" in h: item["y2"]=sy
            self._draw_furn_canvas(item)
            for hid in item["handles"].values():
                self.canvas.itemconfigure(hid,state="normal")

        elif item["kind"]=="freehand":
            if h=="move":
                dx=sx-self.snap_world(self._drag_ox)
                dy=sy-self.snap_world(self._drag_oy)
                item["points"]=[(ox+dx,oy+dy) for ox,oy in self._drag_orig_points]
                self._draw_freehand_canvas(item)
                self._highlight_item(item, True)

    def release(self, event):
        wx,wy = self.event_world(event)

        if self.mode.get() == "draw_free" and self._fh_points is not None:
            pts = self._fh_points
            self._fh_points = None
            if self.preview:
                self.canvas.delete(self.preview); self.preview=None
            if len(pts) >= 2:
                self.add_freehand(pts, color=self.color.get(), width=self.thickness.get())
            return

        if self._rb_start is not None:
            if self._rb_rect:
                self.canvas.delete(self._rb_rect)
                self._rb_rect = None
            rx1,ry1 = self._rb_start
            rx2,ry2 = wx, wy
            self._rb_start = None
            bx1,bx2 = min(rx1,rx2), max(rx1,rx2)
            by1,by2 = min(ry1,ry2), max(ry1,ry2)
            if abs(bx2-bx1) > 4 or abs(by2-by1) > 4:
                hits = []
                for wall in self.walls:
                    wx1,wy1,wx2,wy2 = wall["x1"],wall["y1"],wall["x2"],wall["y2"]
                    if bx1<=min(wx1,wx2) and max(wx1,wx2)<=bx2 and                        by1<=min(wy1,wy2) and max(wy1,wy2)<=by2:
                        hits.append(wall)
                for furn in self.furniture:
                    if self.furniture_dimmed: continue
                    fx1,fy1=min(furn["x1"],furn["x2"]),min(furn["y1"],furn["y2"])
                    fx2,fy2=max(furn["x1"],furn["x2"]),max(furn["y1"],furn["y2"])
                    if bx1<=fx1 and fx2<=bx2 and by1<=fy1 and fy2<=by2:
                        hits.append(furn)
                for fh in self.freehand:
                    fx1,fy1,fx2,fy2 = self._freehand_bbox(fh)
                    if bx1<=fx1 and fx2<=bx2 and by1<=fy1 and fy2<=by2:
                        hits.append(fh)
                if hits:
                    self.deselect_all()
                    for h in hits:
                        self.multi_add(h, _skip_drag_setup=True)
                    self._setup_multi_drag()

        self.drag_handle = None
        info = getattr(self, "_furn_moved", None)
        self._furn_moved = None
        if info:
            moved = [it for it, bb in info["items"]
                     if (it["x1"], it["y1"], it["x2"], it["y2"]) != bb]
            if moved and info["handle"] in ("move", "multi_move"):
                self._stack_on_top(moved)
            elif moved and self._apply_gravity():
                self._redraw_all()
        self._recompute_and_draw_rooms()
        self._schedule_3d_refresh()

    def _highlight_item(self, item, on):
        if item["kind"] == "opening":
            self._draw_opening(item, highlight=on)
        elif item["kind"] == "wall":
            color = self.C("select") if on else self._ink(item["color"])
            self.canvas.itemconfigure(item["line_id"], fill=color)
        elif item["kind"] == "furniture":
            for cid in item.get("group", []):
                try:
                    self.canvas.itemconfigure(cid, outline=self.C("select") if on else "")
                except Exception:
                    pass
        elif item["kind"] == "freehand":
            color = self.C("select") if on else self._ink(item["color"])
            if item.get("line_id"):
                self.canvas.itemconfigure(item["line_id"], fill=color)
        elif item["kind"] == "measure":
            color = self.C("select") if on else self.C("measure")
            for k in ("line_id","t1_id","t2_id"):
                if item.get(k):
                    self.canvas.itemconfigure(item[k], fill=color)

    def _show_handles(self, item, on):
        state = "normal" if on else "hidden"
        if item["kind"] == "wall":
            self.canvas.itemconfigure(item["h1_id"], state=state)
            self.canvas.itemconfigure(item["h2_id"], state=state)
        elif item["kind"] == "furniture":
            for hid in item["handles"].values():
                self.canvas.itemconfigure(hid, state=state)

    def select_single(self, item):
        self.deselect_all()
        self.selected = item
        self._show_handles(item, True)
        if item["kind"] == "furniture":
            self._drag_x1=item["x1"]; self._drag_y1=item["y1"]
            self._drag_ox=(item["x1"]+item["x2"])/2
            self._drag_oy=(item["y1"]+item["y2"])/2
        elif item["kind"] == "freehand":
            bx1,by1,bx2,by2 = self._freehand_bbox(item)
            self._drag_ox=(bx1+bx2)/2
            self._drag_oy=(by1+by2)/2
            self._drag_orig_points=[tuple(p) for p in item["points"]]
            self._highlight_item(item, True)
        elif item["kind"] in ("measure", "opening"):
            self._highlight_item(item, True)

    def multi_add(self, item, _skip_drag_setup=False):
        if item in self.multi_sel: return
        if self.selected and self.selected not in self.multi_sel:
            self._show_handles(self.selected, False)
            self.multi_sel.append(self.selected)
            self.selected = None
        self.multi_sel.append(item)
        self._highlight_item(item, True)
        if not _skip_drag_setup:
            self._setup_multi_drag()

    def multi_remove(self, item):
        if item in self.multi_sel:
            self.multi_sel.remove(item)
            self._highlight_item(item, False)
            self._show_handles(item, False)
        if self.selected is item:
            self._show_handles(item, False)
            self.selected = None

    def _setup_multi_drag(self):
        origins = []
        for it in self.multi_sel:
            if it["kind"] == "opening":
                continue
            if it["kind"] == "freehand":
                origins.append((it, "points", [tuple(p) for p in it["points"]]))
            else:
                origins.append((it, "bbox", it["x1"],it["y1"],it["x2"],it["y2"]))
        self._mdrag_origins = origins

    def deselect_all(self):
        if self.selected:
            self._show_handles(self.selected, False)
            if self.selected["kind"] in ("freehand", "measure", "opening"):
                self._highlight_item(self.selected, False)
            self.selected = None
        for item in self.multi_sel:
            self._highlight_item(item, False)
            self._show_handles(item, False)
        self.multi_sel.clear()
        self.drag_handle = None
        if self._rb_rect:
            self.canvas.delete(self._rb_rect)
            self._rb_rect = None
        self._rb_start = None

    def deselect(self): self.deselect_all()
    def select(self, item): self.select_single(item)

    def delete_selected(self, event=None):
        targets = list(self.multi_sel) if self.multi_sel else                   ([self.selected] if self.selected else [])
        self.deselect_all()
        wall_removed = False
        for item in targets:
            if item["kind"]=="opening":
                for cid in item.get("ids", []): self.canvas.delete(cid)
                ops = item["wall"].get("openings", [])
                if item in ops: ops.remove(item)
            elif item["kind"]=="wall":
                for k in ("line_id","text_id","h1_id","h2_id"):
                    self.canvas.delete(item[k])
                for op in item.get("openings", []):
                    for cid in op.get("ids", []): self.canvas.delete(cid)
                if item in self.walls: self.walls.remove(item); wall_removed = True
            elif item["kind"]=="furniture":
                for cid in item["group"]: self.canvas.delete(cid)
                for hid in item["handles"].values(): self.canvas.delete(hid)
                for k in ("text","sz_text","rot_badge"):
                    if item.get(k): self.canvas.delete(item[k])
                if item in self.furniture: self.furniture.remove(item)
            elif item["kind"]=="freehand":
                if item.get("line_id"): self.canvas.delete(item["line_id"])
                if item in self.freehand: self.freehand.remove(item)
            elif item["kind"]=="measure":
                for k in ("line_id","text_id","t1_id","t2_id"):
                    if item.get(k): self.canvas.delete(item[k])
                if item in self.measurements: self.measurements.remove(item)
        if wall_removed:
            self._recompute_and_draw_rooms()
        if any(t["kind"] == "furniture" for t in targets) and self._apply_gravity():
            self._redraw_all()
        self._schedule_3d_refresh()

    # ═══════════════════════════════════════════════════════════════════════════
    #  Geometry logic
    # ═══════════════════════════════════════════════════════════════════════════

    def segdist(self,px,py,x1,y1,x2,y2):
        dx,dy=x2-x1,y2-y1
        if dx==dy==0: return 999
        t=((px-x1)*dx+(py-y1)*dy)/(dx*dx+dy*dy)
        t=max(0,min(1,t))
        return sqrt((px-x1-t*dx)**2+(py-y1-t*dy)**2)

    # ═══════════════════════════════════════════════════════════════════════════
    #  Local Space Rotated Furniture draw implementations (0..W, 0..H)
    # ═══════════════════════════════════════════════════════════════════════════

    def _draw_furniture_thumb(self, thumb, entry):
        dw, dh = entry["width"], entry["height"]
        TW,TH,PAD=56,44,4
        scale=min((TW-PAD*2)/dw,(TH-PAD*2)/dh)
        W,H=dw*scale,dh*scale
        proxy=RotatedDraw(thumb,TW/2,TH/2,W,H,0)
        self._render_furn_shape(proxy,0,0,W,H,entry)

    def _furn_sofa(self,c,x1,y1,x2,y2):
        ids=[]; W,H=x2-x1,y2-y1; bh=H*0.25
        ids.append(c.create_rectangle(x1,y1,x2,y1+bh,fill="#b0c4de",outline="#607090",width=1))
        ids.append(c.create_rectangle(x1,y1+bh,x2,y2,fill="#d0e4f8",outline="#607090",width=1))
        n=3 if W>150 else 2; seg=W/n
        for i in range(1,n): ids.append(c.create_line(x1+i*seg,y1+bh,x1+i*seg,y2,fill="#607090",width=1))
        arm=max(6,W*0.06)
        ids.append(c.create_rectangle(x1,y1+bh,x1+arm,y2,fill="#90aac8",outline="#607090",width=1))
        ids.append(c.create_rectangle(x2-arm,y1+bh,x2,y2,fill="#90aac8",outline="#607090",width=1))
        return ids

    def _furn_armchair(self,c,x1,y1,x2,y2):
        ids=[]; W,H=x2-x1,y2-y1; bh=H*0.28; arm=W*0.12
        ids.append(c.create_rectangle(x1,y1,x2,y1+bh,fill="#c8b4e0",outline="#6040a0",width=1))
        ids.append(c.create_rectangle(x1,y1+bh,x2,y2,fill="#e0d0f8",outline="#6040a0",width=1))
        ids.append(c.create_rectangle(x1,y1+bh,x1+arm,y2,fill="#b090d0",outline="#6040a0",width=1))
        ids.append(c.create_rectangle(x2-arm,y1+bh,x2,y2,fill="#b090d0",outline="#6040a0",width=1))
        return ids

    def _furn_coffee_table(self,c,x1,y1,x2,y2):
        ids=[]; p=min(6,(x2-x1)*0.1,(y2-y1)*0.1)
        ids.append(c.create_rectangle(x1,y1,x2,y2,fill="#f5deb3",outline="#8b6914",width=2))
        ids.append(c.create_rectangle(x1+p,y1+p,x2-p,y2-p,fill="",outline="#c8a020",width=1))
        return ids

    def _furn_tv_stand(self,c,x1,y1,x2,y2):
        ids=[]; p=4
        ids.append(c.create_rectangle(x1,y1,x2,y2,fill="#555",outline="#999",width=1))
        ids.append(c.create_rectangle(x1+p,y1+p,x2-p,y2-p,fill="#1a1a2e",outline="#777",width=1))
        return ids

    def _furn_tv(self,c,x1,y1,x2,y2):
        ids=[]; W,H=x2-x1,y2-y1
        ids.append(c.create_rectangle(x1,y1,x2,y2,fill="#161616",outline="#888",width=1))
        p=max(1,min(W,H)*0.18)
        ids.append(c.create_rectangle(x1+p,y1+p,x2-p,y2-p,fill="#1f3a66",outline="#6a86b8",width=1))
        if W>=H:
            gw=(W-2*p)*0.18
            ids.append(c.create_rectangle(x1+p+1,y1+p+1,x1+p+1+gw,y2-p-1,fill="#345f9e",outline=""))
        else:
            gh=(H-2*p)*0.18
            ids.append(c.create_rectangle(x1+p+1,y1+p+1,x2-p-1,y1+p+1+gh,fill="#345f9e",outline=""))
        return ids

    def _furn_stairs(self,c,x1,y1,x2,y2):
        ids=[]; W,H=x2-x1,y2-y1
        ids.append(c.create_rectangle(x1,y1,x2,y2,fill="#e8e4dc",outline="#8a8478",width=2))
        n_steps=max(4,int(round(H/20)))
        for i in range(1,n_steps):
            ly=y1+H*i/n_steps
            ids.append(c.create_line(x1,ly,x2,ly,fill="#a8a194",width=1))
        mx=(x1+x2)/2
        ids.append(c.create_line(mx,y2-H*0.08,mx,y1+H*0.10,
                                  fill="#555555",width=2,arrow="last"))
        return ids

    def _furn_spiral_stairs(self,c,x1,y1,x2,y2):
        ids=[]
        cx,cy=(x1+x2)/2,(y1+y2)/2
        rx,ry=(x2-x1)/2,(y2-y1)/2
        ids.append(c.create_oval(x1,y1,x2,y2,fill="#e8e4dc",outline="#8a8478",width=2))
        n=12
        for i in range(n):
            a=2*pi*i/n
            ex,ey=cx+rx*cos(a),cy+ry*sin(a)
            ids.append(c.create_line(cx,cy,ex,ey,fill="#a8a194",width=1))
        r=min(rx,ry)*0.15
        ids.append(c.create_oval(cx-r,cy-r,cx+r,cy+r,fill="#8a8478",outline=""))
        return ids

    def _furn_ladder(self,c,x1,y1,x2,y2):
        ids=[]; W,H=x2-x1,y2-y1
        rail=max(2,W*0.18)
        ids.append(c.create_rectangle(x1,y1,x1+rail,y2,fill="#b08968",outline="#6b4a2c",width=1))
        ids.append(c.create_rectangle(x2-rail,y1,x2,y2,fill="#b08968",outline="#6b4a2c",width=1))
        ecy=(y1+y2)/2
        bar_h=max(2,H*0.10)
        ids.append(c.create_rectangle(x1+rail,ecy-bar_h/2,x2-rail,ecy+bar_h/2,
                                       fill="#8b5e3c",outline="#6b4a2c",width=1))
        return ids

    def _furn_opening_door(self,c,x1,y1,x2,y2):
        return self._furn_door(c,x1,y1,x2,y2)

    def _furn_opening_window(self,c,x1,y1,x2,y2):
        W,H=x2-x1,y2-y1; my=(y1+y2)/2; e=W*0.12
        ids=[c.create_rectangle(x1,y1,x1+e,y2,fill="#555555",outline="#555555"),
             c.create_rectangle(x2-e,y1,x2,y2,fill="#555555",outline="#555555"),
             c.create_rectangle(x1+e,y1,x2-e,y2,fill="#d6ebfb",outline="#3a6fb0",width=1),
             c.create_line(x1+e,my,x2-e,my,fill="#3a6fb0",width=1)]
        return ids

    def _furn_door(self,c,x1,y1,x2,y2):
        ids=[]; W,H=x2-x1,y2-y1
        r=min(W,H)
        hx,hy=x1,y2   # hinge at the bottom-left corner of the footprint
        # wall opening: a frame line across the bottom, with short jamb ticks
        ids.append(c.create_line(x1,y2,x2,y2, fill="#8a8478", width=2))
        tick=max(3,r*0.06)
        ids.append(c.create_line(x1,y2,x1,y2-tick, fill="#8a8478", width=2))
        ids.append(c.create_line(x2,y2,x2,y2-tick, fill="#8a8478", width=2))
        # door leaf, drawn open (perpendicular to the wall)
        ids.append(c.create_line(hx,hy,hx,hy-r, fill="#6b4a2c", width=3))
        # swing arc from the closed position (along the wall) to open
        ids.append(c.create_arc(hx-r,hy-r,hx+r,hy+r, start=0, extent=90,
                                 style="arc", outline="#b0aa9c", width=1))
        return [i for i in ids if i is not None]

    def _furn_rect_table(self,c,x1,y1,x2,y2):
        ids=[]; W,H=x2-x1,y2-y1; leg=max(4,min(W,H)*0.08)
        ids.append(c.create_rectangle(x1,y1,x2,y2,fill="#faebd7",outline="#8b5e3c",width=2))
        for lx,ly in[(x1,y1),(x2-leg,y1),(x1,y2-leg),(x2-leg,y2-leg)]:
            ids.append(c.create_rectangle(lx,ly,lx+leg,ly+leg,fill="#8b5e3c",outline="#6b3e1c"))
        return ids

    def _furn_round_table(self,c,x1,y1,x2,y2):
        ids=[]; ecx,ecy=(x1+x2)/2,(y1+y2)/2; r=3
        ids.append(c.create_oval(x1,y1,x2,y2,fill="#faebd7",outline="#8b5e3c",width=2))
        ids.append(c.create_oval(ecx-r,ecy-r,ecx+r,ecy+r,fill="#8b5e3c",outline=""))
        return ids

    def _furn_chair(self,c,x1,y1,x2,y2):
        ids=[]; bh=(y2-y1)*0.25
        ids.append(c.create_rectangle(x1,y1,x2,y1+bh,fill="#c8a060",outline="#6b4020",width=1))
        ids.append(c.create_rectangle(x1,y1+bh,x2,y2,fill="#e8c888",outline="#6b4020",width=1))
        return ids

    def _furn_bed_double(self,c,x1,y1,x2,y2):
        ids=[]; W,H=x2-x1,y2-y1; hh=H*0.18; p=max(4,min(W,H)*0.04)
        ids.append(c.create_rectangle(x1,y1,x2,y2,fill="#deb887",outline="#8b5e3c",width=2))
        ids.append(c.create_rectangle(x1,y1,x2,y1+hh,fill="#a0522d",outline="#6b3e1c",width=1))
        ids.append(c.create_rectangle(x1+p,y1+hh+p,x2-p,y2-p,fill="#f5f5f5",outline="#ccc",width=1))
        mid=(x1+x2)/2
        ids.append(c.create_line(mid,y1+hh+p,mid,y1+hh+H*0.25,fill="#bbb",width=1))
        pp=p+2; ph=H*0.12
        for px1,px2 in[(x1+pp,mid-2),(mid+2,x2-pp)]:
            ids.append(c.create_oval(px1,y1+hh+pp,px2,y1+hh+pp+ph,fill="white",outline="#bbb",width=1))
        return ids

    def _furn_bed_single(self,c,x1,y1,x2,y2):
        ids=[]; W,H=x2-x1,y2-y1; hh=H*0.18; p=max(4,min(W,H)*0.04)
        ids.append(c.create_rectangle(x1,y1,x2,y2,fill="#deb887",outline="#8b5e3c",width=2))
        ids.append(c.create_rectangle(x1,y1,x2,y1+hh,fill="#a0522d",outline="#6b3e1c",width=1))
        ids.append(c.create_rectangle(x1+p,y1+hh+p,x2-p,y2-p,fill="#f5f5f5",outline="#ccc",width=1))
        ecx=(x1+x2)/2
        ids.append(c.create_oval(ecx-W/4,y1+hh+p+2,ecx+W/4,y1+hh+p+2+H*0.12,fill="white",outline="#bbb",width=1))
        return ids

    def _furn_wardrobe(self,c,x1,y1,x2,y2):
        ids=[]; mid=(x1+x2)/2; ky=(y1+y2)/2
        ids.append(c.create_rectangle(x1,y1,x2,y2,fill="#d2b48c",outline="#8b5e3c",width=2))
        ids.append(c.create_line(mid,y1,mid,y2,fill="#8b5e3c",width=1))
        for kx in[mid-8,mid+8]:
            ids.append(c.create_oval(kx-3,ky-3,kx+3,ky+3,fill="#555",outline="#333"))
        return ids

    def _furn_desk(self,c,x1,y1,x2,y2):
        ids=[]; W,H=x2-x1,y2-y1; mw=W*0.35; mh=H*0.4; ecx=(x1+x2)/2; ecy=y1+H*0.3
        ids.append(c.create_rectangle(x1,y1,x2,y2,fill="#e8d5b0",outline="#8b6914",width=2))
        ids.append(c.create_rectangle(ecx-mw/2,ecy-mh/2,ecx+mw/2,ecy+mh/2,fill="#1a1a2e",outline="#555",width=1))
        return ids

    def _furn_fridge(self,c,x1,y1,x2,y2):
        ids=[]; W,H=x2-x1,y2-y1; sy=y1+H*0.35; hx=x1+W*0.2; hw=max(4,W*0.12)
        ids.append(c.create_rectangle(x1,y1,x2,y2,fill="#e0e8f0",outline="#607080",width=2))
        ids.append(c.create_line(x1,sy,x2,sy,fill="#607080",width=1))
        ids.append(c.create_rectangle(hx,y1+6,hx+hw,sy-6,fill="#aaa",outline="#888"))
        ids.append(c.create_rectangle(hx,sy+6,hx+hw,y2-6,fill="#aaa",outline="#888"))
        return ids

    def _furn_stove(self,c,x1,y1,x2,y2):
        ids=[]; W,H=x2-x1,y2-y1; r=min(W,H)*0.18
        ids.append(c.create_rectangle(x1,y1,x2,y2,fill="#c0c0c0",outline="#606060",width=2))
        for bx,by in[(0.3,0.3),(0.7,0.3),(0.3,0.7),(0.7,0.7)]:
            ecx,ecy=x1+W*bx,y1+H*by
            ids.append(c.create_oval(ecx-r,ecy-r,ecx+r,ecy+r,fill="#1a1a2a",outline="#333"))
            ids.append(c.create_oval(ecx-r*.4,ecy-r*.4,ecx+r*.4,ecy+r*.4,fill="#555",outline=""))
        return ids

    def _furn_sink_kitchen(self,c,x1,y1,x2,y2):
        ids=[]; p=max(3,(y2-y1)*0.08); mid=(x1+x2)/2; ecx,ecy=(x1+x2)/2,(y1+y2)/2; r=3
        ids.append(c.create_rectangle(x1,y1,x2,y2,fill="#d0d8e0",outline="#607080",width=2))
        ids.append(c.create_rectangle(x1+p,y1+p,mid-2,y2-p,fill="#b0bcc8",outline="#708090",width=1))
        ids.append(c.create_rectangle(mid+2,y1+p,x2-p,y2-p,fill="#b0bcc8",outline="#708090",width=1))
        ids.append(c.create_oval(ecx-r,ecy-r,ecx+r,ecy+r,fill="#778899",outline=""))
        return ids

    def _furn_dishwasher(self,c,x1,y1,x2,y2):
        ids=[]; W,H=x2-x1,y2-y1; p=max(4,W*0.1)
        ids.append(c.create_rectangle(x1,y1,x2,y2,fill="#d8e0e8",outline="#607080",width=2))
        ids.append(c.create_rectangle(x1+p,y1+p,x2-p,y2-p,fill="#b8c8d8",outline="#708090",width=1))
        ids.append(c.create_rectangle(x1,y1,x2,y1+H*0.15,fill="#b0b8c0",outline="#607080",width=1))
        return ids

    def _furn_counter(self,c,x1,y1,x2,y2):
        ids=[]; p=4
        ids.append(c.create_rectangle(x1,y1,x2,y2,fill="#e8ddd0",outline="#8b7355",width=2))
        ids.append(c.create_rectangle(x1+p,y1+p,x2-p,y2-p,fill="",outline="#c8b89a",width=1))
        return ids

    def _furn_bathtub(self,c,x1,y1,x2,y2):
        ids=[]; W,H=x2-x1,y2-y1; p=max(6,min(W,H)*0.1)
        ids.append(c.create_rectangle(x1,y1,x2,y2,fill="#e8f0f8",outline="#6080a0",width=2))
        ids.append(c.create_oval(x1+p,y1+p,x2-p,y2-p,fill="#c0d8f0",outline="#80a0c0",width=1))
        ecx,ecy=(x1+x2)/2,y1+H*0.65; r=4; tx,ty=(x1+x2)/2,y1+8; tr=5
        ids.append(c.create_oval(ecx-r,ecy-r,ecx+r,ecy+r,fill="#8090a0",outline="#607080"))
        ids.append(c.create_oval(tx-tr,ty-tr,tx+tr,ty+tr,fill="#c0c0c0",outline="#888"))
        return ids

    def _furn_shower(self,c,x1,y1,x2,y2):
        ids=[]; W,H=x2-x1,y2-y1
        ids.append(c.create_rectangle(x1,y1,x2,y2,fill="#e8f4f8",outline="#6090a0",width=2))
        ids.append(c.create_arc(x1,y1,x1+W*1.4,y2,start=270,extent=90,style="arc",outline="#6090a0",width=2))
        ecx,ecy=x1+W*0.7,y1+H*0.25; r=6
        ids.append(c.create_oval(ecx-r,ecy-r,ecx+r,ecy+r,fill="#b0c0d0",outline="#607080"))
        dx,dy=x1+W*0.55,y1+H*0.7; dr=4
        ids.append(c.create_oval(dx-dr,dy-dr,dx+dr,dy+dr,fill="#8090a0",outline="#607080"))
        return [i for i in ids if i is not None]

    def _furn_toilet(self,c,x1,y1,x2,y2):
        ids=[]; W,H=x2-x1,y2-y1; th=H*0.3; p=max(4,min(W,H-th)*0.08)
        ids.append(c.create_rectangle(x1,y1,x2,y1+th,fill="#e0e8f0",outline="#6080a0",width=2))
        ids.append(c.create_oval(x1,y1+th,x2,y2,fill="#f0f4f8",outline="#6080a0",width=2))
        ids.append(c.create_oval(x1+p,y1+th+p,x2-p,y2-p,fill="",outline="#a0b0c0",width=1))
        return ids

    def _furn_sink_bath(self,c,x1,y1,x2,y2):
        ids=[]; p=max(3,min(x2-x1,y2-y1)*0.1); ecx,ecy=(x1+x2)/2,(y1+y2)/2; r=3
        ids.append(c.create_rectangle(x1,y1,x2,y2,fill="#d8e4ee",outline="#6080a0",width=2))
        ids.append(c.create_oval(x1+p,y1+p,x2-p,y2-p,fill="#b8cce0",outline="#8090a0",width=1))
        ids.append(c.create_oval(ecx-r,ecy-r,ecx+r,ecy+r,fill="#778899",outline=""))
        return ids

    def _furn_washing_machine(self,c,x1,y1,x2,y2):
        ids=[]; W,H=x2-x1,y2-y1; p=max(4,min(W,H)*0.1); ecx,ecy=(x1+x2)/2,(y1+y2)/2; ir=max(4,min(W,H)*0.12)
        ids.append(c.create_rectangle(x1,y1,x2,y2,fill="#dce4ec",outline="#607080",width=2))
        ids.append(c.create_oval(x1+p,y1+p,x2-p,y2-p,fill="#c0ccd8",outline="#708090",width=2))
        ids.append(c.create_oval(ecx-ir,ecy-ir,ecx+ir,ecy+ir,fill="#8090a0",outline=""))
        ids.append(c.create_rectangle(x1,y1,x2,y1+H*0.12,fill="#b0b8c0",outline="#607080",width=1))
        return ids

    # ═══════════════════════════════════════════════════════════════════════════
    #  Length input/output helpers for dialogs (cm internally)
    # ═══════════════════════════════════════════════════════════════════════════

    def _len_unit(self):
        return "cm" if self.units == "metric" else "in"

    def _cm_to_disp(self, cm):
        v = cm if self.units == "metric" else cm / 2.54
        return f"{v:.1f}".rstrip("0").rstrip(".")

    def _disp_to_cm(self, text):
        v = float(str(text).replace(",", ".").strip())
        return v if self.units == "metric" else v * 2.54

    def _props_dialog(self, title, fields, on_ok, checks=()):
        """fields: [(label, initial_cm, min_cm)], checks: [(label, initial_bool)].
        on_ok(values_cm, check_values) -> True closes the dialog."""
        dlg = tk.Toplevel(self.root)
        dlg.configure(bg=self.C("app_bg"))
        dlg.title(title)
        dlg.resizable(False, False)
        dlg.transient(self.root)
        frm = ttk.Frame(dlg, padding=12); frm.pack()
        vars_, cvars = [], []
        unit = self._len_unit()
        for i, fld in enumerate(fields):
            label, init = fld[0], fld[1]
            is_count = len(fld) > 3 and fld[3] == "count"
            ttk.Label(frm, text=f"{label}:" if is_count else f"{label} ({unit}):").grid(
                row=i, column=0, sticky="w", pady=3, padx=(0, 8))
            v = tk.StringVar(value=str(int(init)) if is_count else self._cm_to_disp(init))
            e = ttk.Entry(frm, textvariable=v, width=10)
            e.grid(row=i, column=1, sticky="w")
            if i == 0:
                e.focus_set(); e.select_range(0, "end")
            vars_.append(v)
        row = len(fields)
        for label, init in checks:
            cv = tk.BooleanVar(value=init)
            ttk.Checkbutton(frm, text=label, variable=cv).grid(row=row, column=0, columnspan=2,
                                                               sticky="w", pady=(4, 0))
            cvars.append(cv); row += 1

        def ok(_e=None):
            try:
                vals = [int(float(v.get().replace(",", ".")))
                        if (len(fld) > 3 and fld[3] == "count") else self._disp_to_cm(v.get())
                        for v, fld in zip(vars_, fields)]
                if any(val < fld[2] for val, fld in zip(vals, fields)):
                    raise ValueError
            except ValueError:
                messagebox.showwarning(self.get_text("error_title"),
                                       self.get_text("invalid_number"), parent=dlg)
                return
            if on_ok(vals, [cv.get() for cv in cvars]) is not False:
                dlg.destroy()
                self._schedule_3d_refresh()

        btns = ttk.Frame(frm); btns.grid(row=row, column=0, columnspan=2, sticky="e", pady=(10, 0))
        ttk.Button(btns, text=self.get_text("ok"), command=ok).pack(side="left", padx=2)
        ttk.Button(btns, text=self.get_text("cancel"), command=dlg.destroy).pack(side="left", padx=2)
        dlg.bind("<Return>", ok)
        dlg.bind("<Escape>", lambda e: dlg.destroy())
        dlg.grab_set()

    # ═══════════════════════════════════════════════════════════════════════════
    #  Wall / opening / furniture properties
    # ═══════════════════════════════════════════════════════════════════════════

    def _open_wall_defaults(self):
        def ok(vals, _checks):
            self.default_wall_height, self.default_wall_thickness = vals
            self._save_settings()
        self._props_dialog(self.get_text("wall_defaults").rstrip(".").rstrip("…"),
                           [(self.get_text("wall_height"), self.default_wall_height, 10),
                            (self.get_text("wall_thickness"), self.default_wall_thickness, 1)], ok)

    def _open_wall_props(self, w):
        def ok(vals, checks):
            targets = self.walls if checks[0] else [w]
            for t in targets:
                t["height"], t["thickness"] = vals
                self._clamp_openings(t)
            self._redraw_all()
        self._props_dialog(self.get_text("wall_props"),
                           [(self.get_text("wall_height"), self._wall_h(w), 10),
                            (self.get_text("wall_thickness"), self._wall_t(w), 1)], ok,
                           checks=[(self.get_text("apply_all_walls"), False)])

    def _open_opening_props(self, op):
        is_door = op["type"] == "door"
        title = self.get_text("opening_props_door" if is_door else "opening_props_window")
        fields = [(self.get_text("width"), op["width"], 10),
                  (self.get_text("height"), op["height"], 10)]
        if not is_door:
            fields.append((self.get_text("sill_height"), op["sill"], 0))
        checks = [(self.get_text("hinge_other_end"), bool(op["orient"] & 1)),
                  (self.get_text("swing_other_side"), bool(op["orient"] & 2))] if is_door else []

        def ok(vals, cks):
            op["width"], op["height"] = vals[0], vals[1]
            if not is_door:
                op["sill"] = vals[2]
            else:
                op["orient"] = (1 if cks[0] else 0) | (2 if cks[1] else 0)
            self._clamp_openings(op["wall"])
            self._draw_openings(op["wall"])
            if self.selected is op:
                self._draw_opening(op, highlight=True)
        self._props_dialog(title, fields, ok, checks)

    def _furn_3d_defaults(self, item):
        entry = self._furn_def(item["fid"]) or {}
        fn = entry.get("draw_fn", "")
        if fn in FURN_3D:
            h, z, _p = FURN_3D[fn]
        elif fn in ("stairs", "spiral_stairs", "ladder"):
            h, z = 0, 0
        else:
            h, z = entry.get("z_height") or CUSTOM_FURN_HEIGHT, entry.get("z_elev") or 0
        return h, z

    def _open_furn_props(self, item):
        entry = self._furn_def(item["fid"]) or {}
        if entry.get("draw_fn") in ("stairs", "spiral_stairs", "ladder", "door",
                                    "opening_door", "opening_window"):
            return  # height comes from the floor height
        dh, dz = self._furn_3d_defaults(item)
        old_z = item.get("z_elev", dz)

        def ok(vals, _c):
            item["z_height"] = vals[0]
            if abs(vals[1] - old_z) > 0.05:
                item["z_elev"] = vals[1]
                item["stack"] = False      # a height typed by hand stays where it is
            copies = []
            for _i in range(int(vals[2])):
                copies.append(self._copy_furniture(item))
            if copies:
                self._stack_on_top(copies, force=True)
            elif self._apply_gravity():
                self._redraw_all()
            else:
                self._draw_furn_canvas(item)
        self._props_dialog(self.get_text("furn_props"),
                           [(self.get_text("height_3d"), item.get("z_height", dh), 1),
                            (self.get_text("elevation"), old_z, 0),
                            (self.get_text("stack_copies"), 0, 0, "count")], ok)

    # ═══════════════════════════════════════════════════════════════════════════
    #  Stacking furniture
    # ═══════════════════════════════════════════════════════════════════════════

    NON_STACKING = ("stairs", "spiral_stairs", "ladder", "door", "opening_door", "opening_window")

    def _toggle_auto_stack(self):
        self.auto_stack = self.stack_var.get()
        self._save_settings()

    def _furn_z(self, it):
        dh, dz = self._furn_3d_defaults(it)
        return it.get("z_elev", dz), it.get("z_height", dh)

    def _furn_by_height(self, furniture=None):
        furn = self.furniture if furniture is None else furniture
        order = {id(it): i for i, it in enumerate(furn)}
        return sorted(furn, key=lambda it: (self._furn_z(it)[0], order[id(it)]))

    @staticmethod
    def _furn_overlap(a, b):
        """True when one piece sits over the other: the centre of either
        footprint lies inside the other footprint."""
        def inside(p, it):
            x1, x2 = sorted((it["x1"], it["x2"])); y1, y2 = sorted((it["y1"], it["y2"]))
            return x1 + 0.5 < p[0] < x2 - 0.5 and y1 + 0.5 < p[1] < y2 - 0.5
        ca = ((a["x1"] + a["x2"]) / 2, (a["y1"] + a["y2"]) / 2)
        cb = ((b["x1"] + b["x2"]) / 2, (b["y1"] + b["y2"]) / 2)
        return inside(ca, b) or inside(cb, a)

    def _stackable(self, it):
        return (self._furn_def(it["fid"]) or {}).get("draw_fn") not in self.NON_STACKING

    def _shelf_of(self, it):
        """Shelf settings of a piece (dict) or None for solid furniture."""
        sh = (self._furn_def(it["fid"]) or {}).get("shelf")
        return sh if isinstance(sh, dict) else None

    def _shelf_levels(self, it):
        """[(board top height, room above it or None)] relative to the shelf's
        own bottom. The top board has unlimited room above it."""
        sh = self._shelf_of(it)
        _z, h = self._furn_z(it)
        n = max(2, int(sh.get("levels", 4)))
        bottom = max(0.0, min(float(sh.get("bottom", 10)), h - 1))
        board = float(sh.get("board", SHELF_BOARD))
        tops = [bottom + (h - bottom) * i / (n - 1) for i in range(n)]
        tops[0] = max(tops[0], board)
        out = []
        for i, t in enumerate(tops):
            room = (tops[i + 1] - board - t) if i + 1 < n else None
            out.append((t, room))
        return out

    def _surfaces(self, it, others):
        """Places where `it` could rest: (height, max height of a piece there or None)."""
        surf, on_shelf = [], False
        ceilings = []                     # undersides of shelf boards above `it`
        for o in others:
            if not self._furn_overlap(it, o):
                continue
            oz, oh = self._furn_z(o)
            if self._shelf_of(o):
                on_shelf = True
                board = float(self._shelf_of(o).get("board", SHELF_BOARD))
                levels = self._shelf_levels(o)
                surf += [(oz + t, room) for (t, room) in levels]
                ceilings += [oz + t - board for (t, _r) in levels]
            else:
                surf.append((oz + oh, None))
        if not on_shelf:
            surf.append((0.0, None))      # the floor (not under a shelf's bottom board)
        # something standing on a piece inside a shelf must still fit under
        # the next board, so every surface gets the room up to that board
        out = []
        for (sz, room) in surf:
            above = [c - sz for c in ceilings if c > sz + 0.5]
            if above:
                room = min([room] + above) if room is not None else min(above)
            out.append((sz, room))
        return out

    def _space_free(self, it, z, h, others):
        for o in others:
            if self._shelf_of(o) or not self._furn_overlap(it, o):
                continue
            oz, oh = self._furn_z(o)
            if z < oz + oh - 0.5 and oz < z + h - 0.5:
                return False
        return True

    def _rest_height(self, it, others, new):
        """New/moved pieces take the lowest free spot they fit in (bottom shelf
        first, then on top of what is there); existing pieces just drop onto the
        nearest support below them."""
        h = self._furn_z(it)[1]
        valid = sorted(s for s, room in self._surfaces(it, others)
                       if (room is None or h <= room + 0.5) and self._space_free(it, s, h, others))
        cur = it.get("z_elev", 0) or 0
        if new:
            if valid:
                return valid[0]
        else:
            below = [s for s in valid if s <= cur + 0.5]
            if below:
                return below[-1]
            if valid:
                return valid[0]
        tops = [sum(self._furn_z(o)) for o in others if self._furn_overlap(it, o)]
        return max(tops) if tops else 0.0

    def _apply_gravity(self, furniture=None):
        """Let every auto-stacked piece rest on whatever is below it (another
        piece, a shelf board or the floor), lowest first. Pieces with a
        hand-typed height stay put. Returns True if anything moved."""
        changed = False
        settled = []
        for it in self._furn_by_height(furniture):
            if not self._stackable(it):
                continue
            if it.get("stack"):
                base = self._rest_height(it, settled, it.pop("_new", False))
                if abs((it.get("z_elev", 0) or 0) - base) > 0.01:
                    changed = True
                it["z_elev"] = base
            settled.append(it)
        return changed

    def _move_level(self, direction):
        """PageUp / PageDown: move the selected piece to the next free shelf /
        stack position above or below."""
        it = self.selected
        if not it or it.get("kind") != "furniture" or not self._stackable(it):
            return
        cur, h = self._furn_z(it)
        others = [o for o in self.furniture if o is not it and self._stackable(o)
                  and not (self._furn_overlap(it, o) and self._furn_z(o)[0] >= cur + h - 0.5)]
        cands = sorted(s for s, room in self._surfaces(it, others)
                       if (room is None or h <= room + 0.5) and self._space_free(it, s, h, others))
        nxt = [s for s in cands if s > cur + 0.5] if direction > 0 else \
              [s for s in cands if s < cur - 0.5]
        if not nxt:
            return
        it["z_elev"] = nxt[0] if direction > 0 else nxt[-1]
        it["stack"] = True
        self._apply_gravity()
        self._redraw_all()
        self.select_single(it)

    def _stack_on_top(self, items, force=False):
        """Called after placing/moving pieces: with Stack on they go on top
        of whatever they overlap, and pieces left floating drop down."""
        if self.auto_stack or force:
            for k, it in enumerate(items):
                if self._stackable(it):
                    it["stack"] = True
                    it["_new"] = True             # find the lowest free spot for it
                    it["z_elev"] = 1e9 + k        # sort above everything, keep order
        self._apply_gravity()
        self._redraw_all()

    def _update_stack_labels(self):
        """In a stack only the top piece shows its labels, as "Name ×N"."""
        if self.furniture_dimmed:
            return
        ordered = self._furn_by_height()
        for i, it in enumerate(ordered):
            if not it.get("text"):
                continue
            above = [o for o in ordered[i + 1:] if self._furn_overlap(it, o)]
            # things standing in a shelf: keep the name, hide the size line
            if any(self._shelf_of(o) and self._furn_overlap(it, o) for o in ordered[:i]):
                if it.get("sz_text"):
                    self.canvas.itemconfigure(it["sz_text"], state="hidden")
            if above:
                for k in ("text", "sz_text", "rot_badge"):
                    if it.get(k):
                        self.canvas.itemconfigure(it[k], state="hidden")
                continue
            below = [o for o in ordered[:i] if self._furn_overlap(it, o)
                     and o["fid"] == it["fid"]]
            if below:
                entry = self._furn_def(it["fid"]) or {}
                label = self.get_text(entry.get("label_key", it["fid"]))
                self.canvas.itemconfigure(it["text"], text=f"{label} ×{len(below) + 1}")

    def _copy_furniture(self, item):
        new = self.add_furniture(item["fid"], item["x1"], item["y1"], item["x2"], item["y2"],
                                 angle=item.get("angle", 0), draw=False)
        if new and "z_height" in item:
            new["z_height"] = item["z_height"]
        return new

    def _duplicate_selected(self, event=None):
        """Ctrl+D: copy the selected furniture onto itself - it lands on top."""
        if isinstance(event.widget, (tk.Entry, ttk.Entry)) if event else False:
            return
        if not self.selected or self.selected["kind"] != "furniture":
            return
        new = self._copy_furniture(self.selected)
        if new:
            self._stack_on_top([new], force=True)
            self.select_single(new)

    def _on_double_click(self, event):
        if self.mode.get() not in ("select", "edit"):
            return
        wx, wy = self.event_world(event)
        hit = self._hit_item(wx, wy)
        if not hit:
            return
        self.drag_handle = None
        if hit["kind"] == "wall":
            self._open_wall_props(hit)
        elif hit["kind"] == "opening":
            self._open_opening_props(hit)
        elif hit["kind"] == "furniture":
            shelf = hit if self._shelf_of(hit) else self._shelf_under(hit)
            if shelf is not None:
                self.open_shelf_view(shelf, select=None if shelf is hit else hit)
            else:
                self._open_furn_props(hit)

    # ═══════════════════════════════════════════════════════════════════════════
    #  Doors & windows (openings that belong to a wall)
    # ═══════════════════════════════════════════════════════════════════════════

    def _wall_h(self, w):
        return w.get("height") or self.default_wall_height

    def _wall_t(self, w):
        return w.get("thickness") or self.default_wall_thickness

    @staticmethod
    def _wall_len(w):
        return hypot(w["x2"] - w["x1"], w["y2"] - w["y1"])

    def _new_opening(self, w, otype, pos, width=None, height=None, sill=None, orient=0):
        d = DOOR_DEFAULTS if otype == "door" else WINDOW_DEFAULTS
        op = {"kind": "opening", "type": otype, "wall": w, "pos": pos,
              "width": width if width is not None else d["width"],
              "height": height if height is not None else d["height"],
              "sill": 0 if otype == "door" else (sill if sill is not None else d["sill"]),
              "orient": orient, "ids": []}
        w.setdefault("openings", []).append(op)
        self._clamp_openings(w)
        return op

    def _clamp_openings(self, w):
        L = self._wall_len(w)
        H = self._wall_h(w)
        for op in w.get("openings", []):
            op["width"] = max(10.0, min(op["width"], L))
            op["height"] = max(10.0, min(op["height"], H))
            op["sill"] = max(0.0, min(op["sill"], H - op["height"]))
            half = op["width"] / 2
            op["pos"] = max(half, min(op["pos"], L - half)) if L >= op["width"] else L / 2

    def _project_on_wall(self, w, wx, wy):
        """Distance along the wall (from its start) and perpendicular distance."""
        L = self._wall_len(w) or 1.0
        ux, uy = (w["x2"] - w["x1"]) / L, (w["y2"] - w["y1"]) / L
        dx, dy = wx - w["x1"], wy - w["y1"]
        s = dx * ux + dy * uy
        return s, abs(-dx * uy + dy * ux)

    def _nearest_wall(self, wx, wy, max_dist):
        best, best_w = max_dist, None
        for w in self.walls:
            d = self.segdist(wx, wy, w["x1"], w["y1"], w["x2"], w["y2"])
            if d < best:
                best, best_w = d, w
        return best_w

    def _snap_along(self, s):
        step = self.grid_step()
        return round(s / step) * step

    def _opening_geom(self, op):
        """Canvas-space points for an opening: A/B jamb points, u, n."""
        w = op["wall"]
        L = self._wall_len(w) or 1.0
        ux, uy = (w["x2"] - w["x1"]) / L, (w["y2"] - w["y1"]) / L
        a, b = op["pos"] - op["width"] / 2, op["pos"] + op["width"] / 2
        A = (self.w2c(w["x1"] + ux * a), self.w2c(w["y1"] + uy * a))
        B = (self.w2c(w["x1"] + ux * b), self.w2c(w["y1"] + uy * b))
        return A, B, (ux, uy), (-uy, ux)

    def _draw_opening(self, op, highlight=False):
        for cid in op.get("ids", []):
            self.canvas.delete(cid)
        op["ids"] = []
        w = op["wall"]
        if self._wall_len(w) < 1:
            return
        A, B, (ux, uy), (nx, ny) = self._opening_geom(op)
        ink = self.C("select") if highlight else self._ink(w["color"])
        wpx = w["width"]
        c = self.canvas
        ids = op["ids"]
        ids.append(c.create_line(*A, *B, fill=self.C("canvas_bg"), width=wpx + 1, capstyle="butt"))
        if op["type"] == "window":
            hw = wpx / 2 + 3
            poly = [A[0] + nx * hw, A[1] + ny * hw, B[0] + nx * hw, B[1] + ny * hw,
                    B[0] - nx * hw, B[1] - ny * hw, A[0] - nx * hw, A[1] - ny * hw]
            glass = "#d6ebfb" if self.theme == "light" else "#28405e"
            ids.append(c.create_polygon(poly, fill=glass, outline=ink, width=2))
            ids.append(c.create_line(*A, *B, fill=self.C("ink_blue") if not highlight else ink, width=1))
        else:
            tick = wpx / 2 + 3
            for P in (A, B):
                ids.append(c.create_line(P[0] - nx * tick, P[1] - ny * tick,
                                         P[0] + nx * tick, P[1] + ny * tick, fill=ink, width=2))
            hinge, other = (B, A) if op["orient"] & 1 else (A, B)
            side = -1 if op["orient"] & 2 else 1
            r = hypot(B[0] - A[0], B[1] - A[1])
            dx, dy = (other[0] - hinge[0]) / (r or 1), (other[1] - hinge[1]) / (r or 1)
            ex, ey = hinge[0] + nx * side * r, hinge[1] + ny * side * r
            ids.append(c.create_line(*hinge, ex, ey, fill=ink, width=2))
            arc = []
            for i in range(13):
                t = radians(90 * i / 12)
                arc += [hinge[0] + r * (cos(t) * dx + sin(t) * nx * side),
                        hinge[1] + r * (cos(t) * dy + sin(t) * ny * side)]
            ids.append(c.create_line(*arc, fill=self.C("text_muted"), width=1, dash=(3, 3)))
        for cid in ids:
            c.addtag_withtag("opening", cid)

    def _draw_openings(self, w):
        for op in w.get("openings", []):
            self._draw_opening(op, highlight=(op is self.selected or op in self.multi_sel))
        for key in ("text_id", "h1_id", "h2_id"):
            if w.get(key):
                self.canvas.tag_raise(w[key])

    def _hit_opening(self, wx, wy, tol=12):
        for w in reversed(self.walls):
            for op in w.get("openings", []):
                s, d = self._project_on_wall(w, wx, wy)
                if d <= max(tol, self._wall_t(w)) and abs(s - op["pos"]) <= op["width"] / 2:
                    return op
        return None

    def _place_opening_preview(self, wx, wy):
        if self.preview:
            self.canvas.delete(self.preview); self.preview = None
        w = self._nearest_wall(wx, wy, 40)
        if not w:
            return
        otype = "door" if self.mode.get() == "place_door" else "window"
        d = DOOR_DEFAULTS if otype == "door" else WINDOW_DEFAULTS
        L = self._wall_len(w)
        width = min(d["width"], L)
        s = max(width / 2, min(self._snap_along(self._project_on_wall(w, wx, wy)[0]), L - width / 2))
        fake = {"wall": w, "pos": s, "width": width}
        A, B, _u, _n = self._opening_geom(fake)
        self.preview = self.canvas.create_line(*A, *B, fill=self.C("accent"),
                                               width=w["width"] + 6, capstyle="butt")

    # ═══════════════════════════════════════════════════════════════════════════
    #  3D scene
    # ═══════════════════════════════════════════════════════════════════════════

    def _floor_elevations(self):
        elevs, z = [], 0.0
        for f in self.floors:
            elevs.append(z)
            hs = [self._wall_h(w) for w in f["walls"]]
            z += (max(hs) if hs else self.default_wall_height) + SLAB_THICKNESS
        return elevs, z

    def build_3d_faces(self, only_floor=None, furniture=True, subdivide=True, with_ground=False):
        col = THEME_3D.get(self.theme, THEME_3D["light"])
        palette = self.C("room_palette")
        elevs, top_z = self._floor_elevations()
        faces = []
        xs, ys = [], []
        for fi, floor in enumerate(self.floors):
            if only_floor is not None and fi != only_floor:
                continue
            z0 = elevs[fi]
            level_h = (elevs[fi + 1] if fi + 1 < len(elevs) else top_z) - z0
            walls = floor["walls"]
            for w in walls:
                xs += [w["x1"], w["x2"]]; ys += [w["y1"], w["y2"]]
            # ── floor surfaces from detected rooms
            try:
                rooms = compute_rooms([(w["x1"], w["y1"], w["x2"], w["y2"]) for w in walls])
            except Exception:
                rooms = []
            for ri, room in enumerate(rooms):
                poly = [(x, -y) for (x, y) in room["points"]]
                color = palette[ri % len(palette)]
                if fi == 0:
                    pts = [(x, y, z0 + 0.5) for (x, y) in poly]
                    a = sum(pts[i][0] * pts[(i + 1) % len(pts)][1] - pts[(i + 1) % len(pts)][0] * pts[i][1]
                            for i in range(len(pts)))
                    if a < 0:
                        pts.reverse()
                    faces.append(_face(pts, color, fi, phase=0, edge=False))
                else:
                    for f in _prism(poly, z0 - SLAB_THICKNESS, z0, col["slab"], fi,
                                    top_color=color, edge=False):
                        f["phase"] = 0 if f["normal"][2] > 0.9 else 1
                        faces.append(f)
            # ── walls with openings
            ends = [(w["x1"], w["y1"]) for w in walls] + [(w["x2"], w["y2"]) for w in walls]
            for w in walls:
                faces += self._wall_faces(w, z0, fi, ends, col, subdivide)
            # ── furniture
            if furniture:
                for item in floor["furniture"]:
                    faces += self._furniture_faces(item, z0, level_h, fi)
                    xs += [item["x1"], item["x2"]]; ys += [item["y1"], item["y2"]]
        if with_ground:
            if not xs:
                xs, ys = [0, 600], [0, 600]
            m = 300
            gx0, gx1, gy0, gy1 = min(xs) - m, max(xs) + m, min(ys) - m, max(ys) + m
            g = _face([(gx0, -gy1, 0), (gx1, -gy1, 0), (gx1, -gy0, 0), (gx0, -gy0, 0)],
                      col["ground"], -1, phase=0, edge=False)
            g["ground"] = True
            faces.append(g)
        return faces

    def _wall_faces(self, w, z0, level, ends, col, subdivide):
        L = self._wall_len(w)
        if L < 1:
            return []
        H, t = self._wall_h(w), self._wall_t(w)
        ux, uy = (w["x2"] - w["x1"]) / L, (w["y2"] - w["y1"]) / L
        nx, ny = -uy, ux

        def joined(px, py):
            n = sum(1 for (ex, ey) in ends if hypot(ex - px, ey - py) <= 3.0)
            return n >= 2   # the endpoint itself + at least one other wall
        e0 = t / 2 if joined(w["x1"], w["y1"]) else 0.0
        e1 = t / 2 if joined(w["x2"], w["y2"]) else 0.0

        def P(s, off):
            return (w["x1"] + ux * s + nx * off, -(w["y1"] + uy * s + ny * off))

        ops = sorted(w.get("openings", []), key=lambda o: o["pos"])
        pieces = []           # (s0, s1, zlo, zhi, cap_start, cap_end)
        cur = -e0
        for op in ops:
            a = max(cur, op["pos"] - op["width"] / 2)
            b = min(L, op["pos"] + op["width"] / 2)
            if b <= a:
                continue
            if a > cur:
                pieces.append((cur, a, 0, H, True, True))
            lo, hi = op["sill"], op["sill"] + op["height"]
            if lo > 0.5:
                pieces.append((a, b, 0, lo, False, False))
            if hi < H - 0.5:
                pieces.append((a, b, hi, H, False, False))
            cur = b
        if cur < L + e1:
            pieces.append((cur, L + e1, 0, H, True, True))

        faces = []
        for (s0, s1, zl, zh, _c0, _c1) in pieces:
            n = max(1, int(ceil((s1 - s0) / 120.0))) if subdivide else 1
            for k in range(n):
                a = s0 + (s1 - s0) * k / n
                b = s0 + (s1 - s0) * (k + 1) / n
                poly = [P(a, -t / 2), P(b, -t / 2), P(b, t / 2), P(a, t / 2)]
                # only the real ends of the wall get end faces; the sides of
                # door/window openings get separate jamb faces below
                caps = [True, k == n - 1 and abs(b - (L + e1)) < 0.01,
                        True, k == 0 and abs(a + e0) < 0.01]
                faces += _prism(poly, z0 + zl, z0 + zh, col["wall"], level,
                                top_color=col["wall_top"], caps=caps, edge=False,
                                bottom=zl > 0)
        # jambs: the inner side faces of each opening (only its own height)
        for op in ops:
            a = max(-e0, op["pos"] - op["width"] / 2)
            b = min(L + e1, op["pos"] + op["width"] / 2)
            zl, zh = z0 + op["sill"], z0 + op["sill"] + op["height"]
            for s, sgn in ((a, 1), (b, -1)):
                p1, p2 = P(s, -t / 2), P(s, t / 2)
                q = [(p1[0], p1[1], zl), (p2[0], p2[1], zl), (p2[0], p2[1], zh), (p1[0], p1[1], zh)]
                f = _face(q, col["wall"], level, edge=False)
                if f["normal"][0] * ux * sgn - f["normal"][1] * uy * sgn < 0:
                    f = _face(list(reversed(q)), col["wall"], level, edge=False)
                faces.append(f)
        # glass panes and door leaves
        for op in ops:
            a, b = op["pos"] - op["width"] / 2, op["pos"] + op["width"] / 2
            zl, zh = z0 + op["sill"], z0 + op["sill"] + op["height"]
            if op["type"] == "window":
                p1, p2 = P(a, 0), P(b, 0)
                f = _face([(p1[0], p1[1], zl), (p2[0], p2[1], zl), (p2[0], p2[1], zh), (p1[0], p1[1], zh)],
                          col["glass"], level, two_sided=True, glass=True)
                faces.append(f)
                faces += _prism([P(a, -t / 2 - 3), P(b, -t / 2 - 3), P(b, t / 2 + 3), P(a, t / 2 + 3)],
                                zl, zl + 2, "#f4f4f4", level)
            else:
                side = -1 if op["orient"] & 2 else 1
                hs, dirs = (b, -1) if op["orient"] & 1 else (a, 1)
                o0 = side * t / 2
                o1 = side * (t / 2 + op["width"])
                poly = [P(hs, o0), P(hs + dirs * 4, o0), P(hs + dirs * 4, o1), P(hs, o1)]
                faces += _prism(poly, zl, zh - 2, col["door"], level)
        return faces

    def _furniture_faces(self, item, z0, level_h, level):
        entry = self._furn_def(item["fid"]) or {}
        fn = entry.get("draw_fn", "")
        cx, cy = (item["x1"] + item["x2"]) / 2, (item["y1"] + item["y2"]) / 2
        W, H = abs(item["x2"] - item["x1"]), abs(item["y2"] - item["y1"])
        ang = item.get("angle", 0)
        if (ang // 90) % 2 == 1:
            W, H = H, W
        ca, sa = cos(radians(ang)), sin(radians(ang))

        def to3(lx, ly):
            dx, dy = lx - W / 2, ly - H / 2
            return (cx + dx * ca - dy * sa, -(cy + dx * sa + dy * ca))

        def rect(lx0, ly0, lx1, ly1):
            return [to3(lx0, ly0), to3(lx1, ly0), to3(lx1, ly1), to3(lx0, ly1)]

        faces = []
        if fn == "stairs":
            n = max(4, int(round(level_h / 18)))
            d = H / n
            for i in range(n):
                ly1 = H - i * d; ly0 = ly1 - d
                faces += _prism(rect(0, ly0, W, ly1), z0, z0 + level_h * (i + 1) / n,
                                "#e8e4dc", level, caps=None)
            return faces
        if fn == "spiral_stairs":
            n = max(10, int(round(level_h / 20)))
            faces += _prism([to3(*p) for p in _ellipse_pts(W * 0.44, H * 0.44, W * 0.56, H * 0.56, 10)],
                            z0, z0 + level_h, "#8a8478", level)
            for i in range(n):
                a0 = 2 * pi * i / n * 0.9; a1 = a0 + 2 * pi / n * 0.9
                pts = [(W / 2, H / 2)] + [(W / 2 + W / 2 * cos(a0 + (a1 - a0) * j / 3),
                                           H / 2 + H / 2 * sin(a0 + (a1 - a0) * j / 3)) for j in range(4)]
                zt = z0 + level_h * (i + 1) / n
                faces += _prism([to3(*p) for p in pts], zt - 5, zt, "#e8e4dc", level)
            return faces
        if fn == "ladder":
            rail = W * 0.18
            for lx0 in (0, W - rail):
                faces += _prism(rect(lx0, H * 0.4, lx0 + rail, H * 0.6), z0, z0 + level_h, "#b08968", level)
            for zr in range(25, int(level_h), 30):
                faces += _prism(rect(rail, H * 0.45, W - rail, H * 0.55), z0 + zr - 3, z0 + zr,
                                "#8b5e3c", level)
            return faces

        dh, dz = self._furn_3d_defaults(item)
        h = item.get("z_height", dh)
        zb = z0 + item.get("z_elev", dz)
        if h <= 0:
            return []
        if fn in FURN_3D:
            for (shape, fx0, fy0, fx1, fy1, fz0, fz1, color) in FURN_3D[fn][2]:
                lx0, ly0, lx1, ly1 = fx0 * W, fy0 * H, fx1 * W, fy1 * H
                if shape == "cyl":
                    poly = [to3(*p) for p in _ellipse_pts(lx0, ly0, lx1, ly1)]
                else:
                    poly = rect(lx0, ly0, lx1, ly1)
                faces += _prism(poly, zb + fz0 * h, zb + fz1 * h, color, level)
            return faces
        fill = entry.get("fill") or "#e0d3ae"
        if isinstance(entry.get("shelf"), dict):
            sh = entry["shelf"]
            post = min(float(sh.get("post", SHELF_POST)), W / 3, H / 3)
            board = float(sh.get("board", SHELF_BOARD))
            dark = self._darken_hex(fill, 0.7)
            levels = self._shelf_levels(item)
            # posts are split at every board so they sort correctly against the
            # things standing on the shelves (painter's algorithm)
            cuts = sorted(set([0.0, h] + [t for (t, _r) in levels if 0 < t < h]))
            for (lx, ly) in ((0, 0), (W - post, 0), (0, H - post), (W - post, H - post)):
                for za, zc in zip(cuts, cuts[1:]):
                    faces += _prism(rect(lx, ly, lx + post, ly + post), zb + za, zb + zc, dark, level)
            for (t, _room) in levels:
                faces += _prism(rect(0, 0, W, H), zb + t - board, zb + t, fill, level)
            return faces
        # custom user-drawn furniture: extrude every shape element
        ow, oh = entry.get("width") or W or 1, entry.get("height") or H or 1
        sx, sy = W / ow, H / oh
        shape = entry.get("shape") or ([{"type": "polygon", "points": entry["points"]}]
                                       if entry.get("points") else [])
        if not shape:
            return _prism(rect(0, 0, W, H), zb, zb + h, fill, level)
        for el in shape:
            if el.get("type") == "oval":
                ex, ey = el.get("cx", 0) * sx, el.get("cy", 0) * sy
                rx, ry = el.get("rx", 0) * sx, el.get("ry", 0) * sy
                poly = [to3(*p) for p in _ellipse_pts(ex - rx, ey - ry, ex + rx, ey + ry)]
            else:
                poly = [to3(px * sx, py * sy) for (px, py) in el.get("points", [])]
            faces += _prism(poly, zb, zb + h, fill, level)
        return faces

    def _convert_old_doors(self):
        """Older projects placed doors as furniture symbols. Turn every such
        symbol that sits on a wall into a real door opening in that wall."""
        for item in list(self.furniture):
            entry = self._furn_def(item["fid"]) or {}
            if item["fid"] != "door" and entry.get("draw_fn") not in ("door", "opening_door"):
                continue
            x1, y1, x2, y2 = item["x1"], item["y1"], item["x2"], item["y2"]
            W, H = abs(x2 - x1), abs(y2 - y1)
            ang = item.get("angle", 0)
            Wl, Hl = (H, W) if (ang // 90) % 2 == 1 else (W, H)
            cx, cy = (x1 + x2) / 2, (y1 + y2) / 2
            ca, sa = cos(radians(ang)), sin(radians(ang))

            def local(lx, ly):
                dx, dy = lx - Wl / 2, ly - Hl / 2
                return (cx + dx * ca - dy * sa, cy + dx * sa + dy * ca)
            # the 2D symbol: wall line along the local bottom edge, hinge at bottom-left
            hinge, jamb = local(0, Hl), local(Wl, Hl)
            mid = ((hinge[0] + jamb[0]) / 2, (hinge[1] + jamb[1]) / 2)
            w = self._nearest_wall(mid[0], mid[1], max(30.0, min(Wl, Hl) / 2))
            if w is None:
                continue
            s_h = self._project_on_wall(w, *hinge)[0]
            s_j = self._project_on_wall(w, *jamb)[0]
            L = self._wall_len(w) or 1.0
            nx, ny = -(w["y2"] - w["y1"]) / L, (w["x2"] - w["x1"]) / L
            side = (cx - mid[0]) * nx + (cy - mid[1]) * ny
            orient = (1 if s_h > s_j else 0) | (2 if side < 0 else 0)
            self._new_opening(w, "door", (s_h + s_j) / 2, width=max(30.0, abs(s_j - s_h)),
                              orient=orient)
            self.furniture.remove(item)

    def _shelf_under(self, item):
        """The shelf unit a piece is standing in (or on), if any."""
        z = self._furn_z(item)[0]
        for o in self.furniture:
            if o is not item and self._shelf_of(o) and self._furn_overlap(item, o) \
                    and self._furn_z(o)[0] <= z + 0.5:
                return o
        return None

    def open_shelf_view(self, shelf, select=None):
        sv = getattr(self, "shelf_view", None)
        if sv and sv.exists():
            if sv.shelf is shelf:
                sv.sel = select or sv.sel
                sv.win.lift(); sv.refresh()
                return
            sv.close()
        self.shelf_view = ShelfView(self, shelf, select)

    def open_3d_view(self):
        if getattr(self, "view3d", None) and self.view3d.exists():
            self.view3d.win.lift()
            self.view3d.rebuild()
            return
        self.view3d = View3D(self)

    def _schedule_3d_refresh(self):
        v = getattr(self, "view3d", None)
        if not v or not v.exists():
            return
        if getattr(self, "_3d_after", None):
            try:
                self.root.after_cancel(self._3d_after)
            except tk.TclError:
                pass
        self._3d_after = self.root.after(250, self._do_3d_refresh)

    def _do_3d_refresh(self):
        self._3d_after = None
        v = getattr(self, "view3d", None)
        if v and v.exists():
            v.rebuild()

    def export_obj(self):
        path = filedialog.asksaveasfilename(
            title=self.get_text("export_obj"), defaultextension=".obj",
            filetypes=[(self.get_text("obj_files"), "*.obj"), (self.get_text("all_files"), "*.*")])
        if not path:
            return
        try:
            faces = self.build_3d_faces(furniture=True, subdivide=False, with_ground=False)
            mtl = write_obj(path, faces)
            messagebox.showinfo(self.get_text("exported_title"),
                                f"{self.get_text('exported_msg')}\n{path}\n{mtl}")
        except OSError as e:
            messagebox.showerror(self.get_text("error_title"), str(e))

    # ═══════════════════════════════════════════════════════════════════════════
    #  Save / Load (always in world coords)
    # ═══════════════════════════════════════════════════════════════════════════

    def _floor_to_dict(self, floor):
        return {
            "walls":[{"x1":w["x1"],"y1":w["y1"],"x2":w["x2"],"y2":w["y2"],
                       "color":w["color"],"width":w["width"],
                       "height":self._wall_h(w),"thickness":self._wall_t(w),
                       "openings":[{k: op[k] for k in ("type","pos","width","height","sill","orient")}
                                   for op in w.get("openings", [])]}
                      for w in floor["walls"]],
            "furniture":[dict({"fid":f["fid"],"x1":f["x1"],"y1":f["y1"],
                           "x2":f["x2"],"y2":f["y2"],"angle":f["angle"]},
                           **{k: f[k] for k in ("z_height","z_elev","stack") if k in f})
                         for f in floor["furniture"]],
            "freehand":[{"points":[list(p) for p in fh["points"]],
                          "color":fh["color"],"width":fh["width"]}
                        for fh in floor["freehand"]],
            "measurements":[{"x1":m["x1"],"y1":m["y1"],"x2":m["x2"],"y2":m["y2"]}
                             for m in floor["measurements"]],
        }

    def save_json(self):
        filetypes_list = [
            (self.get_text("json_files"), "*.json"),
            (self.get_text("all_files"), "*.*")
        ]
        path=filedialog.asksaveasfilename(title=self.get_text("save_proj"),
            defaultextension=".json",
            filetypes=filetypes_list)
        if not path: return
        data={
            "grid_val": self.grid_val_var.get(),
            "units": self.units,
            "language": self.language,
            "current_floor": self.current_floor,
            "floors": [self._floor_to_dict(f) for f in self.floors],
        }
        try:
            with open(path,"w",encoding="utf-8") as fp: json.dump(data,fp,indent=2)
            messagebox.showinfo(self.get_text("saved_title"),f"{self.get_text('saved_msg')}\n{path}")
        except OSError as e: messagebox.showerror(self.get_text("error_title"),str(e))

    def load_json(self):
        filetypes_list = [
            (self.get_text("json_files"), "*.json"),
            (self.get_text("all_files"), "*.*")
        ]
        path=filedialog.askopenfilename(title=self.get_text("load_proj"),
            filetypes=filetypes_list)
        if not path: return
        try:
            with open(path,"r",encoding="utf-8") as fp: data=json.load(fp)
        except (OSError,json.JSONDecodeError) as e:
            messagebox.showerror(self.get_text("error_title"),str(e)); return

        self.canvas.delete("all")
        self.selected=None; self.multi_sel.clear()

        # Restore layout settings & preferences
        self.units = data.get("units", "metric")
        self.language = self._valid_language(data.get("language", self.language))
        
        self.unit_var.set(self.units)
        self.lang_var.set(self.language)
        self.root.title(self.get_text("title"))

        gv = data.get("grid_val", 20 if self.units == "metric" else 12)
        self.grid_val_var.set(gv)

        self._build_floor_row_container()
        self._build_toolbar()
        self._build_main_area()

        # Load floor data lists
        floors_data = data.get("floors")
        if floors_data is None:
            floors_data = [{
                "walls": data.get("walls",[]),
                "furniture": data.get("furniture",[]),
                "freehand": data.get("freehand",[]),
                "measurements": data.get("measurements",[]),
            }]

        self.floors = [self._new_floor_data() for _ in floors_data]
        for floor, fd in zip(self.floors, floors_data):
            self.walls, self.furniture, self.freehand, self.measurements = \
                floor["walls"], floor["furniture"], floor["freehand"], floor["measurements"]
            for w in fd.get("walls",[]):
                self.add_wall(w["x1"],w["y1"],w["x2"],w["y2"],
                              color=w.get("color","black"),width=w.get("width",4),
                              draw=False, height=w.get("height"), thickness=w.get("thickness"),
                              openings=w.get("openings"))
            for f in fd.get("furniture",[]):
                it = self.add_furniture(f["fid"],f["x1"],f["y1"],f["x2"],f["y2"],
                                        angle=f.get("angle",0), draw=False)
                if it:
                    for k in ("z_height","z_elev","stack"):
                        if k in f: it[k] = f[k]
            self._convert_old_doors()
            for fh in fd.get("freehand",[]):
                pts=[tuple(p) for p in fh["points"]]
                self.add_freehand(pts, color=fh.get("color","black"),
                                  width=fh.get("width",2), draw=False)
            for m in fd.get("measurements",[]):
                self.add_measurement(m["x1"],m["y1"],m["x2"],m["y2"], draw=False)

        self.current_floor = data.get("current_floor", 0)
        if not (0 <= self.current_floor < len(self.floors)):
            self.current_floor = 0
        active = self.floors[self.current_floor]
        self.walls, self.furniture, self.freehand, self.measurements = \
            active["walls"], active["furniture"], active["freehand"], active["measurements"]

        self._rebuild_floor_buttons()
        self.floor_var.set(self.current_floor)
        self._redraw_all()


def _install_error_log(root):
    """.pyw programs have no console, so errors would vanish silently. Write
    them to error.log next to the program and tell the user once."""
    import traceback
    shown = {"done": False}

    def handler(exc, val, tb):
        text = "".join(traceback.format_exception(exc, val, tb))
        path = os.path.join(APP_DIR, "error.log")
        try:
            with open(path, "a", encoding="utf-8") as fp:
                fp.write(time.strftime("\n=== %Y-%m-%d %H:%M:%S ===\n") + text)
        except OSError:
            path = "(error.log could not be written)"
        print(text, file=sys.stderr)
        if not shown["done"]:
            shown["done"] = True
            try:
                messagebox.showerror("Error", f"{val}\n\n{path}")
            except tk.TclError:
                pass
    root.report_callback_exception = handler


if __name__ == "__main__":
    root=tk.Tk()
    _install_error_log(root)
    root.withdraw()                      # main window stays hidden behind the splash
    root.geometry("1600x950")
    try:
        splash = Splash(root, splash_texts())
    except Exception as e:               # a splash problem must never stop the program
        print(f"[splash] {e}", file=sys.stderr)
        splash = None
    App(root, splash)
    if splash:
        try:
            splash.finish()
        except Exception as e:
            print(f"[splash] {e}", file=sys.stderr)
    root.deiconify()
    root.lift()
    root.mainloop()