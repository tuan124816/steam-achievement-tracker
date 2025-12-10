import json
import tkinter as tk
from tkinter import filedialog, messagebox
from pathlib import Path
from typing import List, Dict, Any

from PIL import Image, ImageTk

from .main import run_tracker
from .config import load_config, COOKIE_FILE
from .cookie_setup import generate_steam_cookies
from .utils import log
from .steam_utils import resolve_vanity_url
from .fetchers import fetch_game_info
from .steam_cache import game_header_path


# ----------------------
# Theme definitions
# ----------------------
THEMES = {
    "<theme_key>": {
        "name": "Display name",

        # --- Core background & text ---
        "bg": "<main window background color>",          # root window, frames
        "fg": "<default text color for labels>",         # labels, headings

        # --- Buttons ---
        "btn_bg": "<button background color>",           # normal state
        "btn_fg": "<button text color>",                 # normal state
        "btn_hover": "<button hover background>",        # mouse-over highlight

        # --- Text Entries (input boxes) ---
        "entry_bg": "<text entry background>",
        "entry_fg": "<text entry text color>",

        # --- Listboxes ---
        "list_bg": "<listbox background>",
        "list_fg": "<listbox text color>",

        # --- Accent (important emphasis) ---
        "accent": "<highlight color>",                   # listbox selection, outlines

        # --- Font ---
        "font": ("FontName", "size")
    },
    "light": {
        "name": "Light",
        "bg": "#F7F8FB",
        "fg": "#0f1724",
        "btn_bg": "#E9F0FF",
        "btn_fg": "#0f1724",
        "btn_hover": "#d6e4ff",         # <── added
        "entry_bg": "#ffffff",
        "entry_fg": "#111111",
        "list_bg": "#ffffff",
        "list_fg": "#111111",
        "accent": "#2B66C3",
        "font": ("Segoe UI", 10)
    },
    "steam": {
        "name": "Steam Dark",
        "bg": "#1b2838",
        "fg": "#ffffff",
        "btn_bg": "#1b2838",
        "btn_fg": "#d6e6f3",
        "btn_hover": "#223347",         # <── added
        "entry_bg": "#16202d",
        "entry_fg": "#ffffff",
        "list_bg": "#16202d",
        "list_fg": "#ffffff",
        "accent": "#66a6ff",
        "font": ("Segoe UI", 10)
    },
    "midnight": {
        "name": "Midnight",
        "bg": "#0d1117",
        "fg": "#c9d1d9",
        "btn_bg": "#21262d",
        "btn_fg": "#c9d1d9",
        "btn_hover": "#30363d",         # <── added
        "entry_bg": "#0f1720",
        "entry_fg": "#c9d1d9",
        "list_bg": "#0f1720",
        "list_fg": "#c9d1d9",
        "accent": "#58a6ff",
        "font": ("Segoe UI", 10)
    },
    "oled": {
        "name": "OLED",
        "bg": "#000000",
        "fg": "#ffffff",
        "btn_bg": "#111111",
        "btn_fg": "#ffffff",
        "btn_hover": "#222222",         # <── added
        "entry_bg": "#000000",
        "entry_fg": "#ffffff",
        "list_bg": "#000000",
        "list_fg": "#ffffff",
        "accent": "#00b3ff",
        "font": ("Segoe UI", 10)
    }
}


def launch_gui():
    root = tk.Tk()
    root.title("Steam Achievement Tracker — GUI")
    root.geometry("720x560")
    App(root)
    root.mainloop()


