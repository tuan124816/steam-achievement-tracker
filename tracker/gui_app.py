# import json
# import tkinter as tk
# from tkinter import filedialog, messagebox
# from pathlib import Path
# from .main import run_tracker
# from .config import load_config
# from .utils import log
# from .steam_utils import resolve_vanity_url
# from PIL import Image, ImageTk
# from .fetchers import fetch_game_info
# from .steam_cache import game_header_path



# def launch_gui():
#     root = tk.Tk()
#     root.title("Steam Achievement Tracker — GUI")
#     root.geometry("650x500")

#     App(root)
#     root.mainloop()


# class App:
#     def __init__(self, root):
#         self.root = root

#         # MENU BAR (NEW)
#         menubar = tk.Menu(self.root)
#         self.root.config(menu=menubar)

#         # ---- File Menu ----
#         file_menu = tk.Menu(menubar, tearoff=0)
#         menubar.add_cascade(label="File", menu=file_menu)

#         file_menu.add_command(label="Run Tracker", command=self.start_tracking)
#         file_menu.add_separator()
#         file_menu.add_command(label="Exit", command=self.root.quit)

#         # ---- Tools Menu ----
#         tools_menu = tk.Menu(menubar, tearoff=0)
#         menubar.add_cascade(label="Tools", menu=tools_menu)

#         tools_menu.add_command(label="Open Config", command=self.menu_open_config)
#         tools_menu.add_command(label="Regenerate Cookies", command=self.menu_regen_cookies)
#         tools_menu.add_separator()
#         tools_menu.add_command(label="Clear Cache", command=self.menu_clear_cache)

#         # ---- Help Menu ----
#         help_menu = tk.Menu(menubar, tearoff=0)
#         menubar.add_cascade(label="Help", menu=help_menu)

#         help_menu.add_command(label="GitHub", command=self.menu_open_github)
#         help_menu.add_command(label="About", command=self.menu_about)

#         # GUI state variables
#         self.config_path = tk.StringVar()
#         self.output_path = tk.StringVar()
#         self.status_text = tk.StringVar(value="Ready.")
#         self.game_name = tk.StringVar(value="(No game selected)")
#         self.game_image_label = None
#         self.game_photo = None    # MUST keep reference
#         self.chart_theme = tk.StringVar(value="light")


#         self.friends = []  # list of {"name": ..., "steamid": ...}

#         self.build_ui()
#         self.build_menu()

#     # Menu handler stubs (safe placeholders)
#     def menu_open_config(self):
#         self.pick_config()

#     def menu_regen_cookies(self):
#         messagebox.showinfo("TODO", "Cookie regeneration will be added in v1.3.")

#     def menu_clear_cache(self):
#         messagebox.showinfo("TODO", "Cache clearing will be added later.")

#     def menu_open_github(self):
#         messagebox.showinfo("GitHub", "Opening repository… (future feature)")

#     def menu_about(self):
#         messagebox.showinfo("About", "Steam Achievement Tracker\nVersion 1.2 GUI")

#     # UI Layout
#     def build_ui(self):
#         frm = tk.Frame(self.root, padx=10, pady=10)
#         frm.pack(fill="both", expand=True)

#         # === CONFIG PICKER ===
#         tk.Label(frm, text="Config File:").grid(row=0, column=0, sticky="w")
#         tk.Entry(frm, textvariable=self.config_path, width=50).grid(row=0, column=1)
#         tk.Button(frm, text="Browse", command=self.pick_config).grid(row=0, column=2)

#         # === Output path ===
#         tk.Label(frm, text="Output Excel:").grid(row=1, column=0, sticky="w")
#         tk.Entry(frm, textvariable=self.output_path, width=50).grid(row=1, column=1)
#         tk.Button(frm, text="Save As", command=self.pick_output).grid(row=1, column=2)

#         # === Friends table ===
#         tk.Label(frm, text="Friends:").grid(row=2, column=0, sticky="w", pady=(20, 5))

#         self.friends_list = tk.Listbox(frm, height=8, width=60)
#         self.friends_list.grid(row=3, column=0, columnspan=2)

#         bt_frame = tk.Frame(frm)
#         bt_frame.grid(row=3, column=2, sticky="n")

#         tk.Button(bt_frame, text="Add", width=8, command=self.add_friend).pack(pady=3)
#         tk.Button(bt_frame, text="Remove", width=8, command=self.remove_friend).pack(pady=3)

#         # === RUN BUTTON ===
#         tk.Button(frm, text="Start Tracking", font=("Arial", 14),
#                   command=self.start_tracking).grid(row=4, column=0, columnspan=3, pady=20)
        
#         # Show graph over time
#         tk.Button(frm, text="Show Progress Graphs", font=("Arial", 12),
#           command=self.show_graphs).grid(row=5, column=0, columnspan=3, pady=10)

#         # === Status area ===
#         tk.Label(frm, text="Status:").grid(row=6, column=0, sticky="w")
#         tk.Label(frm, textvariable=self.status_text, fg="blue").grid(row=7, column=0, columnspan=3, sticky="w")

