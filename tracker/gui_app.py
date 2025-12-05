import json
import tkinter as tk
from tkinter import filedialog, messagebox
from pathlib import Path
from .main import run_tracker
from .config import load_config
from .utils import log
from .steam_utils import resolve_vanity_url
from PIL import Image, ImageTk
from .fetchers import fetch_game_info
from .steam_cache import game_header_path



def launch_gui():
    root = tk.Tk()
    root.title("Steam Achievement Tracker — GUI")
    root.geometry("650x500")

    App(root)
    root.mainloop()


class App:
    def __init__(self, root):
        self.root = root

        # MENU BAR (NEW)
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)

        # ---- File Menu ----
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="File", menu=file_menu)

        file_menu.add_command(label="Run Tracker", command=self.start_tracking)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.root.quit)

        # ---- Tools Menu ----
        tools_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Tools", menu=tools_menu)

        tools_menu.add_command(label="Open Config", command=self.menu_open_config)
        tools_menu.add_command(label="Regenerate Cookies", command=self.menu_regen_cookies)
        tools_menu.add_separator()
        tools_menu.add_command(label="Clear Cache", command=self.menu_clear_cache)

        # ---- Help Menu ----
        help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Help", menu=help_menu)

        help_menu.add_command(label="GitHub", command=self.menu_open_github)
        help_menu.add_command(label="About", command=self.menu_about)

        # GUI state variables
        self.config_path = tk.StringVar()
        self.output_path = tk.StringVar()
        self.status_text = tk.StringVar(value="Ready.")
        self.game_name = tk.StringVar(value="(No game selected)")
        self.game_image_label = None
        self.game_photo = None    # MUST keep reference
        self.chart_theme = tk.StringVar(value="light")


        self.friends = []  # list of {"name": ..., "steamid": ...}

        self.build_ui()
        self.build_menu()

    # Menu handler stubs (safe placeholders)
    def menu_open_config(self):
        self.pick_config()

    def menu_regen_cookies(self):
        messagebox.showinfo("TODO", "Cookie regeneration will be added in v1.3.")

    def menu_clear_cache(self):
        messagebox.showinfo("TODO", "Cache clearing will be added later.")

    def menu_open_github(self):
        messagebox.showinfo("GitHub", "Opening repository… (future feature)")

    def menu_about(self):
        messagebox.showinfo("About", "Steam Achievement Tracker\nVersion 1.2 GUI")

    # UI Layout
    def build_ui(self):
        frm = tk.Frame(self.root, padx=10, pady=10)
        frm.pack(fill="both", expand=True)

        # === CONFIG PICKER ===
        tk.Label(frm, text="Config File:").grid(row=0, column=0, sticky="w")
        tk.Entry(frm, textvariable=self.config_path, width=50).grid(row=0, column=1)
        tk.Button(frm, text="Browse", command=self.pick_config).grid(row=0, column=2)

        # === Output path ===
        tk.Label(frm, text="Output Excel:").grid(row=1, column=0, sticky="w")
        tk.Entry(frm, textvariable=self.output_path, width=50).grid(row=1, column=1)
        tk.Button(frm, text="Save As", command=self.pick_output).grid(row=1, column=2)

        # === Friends table ===
        tk.Label(frm, text="Friends:").grid(row=2, column=0, sticky="w", pady=(20, 5))

        self.friends_list = tk.Listbox(frm, height=8, width=60)
        self.friends_list.grid(row=3, column=0, columnspan=2)

        bt_frame = tk.Frame(frm)
        bt_frame.grid(row=3, column=2, sticky="n")

        tk.Button(bt_frame, text="Add", width=8, command=self.add_friend).pack(pady=3)
        tk.Button(bt_frame, text="Remove", width=8, command=self.remove_friend).pack(pady=3)

        # === RUN BUTTON ===
        tk.Button(frm, text="Start Tracking", font=("Arial", 14),
                  command=self.start_tracking).grid(row=4, column=0, columnspan=3, pady=20)
        
        # Show graph over time
        tk.Button(frm, text="Show Progress Graphs", font=("Arial", 12),
          command=self.show_graphs).grid(row=5, column=0, columnspan=3, pady=10)

        # === Status area ===
        tk.Label(frm, text="Status:").grid(row=6, column=0, sticky="w")
        tk.Label(frm, textvariable=self.status_text, fg="blue").grid(row=7, column=0, columnspan=3, sticky="w")

        # === GAME LABEL ===
        tk.Label(frm, text="Game:").grid(row=8, column=0, sticky="w", pady=(20, 0))
        tk.Label(frm, textvariable=self.game_name, font=("Arial", 14, "bold")).grid(row=9, column=0, columnspan=3, sticky="w")
        
        # Image placeholder
        self.game_image_label = tk.Label(frm)
        self.game_image_label.grid(row=10, column=0, columnspan=3, pady=10)


    # ---------------- Menu ---------------- #
    def build_menu(self):
        menubar = tk.Menu(self.root)
        settings = tk.Menu(menubar, tearoff=0)
        theme_menu = tk.Menu(settings, tearoff=0)
        theme_menu.add_radiobutton(label="Light", variable=self.chart_theme, value="light")
        theme_menu.add_radiobutton(label="Steam Dark", variable=self.chart_theme, value="steam")
        settings.add_cascade(label="Chart Theme", menu=theme_menu)
        menubar.add_cascade(label="Settings", menu=settings)
        self.root.config(menu=menubar)

    # ACTIONS BELOW
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
            # Load game info
            try:
                app_id = cfg.get("app_id")
                if app_id:
                    gameinfo = fetch_game_info(app_id)
                    self.game_name.set(gameinfo.get("name", "(Unknown Game)"))
                    self.load_game_image(app_id)
            except Exception as e:
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

        tk.Label(popup, text="Name:").grid(row=0, column=0)
        name_var = tk.StringVar()
        tk.Entry(popup, textvariable=name_var).grid(row=0, column=1)

        tk.Label(popup, text="SteamID / Vanity URL:").grid(row=1, column=0)
        id_var = tk.StringVar()
        tk.Entry(popup, textvariable=id_var).grid(row=1, column=1)

        def save_friend():
            name = name_var.get().strip()
            sid = id_var.get().strip()

            if "steamcommunity.com/id" in sid:
                try:
                    sid = resolve_vanity_url(sid)
                except Exception:
                    messagebox.showerror("Error", "Invalid vanity URL")
                    return

            self.friends.append({"name": name, "steamid": sid})
            self.refresh_friend_list()
            popup.destroy()

        tk.Button(popup, text="Add", command=save_friend).grid(row=2, column=0, columnspan=2, pady=5)

    def remove_friend(self):
        idx = self.friends_list.curselection()
        if not idx:
            return
        self.friends.pop(idx[0])
        self.refresh_friend_list()

    def start_tracking(self):
        try:
            path = self.config_path.get()
            if not path:
                messagebox.showerror("Error", "Choose config.json first.")
                return

            cfg = load_config(path)
            cfg["friends"] = self.friends

            if self.output_path.get():
                cfg["output_path"] = self.output_path.get()
            
            # pass chart_theme into config so main.run_tracker receives it
            cfg["chart_theme"] = self.chart_theme.get()

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
            # Load config.json first (needed to get app_id)
            if not self.config_path.get():
                messagebox.showerror("Error", "Choose config.json first.")
                return

            cfg = json.loads(Path(self.config_path.get()).read_text("utf-8"))
            app_id = cfg.get("app_id")

            if not app_id:
                messagebox.showerror("Error", "Invalid config.json — missing app_id.")
                return

            from .history_utils import plot_progress, load_history

            # Check if history exists
            history = load_history(app_id)
            if len(history) == 0:
                messagebox.showwarning("No History", "No snapshots found for this game.\nRun the tracker first.")
                return

            # Build graphs
            plot_progress(app_id)

            # Open folder in OS
            folder = Path("history") / str(app_id) / "graphs"
            folder.mkdir(parents=True, exist_ok=True)

            # Open directory (Windows / macOS / Linux)
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
            # Use the cached header file
            img_path = game_header_path(app_id, "header.jpg")
            if img_path.exists():
                img = Image.open(img_path)

                # Resize for GUI (header images are large)
                img = img.resize((400, int(img.height * (400 / img.width))), Image.LANCZOS)

                self.game_photo = ImageTk.PhotoImage(img)
                self.game_image_label.config(image=self.game_photo)
            else:
                self.game_image_label.config(image="")
        except Exception:
            self.game_image_label.config(image="")










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

