"""
gui_app.py
----------
Tkinter-based GUI for Steam Achievement Tracker.

Features included in this rewrite:
- Improved, cleaner layout and spacing.
- Full theme engine with multiple palettes and documented color keys.
- Recursive theming that applies to existing and newly created widgets.
- Button hover effects (simple bg swap).
- Connected "Regenerate Cookies" menu action that calls interactive generator.
- Theme preview window and quick theme switching.
- Docstrings and inline comments explaining key blocks.

To run:
    from tracker.gui_app import launch_gui
    launch_gui()
"""
from __future__ import annotations

import json
import tkinter as tk
from tkinter import filedialog, messagebox
from pathlib import Path
from typing import Any, Dict, List, Optional

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
# Each theme dict uses the following keys (annotated) ---
# bg         : main window / frame background
# fg         : default label text color
# btn_bg     : button background (normal)
# btn_fg     : button text color (normal)
# btn_hover  : button background on hover
# entry_bg   : Entry / Text background
# entry_fg   : Entry / Text foreground
# list_bg    : Listbox background
# list_fg    : Listbox text color
# accent     : accent/highlight color (selection, outlines)
# font       : default font tuple (family, size)
THEMES: Dict[str, Dict[str, Any]] = {
    "light": {
        "name": "Light",
        "bg": "#F7F8FB",
        "fg": "#0f1724",
        "btn_bg": "#E9F0FF",
        "btn_fg": "#0f1724",
        "btn_hover": "#d6e4ff",
        "entry_bg": "#FFFFFF",
        "entry_fg": "#111111",
        "list_bg": "#FFFFFF",
        "list_fg": "#111111",
        "accent": "#2B66C3",
        "font": ("Segoe UI", 10)
    },
    "steam": {
        "name": "Steam Dark",
        "bg": "#1b2838",
        "fg": "#ffffff",
        "btn_bg": "#253341",
        "btn_fg": "#d6e6f3",
        "btn_hover": "#2b3e4f",
        "entry_bg": "#0f1720",
        "entry_fg": "#eaf4ff",
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
        "btn_hover": "#30363d",
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
        "btn_hover": "#222222",
        "entry_bg": "#000000",
        "entry_fg": "#ffffff",
        "list_bg": "#000000",
        "list_fg": "#ffffff",
        "accent": "#00b3ff",
        "font": ("Segoe UI", 10)
    }
}


# ----------------------
# Helper utilities
# ----------------------
def safe_get_theme_key(key: str) -> str:
    """Return a valid theme key (fallback to 'light')."""
    return key if key in THEMES else "light"


def _apply_widget_theme(widget: tk.Widget, theme: Dict[str, Any]) -> None:
    """
    Apply theme to a single widget where applicable.

    This tries common configuration options and ignores errors when a widget
    does not support a particular config key.
    """
    # Labels & Frames: bg + fg
    try:
        if isinstance(widget, (tk.Label, tk.Frame, tk.Toplevel)):
            widget.configure(bg=theme["bg"])
            if isinstance(widget, tk.Label):
                widget.configure(fg=theme["fg"], font=theme["font"])
    except Exception:
        pass

    # Buttons: bg/fg; hover handled separately by binding functions
    try:
        if isinstance(widget, tk.Button):
            widget.configure(bg=theme["btn_bg"], fg=theme["btn_fg"],
                             activebackground=theme["btn_hover"], relief="raised", bd=1,
                             font=theme["font"])
    except Exception:
        pass

    # Entry widgets
    try:
        if isinstance(widget, tk.Entry):
            widget.configure(bg=theme["entry_bg"], fg=theme["entry_fg"],
                             insertbackground=theme["entry_fg"], relief="solid", font=theme["font"])
    except Exception:
        pass

    # Listbox
    try:
        if isinstance(widget, tk.Listbox):
            widget.configure(bg=theme["list_bg"], fg=theme["list_fg"],
                             selectbackground=theme["accent"], font=theme["font"])
    except Exception:
        pass

    # Canvas: set background where possible
    try:
        if isinstance(widget, tk.Canvas):
            widget.configure(bg=theme["bg"], highlightthickness=0)
    except Exception:
        pass


def apply_theme_recursive(root: tk.Misc, theme_key: str) -> None:
    """
    Recursively apply theme to root and all children.

    This covers widgets created before theme application. New widgets should be
    themed automatically by calling this function again (we call on theme change).
    """
    theme = THEMES[safe_get_theme_key(theme_key)]

    # Configure root window specially
    try:
        if isinstance(root, tk.Tk) or isinstance(root, tk.Toplevel):
            root.configure(bg=theme["bg"])
    except Exception:
        pass

    # Walk children
    stack = [root]
    while stack:
        node = stack.pop()
        # Some nodes (like StringVar) are not widgets
        if not isinstance(node, tk.Misc):
            continue

        # Apply to this node (if widget)
        try:
            _apply_widget_theme(node, theme)
        except Exception:
            pass

        # Bind hover styling for Buttons (if not already)
        if isinstance(node, tk.Button):
            # store original color in instance attribute for safety
            try:
                if not hasattr(node, "_orig_bg"):
                    node._orig_bg = theme["btn_bg"]
                # Bind events - use closures to capture node & theme safely
                def _on_enter(ev, btn=node, t=theme):
                    try:
                        btn.configure(bg=t["btn_hover"])
                    except Exception:
                        pass

                def _on_leave(ev, btn=node, t=theme):
                    try:
                        btn.configure(bg=t["btn_bg"])
                    except Exception:
                        pass

                # Re-bindings are idempotent for this usage
                node.bind("<Enter>", _on_enter, add="+")
                node.bind("<Leave>", _on_leave, add="+")
            except Exception:
                pass

        # Add children to stack
        try:
            for child in node.winfo_children():
                stack.append(child)
        except Exception:
            # Not all tk.Misc provide winfo_children
            continue