#         # === GAME LABEL ===
#         tk.Label(frm, text="Game:").grid(row=8, column=0, sticky="w", pady=(20, 0))
#         tk.Label(frm, textvariable=self.game_name, font=("Arial", 14, "bold")).grid(row=9, column=0, columnspan=3, sticky="w")
        
#         # Image placeholder
#         self.game_image_label = tk.Label(frm)
#         self.game_image_label.grid(row=10, column=0, columnspan=3, pady=10)


#     # ---------------- Menu ---------------- #
#     def build_menu(self):
#         menubar = tk.Menu(self.root)
#         settings = tk.Menu(menubar, tearoff=0)
#         theme_menu = tk.Menu(settings, tearoff=0)
#         theme_menu.add_radiobutton(label="Light", variable=self.chart_theme, value="light")
#         theme_menu.add_radiobutton(label="Steam Dark", variable=self.chart_theme, value="steam")
#         settings.add_cascade(label="Chart Theme", menu=theme_menu)
#         menubar.add_cascade(label="Settings", menu=settings)
#         self.root.config(menu=menubar)

#     # ACTIONS BELOW
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
#             # Load game info
#             try:
#                 app_id = cfg.get("app_id")
#                 if app_id:
#                     gameinfo = fetch_game_info(app_id)
#                     self.game_name.set(gameinfo.get("name", "(Unknown Game)"))
#                     self.load_game_image(app_id)
#             except Exception as e:
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

#         tk.Label(popup, text="Name:").grid(row=0, column=0)
#         name_var = tk.StringVar()
#         tk.Entry(popup, textvariable=name_var).grid(row=0, column=1)

#         tk.Label(popup, text="SteamID / Vanity URL:").grid(row=1, column=0)
#         id_var = tk.StringVar()
#         tk.Entry(popup, textvariable=id_var).grid(row=1, column=1)

#         def save_friend():
#             name = name_var.get().strip()
#             sid = id_var.get().strip()

#             if "steamcommunity.com/id" in sid:
#                 try:
#                     sid = resolve_vanity_url(sid)
#                 except Exception:
#                     messagebox.showerror("Error", "Invalid vanity URL")
#                     return

#             self.friends.append({"name": name, "steamid": sid})
#             self.refresh_friend_list()
#             popup.destroy()

#         tk.Button(popup, text="Add", command=save_friend).grid(row=2, column=0, columnspan=2, pady=5)

#     def remove_friend(self):
#         idx = self.friends_list.curselection()
#         if not idx:
#             return
#         self.friends.pop(idx[0])
#         self.refresh_friend_list()

#     def start_tracking(self):
#         try:
#             path = self.config_path.get()
#             if not path:
#                 messagebox.showerror("Error", "Choose config.json first.")
#                 return

#             cfg = load_config(path)
#             cfg["friends"] = self.friends

#             if self.output_path.get():
#                 cfg["output_path"] = self.output_path.get()
            
#             # pass chart_theme into config so main.run_tracker receives it
#             cfg["chart_theme"] = self.chart_theme.get()

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
#             # Load config.json first (needed to get app_id)
#             if not self.config_path.get():
#                 messagebox.showerror("Error", "Choose config.json first.")
#                 return

#             cfg = json.loads(Path(self.config_path.get()).read_text("utf-8"))
#             app_id = cfg.get("app_id")

#             if not app_id:
#                 messagebox.showerror("Error", "Invalid config.json — missing app_id.")
#                 return

#             from .history_utils import plot_progress, load_history

#             # Check if history exists
#             history = load_history(app_id)
#             if len(history) == 0:
#                 messagebox.showwarning("No History", "No snapshots found for this game.\nRun the tracker first.")
#                 return

#             # Build graphs
#             plot_progress(app_id)

#             # Open folder in OS
#             folder = Path("history") / str(app_id) / "graphs"
#             folder.mkdir(parents=True, exist_ok=True)

#             # Open directory (Windows / macOS / Linux)
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
#             # Use the cached header file
#             img_path = game_header_path(app_id, "header.jpg")
#             if img_path.exists():
#                 img = Image.open(img_path)

#                 # Resize for GUI (header images are large)
#                 img = img.resize((400, int(img.height * (400 / img.width))), Image.LANCZOS)

#                 self.game_photo = ImageTk.PhotoImage(img)
#                 self.game_image_label.config(image=self.game_photo)
#             else:
#                 self.game_image_label.config(image="")
#         except Exception:
#             self.game_image_label.config(image="")










# # import json
# # import tkinter as tk
# # from tkinter import filedialog, messagebox
# # from pathlib import Path
# # from .main import run_tracker
# # from .config import load_config
# # from .utils import log
# # from .steam_utils import resolve_vanity_url
# # from PIL import Image, ImageTk
# # from .fetchers import fetch_game_info
# # from .steam_cache import game_header_path



# # def launch_gui():
# #     root = tk.Tk()
# #     root.title("Steam Achievement Tracker — GUI")
# #     root.geometry("650x500")