#         # MENU BAR
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
#         tools_menu.add_separator()
#         tools_menu.add_command(label="Toggle Theme", command=self.toggle_theme)   # NEW

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
#         self.game_photo = None

#         self.theme = tk.StringVar(value="light")   # NEW
#         self.friends = []

#         self.build_ui()

#     # Menu actions
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

#     # ===========================
#     #        THEME SYSTEM
#     # ===========================
#     def toggle_theme(self):
#         """Switch between light and dark themes."""
#         if self.theme.get() == "light":
#             self.theme.set("dark")
#             self.apply_dark_theme()
#         else:
#             self.theme.set("light")
#             self.apply_light_theme()

#     def apply_dark_theme(self):
#         self.root.configure(bg="#1e1e1e")
#         for widget in self.root.winfo_children():
#             self._apply_theme_recursive(widget, dark=True)

#     def apply_light_theme(self):
#         self.root.configure(bg="SystemButtonFace")
#         for widget in self.root.winfo_children():
#             self._apply_theme_recursive(widget, dark=False)

#     def _apply_theme_recursive(self, widget, dark: bool):
#         """Apply theme to widget and all children."""
#         bg = "#1e1e1e" if dark else "SystemButtonFace"
#         fg = "#ffffff" if dark else "#000000"

#         if isinstance(widget, (tk.Frame, tk.Label, tk.Button, tk.Entry, tk.Listbox)):
#             try:
#                 widget.configure(bg=bg, fg=fg)
#             except Exception:
#                 pass