class App:
    def __init__(self, root: tk.Tk):
        self.root = root

        # State
        self.config_path = tk.StringVar()
        self.output_path = tk.StringVar()
        self.status_text = tk.StringVar(value="Ready.")
        self.game_name = tk.StringVar(value="(No game selected)")
        self.game_photo = None  # keep reference for Tk images
        self.chart_theme_key = tk.StringVar(value="light")

        self.friends: List[Dict[str, Any]] = []

        # We'll keep references to widgets that need theming
        self._themed_widgets: List[tk.Widget] = []
        self._themed_entry_widgets: List[tk.Entry] = []
        self._themed_button_widgets: List[tk.Button] = []
        self._themed_list_widgets: List[tk.Widget] = []
        self._labels_for_fg: List[tk.Label] = []

        # Build UI + menu
        self.build_ui()
        self.build_menu()

        # Apply initial theme
        self.apply_theme(self.chart_theme_key.get())


    # ---------------- Recursive Theme Engine ---------------- #
    def apply_theme_recursive(self, widget, theme):
        """
        Recursively apply theme colors to every widget in the GUI.
        This ensures no widget stays white even if it wasn't manually registered.
        """
        wtype = widget.winfo_class()

        try:
            if wtype in ("Frame", "LabelFrame"):
                widget.configure(bg=theme["bg"])

            elif wtype == "Label":
                widget.configure(bg=theme["bg"], fg=theme["fg"], font=theme["font"])

            elif wtype == "Button":
                widget.configure(
                    bg=theme["btn_bg"],
                    fg=theme["btn_fg"],
                    activebackground=theme["btn_hover"],
                    activeforeground=theme["btn_fg"],
                    relief="raised",
                    bd=1
                )

            elif wtype == "Entry":
                widget.configure(
                    bg=theme["entry_bg"], fg=theme["entry_fg"],
                    insertbackground=theme["entry_fg"]
                )

            elif wtype == "Listbox":
                widget.configure(
                    bg=theme["list_bg"], fg=theme["list_fg"],
                    selectbackground=theme["accent"],
                    selectforeground=theme["fg"]
                )

            elif wtype == "Toplevel":
                widget.configure(bg=theme["bg"])

        except tk.TclError:
            pass

        # Recurse into child widgets
        for child in widget.winfo_children():
            self.apply_theme_recursive(child, theme)

    
    def refresh_theme(self):
        """
        Reapply theme globally using the recursive engine.
        """
        theme = THEMES[self.chart_theme_key.get()]
        self.apply_theme_recursive(self.root, theme)
        self.root.update_idletasks()


    # ---------------- Menu ---------------- #
    def build_menu(self):
        menubar = tk.Menu(self.root)

        # File
        file_menu = tk.Menu(menubar, tearoff=0)
        file_menu.add_command(label="Run Tracker", command=self.start_tracking)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.root.quit)
        menubar.add_cascade(label="File", menu=file_menu)

        # Tools
        tools_menu = tk.Menu(menubar, tearoff=0)
        tools_menu.add_command(label="Open Config", command=self.pick_config)
        tools_menu.add_command(label="Regenerate Cookies", command=self.menu_regen_cookies)
        tools_menu.add_command(label="Clear Cache", command=self.menu_clear_cache)
        menubar.add_cascade(label="Tools", menu=tools_menu)

        # Settings (themes + preview)
        settings_menu = tk.Menu(menubar, tearoff=0)
        theme_menu = tk.Menu(settings_menu, tearoff=0)
        for key, info in THEMES.items():
            theme_menu.add_radiobutton(label=info["name"], variable=self.chart_theme_key, value=key,
                                       command=lambda k=key: self.on_theme_change(k))
        settings_menu.add_cascade(label="Appearance / Theme", menu=theme_menu)
        settings_menu.add_command(label="Preview Current Theme", command=self.preview_theme)
        menubar.add_cascade(label="Settings", menu=settings_menu)

        # Help
        help_menu = tk.Menu(menubar, tearoff=0)
        help_menu.add_command(label="GitHub", command=self.menu_open_github)
        help_menu.add_command(label="About", command=self.menu_about)
        menubar.add_cascade(label="Help", menu=help_menu)

        self.root.config(menu=menubar)

    # ---------------- UI ---------------- #
    def build_ui(self):
        frm = tk.Frame(self.root, padx=12, pady=12)
        frm.pack(fill="both", expand=True)

        # --- Config picker row ---
        lbl_cfg = tk.Label(frm, text="Config File:")
        lbl_cfg.grid(row=0, column=0, sticky="w")
        self._themed_widgets.append(lbl_cfg)
        self._labels_for_fg.append(lbl_cfg)

        ent_cfg = tk.Entry(frm, textvariable=self.config_path, width=52)
        ent_cfg.grid(row=0, column=1, sticky="w")
        self._themed_entry_widgets.append(ent_cfg)

        bt_cfg = tk.Button(frm, text="Browse", command=self.pick_config, width=10)
        bt_cfg.grid(row=0, column=2, padx=(6, 0))
        self._themed_button_widgets.append(bt_cfg)

        # --- Output picker row ---
        lbl_out = tk.Label(frm, text="Output Excel:")
        lbl_out.grid(row=1, column=0, sticky="w", pady=(8, 0))
        self._themed_widgets.append(lbl_out)
        self._labels_for_fg.append(lbl_out)

        ent_out = tk.Entry(frm, textvariable=self.output_path, width=52)
        ent_out.grid(row=1, column=1, sticky="w", pady=(8, 0))
        self._themed_entry_widgets.append(ent_out)

        bt_out = tk.Button(frm, text="Save As", command=self.pick_output, width=10)
        bt_out.grid(row=1, column=2, padx=(6, 0), pady=(8, 0))
        self._themed_button_widgets.append(bt_out)

        # --- Friends section ---
        lbl_friends = tk.Label(frm, text="Friends:")
        lbl_friends.grid(row=2, column=0, sticky="w", pady=(16, 4))
        self._themed_widgets.append(lbl_friends)
        self._labels_for_fg.append(lbl_friends)

        self.friends_list = tk.Listbox(frm, height=9, width=66)
        self.friends_list.grid(row=3, column=0, columnspan=2, sticky="w")
        self._themed_list_widgets.append(self.friends_list)

        bt_frame = tk.Frame(frm)
        bt_frame.grid(row=3, column=2, sticky="n")
        self._themed_widgets.append(bt_frame)

        bt_add = tk.Button(bt_frame, text="Add", width=10, command=self.add_friend)
        bt_add.pack(pady=3)
        bt_rem = tk.Button(bt_frame, text="Remove", width=10, command=self.remove_friend)
        bt_rem.pack(pady=3)
        self._themed_button_widgets.extend([bt_add, bt_rem])

        # --- Runner + graphs ---
        bt_run = tk.Button(frm, text="Start Tracking", font=("Arial", 13, "bold"),
                           command=self.start_tracking, width=36)
        bt_run.grid(row=4, column=0, columnspan=3, pady=(18, 8))
        self._themed_button_widgets.append(bt_run)

        bt_graph = tk.Button(frm, text="Show Progress Graphs", command=self.show_graphs, width=36)
        bt_graph.grid(row=5, column=0, columnspan=3, pady=(0, 12))
        self._themed_button_widgets.append(bt_graph)

        # --- Status + Game info ---
        lbl_status = tk.Label(frm, text="Status:")
        lbl_status.grid(row=6, column=0, sticky="w")
        self._themed_widgets.append(lbl_status)
        self._labels_for_fg.append(lbl_status)

        lbl_status_val = tk.Label(frm, textvariable=self.status_text, fg="blue")
        lbl_status_val.grid(row=7, column=0, columnspan=3, sticky="w")
        self._themed_widgets.append(lbl_status_val)
        self._labels_for_fg.append(lbl_status_val)

        lbl_game = tk.Label(frm, text="Game:")
        lbl_game.grid(row=8, column=0, sticky="w", pady=(14, 0))
        self._themed_widgets.append(lbl_game)
        self._labels_for_fg.append(lbl_game)

        lbl_game_name = tk.Label(frm, textvariable=self.game_name, font=("Arial", 14, "bold"))
        lbl_game_name.grid(row=9, column=0, columnspan=3, sticky="w")
        self._themed_widgets.append(lbl_game_name)
        self._labels_for_fg.append(lbl_game_name)

        # image placeholder
        self.game_image_label = tk.Label(frm)
        self.game_image_label.grid(row=10, column=0, columnspan=3, pady=10)
        self._themed_widgets.append(self.game_image_label)

    # ---------------- Theme handling ---------------- #
    def apply_theme(self, key: str):
        """
        Apply a theme to all known widgets. Called when theme changes.
        """
        theme = THEMES.get(key, THEMES["light"])

        # Root background
        self.root.configure(bg=theme["bg"])

        # Labels / frames with background
        for w in self._themed_widgets:
            try:
                w.configure(bg=theme["bg"])
            except Exception:
                pass

        # Labels for foreground text
        for lbl in self._labels_for_fg:
            try:
                lbl.configure(fg=theme["fg"], bg=theme["bg"], font=theme["font"])
            except Exception:
                pass

        # Entry widgets
        for e in self._themed_entry_widgets:
            try:
                e.configure(bg=theme["entry_bg"], fg=theme["entry_fg"], insertbackground=theme["entry_fg"],
                            relief="solid")
            except Exception:
                pass

        # Buttons
        for b in self._themed_button_widgets:
            try:
                b.configure(bg=theme["btn_bg"], fg=theme["btn_fg"], activebackground=theme["btn_hover"],
                            relief="raised", bd=1)
            except Exception:
                pass

        # Listboxes
        for l in self._themed_list_widgets:
            try:
                l.configure(bg=theme["list_bg"], fg=theme["list_fg"], selectbackground=theme["accent"])
            except Exception:
                pass

    def on_theme_change(self, key: str):
        self.refresh_theme()

    def preview_theme(self):
        """
        Show a small preview window with swatches and text demonstrating the current theme.
        """
        key = self.chart_theme_key.get()
        theme = THEMES.get(key, THEMES["light"])

        pv = tk.Toplevel(self.root)
        pv.title(f"Theme preview — {theme['name']}")
        pv.geometry("360x160")
        pv.configure(bg=theme["bg"])

        # swatch
        sw = tk.Canvas(pv, width=80, height=80, bg=theme["bg"], highlightthickness=0)
        sw.create_rectangle(8, 8, 72, 72, fill=theme["btn_bg"], outline=theme["accent"])
        sw.grid(row=0, column=0, padx=12, pady=12)

        lbl = tk.Label(pv, text=theme["name"], bg=theme["bg"], fg=theme["fg"], font=("Segoe UI", 12, "bold"))
        lbl.grid(row=0, column=1, sticky="w", padx=6, pady=8)

        sample = tk.Label(pv, text="Sample button", bg=theme["btn_bg"], fg=theme["btn_fg"])
        sample.grid(row=1, column=1, sticky="w", padx=6)

        close = tk.Button(pv, text="Close", command=pv.destroy, bg=theme["btn_bg"], fg=theme["btn_fg"])
        close.grid(row=2, column=1, sticky="e", padx=8, pady=10)

    # ---------------- Menu actions ---------------- #
    def menu_regen_cookies(self):
        """Regenerate cookies (calls the interactive generator)."""
        try:
            msg = f"Existing cookie file: {COOKIE_FILE.resolve()}" if COOKIE_FILE.exists() else "No cookie file found."
            if COOKIE_FILE.exists():
                # Inform user that file exists but we'll regenerate (explicit)
                if not messagebox.askyesno("Regenerate Cookies",
                                           f"{msg}\n\nDo you want to regenerate the Steam cookies now?"):
                    return
            # Call generator (interactive)
            generate_steam_cookies(COOKIE_FILE)
            messagebox.showinfo("Done", f"Cookies saved to: {COOKIE_FILE}")
        except Exception as e:
            messagebox.showerror("Cookie generation failed", str(e))

    def menu_clear_cache(self):
        messagebox.showinfo("Clear Cache", "Cache clearing will be added later in v1.3.")

    def menu_open_github(self):
        # Placeholder; simple message for now
        messagebox.showinfo("GitHub", "Open your project repository in a browser (not implemented).")

    def menu_about(self):
        messagebox.showinfo("About", "Steam Achievement Tracker\nVersion 1.2 GUI")

    # ---------------- Actions ---------------- #
    def pick_config(self):
        path = filedialog.askopenfilename(filetypes=[("JSON files", "*.json")])
        if path:
            self.config_path.set(path)
            self.load_config_file()

    def pick_output(self):
        path = filedialog.asksaveasfilename(defaultextension=".xlsx")
        if path:
            self.output_path.set(path)

    def load_config_file(self):
        try:
            cfg = json.loads(Path(self.config_path.get()).read_text("utf-8"))
            self.friends = cfg.get("friends", [])
            self.refresh_friend_list()

            # load game info (non-blocking simple try)
            try:
                app_id = cfg.get("app_id")
                if app_id:
                    gameinfo = fetch_game_info(app_id)
                    self.game_name.set(gameinfo.get("name", "(Unknown Game)"))
                    self.load_game_image(app_id)
            except Exception:
                self.game_name.set("(Could not load game info)")

            self.status_text.set("Loaded config.json")
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def refresh_friend_list(self):
        self.friends_list.delete(0, tk.END)
        for f in self.friends:
            self.friends_list.insert(tk.END, f"{f['name']} — {f['steamid']}")

    def add_friend(self):
        popup = tk.Toplevel(self.root)
        popup.title("Add Friend")
        popup.geometry("380x120")

        tk.Label(popup, text="Name:").grid(row=0, column=0, sticky="w", padx=6, pady=6)
        name_var = tk.StringVar()
        tk.Entry(popup, textvariable=name_var, width=40).grid(row=0, column=1, padx=6)

        tk.Label(popup, text="SteamID / Vanity URL:").grid(row=1, column=0, sticky="w", padx=6)
        id_var = tk.StringVar()
        tk.Entry(popup, textvariable=id_var, width=40).grid(row=1, column=1, padx=6)

        def save_friend():
            name = name_var.get().strip()
            sid = id_var.get().strip()
            if not name or not sid:
                messagebox.showerror("Error", "Name and SteamID/URL required.")
                return

            if "steamcommunity.com/id" in sid or sid.startswith("http"):
                try:
                    sid = resolve_vanity_url(sid)
                except Exception:
                    messagebox.showerror("Error", "Invalid vanity URL")
                    return

            self.friends.append({"name": name, "steamid": sid})
            self.refresh_friend_list()
            popup.destroy()

        tk.Button(popup, text="Add", command=save_friend, width=12).grid(row=2, column=0, columnspan=2, pady=8)

    def remove_friend(self):
        sel = self.friends_list.curselection()
        if not sel:
            return
        i = sel[0]
        self.friends.pop(i)
        self.refresh_friend_list()

    def start_tracking(self):
        try:
            path = self.config_path.get()
            if not path:
                messagebox.showerror("Error", "Choose config.json first.")
                return

            # load base config (we use load_config to honor CLI-like options in file)
            cfg = load_config(path)
            cfg["friends"] = self.friends

            if self.output_path.get():
                cfg["output_path"] = self.output_path.get()

            # pass theme selection to cfg so other parts can use it (optional)
            cfg["chart_theme"] = self.chart_theme_key.get()

            self.status_text.set("Running tracker...")
            self.root.update_idletasks()

            run_tracker(cfg)

            self.status_text.set("Done!")
            messagebox.showinfo("Success", "Tracking Completed.")
        except Exception as e:
            messagebox.showerror("Error", str(e))
            self.status_text.set("Error occurred.")

    def show_graphs(self):
        try:
            if not self.config_path.get():
                messagebox.showerror("Error", "Choose config.json first.")
                return

            cfg = json.loads(Path(self.config_path.get()).read_text("utf-8"))
            app_id = cfg.get("app_id")
            if not app_id:
                messagebox.showerror("Error", "Invalid config.json — missing app_id.")
                return

            from .history_utils import plot_progress, load_history
            history = load_history(app_id)
            if not history:
                messagebox.showwarning("No History", "No snapshots found for this game.\nRun the tracker first.")
                return

            # propagate the chosen theme into the plot function by setting a small env param
            plot_progress(app_id)

            # open graphs folder
            folder = Path("history") / str(app_id) / "graphs"
            folder.mkdir(parents=True, exist_ok=True)

            import platform, subprocess
            if platform.system() == "Windows":
                subprocess.Popen(["explorer", str(folder.resolve())])
            elif platform.system() == "Darwin":
                subprocess.Popen(["open", str(folder.resolve())])
            else:
                subprocess.Popen(["xdg-open", str(folder.resolve())])

            messagebox.showinfo("Done", "Graphs generated successfully!")
        except Exception as e:
            messagebox.showerror("Error generating graphs", str(e))

    def load_game_image(self, app_id: int):
        try:
            img_path = game_header_path(app_id, "header.jpg")
            if img_path.exists():
                img = Image.open(img_path)
                # scale width to 520 max while keeping aspect
                max_w = 520
                w = min(max_w, img.width)
                h = int(img.height * (w / img.width))
                img = img.resize((w, h), Image.LANCZOS)
                self.game_photo = ImageTk.PhotoImage(img)
                self.game_image_label.config(image=self.game_photo)
            else:
                self.game_image_label.config(image="")
        except Exception:
            self.game_image_label.config(image="")