# #     App(root)
# #     root.mainloop()


# # class App:
# #     def __init__(self, root):
# #         self.root = root

# #         # MENU BAR
# #         menubar = tk.Menu(self.root)
# #         self.root.config(menu=menubar)

# #         # ---- File Menu ----
# #         file_menu = tk.Menu(menubar, tearoff=0)
# #         menubar.add_cascade(label="File", menu=file_menu)

# #         file_menu.add_command(label="Run Tracker", command=self.start_tracking)
# #         file_menu.add_separator()
# #         file_menu.add_command(label="Exit", command=self.root.quit)

# #         # ---- Tools Menu ----
# #         tools_menu = tk.Menu(menubar, tearoff=0)
# #         menubar.add_cascade(label="Tools", menu=tools_menu)

# #         tools_menu.add_command(label="Open Config", command=self.menu_open_config)
# #         tools_menu.add_command(label="Regenerate Cookies", command=self.menu_regen_cookies)
# #         tools_menu.add_separator()
# #         tools_menu.add_command(label="Clear Cache", command=self.menu_clear_cache)
# #         tools_menu.add_separator()
# #         tools_menu.add_command(label="Toggle Theme", command=self.toggle_theme)   # NEW

# #         # ---- Help Menu ----
# #         help_menu = tk.Menu(menubar, tearoff=0)
# #         menubar.add_cascade(label="Help", menu=help_menu)

# #         help_menu.add_command(label="GitHub", command=self.menu_open_github)
# #         help_menu.add_command(label="About", command=self.menu_about)

# #         # GUI state variables
# #         self.config_path = tk.StringVar()
# #         self.output_path = tk.StringVar()
# #         self.status_text = tk.StringVar(value="Ready.")
# #         self.game_name = tk.StringVar(value="(No game selected)")
# #         self.game_image_label = None
# #         self.game_photo = None

# #         self.theme = tk.StringVar(value="light")   # NEW
# #         self.friends = []

# #         self.build_ui()

# #     # Menu actions
# #     def menu_open_config(self):
# #         self.pick_config()

# #     def menu_regen_cookies(self):
# #         messagebox.showinfo("TODO", "Cookie regeneration will be added in v1.3.")

# #     def menu_clear_cache(self):
# #         messagebox.showinfo("TODO", "Cache clearing will be added later.")

# #     def menu_open_github(self):
# #         messagebox.showinfo("GitHub", "Opening repository… (future feature)")

# #     def menu_about(self):
# #         messagebox.showinfo("About", "Steam Achievement Tracker\nVersion 1.2 GUI")

# #     # ===========================
# #     #        THEME SYSTEM
# #     # ===========================
# #     def toggle_theme(self):
# #         """Switch between light and dark themes."""
# #         if self.theme.get() == "light":
# #             self.theme.set("dark")
# #             self.apply_dark_theme()
# #         else:
# #             self.theme.set("light")
# #             self.apply_light_theme()

# #     def apply_dark_theme(self):
# #         self.root.configure(bg="#1e1e1e")
# #         for widget in self.root.winfo_children():
# #             self._apply_theme_recursive(widget, dark=True)

# #     def apply_light_theme(self):
# #         self.root.configure(bg="SystemButtonFace")
# #         for widget in self.root.winfo_children():
# #             self._apply_theme_recursive(widget, dark=False)

# #     def _apply_theme_recursive(self, widget, dark: bool):
# #         """Apply theme to widget and all children."""
# #         bg = "#1e1e1e" if dark else "SystemButtonFace"
# #         fg = "#ffffff" if dark else "#000000"

# #         if isinstance(widget, (tk.Frame, tk.Label, tk.Button, tk.Entry, tk.Listbox)):
# #             try:
# #                 widget.configure(bg=bg, fg=fg)
# #             except Exception:
# #                 pass

# #         for child in widget.winfo_children():
# #             self._apply_theme_recursive(child, dark)

# #     # ===========================
# #     #        UI BUILD
# #     # ===========================
# #     def build_ui(self):
# #         frm = tk.Frame(self.root, padx=10, pady=10)
# #         frm.pack(fill="both", expand=True)

# #         tk.Label(frm, text="Config File:").grid(row=0, column=0, sticky="w")
# #         tk.Entry(frm, textvariable=self.config_path, width=50).grid(row=0, column=1)
# #         tk.Button(frm, text="Browse", command=self.pick_config).grid(row=0, column=2)

# #         tk.Label(frm, text="Output Excel:").grid(row=1, column=0, sticky="w")
# #         tk.Entry(frm, textvariable=self.output_path, width=50).grid(row=1, column=1)
# #         tk.Button(frm, text="Save As", command=self.pick_output).grid(row=1, column=2)

# #         tk.Label(frm, text="Friends:").grid(row=2, column=0, sticky="w", pady=(20, 5))

# #         self.friends_list = tk.Listbox(frm, height=8, width=60)
# #         self.friends_list.grid(row=3, column=0, columnspan=2)