# ----------------------
# GUI Application
# ----------------------
def launch_gui():
    """Create root window and start the Tk event loop."""
    root = tk.Tk()
    root.title("Steam Achievement Tracker — GUI")
    root.geometry("760x620")
    App(root)
    root.mainloop()


class App:
    """
    Main GUI application class.

    Responsibilities:
    - Build and layout widgets.
    - Wire menus and actions (including regenerate cookies).
    - Apply theme changes and show theme preview.
    - Provide a Light-weight UX for running the tracker and viewing graphs.
    """

    def __init__(self, root: tk.Tk):
        self.root = root

        # Application state (tk variables for auto-binding)
        self.config_path = tk.StringVar()
        self.output_path = tk.StringVar()
        self.status_text = tk.StringVar(value="Ready.")
        self.game_name = tk.StringVar(value="(No game selected)")
        self.game_photo: Optional[ImageTk.PhotoImage] = None
        self.chart_theme_key = tk.StringVar(value="light")

        # Friends list: list of {"name": str, "steamid": str}
        self.friends: List[Dict[str, Any]] = []

        # Build UI & menus (improved spacing & grouping)
        self._build_ui()
        self._build_menu()

        # Apply initial theme to entire window
        apply_theme_recursive(self.root, self.chart_theme_key.get())

    # ----------------------
    # UI Construction
    # ----------------------
    def _build_ui(self) -> None:
        """Create and place all widgets with improved layout and consistent padding."""
        pad_x = 10
        pad_y = 8

        container = tk.Frame(self.root, padx=12, pady=12)
        container.pack(fill="both", expand=True)

        # Top row: config + output fields
        cfg_frame = tk.Frame(container)
        cfg_frame.pack(fill="x", pady=(0, pad_y))

        tk.Label(cfg_frame, text="Config File:").grid(row=0, column=0, sticky="w")
        ent_cfg = tk.Entry(cfg_frame, textvariable=self.config_path, width=56)
        ent_cfg.grid(row=0, column=1, padx=(8, 6))
        tk.Button(cfg_frame, text="Browse", command=self.pick_config, width=10).grid(row=0, column=2)

        tk.Label(cfg_frame, text="Output Excel:").grid(row=1, column=0, sticky="w", pady=(8, 0))
        ent_out = tk.Entry(cfg_frame, textvariable=self.output_path, width=56)
        ent_out.grid(row=1, column=1, padx=(8, 6), pady=(8, 0))
        tk.Button(cfg_frame, text="Save As", command=self.pick_output, width=10).grid(row=1, column=2, pady=(8, 0))

        # Middle: Friends + controls + game preview
        middle = tk.Frame(container)
        middle.pack(fill="both", expand=True, pady=(6, pad_y))

        # Left: friends list
        left = tk.Frame(middle)
        left.pack(side="left", fill="both", expand=True)

        tk.Label(left, text="Friends:").pack(anchor="w")
        self.friends_list = tk.Listbox(left, height=12)
        self.friends_list.pack(fill="both", expand=True, pady=(6, 0))

        # Right: add/remove buttons and game preview
        right = tk.Frame(middle, width=220)
        right.pack(side="right", fill="y", padx=(12, 0))
        right.pack_propagate(False)

        btn_add = tk.Button(right, text="Add Friend", command=self.add_friend, width=18)
        btn_add.pack(pady=(6, 6))
        btn_rem = tk.Button(right, text="Remove Selected", command=self.remove_friend, width=18)
        btn_rem.pack(pady=(0, 12))

        # Game info box (under friend controls)
        tk.Label(right, text="Game:").pack(anchor="w", pady=(6, 0))
        tk.Label(right, textvariable=self.game_name, font=("Arial", 11, "bold")).pack(anchor="w", pady=(2, 8))
        self.game_image_label = tk.Label(right)
        self.game_image_label.pack(pady=(4, 0))

        # Bottom controls: Run + Graphs + Status
        bottom = tk.Frame(container)
        bottom.pack(fill="x", pady=(8, 0))

        btn_run = tk.Button(bottom, text="Start Tracking", command=self.start_tracking, width=36, height=2)
        btn_run.pack(pady=(0, 8))

        btn_graph = tk.Button(bottom, text="Show Progress Graphs", command=self.show_graphs, width=36)
        btn_graph.pack()

        status_frame = tk.Frame(container)
        status_frame.pack(fill="x", pady=(12, 0))
        tk.Label(status_frame, text="Status:").pack(side="left")
        tk.Label(status_frame, textvariable=self.status_text).pack(side="left", padx=(6, 0))

    # ----------------------
    # Menu Construction
    # ----------------------
    def _build_menu(self) -> None:
        """Create application menus (File, Tools, Settings, Help)."""
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
        tools_menu.add_command(label="Regenerate Cookies", command=self._menu_regen_cookies)
        tools_menu.add_command(label="Clear Cache (TODO)", command=lambda: messagebox.showinfo("Clear Cache", "Coming in a future release."))
        menubar.add_cascade(label="Tools", menu=tools_menu)

        # Settings: theme radio + preview
        settings_menu = tk.Menu(menubar, tearoff=0)
        theme_menu = tk.Menu(settings_menu, tearoff=0)
        for key, info in THEMES.items():
            theme_menu.add_radiobutton(label=info["name"], variable=self.chart_theme_key, value=key,
                                       command=lambda k=key: self.on_theme_change(k))
        settings_menu.add_cascade(label="Appearance", menu=theme_menu)
        settings_menu.add_command(label="Preview Theme", command=self.preview_theme)
        menubar.add_cascade(label="Settings", menu=settings_menu)

        # Help
        help_menu = tk.Menu(menubar, tearoff=0)
        help_menu.add_command(label="GitHub (TODO)", command=lambda: messagebox.showinfo("GitHub", "Open repository (not implemented)."))
        help_menu.add_command(label="About", command=lambda: messagebox.showinfo("About", "Steam Achievement Tracker\nGUI v1.2+"))
        menubar.add_cascade(label="Help", menu=help_menu)

        self.root.config(menu=menubar)

    # ----------------------
    # Theme actions
    # ----------------------
    def on_theme_change(self, key: str) -> None:
        """Called when user selects a different theme from the menu."""
        apply_theme_recursive(self.root, key)
        self.chart_theme_key.set(key)

    def preview_theme(self) -> None:
        """Open a small preview window showing palette swatches + sample controls."""
        key = self.chart_theme_key.get()
        theme = THEMES.get(safe_get_theme_key(key), THEMES["light"])

        pv = tk.Toplevel(self.root)
        pv.title(f"Preview — {theme['name']}")
        pv.geometry("420x160")
        pv.configure(bg=theme["bg"])

        # left: swatches
        sw = tk.Canvas(pv, width=96, height=96, bg=theme["bg"], highlightthickness=0)
        sw.create_rectangle(8, 8, 88, 88, fill=theme["btn_bg"], outline=theme["accent"])
        sw.grid(row=0, column=0, rowspan=2, padx=12, pady=12)

        tk.Label(pv, text=theme["name"], bg=theme["bg"], fg=theme["fg"], font=(theme["font"][0], 12, "bold")).grid(row=0, column=1, sticky="w", padx=6, pady=(14, 0))
        tk.Button(pv, text="Sample Button", bg=theme["btn_bg"], fg=theme["btn_fg"]).grid(row=1, column=1, sticky="w", padx=6)

        tk.Button(pv, text="Close", command=pv.destroy).grid(row=2, column=1, sticky="e", padx=8, pady=8)

    # ----------------------
    # Menu commands
    # ----------------------
    def _menu_regen_cookies(self) -> None:
        """
        Regenerate cookies using the interactive helper.
        Shows the current cookie path and asks for confirmation before regenerating.
        """
        try:
            # Inform user of current cookie file
            if COOKIE_FILE.exists():
                msg = f"Existing cookie file detected at:\n{COOKIE_FILE.resolve()}\n\nRegenerating will overwrite it.\nProceed?"
                if not messagebox.askyesno("Regenerate Cookies", msg):
                    return
            else:
                if not messagebox.askyesno("Regenerate Cookies", "No cookie file found. Create a new one now?"):
                    return

            # Call interactive generator (this opens a browser window for login)
            generate_steam_cookies(COOKIE_FILE)
            messagebox.showinfo("Done", f"Cookies saved to: {COOKIE_FILE}")
        except Exception as e:
            messagebox.showerror("Cookie generation failed", str(e))

    # ----------------------
    # Actions - File pickers / friend management
    # ----------------------
    def pick_config(self) -> None:
        path = filedialog.askopenfilename(filetypes=[("JSON files", "*.json")])
        if path:
            self.config_path.set(path)
            self.load_config_file()

    def pick_output(self) -> None:
        path = filedialog.asksaveasfilename(defaultextension=".xlsx")
        if path:
            self.output_path.set(path)

    def load_config_file(self) -> None:
        """Load config.json and populate friends + game info. Non-blocking, best-effort."""
        try:
            cfg = json.loads(Path(self.config_path.get()).read_text("utf-8"))
            self.friends = cfg.get("friends", [])
            self._refresh_friend_list()

            # Try to load game info (non-fatal)
            try:
                app_id = cfg.get("app_id")
                if app_id:
                    info = fetch_game_info(app_id)
                    self.game_name.set(info.get("name", "(Unknown Game)"))
                    self._load_game_image(app_id)
            except Exception:
                self.game_name.set("(Could not load game info)")

            self.status_text.set("Loaded config.json")
            apply_theme_recursive(self.root, self.chart_theme_key.get())
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def _refresh_friend_list(self) -> None:
        """Refresh the visible listbox from self.friends."""
        self.friends_list.delete(0, tk.END)
        for f in self.friends:
            self.friends_list.insert(tk.END, f"{f.get('name')} — {f.get('steamid')}")

    def add_friend(self) -> None:
        """Popup to add a new friend (resolves vanity URL if provided)."""
        popup = tk.Toplevel(self.root)
        popup.title("Add Friend")
        popup.geometry("420x140")
        popup.transient(self.root)

        tk.Label(popup, text="Name:").grid(row=0, column=0, sticky="w", padx=8, pady=6)
        name_var = tk.StringVar()
        tk.Entry(popup, textvariable=name_var, width=44).grid(row=0, column=1, padx=8, pady=6)

        tk.Label(popup, text="SteamID / Vanity URL:").grid(row=1, column=0, sticky="w", padx=8)
        id_var = tk.StringVar()
        tk.Entry(popup, textvariable=id_var, width=44).grid(row=1, column=1, padx=8)

        def _save():
            name = name_var.get().strip()
            sid = id_var.get().strip()
            if not name or not sid:
                messagebox.showerror("Error", "Both name and SteamID/URL are required.")
                return
            # resolve vanity url if detected
            if "steamcommunity.com/id" in sid or sid.startswith("http"):
                try:
                    sid = resolve_vanity_url(sid)
                except Exception:
                    messagebox.showerror("Error", "Failed to resolve vanity URL.")
                    return
            self.friends.append({"name": name, "steamid": sid})
            self._refresh_friend_list()
            popup.destroy()

        tk.Button(popup, text="Add", width=12, command=_save).grid(row=2, column=0, columnspan=2, pady=10)

    def remove_friend(self) -> None:
        sel = self.friends_list.curselection()
        if not sel:
            return
        idx = sel[0]
        self.friends.pop(idx)
        self._refresh_friend_list()

    # ----------------------
    # Main operations
    # ----------------------
    def start_tracking(self) -> None:
        """Run the tracker using the selected config + friends list."""
        try:
            cfg_path = self.config_path.get()
            if not cfg_path:
                messagebox.showerror("Error", "Choose config.json first.")
                return

            cfg = load_config(cfg_path)
            cfg["friends"] = self.friends
            if self.output_path.get():
                cfg["output_path"] = self.output_path.get()

            # Pass theme key into config (optional usage by plotting)
            cfg["chart_theme"] = self.chart_theme_key.get()

            self.status_text.set("Running tracker...")
            self.root.update_idletasks()

            run_tracker(cfg)

            self.status_text.set("Done!")
            messagebox.showinfo("Success", "Tracking Completed.")
            apply_theme_recursive(self.root, self.chart_theme_key.get())
        except Exception as e:
            messagebox.showerror("Error", str(e))
            self.status_text.set("Error occurred.")

    def show_graphs(self) -> None:
        """Generate and open graphs for the loaded game (requires history snapshots)."""
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

            # propagate theme setting where possible (plot_progress may accept theme in future)
            plot_progress(app_id)

            # Open graphs directory
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

    # ----------------------
    # Game image handling
    # ----------------------
    def _load_game_image(self, app_id: int) -> None:
        """Load and display a cached game header image if available."""
        try:
            img_path = game_header_path(app_id, "header.jpg")
            if img_path.exists():
                img = Image.open(img_path)
                max_w = 200
                w = min(max_w, img.width)
                h = int(img.height * (w / img.width))
                img = img.resize((w, h), Image.LANCZOS)
                self.game_photo = ImageTk.PhotoImage(img)
                self.game_image_label.config(image=self.game_photo)
            else:
                self.game_image_label.config(image="")
        except Exception:
            self.game_image_label.config(image="")


















