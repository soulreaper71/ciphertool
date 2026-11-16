import customtkinter as ctk
import tkinter as tk
from tkinter import ttk
from tkinter import font as tkfont
import threading
import time
import sys
import re

widget_scale = 1.2

ctk.set_appearance_mode("system")
ctk.deactivate_automatic_dpi_awareness()
ctk.set_widget_scaling(widget_scale)

root = ctk.CTk()

root_width = 700
root_height = 900

x_root = root.winfo_screenwidth()
horizontal_pos_root = int(x_root/2-root_width/2)


# ---------- fonts ----------

def pick_font(*names):
    # first family that is really installed is used, otherwise use the system default
    installed = {family.lower() for family in tkfont.families(root)}
    for name in names:
        if name.lower() in installed:
            return name
    return tkfont.nametofont("TkDefaultFont").actual("family")


serif_fallbacks = ("Georgia", "Times New Roman", "DejaVu Serif", "Liberation Serif")

fonts = {
    "title": pick_font("Constantine", *serif_fallbacks),
    "splash": pick_font("Praetorium BB", *serif_fallbacks),
    "card": pick_font("Castelforte", *serif_fallbacks),
    "mono": pick_font("Consolas", "DejaVu Sans Mono", "Courier New", "Liberation Mono", "Menlo"),
}


def ui_font(kind, size, weight="normal"):
    return (fonts[kind], size, weight)


# ---------- colours ----------
# every pair is (light mode, dark mode)

palette = {
    "window": ("#FFF9D6", "#2B2D42"),
    "panel": ("#FAF1CA", "#313342"),
    "text": ("#7F2122", "#F4D03F"),
    "hover_fill": ("#2B2D42", "#FFF9D6"),
    "hover_text": ("#FACD1E", "#7F2122"),
    "hover_border": ("#F4D03F", "#7F2122"),
    "bar_hover": ("#5D6D7E", "#FAF1CA"),
    "bar_hover_text": ("#F4D03F", "#D32929"),
    "toggle_hover_text": ("#F4D03F", "#FACD1E"),
    "selected": ("#FACD1E", "#7F2122"),
    "placeholder": ("#5D6D7E", "#5D6D7E"),
    "error": ("#D32929", "#FF6B6B"),
}


def pick_cursor(*names):
    for name in names:
        try:
            probe = tk.Label(root, cursor=name)
            probe.destroy()
            return name
        except tk.TclError:
            pass
    return "arrow"


grip_cursor = pick_cursor("size_nw_se", "bottom_right_corner", "resizebottomright", "sizing")


# ---------- cipher logic ----------

alphabet = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
lower = alphabet.lower()
playfair_letters = alphabet.replace("J", "")

# english letter frequencies in percent, A to Z
english_freq = (
    8.167, 1.492, 2.782, 4.253, 12.702, 2.228, 2.015, 6.094, 6.966, 0.153,
    0.772, 4.025, 2.406, 6.749, 7.507, 1.929, 0.095, 5.987, 6.327, 9.056,
    2.758, 0.978, 2.360, 0.150, 1.974, 0.074,
)
# same numbers as fractions so the scoring code can be used directly
expected = tuple(f / 100 for f in english_freq)

# common keywords tried first when solving vigenere
keywords = (
    "KEY", "LOCK", "CODE", "CIPHER", "SECRET", "PASSWORD", "ADMIN", "LEMON",
    "ORANGE", "APPLE", "BANANA", "GRAPE", "MANGO", "PEACH", "CHERRY", "MELON",
    "JULIUS", "CAESAR", "ROME", "ROMAN", "EMPEROR", "AUGUSTUS", "BRUTUS",
    "CICERO", "LATIN", "ENIGMA", "TURING", "CRYPTO", "HIDDEN", "PUZZLE",
    "RIDDLE", "MYSTERY", "SPY", "AGENT", "BOND", "SHADOW", "NIGHT", "MIDNIGHT",
    "MOON", "STAR", "SUN", "SKY", "RAIN", "STORM", "THUNDER", "OCEAN", "RIVER",
    "MOUNTAIN", "FOREST", "TREE", "FLOWER", "GARDEN", "SUMMER", "WINTER",
    "SPRING", "AUTUMN", "DRAGON", "KNIGHT", "KING", "QUEEN", "PRINCE", "CASTLE",
    "SWORD", "SHIELD", "WIZARD", "MAGIC", "TIGER", "LION", "EAGLE", "WOLF",
    "FALCON", "RAVEN", "HORSE", "MONKEY", "ZEBRA", "PYTHON", "JAVA", "CODER",
    "LINUX", "COMPUTER", "SCHOOL", "STUDENT", "TEACHER", "HELLO", "WORLD",
    "FRIEND", "FAMILY", "HOME", "HOUSE", "MONEY", "GOLD", "SILVER", "DIAMOND",
    "TREASURE", "PIRATE", "ABC", "TEST", "EXAMPLE", "DEFAULT", "MASTER",
    "GUEST", "ALPHA", "BETA", "GAMMA", "DELTA", "OMEGA", "SIGMA", "VIGENERE",
    "PLAYFAIR", "ATBASH", "KEYWORD", "SECURITY", "WHISPER", "FREEDOM", "VICTORY",
)

disallowed = re.compile(r"[^A-Za-z0-9\s]")
non_letter = re.compile(r"[^A-Za-z]+")

caesar_tables = {}
playfair_tables = {}


def sanitise(text):
    # keep only letters, digits and whitespace
    return disallowed.sub("", text)


def clean_key(key):
    cleaned = non_letter.sub("", key).upper()
    if not cleaned:
        raise ValueError("Key must contain at least one letter")
    return cleaned


def split_text(text):
    letters = non_letter.sub("", text)
    marks = []
    removed = 0
    for m in non_letter.finditer(text):
        run = m.group()
        marks.append((m.start() - removed, run))
        removed += len(run)
    return letters, marks


def merge_text(out, marks, place=None, count=0):
    parts = []
    last = 0
    for before, run in marks:
        if place is None:
            target = before
        elif before == 0:
            target = 0
        elif before == count:
            target = len(out)
        else:
            target = place[before - 1] + 1
        parts.append(out[last:target])
        parts.append(run)
        last = target
    parts.append(out[last:])
    return "".join(parts)