# #         bt_frame = tk.Frame(frm)
# #         bt_frame.grid(row=3, column=2, sticky="n")

# #         tk.Button(bt_frame, text="Add", width=8, command=self.add_friend).pack(pady=3)
# #         tk.Button(bt_frame, text="Remove", width=8, command=self.remove_friend).pack(pady=3)

# #         tk.Button(frm, text="Start Tracking", font=("Arial", 14),
# #                   command=self.start_tracking).grid(row=4, column=0, columnspan=3, pady=20)

# #         tk.Button(frm, text="Show Progress Graphs", font=("Arial", 12),
# #                   command=self.show_graphs).grid(row=5, column=0, columnspan=3, pady=10)

# #         tk.Label(frm, text="Status:").grid(row=6, column=0, sticky="w")
# #         tk.Label(frm, textvariable=self.status_text, fg="blue").grid(row=7, column=0, columnspan=3, sticky="w")

# #         tk.Label(frm, text="Game:").grid(row=8, column=0, sticky="w", pady=(20, 0))
# #         tk.Label(frm, textvariable=self.game_name, font=("Arial", 14, "bold")).grid(row=9, column=0, columnspan=3, sticky="w")

# #         self.game_image_label = tk.Label(frm)
# #         self.game_image_label.grid(row=10, column=0, columnspan=3, pady=10)

# #     # ===========================
# #     #        ACTIONS
# #     # ===========================
# #     def pick_config(self):
# #         path = filedialog.askopenfilename(filetypes=[("JSON files", "*.json")])
# #         if path:
# #             self.config_path.set(path)
# #             self.load_config_file()

# #     def pick_output(self):
# #         path = filedialog.asksaveasfilename(defaultextension=".xlsx")
# #         if path:
# #             self.output_path.set(path)

# #     def load_config_file(self):
# #         try:
# #             cfg = json.loads(Path(self.config_path.get()).read_text("utf-8"))
# #             self.friends = cfg.get("friends", [])
# #             self.refresh_friend_list()

# #             try:
# #                 app_id = cfg.get("app_id")
# #                 if app_id:
# #                     gameinfo = fetch_game_info(app_id)
# #                     self.game_name.set(gameinfo.get("name", "(Unknown Game)"))
# #                     self.load_game_image(app_id)
# #             except Exception:
# #                 self.game_name.set("(Could not load game info)")

# #             self.status_text.set("Loaded config.json")
# #         except Exception as e:
# #             messagebox.showerror("Error", str(e))

# #     def refresh_friend_list(self):
# #         self.friends_list.delete(0, tk.END)
# #         for f in self.friends:
# #             self.friends_list.insert(tk.END, f"{f['name']} — {f['steamid']}")

# #     def add_friend(self):
# #         popup = tk.Toplevel(self.root)
# #         popup.title("Add Friend")

# #         tk.Label(popup, text="Name:").grid(row=0, column=0)
# #         name_var = tk.StringVar()
# #         tk.Entry(popup, textvariable=name_var).grid(row=0, column=1)

# #         tk.Label(popup, text="SteamID / Vanity URL:").grid(row=1, column=0)
# #         id_var = tk.StringVar()
# #         tk.Entry(popup, textvariable=id_var).grid(row=1, column=1)

# #         def save_friend():
# #             name = name_var.get().strip()
# #             sid = id_var.get().strip()

# #             if "steamcommunity.com/id" in sid:
# #                 try:
# #                     sid = resolve_vanity_url(sid)
# #                 except Exception:
# #                     messagebox.showerror("Error", "Invalid vanity URL")
# #                     return

# #             self.friends.append({"name": name, "steamid": sid})
# #             self.refresh_friend_list()
# #             popup.destroy()

# #         tk.Button(popup, text="Add", command=save_friend).grid(row=2, column=0, columnspan=2, pady=5)

# #     def remove_friend(self):
# #         idx = self.friends_list.curselection()
# #         if not idx:
# #             return
# #         self.friends.pop(idx[0])
# #         self.refresh_friend_list()

# #     def start_tracking(self):
# #         try:
# #             path = self.config_path.get()
# #             if not path:
# #                 messagebox.showerror("Error", "Choose config.json first.")
# #                 return

# #             cfg = load_config(path)
# #             cfg["friends"] = self.friends

# #             if self.output_path.get():
# #                 cfg["output_path"] = self.output_path.get()

# #             self.status_text.set("Running tracker...")
# #             self.root.update_idletasks()

# #             run_tracker(cfg)

# #             self.status_text.set("Done!")
# #             messagebox.showinfo("Success", "Tracking Completed.")

# #         except Exception as e:
# #             messagebox.showerror("Error", str(e))
# #             self.status_text.set("Error occurred.")

# #     def show_graphs(self):
# #         try:
# #             if not self.config_path.get():
# #                 messagebox.showerror("Error", "Choose config.json first.")
# #                 return

# #             cfg = json.loads(Path(self.config_path.get()).read_text("utf-8"))
# #             app_id = cfg.get("app_id")

