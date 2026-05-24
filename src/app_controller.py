import tkinter as tk
from tkinter import messagebox
import customtkinter as ctk
import src.constants as const
from src.data_manager import DataManager
from src.gui.sidebar_view import SidebarView
from src.gui.calculator_view import CalculatorView
from src.gui.profiles_view import ProfilesView
from src.gui.history_view import HistoryView

class BMICalculatorApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        # Window settings
        self.title("BMI Calculator")
        self.geometry("1000x650")
        self.minsize(980, 620)
        
        # Default appearance
        ctk.set_appearance_mode("Light")
        
        # Configure layout (2 columns: Sidebar & Content Area)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # Instantiate State Manager
        self.data_manager = DataManager()
        self.current_user_id = 1

        # Left Sidebar View
        self.sidebar = SidebarView(
            parent=self, 
            on_tab_select=self.select_tab, 
            on_theme_change=self.change_appearance_mode
        )
        self.sidebar.grid(row=0, column=0, sticky="nsew")

        # Right Content Area Container
        self.container_frame = ctk.CTkFrame(self, corner_radius=0, fg_color=const.COLOR_BG)
        self.container_frame.grid(row=0, column=1, sticky="nsew")
        self.container_frame.grid_columnconfigure(0, weight=1)
        self.container_frame.grid_rowconfigure(0, weight=1)

        # Instantiate View Sub-Frames
        self.calculator_view = CalculatorView(
            parent=self.container_frame, 
            data_manager=self.data_manager,
            on_save_record=self.on_save_record,
            get_active_user_id_cb=self.get_active_user_id,
            on_user_switch_cb=self.on_user_switch
        )
        
        self.profiles_view = ProfilesView(
            parent=self.container_frame,
            data_manager=self.data_manager,
            get_active_user_id_cb=self.get_active_user_id,
            on_user_create_cb=self.on_user_create,
            on_user_delete_cb=self.on_user_delete
        )
        
        self.history_view = HistoryView(
            parent=self.container_frame,
            data_manager=self.data_manager,
            get_active_user_id_cb=self.get_active_user_id
        )

        self.views = {
            "calculator": self.calculator_view,
            "profiles": self.profiles_view,
            "history": self.history_view
        }

        # Select calculator tab on startup
        self.select_tab("calculator")

    def get_active_user_id(self):
        return self.current_user_id

    def select_tab(self, tab_name):
        """Hides inactive views and grid packs the selected view."""
        for name, frame in self.views.items():
            frame.grid_forget()
        
        self.views[tab_name].grid(row=0, column=0, sticky="nsew", padx=25, pady=25)
        self.sidebar.set_active_tab(tab_name)

        # Context updates on tab switch
        if tab_name == "history":
            self.history_view.refresh_history_tab()
        elif tab_name == "calculator":
            self.calculator_view.refresh_user_dropdown()
        elif tab_name == "profiles":
            self.profiles_view.refresh_profiles_list()

    def change_appearance_mode(self, new_mode):
        ctk.set_appearance_mode(new_mode)
        # Give Tkinter time to swap theme properties before rendering charts
        self.after(50, lambda: self.history_view.refresh_matplotlib_chart() if self.views["history"].winfo_ismapped() else None)

    def on_user_switch(self, user_id):
        """Sets active profile, fetches their latest data measurements, and updates calculator fields."""
        self.current_user_id = user_id
        history = self.data_manager.get_user_history(user_id)
        
        if history:
            # Load user's latest recorded measurements
            latest = history[0]
            h, w = latest["height"], latest["weight"]
            
            # Update inputs
            if self.calculator_view.unit_toggle.get() == "Metric":
                self.calculator_view.set_inputs(h, w)
            else:
                h_in = h / 2.54
                w_lb = w / 0.45359237
                self.calculator_view.set_inputs(h_in, w_lb)
        else:
            # Set default metrics
            h_def = const.RANGE_METRIC["height"]["default"] if self.calculator_view.unit_toggle.get() == "Metric" else const.RANGE_IMPERIAL["height"]["default"]
            w_def = const.RANGE_METRIC["weight"]["default"] if self.calculator_view.unit_toggle.get() == "Metric" else const.RANGE_IMPERIAL["weight"]["default"]
            self.calculator_view.set_inputs(h_def, w_def)

    def on_user_create(self, name, age, gender):
        """Adds user in state manager, updates views and sets as active."""
        try:
            new_id = self.data_manager.add_user(name, age, gender)
            self.current_user_id = new_id
            
            self.profiles_view.refresh_profiles_list()
            self.calculator_view.refresh_user_dropdown()
            self.on_user_switch(new_id)
            
            messagebox.showinfo("Success", f"Profile for '{name}' created successfully!")
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def on_user_delete(self, user_id):
        """Validates, removes profile in manager, and updates interface view state."""
        user_name = self.data_manager.users[user_id]["name"]
        
        if len(self.data_manager.users) <= 1:
            messagebox.showerror("Error", "You must keep at least one user profile.")
            return
            
        confirm = messagebox.askyesno("Confirm Delete", f"Are you sure you want to delete profile '{user_name}' and all their historical weight logs?")
        if not confirm:
            return

        try:
            self.data_manager.delete_user(user_id)
            
            # Shift active user focus if deleted
            if self.current_user_id == user_id:
                remaining_id = list(self.data_manager.users.keys())[0]
                self.current_user_id = remaining_id
                self.on_user_switch(remaining_id)
                
            self.profiles_view.refresh_profiles_list()
            self.calculator_view.refresh_user_dropdown()
            messagebox.showinfo("Deleted", f"Profile for '{user_name}' has been deleted.")
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def on_save_record(self, weight, height, bmi, category):
        """Saves active user record to history (normalizing imperial units)."""
        active_id = self.current_user_id
        user_name = self.data_manager.users[active_id]["name"]
        
        # Database normalization: height and weight saved in metric format (cm/kg)
        if self.calculator_view.unit_toggle.get() == "Imperial":
            h_cm = height * 2.54
            w_kg = weight * 0.45359237
        else:
            h_cm = height
            w_kg = weight

        self.data_manager.add_history_record(active_id, w_kg, h_cm, bmi, category)
        messagebox.showinfo("Record Logged", f"Weight record (BMI: {bmi:.1f}) saved successfully for {user_name}!")