# ---------- caesar ----------

def caesar_table(shift):
    table = caesar_tables.get(shift)
    if table is None:
        table = str.maketrans(
            alphabet + lower,
            alphabet[shift:] + alphabet[:shift] + lower[shift:] + lower[:shift],
        )
        caesar_tables[shift] = table
    return table


def caesar(text, shift, decode=False):
    try:
        shift = int(shift)
    except (TypeError, ValueError):
        raise ValueError("Caesar shift must be a whole number") from None
    if decode:
        shift = -shift
    shift %= 26
    clean = sanitise(text)
    if shift == 0:
        return clean
    return clean.translate(caesar_table(shift))


# ---------- atbash ----------

atbash_table = str.maketrans(alphabet + lower, alphabet[::-1] + lower[::-1])

def atbash(text, decode=False):
    return sanitise(text).translate(atbash_table)

# ---------- vigenere ----------

def vigenere_apply(clean, key, decode):
    letters, marks = split_text(clean)
    if not letters:
        return clean
    size = len(key)
    out = list(letters)
    for j in range(min(size, len(letters))):
        shift = ord(key[j]) - 65
        if decode:
            shift = -shift
        out[j::size] = letters[j::size].translate(caesar_table(shift % 26))
    return merge_text("".join(out), marks)


def vigenere(text, key, decode=False):
    return vigenere_apply(sanitise(text), clean_key(key), decode)


# ---------- playfair ----------

def playfair_grid(key):
    return tuple(dict.fromkeys(key.replace("J", "I") + playfair_letters))


def playfair_table(key, decode):
    cache_key = (key, decode)
    table = playfair_tables.get(cache_key)
    if table is None:
        if len(playfair_tables) >= 64:
            playfair_tables.clear()
        grid = playfair_grid(key)
        pos = {ch: divmod(i, 5) for i, ch in enumerate(grid)}
        step = -1 if decode else 1
        table = {}
        for a in grid:
            r1, c1 = pos[a]
            for b in grid:
                r2, c2 = pos[b]
                if r1 == r2:
                    pair = grid[r1 * 5 + (c1 + step) % 5] + grid[r2 * 5 + (c2 + step) % 5]
                elif c1 == c2:
                    pair = grid[((r1 + step) % 5) * 5 + c1] + grid[((r2 + step) % 5) * 5 + c2]
                else:
                    pair = grid[r1 * 5 + c2] + grid[r2 * 5 + c1]
                table[a + b] = pair
        playfair_tables[cache_key] = table
    return table


def playfair_pairs(letters):
    padded = []
    place = []
    i = 0
    total = len(letters)
    while i < total:
        a = letters[i]
        b = letters[i + 1] if i + 1 < total else ""
        place.append(len(padded))
        if b and b != a:
            place.append(len(padded) + 1)
            padded += (a, b)
            i += 2
        else:
            padded += (a, "Q" if a == "X" else "X")
            i += 1
    return "".join(padded), place


def playfair(text, key, decode=False):
    key = clean_key(key)
    clean = sanitise(text)
    letters, marks = split_text(clean)
    # playfair has no J, so it gets merged into I
    letters = letters.upper().replace("J", "I")
    count = len(letters)
    if count == 0:
        return clean
    if decode:
        if count % 2:
            raise ValueError("Playfair ciphertext must have an even number of letters")
        padded, place = letters, None
    else:
        padded, place = playfair_pairs(letters)
    table = playfair_table(key, decode)
    out = "".join([table[padded[i:i + 2]] for i in range(0, len(padded), 2)])
    return merge_text(out, marks, place, count)


# ---------- solver helpers ----------

def letter_counts(letters):
    return tuple([letters.count(ch) for ch in alphabet])


def chi_squared(counts, total, shift):
    chi = 0.0
    for i in range(26):
        want = total * expected[i]
        diff = counts[(i + shift) % 26] - want
        chi += diff * diff / want
    return chi


def best_shift(counts, total):
    return min(range(26), key=lambda s: chi_squared(counts, total, s))


def index_of_coincidence(counts, total):
    return sum(c * (c - 1) for c in counts) / (total * (total - 1))