# #             if not app_id:
# #                 messagebox.showerror("Error", "Invalid config.json — missing app_id.")
# #                 return

# #             from .history_utils import plot_progress, load_history

# #             history = load_history(app_id)
# #             if len(history) == 0:
# #                 messagebox.showwarning("No History", "No snapshots found.\nRun the tracker first.")
# #                 return

# #             plot_progress(app_id)

# #             folder = Path("history") / str(app_id) / "graphs"
# #             folder.mkdir(parents=True, exist_ok=True)

# #             import platform, subprocess

# #             if platform.system() == "Windows":
# #                 subprocess.Popen(["explorer", str(folder.resolve())])
# #             elif platform.system() == "Darwin":
# #                 subprocess.Popen(["open", str(folder.resolve())])
# #             else:
# #                 subprocess.Popen(["xdg-open", str(folder.resolve())])

# #             messagebox.showinfo("Done", "Graphs generated successfully!")

# #         except Exception as e:
# #             messagebox.showerror("Error generating graphs", str(e))

# #     def load_game_image(self, app_id: int):
# #         try:
# #             img_path = game_header_path(app_id, "header.jpg")
# #             if img_path.exists():
# #                 img = Image.open(img_path)
# #                 img = img.resize((400, int(img.height * (400 / img.width))), Image.LANCZOS)
# #                 self.game_photo = ImageTk.PhotoImage(img)
# #                 self.game_image_label.config(image=self.game_photo)
# #             else:
# #                 self.game_image_label.config(image="")
# #         except Exception:
# #             self.game_image_label.config(image="")

"""
gui_app.py
----------
Tkinter GUI for Steam Achievement Tracker.

Features added in this version:
- Menu bar with File / Tools / Settings / Help.
- 4 selectable UI themes (Light, Dark, Steam, Graph).
- Theme persistence in `theme_config.json`.
- Game header preview (uses cached header image if available).
- Run Tracker and Show Graphs buttons integrated.
- Vanity URL resolution when adding friends.
- Safe placeholders for cookie regen / cache clear (can be connected later).

Drop this file into `tracker/gui_app.py` (overwrite existing).
"""






















# import json
# import tkinter as tk
# from tkinter import filedialog, messagebox
# from pathlib import Path
# from typing import Dict, Any
# from .main import run_tracker
# from .config import load_config
# from .utils import log
# from .steam_utils import resolve_vanity_url
# from PIL import Image, ImageTk
# from .fetchers import fetch_game_info
# from .steam_cache import game_header_path

# # Where to persist theme choice
# THEME_FILE = Path("theme_config.json")


# # ---------------- Theme definitions ---------------- #
# THEMES: Dict[str, Dict[str, str]] = {
#     "light": {
#         "bg": "#F7F8FB",
#         "fg": "#0f1724",
#         "btn_bg": "#E9F0FF",
#         "btn_fg": "#0f1724",
#         "accent": "#2B66C3",
#         "status_fg": "#0a66a3",
#     },
#     "dark": {
#         "bg": "#1e1f26",
#         "fg": "#e6eef5",
#         "btn_bg": "#2b2f38",
#         "btn_fg": "#e6eef5",
#         "accent": "#6fb3ff",
#         "status_fg": "#9bd0ff",
#     },
#     "steam": {
#         # Steam-ish palette
#         "bg": "#0f1724",            # deep navy
#         "fg": "#d6e6f3",            # light text
#         "btn_bg": "#1b2838",        # steam-blue
#         "btn_fg": "#d6e6f3",
#         "accent": "#66a6ff",
#         "status_fg": "#9bd0ff",
#     },
#     "graph": {
#         # Soft blues like history graphs
#         "bg": "#ffffff",
#         "fg": "#123e6f",
#         "btn_bg": "#eef6ff",
#         "btn_fg": "#123e6f",
#         "accent": "#2B66C3",
#         "status_fg": "#2B66C3",
#     },
# }


# def save_theme_choice(name: str) -> None:
#     try:
#         THEME_FILE.write_text(json.dumps({"theme": name}), encoding="utf-8")
#     except Exception:
#         # best-effort, don't crash the GUI for IO issues
#         pass


# def load_theme_choice() -> str:
#     try:
#         if THEME_FILE.exists():
#             data = json.loads(THEME_FILE.read_text(encoding="utf-8"))
#             t = data.get("theme")
#             if t in THEMES:
#                 return t
#     except Exception:
#         pass
#     return "light"


# def apply_theme_recursive(widget: tk.Widget, theme: Dict[str, str]) -> None:
#     """
#     Apply color scheme to widget and children, best-effort.
#     We don't attempt to style every widget option for every widget class,
#     but cover the common ones (Frame, Label, Entry, Button, Listbox).
#     """
#     try:
#         cls = widget.winfo_class()
#         bg = theme["bg"]
#         fg = theme["fg"]
#         btn_bg = theme["btn_bg"]
#         btn_fg = theme["btn_fg"]