# OLD GUI code, this is suck a pain in the ass to update the color for each part, each at your own risk


# import json
# import tkinter as tk
# from tkinter import filedialog, messagebox
# from pathlib import Path
# from typing import List, Dict, Any

# from PIL import Image, ImageTk

# from .main import run_tracker
# from .config import load_config, COOKIE_FILE
# from .cookie_setup import generate_steam_cookies
# from .utils import log
# from .steam_utils import resolve_vanity_url
# from .fetchers import fetch_game_info
# from .steam_cache import game_header_path


# # ----------------------
# # Theme definitions
# # ----------------------
# THEMES = {
#     "<theme_key>": {
#         "name": "Display name",

#         # --- Core background & text ---
#         "bg": "<main window background color>",          # root window, frames
#         "fg": "<default text color for labels>",         # labels, headings

#         # --- Buttons ---
#         "btn_bg": "<button background color>",           # normal state
#         "btn_fg": "<button text color>",                 # normal state
#         "btn_hover": "<button hover background>",        # mouse-over highlight

#         # --- Text Entries (input boxes) ---
#         "entry_bg": "<text entry background>",
#         "entry_fg": "<text entry text color>",

#         # --- Listboxes ---
#         "list_bg": "<listbox background>",
#         "list_fg": "<listbox text color>",