#         for child in widget.winfo_children():
#             self._apply_theme_recursive(child, dark)

#     # ===========================
#     #        UI BUILD
#     # ===========================
#     def build_ui(self):
#         frm = tk.Frame(self.root, padx=10, pady=10)
#         frm.pack(fill="both", expand=True)

#         tk.Label(frm, text="Config File:").grid(row=0, column=0, sticky="w")
#         tk.Entry(frm, textvariable=self.config_path, width=50).grid(row=0, column=1)
#         tk.Button(frm, text="Browse", command=self.pick_config).grid(row=0, column=2)

#         tk.Label(frm, text="Output Excel:").grid(row=1, column=0, sticky="w")
#         tk.Entry(frm, textvariable=self.output_path, width=50).grid(row=1, column=1)
#         tk.Button(frm, text="Save As", command=self.pick_output).grid(row=1, column=2)

#         tk.Label(frm, text="Friends:").grid(row=2, column=0, sticky="w", pady=(20, 5))

#         self.friends_list = tk.Listbox(frm, height=8, width=60)
#         self.friends_list.grid(row=3, column=0, columnspan=2)

#         bt_frame = tk.Frame(frm)
#         bt_frame.grid(row=3, column=2, sticky="n")

#         tk.Button(bt_frame, text="Add", width=8, command=self.add_friend).pack(pady=3)
#         tk.Button(bt_frame, text="Remove", width=8, command=self.remove_friend).pack(pady=3)

#         tk.Button(frm, text="Start Tracking", font=("Arial", 14),
#                   command=self.start_tracking).grid(row=4, column=0, columnspan=3, pady=20)

#         tk.Button(frm, text="Show Progress Graphs", font=("Arial", 12),
#                   command=self.show_graphs).grid(row=5, column=0, columnspan=3, pady=10)

#         tk.Label(frm, text="Status:").grid(row=6, column=0, sticky="w")
#         tk.Label(frm, textvariable=self.status_text, fg="blue").grid(row=7, column=0, columnspan=3, sticky="w")

#         tk.Label(frm, text="Game:").grid(row=8, column=0, sticky="w", pady=(20, 0))
#         tk.Label(frm, textvariable=self.game_name, font=("Arial", 14, "bold")).grid(row=9, column=0, columnspan=3, sticky="w")

#         self.game_image_label = tk.Label(frm)
#         self.game_image_label.grid(row=10, column=0, columnspan=3, pady=10)

#     # ===========================
#     #        ACTIONS
#     # ===========================
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
#             if len(history) == 0:
#                 messagebox.showwarning("No History", "No snapshots found.\nRun the tracker first.")
#                 return

#             plot_progress(app_id)

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
#                 img = img.resize((400, int(img.height * (400 / img.width))), Image.LANCZOS)
#                 self.game_photo = ImageTk.PhotoImage(img)
#                 self.game_image_label.config(image=self.game_photo)
#             else:
#                 self.game_image_label.config(image="")
#         except Exception:
#             self.game_image_label.config(image="")