#         if cls in ("TFrame", "Frame"):
#             widget.configure(bg=bg)
#         elif cls in ("TLabel", "Label"):
#             widget.configure(bg=bg, fg=fg)
#         elif cls in ("TButton", "Button"):
#             widget.configure(bg=btn_bg, fg=btn_fg, activebackground=theme.get("accent", btn_bg))
#         elif cls in ("TEntry", "Entry"):
#             widget.configure(bg="#ffffff" if theme["bg"] != "#ffffff" else "#f6f8fc", fg=fg)
#         elif cls in ("Listbox",):
#             widget.configure(bg="#ffffff" if theme["bg"] != "#ffffff" else "#f6f8fc", fg=fg)
#         elif cls in ("TMenubutton", "Menubutton"):
#             widget.configure(bg=btn_bg, fg=btn_fg)
#         # some widgets (like Canvas) we skip styling
#     except Exception:
#         pass

#     # recurse
#     for child in widget.winfo_children():
#         apply_theme_recursive(child, theme)


# # ---------------- GUI Implementation ---------------- #
# def launch_gui() -> None:
#     root = tk.Tk()
#     root.title("Steam Achievement Tracker — GUI")
#     root.geometry("650x520")
#     App(root)
#     root.mainloop()


# class App:
#     def __init__(self, root: tk.Tk):
#         self.root = root

#         # load theme preference
#         self.current_theme_name = load_theme_choice()
#         self.current_theme = THEMES.get(self.current_theme_name, THEMES["light"])

#         # GUI state variables
#         self.config_path = tk.StringVar()
#         self.output_path = tk.StringVar()
#         self.status_text = tk.StringVar(value="Ready.")
#         self.game_name = tk.StringVar(value="(No game selected)")
#         self.game_image_label = None
#         self.game_photo = None    # MUST keep reference
#         self.chart_theme = tk.StringVar(value=self.current_theme_name)

#         self.friends = []  # list of {"name": ..., "steamid": ...}

#         # build UI and menus
#         self.build_ui()
#         self.build_menus()

#         # apply theme after widgets exist
#         self.apply_theme(self.current_theme_name)

#     # ---------------- Menu building ---------------- #
#     def build_menus(self) -> None:
#         menubar = tk.Menu(self.root)

#         # File menu
#         file_menu = tk.Menu(menubar, tearoff=0)
#         file_menu.add_command(label="Run Tracker", command=self.start_tracking)
#         file_menu.add_separator()
#         file_menu.add_command(label="Exit", command=self.root.quit)
#         menubar.add_cascade(label="File", menu=file_menu)

#         # Tools menu
#         tools_menu = tk.Menu(menubar, tearoff=0)
#         tools_menu.add_command(label="Open Config", command=self.menu_open_config)
#         tools_menu.add_command(label="Regenerate Cookies", command=self.menu_regen_cookies)
#         tools_menu.add_separator()
#         tools_menu.add_command(label="Clear Cache", command=self.menu_clear_cache)
#         menubar.add_cascade(label="Tools", menu=tools_menu)

#         # Settings menu -> Theme selector
#         settings_menu = tk.Menu(menubar, tearoff=0)
#         theme_menu = tk.Menu(settings_menu, tearoff=0)

#         for key in THEMES.keys():
#             theme_menu.add_radiobutton(
#                 label=key.capitalize(),
#                 value=key,
#                 variable=self.chart_theme,
#                 command=lambda k=key: self.on_theme_change(k)
#             )
#         settings_menu.add_cascade(label="Theme", menu=theme_menu)
#         menubar.add_cascade(label="Settings", menu=settings_menu)

#         # Help
#         help_menu = tk.Menu(menubar, tearoff=0)
#         help_menu.add_command(label="GitHub", command=self.menu_open_github)
#         help_menu.add_command(label="About", command=self.menu_about)
#         menubar.add_cascade(label="Help", menu=help_menu)

#         self.root.config(menu=menubar)

#     # ---------------- UI Layout ---------------- #
#     def build_ui(self) -> None:
#         frm = tk.Frame(self.root, padx=10, pady=10)
#         frm.pack(fill="both", expand=True)

#         # === CONFIG PICKER ===
#         tk.Label(frm, text="Config File:").grid(row=0, column=0, sticky="w")
#         tk.Entry(frm, textvariable=self.config_path, width=50).grid(row=0, column=1)
#         tk.Button(frm, text="Browse", command=self.pick_config).grid(row=0, column=2)

#         # === Output path ===
#         tk.Label(frm, text="Output Excel:").grid(row=1, column=0, sticky="w")
#         tk.Entry(frm, textvariable=self.output_path, width=50).grid(row=1, column=1)
#         tk.Button(frm, text="Save As", command=self.pick_output).grid(row=1, column=2)

#         # === Friends table ===
#         tk.Label(frm, text="Friends:").grid(row=2, column=0, sticky="w", pady=(16, 4))

#         self.friends_list = tk.Listbox(frm, height=8, width=60)
#         self.friends_list.grid(row=3, column=0, columnspan=2, sticky="w")

#         bt_frame = tk.Frame(frm)
#         bt_frame.grid(row=3, column=2, sticky="n")

