import customtkinter as ctk
import src.constants as const

class SidebarView(ctk.CTkFrame):
    def __init__(self, parent, on_tab_select, on_theme_change):
        super().__init__(parent, width=200, corner_radius=0, fg_color=const.COLOR_SIDEBAR_BG)
        
        self.on_tab_select = on_tab_select
        self.on_theme_change = on_theme_change
        
        self.grid_rowconfigure(5, weight=1)

        # App Logo & Title
        self.title_label = ctk.CTkLabel(
            self, 
            text="BMI Calculator", 
            font=ctk.CTkFont(family="Helvetica", size=22, weight="bold"),
            text_color=const.COLOR_TEXT
        )
        self.title_label.grid(row=0, column=0, padx=20, pady=(30, 20))

        # Navigation Buttons
        self.nav_calc_btn = ctk.CTkButton(
            self,
            text="Calculator",
            font=ctk.CTkFont(size=14, weight="bold"),
            fg_color="transparent",
            text_color=const.COLOR_TEXT,
            hover_color=const.COLOR_BORDER,
            anchor="w",
            height=40,
            command=lambda: self._select_tab("calculator")
        )
        self.nav_calc_btn.grid(row=1, column=0, padx=15, pady=5, sticky="ew")

        self.nav_profiles_btn = ctk.CTkButton(
            self,
            text="User Profiles",
            font=ctk.CTkFont(size=14, weight="bold"),
            fg_color="transparent",
            text_color=const.COLOR_TEXT,
            hover_color=const.COLOR_BORDER,
            anchor="w",
            height=40,
            command=lambda: self._select_tab("profiles")
        )
        self.nav_profiles_btn.grid(row=2, column=0, padx=15, pady=5, sticky="ew")

        self.nav_history_btn = ctk.CTkButton(
            self,
            text="History & Trends",
            font=ctk.CTkFont(size=14, weight="bold"),
            fg_color="transparent",
            text_color=const.COLOR_TEXT,
            hover_color=const.COLOR_BORDER,
            anchor="w",
            height=40,
            command=lambda: self._select_tab("history")
        )
        self.nav_history_btn.grid(row=3, column=0, padx=15, pady=5, sticky="ew")

        # Theme Selector (At the bottom of the sidebar)
        self.theme_label = ctk.CTkLabel(
            self, 
            text="Theme Preference", 
            font=ctk.CTkFont(size=11),
            text_color=const.COLOR_TEXT_MUTED
        )
        self.theme_label.grid(row=6, column=0, padx=20, pady=(10, 0), sticky="w")

        self.theme_menu = ctk.CTkOptionMenu(
            self,
            values=["Light", "Dark", "System"],
            command=self._change_theme,
            fg_color=const.COLOR_ACCENT,
            button_color=const.COLOR_ACCENT,
            button_hover_color=const.COLOR_ACCENT_HOVER,
            text_color="#FFFFFF"
        )
        self.theme_menu.grid(row=7, column=0, padx=15, pady=(5, 30), sticky="ew")
        
        self.buttons = {
            "calculator": self.nav_calc_btn,
            "profiles": self.nav_profiles_btn,
            "history": self.nav_history_btn
        }

    def _select_tab(self, tab_name):
        """Highlights the active button and executes outer callback."""
        for name, btn in self.buttons.items():
            if name == tab_name:
                btn.configure(fg_color=const.COLOR_ACCENT, text_color="#FFFFFF")
            else:
                btn.configure(fg_color="transparent", text_color=const.COLOR_TEXT)
        
        self.on_tab_select(tab_name)

    def set_active_tab(self, tab_name):
        """External helper to force highlight state."""
        for name, btn in self.buttons.items():
            if name == tab_name:
                btn.configure(fg_color=const.COLOR_ACCENT, text_color="#FFFFFF")
            else:
                btn.configure(fg_color="transparent", text_color=const.COLOR_TEXT)

    def _change_theme(self, new_theme):
        self.on_theme_change(new_theme)