#         # --- Accent (important emphasis) ---
#         "accent": "<highlight color>",                   # listbox selection, outlines

#         # --- Font ---
#         "font": ("FontName", "size")
#     },
#     "light": {
#         "name": "Light",
#         "bg": "#F7F8FB",
#         "fg": "#0f1724",
#         "btn_bg": "#E9F0FF",
#         "btn_fg": "#0f1724",
#         "btn_hover": "#d6e4ff",         # <── added
#         "entry_bg": "#ffffff",
#         "entry_fg": "#111111",
#         "list_bg": "#ffffff",
#         "list_fg": "#111111",
#         "accent": "#2B66C3",
#         "font": ("Segoe UI", 10)
#     },
#     "steam": {
#         "name": "Steam Dark",
#         "bg": "#1b2838",
#         "fg": "#ffffff",
#         "btn_bg": "#1b2838",
#         "btn_fg": "#d6e6f3",
#         "btn_hover": "#223347",         # <── added
#         "entry_bg": "#16202d",
#         "entry_fg": "#ffffff",
#         "list_bg": "#16202d",
#         "list_fg": "#ffffff",
#         "accent": "#66a6ff",
#         "font": ("Segoe UI", 10)
#     },
#     "midnight": {
#         "name": "Midnight",
#         "bg": "#0d1117",
#         "fg": "#c9d1d9",
#         "btn_bg": "#21262d",
#         "btn_fg": "#c9d1d9",
#         "btn_hover": "#30363d",         # <── added
#         "entry_bg": "#0f1720",
#         "entry_fg": "#c9d1d9",
#         "list_bg": "#0f1720",
#         "list_fg": "#c9d1d9",
#         "accent": "#58a6ff",
#         "font": ("Segoe UI", 10)
#     },
#     "oled": {
#         "name": "OLED",
#         "bg": "#000000",
#         "fg": "#ffffff",
#         "btn_bg": "#111111",
#         "btn_fg": "#ffffff",
#         "btn_hover": "#222222",         # <── added
#         "entry_bg": "#000000",
#         "entry_fg": "#ffffff",
#         "list_bg": "#000000",
#         "list_fg": "#ffffff",
#         "accent": "#00b3ff",
#         "font": ("Segoe UI", 10)
#     }
# }