#         tk.Button(bt_frame, text="Add", width=8, command=self.add_friend).pack(pady=3)
#         tk.Button(bt_frame, text="Remove", width=8, command=self.remove_friend).pack(pady=3)

#         # === RUN BUTTON ===
#         tk.Button(frm, text="Start Tracking", font=("Arial", 14),
#                   command=self.start_tracking).grid(row=4, column=0, columnspan=3, pady=16)

#         # Show graph over time
#         tk.Button(frm, text="Show Progress Graphs", font=("Arial", 12),
#                   command=self.show_graphs).grid(row=5, column=0, columnspan=3, pady=(0, 12))

#         # === Status area ===
#         tk.Label(frm, text="Status:").grid(row=6, column=0, sticky="w")
#         tk.Label(frm, textvariable=self.status_text, fg=self.current_theme.get("status_fg", "#2B66C3")).grid(
#             row=7, column=0, columnspan=3, sticky="w"
#         )

#         # === GAME LABEL & IMAGE ===
#         tk.Label(frm, text="Game:").grid(row=8, column=0, sticky="w", pady=(18, 0))
#         tk.Label(frm, textvariable=self.game_name, font=("Arial", 14, "bold")).grid(
#             row=9, column=0, columnspan=3, sticky="w"
#         )

#         self.game_image_label = tk.Label(frm)
#         self.game_image_label.grid(row=10, column=0, columnspan=3, pady=6)

#     # ---------------- Menu handler stubs ---------------- #
#     def menu_open_config(self) -> None:
#         self.pick_config()

#     def menu_regen_cookies(self) -> None:
#         # Placeholder: keep UX safe. In future we can call generate_steam_cookies here.
#         messagebox.showinfo("Regenerate Cookies", "This will launch the Steam login helper in v1.3.")

#     def menu_clear_cache(self) -> None:
#         # Placeholder: warn before clearing
#         if messagebox.askyesno("Clear Cache", "Clear cached schema/icons?"):
#             from .steam_cache import CACHE_DIR
#             try:
#                 import shutil
#                 shutil.rmtree(CACHE_DIR)
#                 messagebox.showinfo("Cache Cleared", "Cache folder removed. It will be recreated on next run.")
#             except Exception as e:
#                 messagebox.showerror("Error", f"Failed to clear cache: {e}")

#     def menu_open_github(self) -> None:
#         # simple info for now; could open a URL later
#         messagebox.showinfo("GitHub", "Repository: https://github.com/your/repo (placeholder)")

#     def menu_about(self) -> None:
#         messagebox.showinfo("About", "Steam Achievement Tracker\nVersion 1.2+ (GUI)")

#     # ---------------- Actions ---------------- #
#     def pick_config(self) -> None:
#         path = filedialog.askopenfilename(filetypes=[("JSON files", "*.json")])
#         if path:
#             self.config_path.set(path)
#             self.load_config_file()

#     def pick_output(self) -> None:
#         path = filedialog.asksaveasfilename(defaultextension=".xlsx")
#         if path:
#             self.output_path.set(path)

#     def load_config_file(self) -> None:
#         try:
#             cfg = json.loads(Path(self.config_path.get()).read_text("utf-8"))
#             self.friends = cfg.get("friends", [])
#             self.refresh_friend_list()

#             # Load game info (non-blocking best-effort)
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

#     def refresh_friend_list(self) -> None:
#         self.friends_list.delete(0, tk.END)
#         for f in self.friends:
#             self.friends_list.insert(tk.END, f"{f['name']} — {f['steamid']}")

#     def add_friend(self) -> None:
#         popup = tk.Toplevel(self.root)
#         popup.title("Add Friend")

#         tk.Label(popup, text="Name:").grid(row=0, column=0, sticky="w", padx=6, pady=6)
#         name_var = tk.StringVar()
#         tk.Entry(popup, textvariable=name_var, width=40).grid(row=0, column=1, padx=6, pady=6)

#         tk.Label(popup, text="SteamID / Vanity URL:").grid(row=1, column=0, sticky="w", padx=6, pady=6)
#         id_var = tk.StringVar()
#         tk.Entry(popup, textvariable=id_var, width=40).grid(row=1, column=1, padx=6, pady=6)

#         def save_friend() -> None:
#             name = name_var.get().strip()
#             sid = id_var.get().strip()

#             if not name or not sid:
#                 messagebox.showerror("Error", "Name and SteamID are required.")
#                 return

#             if "steamcommunity.com/id" in sid:
#                 try:
#                     sid = resolve_vanity_url(sid)
#                 except Exception:
#                     messagebox.showerror("Error", "Invalid vanity URL")
#                     return

#             self.friends.append({"name": name, "steamid": sid})
#             self.refresh_friend_list()
#             popup.destroy()

#         tk.Button(popup, text="Add", command=save_friend).grid(row=2, column=0, columnspan=2, pady=8)