def shortest_repeat(key):
    # avoids double counting key
    length = len(key)
    for p in range(1, length // 2 + 1):
        if length % p == 0 and key[:p] * (length // p) == key:
            return key[:p]
    return key


def solver_input(text):
    clean = sanitise(text)
    letters = non_letter.sub("", clean).upper()
    if not letters:
        raise ValueError("No letters to solve")
    return clean, letters


# ---------- solvers ----------
# both return a list of (score, key, plaintext), best first, lower score is better

def caesar_solve(text, top=5, report=None, should_cancel=None):
    clean, letters = solver_input(text)
    total = len(letters)
    counts = letter_counts(letters)
    scored = []
    for shift in range(26):
        if should_cancel and should_cancel():
            break
        score = chi_squared(counts, total, shift) / total
        scored.append((score, shift))
        if report:
            report((shift + 1) / 26, shift, score)
    scored.sort()
    results = []
    for score, shift in scored[:max(1, int(top))]:
        results.append((score, shift, clean.translate(caesar_table((-shift) % 26))))
    return results


def vigenere_solve(text, top=5, max_key_len=16, wordlist=keywords,
                   top_lengths=3, report=None, should_cancel=None):
    clean, letters = solver_input(text)
    total = len(letters)
    column_cache = {}

    def columns(length):
        cols = column_cache.get(length)
        if cols is None:
            chunks = [letters[j::length] for j in range(length)]
            cols = tuple([(letter_counts(c), len(c)) for c in chunks])
            column_cache[length] = cols
        return cols

    def score_key(key):
        score = 0.0
        for (counts, size), ch in zip(columns(len(key)), key):
            if size:
                score += chi_squared(counts, size, ord(ch) - 65)
        return score / total

    candidates = {}

    words = [w for w in dict.fromkeys(wordlist) if len(w) <= total]
    for done, word in enumerate(words, 1):
        if should_cancel and should_cancel():
            break
        key = shortest_repeat(word)
        if key not in candidates:
            candidates[key] = score_key(key)
            if report:
                report(0.7 * done / len(words), key, candidates[key])

    if not (should_cancel and should_cancel()):
        longest = min(int(max_key_len), total // 6)
        ic_by_length = {}
        for length in range(1, longest + 1):
            ics = [index_of_coincidence(c, size) for c, size in columns(length) if size > 1]
            if ics:
                ic_by_length[length] = sum(ics) / len(ics)
        likely = sorted(ic_by_length, key=ic_by_length.get, reverse=True)[:top_lengths]
        for step, length in enumerate(likely, 1):
            if should_cancel and should_cancel():
                break
            key = "".join([alphabet[best_shift(c, size)] for c, size in columns(length)])
            key = shortest_repeat(key)
            if key not in candidates:
                candidates[key] = score_key(key)
                if report:
                    report(0.7 + 0.3 * step / len(likely), key, candidates[key])

    ranked = sorted((score, key) for key, score in candidates.items())[:max(1, int(top))]
    return [(score, key, vigenere_apply(clean, key, True)) for score, key in ranked]


# ---------- small widget helpers ----------

def hover_on(button):
    if button.cget("state") == "normal":
        button.configure(fg_color=palette["hover_fill"], text_color=palette["hover_text"],
                         border_color=palette["hover_border"])


def hover_off(button):
    button.configure(fg_color=palette["panel"], text_color=palette["text"],
                     border_color=palette["text"])


def make_button(master, text, command, width=100, height=34, size=14, radius=10,
                border=2, highlight=True):
    button = ctk.CTkButton(
        master=master, text=text, command=command, width=width, height=height,
        corner_radius=radius, border_width=border, hover=False,
        fg_color=palette["panel"], text_color=palette["text"], border_color=palette["text"],
        font=ui_font("card", size, "bold"))
    if highlight:
        button.bind("<Enter>", lambda e: hover_on(button))
        button.bind("<Leave>", lambda e: hover_off(button))
    return button


def make_label(master, text, size=14, weight="bold", anchor="w"):
    return ctk.CTkLabel(master=master, text=text, anchor=anchor, text_color=palette["text"],
                        font=ui_font("card", size, weight))


def make_entry(master, width=200, placeholder=""):
    return ctk.CTkEntry(
        master=master, width=width, height=32, corner_radius=8, border_width=2,
        fg_color=palette["window"], border_color=palette["text"], text_color=palette["text"],
        placeholder_text=placeholder, placeholder_text_color=palette["placeholder"],
        font=ui_font("mono", 14))


def make_textbox(master, readonly=False):
    box = ctk.CTkTextbox(
        master=master, height=80, corner_radius=10, border_width=2, wrap="word",
        fg_color=palette["window"], border_color=palette["text"], text_color=palette["text"],
        font=ui_font("mono", 14))
    if readonly:
        box.configure(state="disabled")
    return box


def make_panel(master):
    return ctk.CTkFrame(master=master, corner_radius=10, border_width=2,
                        fg_color=palette["window"], border_color=palette["text"])


def make_slider(master, low, high, command):
    return ctk.CTkSlider(
        master=master, from_=low, to=high, number_of_steps=high - low, command=command,
        fg_color=palette["panel"], progress_color=palette["text"], button_color=palette["text"],
        button_hover_color=palette["hover_text"])


def set_textbox(box, text):
    box.configure(state="normal")
    box.delete("1.0", "end")
    box.insert("1.0", text)
    box.configure(state="disabled")


def set_status(ui, message, error=False):
    colour = palette["error"] if error else palette["text"]
    ui["status_label"].configure(text=message, text_color=colour)


def join_notes(notes):
    return "  ·  ".join(notes)


# ---------- theme toggle ----------

# button toggle update.
mode_buttons = []


def mode_icon():
    return "☼" if ctk.get_appearance_mode() == "Dark" else "☽"


def refresh_mode_buttons():
    icon = mode_icon()
    for button in list(mode_buttons):
        try:
            if button.winfo_exists():
                button.configure(text=icon)
            else:
                mode_buttons.remove(button)
        except tk.TclError:
            mode_buttons.remove(button)


def toggle_mode():
    if ctk.get_appearance_mode() == "Dark":
        ctk.set_appearance_mode("light")
    else:
        ctk.set_appearance_mode("dark")
    refresh_mode_buttons()


# ---------- key panels (one per cipher) ----------

def read_key_entry(ui):
    return ui["key_entry"].get()


def read_no_key(ui):
    return ""


def letters_only_note(key):
    cleaned = non_letter.sub("", key).upper()
    if cleaned and cleaned != key.strip().upper():
        return "Key letters only, using " + cleaned
    return ""


def no_key_note(key):
    return ""


def schedule_run(ui):
    if ui["mode"] == "Solve":
        return
    if ui["after_id"] is not None:
        try:
            ui["window"].after_cancel(ui["after_id"])
        except tk.TclError:
            pass

    def fire():
        ui["after_id"] = None
        run_action(ui)

    ui["after_id"] = ui["window"].after(120, fire)


def build_caesar_panel(frame, ui):
    frame.columnconfigure(1, weight=1)
    make_label(frame, "Shift").grid(row=0, column=0, padx=12, pady=12)
    ui["shift_slider"] = make_slider(frame, 1, 25, lambda value: caesar_slider_moved(ui, value))
    ui["shift_slider"].set(3)
    ui["shift_slider"].grid(row=0, column=1, sticky="ew", padx=6, pady=12)
    ui["key_entry"] = make_entry(frame, width=60)
    ui["key_entry"].insert(0, "3")
    ui["key_entry"].grid(row=0, column=2, padx=12, pady=12)
    ui["key_entry"].bind("<KeyRelease>", lambda e: caesar_entry_changed(ui))


def caesar_slider_moved(ui, value):
    ui["key_entry"].delete(0, "end")
    ui["key_entry"].insert(0, str(int(round(value))))
    schedule_run(ui)


def caesar_entry_changed(ui):
    try:
        shift = int(ui["key_entry"].get()) % 26
        if shift:
            ui["shift_slider"].set(shift)
    except ValueError:
        pass
    schedule_run(ui)


def build_atbash_panel(frame, ui):
    frame.columnconfigure(0, weight=1)
    make_label(frame, "No key needed, every letter is mirrored", anchor="center").grid(
        row=0, column=0, padx=12, pady=(12, 4))
    strip = ctk.CTkLabel(
        master=frame, text=" ".join(alphabet) + "\n" + " ".join(alphabet[::-1]),
        text_color=palette["text"], font=ui_font("mono", 12, "bold"))
    strip.grid(row=1, column=0, padx=12, pady=(0, 12))


def build_vigenere_panel(frame, ui):
    frame.columnconfigure(1, weight=1)
    make_label(frame, "Keyword").grid(row=0, column=0, padx=12, pady=12)
    ui["key_entry"] = make_entry(frame, placeholder="e.g. LEMON")
    ui["key_entry"].grid(row=0, column=1, sticky="ew", padx=12, pady=12)
    ui["key_entry"].bind("<KeyRelease>", lambda e: schedule_run(ui))


def refresh_playfair_grid(ui):
    cleaned = non_letter.sub("", ui["key_entry"].get()).upper()
    grid = playfair_grid(cleaned)
    used = len(dict.fromkeys(cleaned.replace("J", "I")))
    for i, cell in enumerate(ui["grid_cells"]):
        fill = palette["selected"] if i < used else palette["panel"]
        cell.configure(text=grid[i], fg_color=fill)


def playfair_key_changed(ui):
    refresh_playfair_grid(ui)
    schedule_run(ui)


def build_playfair_panel(frame, ui):
    frame.columnconfigure(1, weight=1)
    make_label(frame, "Keyword").grid(row=0, column=0, padx=12, pady=(12, 4))
    ui["key_entry"] = make_entry(frame, placeholder="e.g. MONARCHY")
    ui["key_entry"].grid(row=0, column=1, sticky="ew", padx=12, pady=(12, 4))
    ui["key_entry"].bind("<KeyRelease>", lambda e: playfair_key_changed(ui))
    grid_frame = ctk.CTkFrame(master=frame, fg_color="transparent")
    grid_frame.grid(row=1, column=0, columnspan=2, pady=4)
    ui["grid_cells"] = []
    for i in range(25):
        cell = ctk.CTkLabel(
            master=grid_frame, text="", width=30, height=30, corner_radius=6,
            fg_color=palette["panel"], text_color=palette["text"], font=ui_font("mono", 14, "bold"))
        cell.grid(row=i // 5, column=i % 5, padx=2, pady=2)
        ui["grid_cells"].append(cell)
    make_label(frame, "J is read as I, and encoding may add filler X letters",
               size=12, weight="normal", anchor="center").grid(
        row=2, column=0, columnspan=2, padx=12, pady=(0, 10))
    refresh_playfair_grid(ui)


# ---------- solver option panels ----------

def build_caesar_options(frame, ui):
    frame.columnconfigure(0, weight=1)
    make_label(frame, "Tries all 26 shifts and ranks them by how English they look",
               weight="normal", anchor="center").grid(row=0, column=0, padx=12, pady=14)


def read_caesar_options(ui):
    return {}


def build_vigenere_options(frame, ui):
    frame.columnconfigure(1, weight=1)
    make_label(frame, "Max key length").grid(row=0, column=0, padx=12, pady=(12, 4))
    ui["length_value"] = make_label(frame, "16", anchor="e")
    ui["length_value"].grid(row=0, column=2, padx=12, pady=(12, 4))
    ui["length_slider"] = make_slider(
        frame, 2, 24, lambda value: ui["length_value"].configure(text=str(int(round(value)))))
    ui["length_slider"].set(16)
    ui["length_slider"].grid(row=0, column=1, sticky="ew", padx=6, pady=(12, 4))
    ui["use_words"] = ctk.BooleanVar(value=True)
    box = ctk.CTkCheckBox(
        master=frame, text="Try a list of common keywords first", variable=ui["use_words"],
        fg_color=palette["text"], hover_color=palette["bar_hover"], border_color=palette["text"],
        checkmark_color=palette["window"], text_color=palette["text"], font=ui_font("card", 14))
    box.grid(row=1, column=0, columnspan=3, sticky="w", padx=12, pady=(4, 12))


def read_vigenere_options(ui):
    words = keywords if ui["use_words"].get() else ()
    return {"max_key_len": int(round(ui["length_slider"].get())), "wordlist": words}



def caesar_key_label(key):
    return "Shift " + str(key)


def vigenere_key_label(key):
    return "Key " + key


def caesar_result_note(results):
    if results and results[0][1] == 0:
        return "Looks like plain English already"
    return ""


def no_result_note(results):
    return ""


# ---------- cipher specs ----------
# Cipher dictionaries for window builder.

def run_atbash(text, key, decode):
    return atbash(text, decode)


caesar_spec = {
    "name": "Caesar", "description": "Shift each letter by N",
    "window_title": "Julius - Caesar Cipher", "modes": ("Encode", "Decode", "Solve"),
    "run": caesar, "needs_key": True, "key_hint": "Pick a shift to begin",
    "read_key": read_key_entry, "key_note": no_key_note, "build_key_panel": build_caesar_panel,
    "solve": caesar_solve, "build_solver_options": build_caesar_options,
    "read_solver_options": read_caesar_options, "key_label": caesar_key_label,
    "min_letters": 30, "result_note": caesar_result_note,
}

atbash_spec = {
    "name": "Atbash", "description": "Alphabet reversal",
    "window_title": "Julius - Atbash Cipher", "modes": ("Encode", "Decode"),
    "run": run_atbash, "needs_key": False, "key_hint": "",
    "read_key": read_no_key, "key_note": no_key_note, "build_key_panel": build_atbash_panel,
    "solve": None, "build_solver_options": None, "read_solver_options": None,
    "key_label": None, "min_letters": 0, "result_note": no_result_note,
}

vigenere_spec = {
    "name": "Vigenere", "description": "Keyword-based shifting",
    "window_title": "Julius - Vigenere Cipher", "modes": ("Encode", "Decode", "Solve"),
    "run": vigenere, "needs_key": True, "key_hint": "Type a keyword to begin",
    "read_key": read_key_entry, "key_note": letters_only_note, "build_key_panel": build_vigenere_panel,
    "solve": vigenere_solve, "build_solver_options": build_vigenere_options,
    "read_solver_options": read_vigenere_options, "key_label": vigenere_key_label,
    "min_letters": 150, "result_note": no_result_note,
}

playfair_spec = {
    "name": "Playfair", "description": "Digraphs on a 5x5 grid",
    "window_title": "Julius - Playfair Cipher", "modes": ("Encode", "Decode"),
    "run": playfair, "needs_key": True, "key_hint": "Type a keyword to begin",
    "read_key": read_key_entry, "key_note": letters_only_note, "build_key_panel": build_playfair_panel,
    "solve": None, "build_solver_options": None, "read_solver_options": None,
    "key_label": None, "min_letters": 0, "result_note": no_result_note,
}

cipher_specs = [caesar_spec, atbash_spec, vigenere_spec, playfair_spec]

# ---------- encode and decode actions ----------

def run_action(ui):
    if ui["mode"] == "Solve":
        start_solver(ui)
        return
    spec = ui["spec"]
    text = ui["input_box"].get("1.0", "end-1c")
    if not text.strip():
        set_textbox(ui["output_box"], "")
        set_status(ui, "")
        return
    key = spec["read_key"](ui)
    if spec["needs_key"] and not key.strip():
        set_textbox(ui["output_box"], "")
        set_status(ui, spec["key_hint"])
        return
    try:
        result = spec["run"](text, key, ui["mode"] == "Decode")
    except ValueError as error:
        set_textbox(ui["output_box"], "")
        set_status(ui, str(error), True)
        return
    set_textbox(ui["output_box"], result)
    notes = []
    if sanitise(text) != text:
        notes.append("Special characters were removed")
    key_note = spec["key_note"](key)
    if key_note:
        notes.append(key_note)
    set_status(ui, join_notes(notes))


def swap_action(ui):
    output = ui["output_box"].get("1.0", "end-1c")
    ui["input_box"].delete("1.0", "end")
    ui["input_box"].insert("1.0", output)
    apply_mode(ui, "Decode" if ui["mode"] == "Encode" else "Encode")


def clear_action(ui):
    if ui["busy"]:
        ui["cancel"] = True
    ui["input_box"].delete("1.0", "end")
    set_textbox(ui["output_box"], "")
    if ui["spec"]["solve"]:
        clear_results(ui)
    set_status(ui, "")


def copy_action(ui):
    box = ui["preview_box"] if ui["mode"] == "Solve" else ui["output_box"]
    text = box.get("1.0", "end-1c")
    if not text:
        set_status(ui, "Nothing to copy yet")
        return
    ui["window"].clipboard_clear()
    ui["window"].clipboard_append(text)
    set_status(ui, "Copied to clipboard")


# ---------- solver actions ----------

def set_busy(ui, busy):
    ui["busy"] = busy
    state = "disabled" if busy else "normal"
    ui["run_button"].configure(state=state)
    ui["mode_selector"].configure(state=state)
    ui["cancel_button"].configure(state="normal" if busy else "disabled")


def clear_results(ui, hint="Press Solve to rank the most likely keys"):
    for child in ui["results_frame"].winfo_children():
        child.destroy()
    ui["results"] = []
    ui["result_buttons"] = []
    set_textbox(ui["preview_box"], "")
    if hint:
        make_label(ui["results_frame"], hint, weight="normal").grid(
            row=0, column=0, sticky="w", padx=4, pady=6)


def select_result(ui, index):
    for i, button in enumerate(ui["result_buttons"]):
        button.configure(fg_color=palette["selected"] if i == index else palette["panel"])
    set_textbox(ui["preview_box"], ui["results"][index][2])


def show_results(ui, results):
    spec = ui["spec"]
    if not results:
        clear_results(ui, "No candidates found, the text may be too short")
        return
    clear_results(ui, None)
    ui["results"] = results
    for rank, (score, key, plain) in enumerate(results):
        line = " ".join(plain.split())
        preview = line[:30] + ("…" if len(line) > 30 else "")
        text = str(rank + 1) + ".  " + spec["key_label"](key) + "   fit " + format(score, ".2f") + "   " + preview
        button = make_button(ui["results_frame"], text, lambda i=rank: select_result(ui, i),
                             width=10, height=30, highlight=False)
        button.configure(anchor="w")
        button.grid(row=rank, column=0, sticky="ew", pady=2)
        ui["result_buttons"].append(button)
    select_result(ui, 0)


def finish_solver(ui, results):
    set_busy(ui, False)
    ui["progress"].set(1)
    if ui["cancel"]:
        clear_results(ui)
        set_status(ui, "Solve cancelled")
        return
    show_results(ui, results)
    notes = list(ui["solve_notes"])
    if results:
        note = ui["spec"]["result_note"](results)
        if note:
            notes.append(note)
        if len(results) > 1 and results[1][0] < results[0][0] * 1.25:
            notes.append("Top results are close, check the other candidates")
    set_status(ui, join_notes(notes))


def poll_solver(ui, mailbox):
    try:
        if not ui["window"].winfo_exists():
            return
    except tk.TclError:
        return
    progress = None
    while mailbox:
        kind, payload = mailbox.pop(0)
        if kind == "progress":
            progress = payload
        elif kind == "done":
            finish_solver(ui, payload)
            return
        else:
            set_busy(ui, False)
            clear_results(ui)
            set_status(ui, payload, True)
            return
    if progress is not None:
        ui["progress"].set(progress)
    ui["window"].after(50, lambda: poll_solver(ui, mailbox))


def start_solver(ui):
    spec = ui["spec"]
    text = ui["input_box"].get("1.0", "end-1c")
    count = len(non_letter.sub("", text))
    if count == 0:
        set_status(ui, "Paste the ciphertext above, then press Solve")
        return
    options = spec["read_solver_options"](ui)
    clear_results(ui, "Solving...")
    ui["cancel"] = False
    ui["progress"].set(0)
    ui["solve_notes"] = []
    if sanitise(text) != text:
        ui["solve_notes"].append("Special characters were removed")
    if count < spec["min_letters"]:
        ui["solve_notes"].append("Only " + str(count) + " letters, " + str(spec["min_letters"]) + "+ works best")
    set_busy(ui, True)
    set_status(ui, join_notes(["Solving..."] + ui["solve_notes"]))

    mailbox = []

    def report(progress, key, score):
        mailbox.append(("progress", progress))

    def should_cancel():
        return ui["cancel"]

    def worker():
        try:
            results = spec["solve"](text, report=report, should_cancel=should_cancel, **options)
            mailbox.append(("done", results))
        except ValueError as error:
            mailbox.append(("error", str(error)))
        except Exception as error:
            mailbox.append(("error", "Solver failed: " + str(error)))

    threading.Thread(target=worker, daemon=True).start()
    poll_solver(ui, mailbox)


def cancel_action(ui):
    ui["cancel"] = True
    set_status(ui, "Cancelling...")


# ---------- switching between encode, decode and solve ----------

def apply_mode(ui, mode):
    ui["mode"] = mode
    ui["mode_var"].set(mode)
    if mode == "Solve":
        ui["key_frame"].grid_remove()
        ui["options_frame"].grid()
        ui["output_box"].grid_remove()
        ui["solver_area"].grid()
        ui["swap_button"].grid_remove()
        ui["cancel_button"].grid()
        ui["progress"].grid()
        ui["output_label"].configure(text="Candidates")
        ui["run_button"].configure(text="Solve")
        set_status(ui, "")
    else:
        ui["key_frame"].grid()
        if ui["spec"]["solve"]:
            ui["options_frame"].grid_remove()
            ui["solver_area"].grid_remove()
            ui["cancel_button"].grid_remove()
            ui["progress"].grid_remove()
        ui["output_box"].grid()
        ui["swap_button"].grid()
        ui["output_label"].configure(text="Output")
        ui["run_button"].configure(text=mode)
        run_action(ui)


def cleanup_ui(event, ui):
    if event.widget != ui["window"]:
        return
    ui["cancel"] = True
    if ui["after_id"] is not None:
        try:
            ui["window"].after_cancel(ui["after_id"])
        except tk.TclError:
            pass


def update_status_wrap(ui, width):
    ui["status_label"].configure(wraplength=max(200, int((width - 60) / widget_scale)))



def build_cipher_ui(window, spec):
    ui = {
        "window": window, "spec": spec, "mode": "Encode", "busy": False, "cancel": False,
        "after_id": None, "solve_notes": [], "results": [], "result_buttons": [],
    }

    main_frame = ctk.CTkFrame(master=window, fg_color=palette["panel"])
    main_frame.grid(row=3, column=0, sticky="nsew", padx=20, pady=20)
    main_frame.columnconfigure(0, weight=1)
    main_frame.rowconfigure(3, weight=1)
    main_frame.rowconfigure(7, weight=1)

    # row 0, encode / decode / solve
    ui["mode_var"] = ctk.StringVar(value="Encode")
    ui["mode_selector"] = ctk.CTkSegmentedButton(
        master=main_frame, values=list(spec["modes"]), variable=ui["mode_var"],
        command=lambda value: apply_mode(ui, value), height=34, corner_radius=10,
        fg_color=palette["window"], selected_color=palette["selected"],
        selected_hover_color=palette["selected"], unselected_color=palette["panel"],
        unselected_hover_color=palette["window"], text_color=palette["text"],
        font=ui_font("card", 14, "bold"))
    ui["mode_selector"].grid(row=0, column=0, sticky="ew", padx=15, pady=(15, 10))

    # row 1, key panel and solver options share the same cell
    ui["key_frame"] = make_panel(main_frame)
    ui["key_frame"].grid(row=1, column=0, sticky="ew", padx=15, pady=5)
    spec["build_key_panel"](ui["key_frame"], ui)
    if spec["solve"]:
        ui["options_frame"] = make_panel(main_frame)
        ui["options_frame"].grid(row=1, column=0, sticky="ew", padx=15, pady=5)
        spec["build_solver_options"](ui["options_frame"], ui)
        ui["options_frame"].grid_remove()

    # rows 2 and 3, input
    make_label(main_frame, "Input").grid(row=2, column=0, sticky="w", padx=15, pady=(10, 0))
    ui["input_box"] = make_textbox(main_frame)
    ui["input_box"].grid(row=3, column=0, sticky="nsew", padx=15, pady=5)
    ui["input_box"].bind("<KeyRelease>", lambda e: schedule_run(ui))

    # row 4, buttons
    actions = ctk.CTkFrame(master=main_frame, fg_color="transparent")
    actions.grid(row=4, column=0, sticky="w", padx=15, pady=5)
    ui["run_button"] = make_button(actions, "Encode", lambda: run_action(ui))
    ui["run_button"].grid(row=0, column=0, padx=(0, 8))
    ui["swap_button"] = make_button(actions, "Swap", lambda: swap_action(ui))
    ui["swap_button"].grid(row=0, column=1, padx=8)
    ui["clear_button"] = make_button(actions, "Clear", lambda: clear_action(ui))
    ui["clear_button"].grid(row=0, column=2, padx=8)
    ui["cancel_button"] = make_button(actions, "Cancel", lambda: cancel_action(ui))
    ui["cancel_button"].grid(row=0, column=3, padx=8)
    ui["cancel_button"].grid_remove()

    # row 5, progress bar, only used while solving
    ui["progress"] = ctk.CTkProgressBar(
        master=main_frame, height=10, progress_color=palette["text"], fg_color=palette["window"])
    ui["progress"].set(0)
    ui["progress"].grid(row=5, column=0, sticky="ew", padx=15, pady=4)
    ui["progress"].grid_remove()

    # row 6, output heading and copy button
    header = ctk.CTkFrame(master=main_frame, fg_color="transparent")
    header.grid(row=6, column=0, sticky="ew", padx=15, pady=(6, 0))
    header.columnconfigure(0, weight=1)
    ui["output_label"] = make_label(header, "Output")
    ui["output_label"].grid(row=0, column=0, sticky="w")
    ui["copy_button"] = make_button(header, "Copy", lambda: copy_action(ui), width=70, height=28)
    ui["copy_button"].grid(row=0, column=1, sticky="e")

    # row 7, output box, or the candidate list when solving
    ui["output_box"] = make_textbox(main_frame, readonly=True)
    ui["output_box"].grid(row=7, column=0, sticky="nsew", padx=15, pady=5)
    if spec["solve"]:
        ui["solver_area"] = ctk.CTkFrame(master=main_frame, fg_color="transparent")
        ui["solver_area"].grid(row=7, column=0, sticky="nsew", padx=15, pady=5)
        ui["solver_area"].columnconfigure(0, weight=1)
        ui["solver_area"].rowconfigure(1, weight=1)
        ui["results_frame"] = ctk.CTkFrame(master=ui["solver_area"], fg_color="transparent")
        ui["results_frame"].grid(row=0, column=0, sticky="ew")
        ui["results_frame"].columnconfigure(0, weight=1)
        ui["preview_box"] = make_textbox(ui["solver_area"], readonly=True)
        ui["preview_box"].grid(row=1, column=0, sticky="nsew", pady=(6, 0))
        clear_results(ui)
        ui["solver_area"].grid_remove()

    # row 8, one status line for hints, notes and errors
    ui["status_label"] = ctk.CTkLabel(
        master=main_frame, text="", anchor="w", justify="left", height=44,
        text_color=palette["text"], font=ui_font("card", 13))
    ui["status_label"].grid(row=8, column=0, sticky="ew", padx=15, pady=(0, 10))
    main_frame.bind("<Configure>", lambda e: update_status_wrap(ui, e.width))

    window.bind("<Destroy>", lambda e: cleanup_ui(e, ui), add="+")
    apply_mode(ui, "Encode")
    window.resize_grip.lift()


def open_cipher(spec, button):
    window = create_cipher_window(spec["window_title"], button)
    build_cipher_ui(window, spec)


def make_opener(spec, button):
    return lambda: open_cipher(spec, button)


# ---------- window handling ----------

def release_button(event, win, button):
    if event.widget == win:
        try:
            button.configure(state="normal")
        except tk.TclError:
            pass


def create_cipher_window(title,button,width=600,height=900):

    win = ctk.CTkToplevel(root)

    screen_width = win.winfo_screenwidth()
    horizontal_pos_win = int(screen_width/2-width/4)
    win.geometry(f"{width}x{height}+{horizontal_pos_win}+0")
    win.configure(fg_color=palette["window"])
    win.columnconfigure(0,weight=1)
    win.rowconfigure(3,weight=1)
    win.focus_set()
    if sys.platform.startswith('linux'):
        win.wm_attributes('-type', 'splash')
    else:
        win.overrideredirect(True)

    create_title_bar(win,title_text=title)

    win.update_idletasks()

    if sys.platform.startswith("linux"):
        win.wm_attributes('-type', 'utility')
    else:
        win.overrideredirect(True)

    button.configure(state="disabled")
    win.bind("<Destroy>", lambda e: release_button(e, win, button))
    return win


def create_title_bar(window, title_text="Julius - Classical cipher tool"):
    title_bar = ctk.CTkFrame(master=window, fg_color=palette["panel"])
    title_bar.grid(row=0, column=0, sticky='ew')
    title_bar.columnconfigure(0, weight=1)

    title_label = ctk.CTkLabel(
        master=title_bar,
        text=title_text,
        font=ui_font("title", 14, "bold"),
        fg_color="transparent",
        text_color=palette["text"]
    )
    title_label.grid(row=0, column=0, sticky="ns")

    minimise_button = ctk.CTkButton(
        master=title_bar, text="—", hover_color=palette["bar_hover"],
        fg_color="transparent", font=("Helvetica", 16, "bold"),
        text_color=palette["text"], width=35, corner_radius=0,
        command= lambda: minimise_window(window))
    minimise_button.grid(row=0, column=1, sticky="e")

    maximise_button = ctk.CTkButton(
        master=title_bar, text="☐", hover_color=palette["bar_hover"],
        fg_color="transparent", font=("Helvetica", 16, "bold"),
        text_color=palette["text"], width=35, corner_radius=0
    )
    maximise_button.grid(row=0, column=2, sticky="e")
    maximise_button.configure(command=lambda: maximise_window(window, maximise_button))

    close_button = ctk.CTkButton(
        master=title_bar, text="X", hover_color=palette["bar_hover"],
        fg_color="transparent", font=("Helvetica", 16, "bold"),
        text_color=palette["text"], width=35, corner_radius=0,
        command=window.destroy
    )
    close_button.grid(row=0, column=3, sticky="e")

    seperator = ttk.Separator(master=window,orient="horizontal")
    seperator.grid(row=1,column=0,sticky="ew")

    # Drag bindings scoped to this specific window
    for widget in (title_bar, title_label):
        widget.bind("<Button-1>", lambda e: start_move(e, window))
        widget.bind("<B1-Motion>", lambda e: do_move(e, window))

    # Hover color bindings for all three buttons
    for btn in (close_button, maximise_button, minimise_button):
        btn.bind("<Enter>", lambda e, b=btn: b.configure(
            fg_color=palette["bar_hover"], text_color=palette["bar_hover_text"]))
        btn.bind("<Leave>", lambda e, b=btn: b.configure(
            fg_color='transparent', text_color=palette["text"]))

    resize_grip = ctk.CTkLabel(
        master=window,
        text="◢",
        font=("Arial", 14),
        text_color=("gray40", "gray60"),
        cursor=grip_cursor,
        width=20,
        height=20
    )
    resize_grip.place(relx=1.0,rely=1.0,anchor="se",x=-2,y=-2)
    resize_grip.bind("<Button-1>", lambda e: start_resize(e,window))
    resize_grip.bind("<B1-Motion>", lambda e: do_resize(e,window))
    window.resize_grip = resize_grip

    mode_toggle = ctk.CTkButton(master=window,text=mode_icon(),hover_color=palette["bar_hover"],fg_color="transparent",font=("Helvetica",16,"bold"),text_color=palette["text"],width=30,corner_radius=0,command=toggle_mode)
    mode_toggle.grid(row=2,column=0 ,sticky="e",padx=8,pady=6)
    mode_toggle.bind("<Enter>", lambda e: mode_toggle.configure(fg_color=palette["bar_hover"],text_color=palette["toggle_hover_text"]))
    mode_toggle.bind("<Leave>", lambda e: mode_toggle.configure(fg_color='transparent',text_color=palette["text"]))
    mode_buttons.append(mode_toggle)

    return title_bar


def splash_animation():
    full_text = "Welcome to Julius..."
    typed_text = ""

    if sys.platform.startswith('linux'):
        root.wm_attributes('-type','splash')
    else:
        root.overrideredirect(True)

    root_width = 500
    root_height = 300
    x_root = root.winfo_screenwidth()
    y_root = root.winfo_screenheight()
    horizontal_pos_root = int(x_root/2-root_width/2)
    vertical_pos_root = int(y_root/2-root_height/2)
    root.geometry(f"{root_width}x{root_height}+{horizontal_pos_root}+{vertical_pos_root}")
    root.configure(fg_color=palette["window"])
    root.update()

    for char in full_text:
        typed_text += char
        greeting_label.configure(text=typed_text)
        greeting_label.update()
        time.sleep(0.1)



def maximise_window(window, button):

    fullscreen_width = int(window.winfo_screenwidth())
    fullscreen_height = int(window.winfo_screenheight())

    if not getattr(window, "is_maximised", False):

        window.prev_geometry = window.geometry()

        window.geometry(f"{fullscreen_width}x{fullscreen_height}+0+0")
        window.is_maximised = True
        button.configure(text="⮺")
        window.update()
    else:
        if sys.platform.startswith('linux'):
            window.wm_attributes('-type', 'normal')
        else:
            window.overrideredirect(True)
        window.update_idletasks()
        saved_geometry = getattr(window, "prev_geometry", f"{root_width}x{root_height}+100+0")
        window.geometry(saved_geometry)
        button.configure(text="☐")
        window.is_maximised = False
        window.update_idletasks()


def check_window_state(window):

    
    if sys.platform.startswith('linux'):
        if getattr(window,"is_minimized",False) and window.state() != "iconic":
            window.is_minmized = False
            window.wm_attributes('-type', 'normal')
            window.update_idletasks()
            window.wm_attributes('-type', 'utility')
            window.update_idletasks()
        elif window.state() == "iconic":
            window.after(300, lambda: check_window_state(window))
    else:
        if window.state() != "iconic":
            window.overrideredirect(True)
            window.after(300, lambda: check_window_state(window))

        else:
            window.after(300, lambda: check_window_state(window))
            window.state("iconic")

def minimise_window(window):

    if sys.platform.startswith('linux'):
        window.iconify()
        window.is_minimized = True
        window.after(300,lambda: check_window_state(window))
    else:
        window.update_idletasks()
        window.overrideredirect(False)
        window.state("iconic")
        window.after(300, lambda: check_window_state(window))


drag_data = {"x": 0, "y": 0}

def start_move(event,window):
    drag_data["x"] = event.x
    drag_data["y"] = event.y

def do_move(event,window):
    deltax = event.x - drag_data["x"]
    deltay = event.y - drag_data["y"]
    x = window.winfo_x() + deltax
    y = window.winfo_y() + deltay
    window.geometry(f"+{x}+{y}")


resize_data = {"x": 0, "y": 0, "width": 0, "height": 0}

def start_resize(event,window):
    resize_data["x"] = event.x_root
    resize_data["y"] = event.y_root
    resize_data["width"] = window.winfo_width()
    resize_data["height"] = window.winfo_height()

def do_resize(event,window):
    # a maximised window has nothing to resize into
    if getattr(window, "is_maximised", False):
        return
    delta_x = event.x_root - resize_data["x"]
    delta_y = event.y_root - resize_data["y"]

    # Keeping a minimum size of 450x350 so the window doesn't disappear
    new_width = max(450, resize_data["width"] + delta_x)
    new_height = max(350, resize_data["height"] + delta_y)
    window.geometry(f"{new_width}x{new_height}")



greeting_label = ctk.CTkLabel(master=root,text_color=palette["text"],font=ui_font("splash",24,"bold"))
greeting_label.pack(pady=100)

splash_animation()
greeting_label.destroy()


# cards are sized from the text width to avoic clipping 
card_font = tkfont.Font(root=root, family=fonts["card"], size=-round(18 * widget_scale), weight="bold")
longest_line = max(card_font.measure(line) for spec in cipher_specs for line in (spec["name"], spec["description"]))
card_width = max(200, int(longest_line / widget_scale) + 50)


needed_width = int((card_width + 20) * 2 * widget_scale) + 80
if needed_width > root_width:
    root_width = needed_width
    horizontal_pos_root = int(x_root/2-root_width/2)

root.title("Julius — Classical Cipher De/Encoder")
root.geometry(f"{root_width}x{root_height}+{horizontal_pos_root}+0")
root.configure(fg_color=palette["window"])
root.columnconfigure(0,weight=1)
root.overrideredirect(False)
create_title_bar(root,title_text="Julius - Classical Cipher Tool")


welcome_frame= ctk.CTkFrame(master=root,fg_color=palette["panel"],corner_radius=15)
welcome_frame.grid(row=3,column=0,sticky="ns",pady=20)

for index, spec in enumerate(cipher_specs):
    card = make_button(welcome_frame, spec["name"] + "\n" + spec["description"], None,
                       width=card_width, height=100, size=18, radius=15, border=3)
    card.configure(command=make_opener(spec, card))
    card.grid(row=index // 2, column=index % 2, pady=20, padx=10)

footer_label = ctk.CTkLabel(master=root,fg_color=palette["window"],text="Select a cipher to begin...",font=ui_font("card",18,"bold"),text_color=palette["text"])
footer_label.grid(row=5,column=0,pady=50,sticky="s")

if sys.platform.startswith('linux'):
    root.wm_attributes('-type', 'utility')
else:
    root.overrideredirect(True)

root.resize_grip.lift()

root.mainloop()