# def launch_gui():
#     root = tk.Tk()
#     root.title("Steam Achievement Tracker — GUI")
#     root.geometry("720x560")
#     App(root)
#     root.mainloop()


# class App:
#     def __init__(self, root: tk.Tk):
#         self.root = root

#         # State
#         self.config_path = tk.StringVar()
#         self.output_path = tk.StringVar()
#         self.status_text = tk.StringVar(value="Ready.")
#         self.game_name = tk.StringVar(value="(No game selected)")
#         self.game_photo = None  # keep reference for Tk images
#         self.chart_theme_key = tk.StringVar(value="light")

#         self.friends: List[Dict[str, Any]] = []

#         # We'll keep references to widgets that need theming
#         self._themed_widgets: List[tk.Widget] = []
#         self._themed_entry_widgets: List[tk.Entry] = []
#         self._themed_button_widgets: List[tk.Button] = []
#         self._themed_list_widgets: List[tk.Widget] = []
#         self._labels_for_fg: List[tk.Label] = []

#         # Build UI + menu
#         self.build_ui()
#         self.build_menu()

#         # Apply initial theme
#         self.apply_theme(self.chart_theme_key.get())


#     # ---------------- Recursive Theme Engine ---------------- #
#     def apply_theme_recursive(self, widget, theme):
#         """
#         Recursively apply theme colors to every widget in the GUI.
#         This ensures no widget stays white even if it wasn't manually registered.
#         """
#         wtype = widget.winfo_class()

#         try:
#             if wtype in ("Frame", "LabelFrame"):
#                 widget.configure(bg=theme["bg"])

#             elif wtype == "Label":
#                 widget.configure(bg=theme["bg"], fg=theme["fg"], font=theme["font"])

#             elif wtype == "Button":
#                 widget.configure(
#                     bg=theme["btn_bg"],
#                     fg=theme["btn_fg"],
#                     activebackground=theme["btn_hover"],
#                     activeforeground=theme["btn_fg"],
#                     relief="raised",
#                     bd=1
#                 )

#             elif wtype == "Entry":
#                 widget.configure(
#                     bg=theme["entry_bg"], fg=theme["entry_fg"],
#                     insertbackground=theme["entry_fg"]
#                 )

#             elif wtype == "Listbox":
#                 widget.configure(
#                     bg=theme["list_bg"], fg=theme["list_fg"],
#                     selectbackground=theme["accent"],
#                     selectforeground=theme["fg"]
#                 )

#             elif wtype == "Toplevel":
#                 widget.configure(bg=theme["bg"])

#         except tk.TclError:
#             pass

#         # Recurse into child widgets
#         for child in widget.winfo_children():
#             self.apply_theme_recursive(child, theme)

    
#     def refresh_theme(self):
#         """
#         Reapply theme globally using the recursive engine.
#         """
#         theme = THEMES[self.chart_theme_key.get()]
#         self.apply_theme_recursive(self.root, theme)
#         self.root.update_idletasks()


#     # ---------------- Menu ---------------- #
#     def build_menu(self):
#         menubar = tk.Menu(self.root)

#         # File
#         file_menu = tk.Menu(menubar, tearoff=0)
#         file_menu.add_command(label="Run Tracker", command=self.start_tracking)
#         file_menu.add_separator()
#         file_menu.add_command(label="Exit", command=self.root.quit)
#         menubar.add_cascade(label="File", menu=file_menu)