#     def remove_friend(self) -> None:
#         idx = self.friends_list.curselection()
#         if not idx:
#             return
#         self.friends.pop(idx[0])
#         self.refresh_friend_list()

#     def start_tracking(self) -> None:
#         try:
#             path = self.config_path.get()
#             if not path:
#                 messagebox.showerror("Error", "Choose config.json first.")
#                 return

#             cfg = load_config(path)
#             cfg["friends"] = self.friends

#             if self.output_path.get():
#                 cfg["output_path"] = self.output_path.get()

#             # pass theme choice to run_tracker (optional)
#             cfg["chart_theme"] = self.chart_theme.get()

#             self.status_text.set("Running tracker...")
#             self.root.update_idletasks()

#             run_tracker(cfg)

#             self.status_text.set("Done!")
#             messagebox.showinfo("Success", "Tracking Completed.")
#         except Exception as e:
#             messagebox.showerror("Error", str(e))
#             self.status_text.set("Error occurred.")

#     def show_graphs(self) -> None:
#         try:
#             # Load config.json first (needed to get app_id)
#             if not self.config_path.get():
#                 messagebox.showerror("Error", "Choose config.json first.")
#                 return

#             cfg = json.loads(Path(self.config_path.get()).read_text("utf-8"))
#             app_id = cfg.get("app_id")

#             if not app_id:
#                 messagebox.showerror("Error", "Invalid config.json — missing app_id.")
#                 return

#             from .history_utils import plot_progress, load_history

#             # Check if history exists
#             history = load_history(app_id)
#             if len(history) == 0:
#                 messagebox.showwarning("No History", "No snapshots found for this game.\nRun the tracker first.")
#                 return

#             # Build graphs (plot_progress writes image files)
#             # plot_progress(app_id, theme=self.chart_theme.get())
#             theme = THEMES.get(self.chart_theme.get(), THEMES["light"])
#             plot_progress(app_id, theme=theme)

#             # Open folder in OS where graphs were saved
#             folder = Path("history") / str(app_id) / "graphs"
#             folder.mkdir(parents=True, exist_ok=True)

#             # Open directory (Windows / macOS / Linux)
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

#     def load_game_image(self, app_id: int) -> None:
#         try:
#             # Use the cached header file
#             img_path = game_header_path(app_id, "header.jpg")
#             if img_path.exists():
#                 img = Image.open(img_path)

#                 # Resize for GUI (header images are large)
#                 img = img.resize((400, int(img.height * (400 / img.width))), Image.LANCZOS)

#                 self.game_photo = ImageTk.PhotoImage(img)
#                 self.game_image_label.config(image=self.game_photo)
#             else:
#                 self.game_image_label.config(image="")
#         except Exception:
#             self.game_image_label.config(image="")

#     # ---------------- Theme helpers ---------------- #
#     def on_theme_change(self, key: str) -> None:
#         """User selected a new theme from the menu."""
#         if key not in THEMES:
#             return
#         self.chart_theme.set(key)
#         self.apply_theme(key)
#         save_theme_choice(key)

#     def apply_theme(self, key: str) -> None:
#         """Apply a theme to the whole GUI (best-effort)."""
#         theme = THEMES.get(key, THEMES["light"])

#         # apply root background
#         try:
#             self.root.configure(bg=theme["bg"])
#         except Exception:
#             pass

#         # apply recursively to widgets
#         apply_theme_recursive(self.root, theme)

#         # update status color explicitly
#         try:
#             # we set the status Label's fg if possible
#             for w in self.root.winfo_children():
#                 if isinstance(w, tk.Frame):
#                     for ch in w.winfo_children():
#                         if getattr(ch, "cget", None) and ch.cget("text") == "Status:":
#                             # the next widget is the status value label
#                             # not bulletproof but helpful
#                             pass
#         except Exception:
#             pass

#         # keep current theme name
#         self.current_theme_name = key
#         self.current_theme = theme

#         # set status color explicitly on the status label if present
#         try:
#             # find label that displays status_text
#             for w in self.root.winfo_children():
#                 for ch in w.winfo_children():
#                     if isinstance(ch, tk.Label) and getattr(ch, "cget", None) and ch.cget("textvariable") == str(self.status_text):
#                         ch.configure(fg=theme.get("status_fg", theme.get("accent", "#2B66C3")))
#         except Exception:
#             pass


# # allow running the GUI module directly: python -m tracker.gui_app
# if __name__ == "__main__":
#     launch_gui()












"""
gui_app.py
----------
Tkinter GUI for Steam Achievement Tracker (v1.2+).

Features implemented here:
- Config / output picker
- Add / remove friends (vanity URL resolver)
- Run tracker from GUI (calls run_tracker(cfg))
- Show progress graphs (uses history_utils.plot_progress)
- Game header preview (uses steam_cache cached header)
- Menu: File / Tools / Help / Settings
- Theme system: multiple predefined themes, live preview, apply theme
- Regenerate cookies menu item wired to generate_steam_cookies(COOKIE_FILE)
- Clear cache & Open GitHub are placeholders (safe)
"""

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
        self.apply_theme(key)

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