#         # Tools
#         tools_menu = tk.Menu(menubar, tearoff=0)
#         tools_menu.add_command(label="Open Config", command=self.pick_config)
#         tools_menu.add_command(label="Regenerate Cookies", command=self.menu_regen_cookies)
#         tools_menu.add_command(label="Clear Cache", command=self.menu_clear_cache)
#         menubar.add_cascade(label="Tools", menu=tools_menu)

#         # Settings (themes + preview)
#         settings_menu = tk.Menu(menubar, tearoff=0)
#         theme_menu = tk.Menu(settings_menu, tearoff=0)
#         for key, info in THEMES.items():
#             theme_menu.add_radiobutton(label=info["name"], variable=self.chart_theme_key, value=key,
#                                        command=lambda k=key: self.on_theme_change(k))
#         settings_menu.add_cascade(label="Appearance / Theme", menu=theme_menu)
#         settings_menu.add_command(label="Preview Current Theme", command=self.preview_theme)
#         menubar.add_cascade(label="Settings", menu=settings_menu)

#         # Help
#         help_menu = tk.Menu(menubar, tearoff=0)
#         help_menu.add_command(label="GitHub", command=self.menu_open_github)
#         help_menu.add_command(label="About", command=self.menu_about)
#         menubar.add_cascade(label="Help", menu=help_menu)

#         self.root.config(menu=menubar)

#     # ---------------- UI ---------------- #
#     def build_ui(self):
#         frm = tk.Frame(self.root, padx=12, pady=12)
#         frm.pack(fill="both", expand=True)

#         # --- Config picker row ---
#         lbl_cfg = tk.Label(frm, text="Config File:")
#         lbl_cfg.grid(row=0, column=0, sticky="w")
#         self._themed_widgets.append(lbl_cfg)
#         self._labels_for_fg.append(lbl_cfg)

#         ent_cfg = tk.Entry(frm, textvariable=self.config_path, width=52)
#         ent_cfg.grid(row=0, column=1, sticky="w")
#         self._themed_entry_widgets.append(ent_cfg)

#         bt_cfg = tk.Button(frm, text="Browse", command=self.pick_config, width=10)
#         bt_cfg.grid(row=0, column=2, padx=(6, 0))
#         self._themed_button_widgets.append(bt_cfg)

#         # --- Output picker row ---
#         lbl_out = tk.Label(frm, text="Output Excel:")
#         lbl_out.grid(row=1, column=0, sticky="w", pady=(8, 0))
#         self._themed_widgets.append(lbl_out)
#         self._labels_for_fg.append(lbl_out)

#         ent_out = tk.Entry(frm, textvariable=self.output_path, width=52)
#         ent_out.grid(row=1, column=1, sticky="w", pady=(8, 0))
#         self._themed_entry_widgets.append(ent_out)

#         bt_out = tk.Button(frm, text="Save As", command=self.pick_output, width=10)
#         bt_out.grid(row=1, column=2, padx=(6, 0), pady=(8, 0))
#         self._themed_button_widgets.append(bt_out)

#         # --- Friends section ---
#         lbl_friends = tk.Label(frm, text="Friends:")
#         lbl_friends.grid(row=2, column=0, sticky="w", pady=(16, 4))
#         self._themed_widgets.append(lbl_friends)
#         self._labels_for_fg.append(lbl_friends)

#         self.friends_list = tk.Listbox(frm, height=9, width=66)
#         self.friends_list.grid(row=3, column=0, columnspan=2, sticky="w")
#         self._themed_list_widgets.append(self.friends_list)

#         bt_frame = tk.Frame(frm)
#         bt_frame.grid(row=3, column=2, sticky="n")
#         self._themed_widgets.append(bt_frame)

#         bt_add = tk.Button(bt_frame, text="Add", width=10, command=self.add_friend)
#         bt_add.pack(pady=3)
#         bt_rem = tk.Button(bt_frame, text="Remove", width=10, command=self.remove_friend)
#         bt_rem.pack(pady=3)
#         self._themed_button_widgets.extend([bt_add, bt_rem])

#         # --- Runner + graphs ---
#         bt_run = tk.Button(frm, text="Start Tracking", font=("Arial", 13, "bold"),
#                            command=self.start_tracking, width=36)
#         bt_run.grid(row=4, column=0, columnspan=3, pady=(18, 8))
#         self._themed_button_widgets.append(bt_run)

#         bt_graph = tk.Button(frm, text="Show Progress Graphs", command=self.show_graphs, width=36)
#         bt_graph.grid(row=5, column=0, columnspan=3, pady=(0, 12))
#         self._themed_button_widgets.append(bt_graph)

#         # --- Status + Game info ---
#         lbl_status = tk.Label(frm, text="Status:")
#         lbl_status.grid(row=6, column=0, sticky="w")
#         self._themed_widgets.append(lbl_status)
#         self._labels_for_fg.append(lbl_status)

#         lbl_status_val = tk.Label(frm, textvariable=self.status_text, fg="blue")
#         lbl_status_val.grid(row=7, column=0, columnspan=3, sticky="w")
#         self._themed_widgets.append(lbl_status_val)
#         self._labels_for_fg.append(lbl_status_val)

#         lbl_game = tk.Label(frm, text="Game:")
#         lbl_game.grid(row=8, column=0, sticky="w", pady=(14, 0))
#         self._themed_widgets.append(lbl_game)
#         self._labels_for_fg.append(lbl_game)

#         lbl_game_name = tk.Label(frm, textvariable=self.game_name, font=("Arial", 14, "bold"))
#         lbl_game_name.grid(row=9, column=0, columnspan=3, sticky="w")
#         self._themed_widgets.append(lbl_game_name)
#         self._labels_for_fg.append(lbl_game_name)

#         # image placeholder
#         self.game_image_label = tk.Label(frm)
#         self.game_image_label.grid(row=10, column=0, columnspan=3, pady=10)
#         self._themed_widgets.append(self.game_image_label)

#     # ---------------- Theme handling ---------------- #
#     def apply_theme(self, key: str):
#         """
#         Apply a theme to all known widgets. Called when theme changes.
#         """
#         theme = THEMES.get(key, THEMES["light"])

#         # Root background
#         self.root.configure(bg=theme["bg"])

#         # Labels / frames with background
#         for w in self._themed_widgets:
#             try:
#                 w.configure(bg=theme["bg"])
#             except Exception:
#                 pass

#         # Labels for foreground text
#         for lbl in self._labels_for_fg:
#             try:
#                 lbl.configure(fg=theme["fg"], bg=theme["bg"], font=theme["font"])
#             except Exception:
#                 pass

#         # Entry widgets
#         for e in self._themed_entry_widgets:
#             try:
#                 e.configure(bg=theme["entry_bg"], fg=theme["entry_fg"], insertbackground=theme["entry_fg"],
#                             relief="solid")
#             except Exception:
#                 pass

#         # Buttons
#         for b in self._themed_button_widgets:
#             try:
#                 b.configure(bg=theme["btn_bg"], fg=theme["btn_fg"], activebackground=theme["btn_hover"],
#                             relief="raised", bd=1)
#             except Exception:
#                 pass

#         # Listboxes
#         for l in self._themed_list_widgets:
#             try:
#                 l.configure(bg=theme["list_bg"], fg=theme["list_fg"], selectbackground=theme["accent"])
#             except Exception:
#                 pass

#     def on_theme_change(self, key: str):
#         self.refresh_theme()

#     def preview_theme(self):
#         """
#         Show a small preview window with swatches and text demonstrating the current theme.
#         """
#         key = self.chart_theme_key.get()
#         theme = THEMES.get(key, THEMES["light"])

#         pv = tk.Toplevel(self.root)
#         pv.title(f"Theme preview — {theme['name']}")
#         pv.geometry("360x160")
#         pv.configure(bg=theme["bg"])

#         # swatch
#         sw = tk.Canvas(pv, width=80, height=80, bg=theme["bg"], highlightthickness=0)
#         sw.create_rectangle(8, 8, 72, 72, fill=theme["btn_bg"], outline=theme["accent"])
#         sw.grid(row=0, column=0, padx=12, pady=12)

#         lbl = tk.Label(pv, text=theme["name"], bg=theme["bg"], fg=theme["fg"], font=("Segoe UI", 12, "bold"))
#         lbl.grid(row=0, column=1, sticky="w", padx=6, pady=8)

#         sample = tk.Label(pv, text="Sample button", bg=theme["btn_bg"], fg=theme["btn_fg"])
#         sample.grid(row=1, column=1, sticky="w", padx=6)

#         close = tk.Button(pv, text="Close", command=pv.destroy, bg=theme["btn_bg"], fg=theme["btn_fg"])
#         close.grid(row=2, column=1, sticky="e", padx=8, pady=10)

#     # ---------------- Menu actions ---------------- #
#     def menu_regen_cookies(self):
#         """Regenerate cookies (calls the interactive generator)."""
#         try:
#             msg = f"Existing cookie file: {COOKIE_FILE.resolve()}" if COOKIE_FILE.exists() else "No cookie file found."
#             if COOKIE_FILE.exists():
#                 # Inform user that file exists but we'll regenerate (explicit)
#                 if not messagebox.askyesno("Regenerate Cookies",
#                                            f"{msg}\n\nDo you want to regenerate the Steam cookies now?"):
#                     return
#             # Call generator (interactive)
#             generate_steam_cookies(COOKIE_FILE)
#             messagebox.showinfo("Done", f"Cookies saved to: {COOKIE_FILE}")
#         except Exception as e:
#             messagebox.showerror("Cookie generation failed", str(e))

#     def menu_clear_cache(self):
#         messagebox.showinfo("Clear Cache", "Cache clearing will be added later in v1.3.")

#     def menu_open_github(self):
#         # Placeholder; simple message for now
#         messagebox.showinfo("GitHub", "Open your project repository in a browser (not implemented).")

#     def menu_about(self):
#         messagebox.showinfo("About", "Steam Achievement Tracker\nVersion 1.2 GUI")

#     # ---------------- Actions ---------------- #
#     def pick_config(self):
#         path = filedialog.askopenfilename(filetypes=[("JSON files", "*.json")])
#         if path:
#             self.config_path.set(path)
#             self.load_config_file()

#     def pick_output(self):
#         path = filedialog.asksaveasfilename(defaultextension=".xlsx")
#         if path:
#             self.output_path.set(path)

#     def load_config_file(self):
#         try:
#             cfg = json.loads(Path(self.config_path.get()).read_text("utf-8"))
#             self.friends = cfg.get("friends", [])
#             self.refresh_friend_list()

#             # load game info (non-blocking simple try)
#             try:
#                 app_id = cfg.get("app_id")
#                 if app_id:
#                     gameinfo = fetch_game_info(app_id)
#                     self.game_name.set(gameinfo.get("name", "(Unknown Game)"))
#                     self.load_game_image(app_id)
#             except Exception:
#                 self.game_name.set("(Could not load game info)")

#             self.status_text.set("Loaded config.json")
#         except Exception as e:
#             messagebox.showerror("Error", str(e))

#     def refresh_friend_list(self):
#         self.friends_list.delete(0, tk.END)
#         for f in self.friends:
#             self.friends_list.insert(tk.END, f"{f['name']} — {f['steamid']}")

#     def add_friend(self):
#         popup = tk.Toplevel(self.root)
#         popup.title("Add Friend")
#         popup.geometry("380x120")

#         tk.Label(popup, text="Name:").grid(row=0, column=0, sticky="w", padx=6, pady=6)
#         name_var = tk.StringVar()
#         tk.Entry(popup, textvariable=name_var, width=40).grid(row=0, column=1, padx=6)

#         tk.Label(popup, text="SteamID / Vanity URL:").grid(row=1, column=0, sticky="w", padx=6)
#         id_var = tk.StringVar()
#         tk.Entry(popup, textvariable=id_var, width=40).grid(row=1, column=1, padx=6)

#         def save_friend():
#             name = name_var.get().strip()
#             sid = id_var.get().strip()
#             if not name or not sid:
#                 messagebox.showerror("Error", "Name and SteamID/URL required.")
#                 return

#             if "steamcommunity.com/id" in sid or sid.startswith("http"):
#                 try:
#                     sid = resolve_vanity_url(sid)
#                 except Exception:
#                     messagebox.showerror("Error", "Invalid vanity URL")
#                     return

#             self.friends.append({"name": name, "steamid": sid})
#             self.refresh_friend_list()
#             popup.destroy()

#         tk.Button(popup, text="Add", command=save_friend, width=12).grid(row=2, column=0, columnspan=2, pady=8)

#     def remove_friend(self):
#         sel = self.friends_list.curselection()
#         if not sel:
#             return
#         i = sel[0]
#         self.friends.pop(i)
#         self.refresh_friend_list()

#     def start_tracking(self):
#         try:
#             path = self.config_path.get()
#             if not path:
#                 messagebox.showerror("Error", "Choose config.json first.")
#                 return

#             # load base config (we use load_config to honor CLI-like options in file)
#             cfg = load_config(path)
#             cfg["friends"] = self.friends

#             if self.output_path.get():
#                 cfg["output_path"] = self.output_path.get()

#             # pass theme selection to cfg so other parts can use it (optional)
#             cfg["chart_theme"] = self.chart_theme_key.get()

#             self.status_text.set("Running tracker...")
#             self.root.update_idletasks()

#             run_tracker(cfg)

#             self.status_text.set("Done!")
#             messagebox.showinfo("Success", "Tracking Completed.")
#         except Exception as e:
#             messagebox.showerror("Error", str(e))
#             self.status_text.set("Error occurred.")

#     def show_graphs(self):
#         try:
#             if not self.config_path.get():
#                 messagebox.showerror("Error", "Choose config.json first.")
#                 return

#             cfg = json.loads(Path(self.config_path.get()).read_text("utf-8"))
#             app_id = cfg.get("app_id")
#             if not app_id:
#                 messagebox.showerror("Error", "Invalid config.json — missing app_id.")
#                 return

#             from .history_utils import plot_progress, load_history
#             history = load_history(app_id)
#             if not history:
#                 messagebox.showwarning("No History", "No snapshots found for this game.\nRun the tracker first.")
#                 return

#             # propagate the chosen theme into the plot function by setting a small env param
#             plot_progress(app_id)

#             # open graphs folder
#             folder = Path("history") / str(app_id) / "graphs"
#             folder.mkdir(parents=True, exist_ok=True)

#             import platform, subprocess
#             if platform.system() == "Windows":
#                 subprocess.Popen(["explorer", str(folder.resolve())])
#             elif platform.system() == "Darwin":
#                 subprocess.Popen(["open", str(folder.resolve())])
#             else:
#                 subprocess.Popen(["xdg-open", str(folder.resolve())])

#             messagebox.showinfo("Done", "Graphs generated successfully!")
#         except Exception as e:
#             messagebox.showerror("Error generating graphs", str(e))

#     def load_game_image(self, app_id: int):
#         try:
#             img_path = game_header_path(app_id, "header.jpg")
#             if img_path.exists():
#                 img = Image.open(img_path)
#                 # scale width to 520 max while keeping aspect
#                 max_w = 520
#                 w = min(max_w, img.width)
#                 h = int(img.height * (w / img.width))
#                 img = img.resize((w, h), Image.LANCZOS)
#                 self.game_photo = ImageTk.PhotoImage(img)
#                 self.game_image_label.config(image=self.game_photo)
#             else:
#                 self.game_image_label.config(image="")
#         except Exception:
#             self.game_image_label.config(image="")
