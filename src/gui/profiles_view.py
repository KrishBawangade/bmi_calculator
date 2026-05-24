import tkinter as tk
from tkinter import messagebox
import customtkinter as ctk
import src.constants as const

class ProfilesView(ctk.CTkFrame):
    def __init__(self, parent, data_manager, get_active_user_id_cb, on_user_create_cb, on_user_delete_cb):
        super().__init__(parent, fg_color="transparent")
        
        self.data_manager = data_manager
        self.get_active_user_id_cb = get_active_user_id_cb
        self.on_user_create_cb = on_user_create_cb
        self.on_user_delete_cb = on_user_delete_cb
        
        self.grid_columnconfigure(0, weight=2)
        self.grid_columnconfigure(1, weight=3)
        self.grid_rowconfigure(0, weight=1)

        # Traced variables for form validation
        self.name_var = tk.StringVar()
        self.age_var = tk.StringVar()
        self.name_var.trace_add("write", self.validate_name_on_type)
        self.age_var.trace_add("write", self.validate_age_on_type)

        self.setup_left_form()
        self.setup_right_list()
        
        self.refresh_profiles_list()

    def setup_left_form(self):
        form_frame = ctk.CTkFrame(
            self, 
            fg_color=const.COLOR_CARD_BG, 
            corner_radius=15, 
            border_width=1, 
            border_color=const.COLOR_BORDER
        )
        form_frame.grid(row=0, column=0, sticky="nsew", padx=(0, 10))
        form_frame.grid_columnconfigure(0, weight=1)

        form_title = ctk.CTkLabel(
            form_frame, 
            text="Create Profile", 
            font=ctk.CTkFont(size=20, weight="bold"),
            text_color=const.COLOR_TEXT
        )
        form_title.grid(row=0, column=0, padx=25, pady=(25, 20), sticky="w")

        # Name Entry
        name_lbl = ctk.CTkLabel(form_frame, text="Full Name", font=ctk.CTkFont(size=13, weight="bold"), text_color=const.COLOR_TEXT)
        name_lbl.grid(row=1, column=0, padx=25, pady=(5, 2), sticky="w")
        self.profile_name_entry = ctk.CTkEntry(form_frame, fg_color=const.COLOR_BG, border_color=const.COLOR_BORDER, text_color=const.COLOR_TEXT, textvariable=self.name_var)
        self.profile_name_entry.grid(row=2, column=0, padx=25, pady=(0, 15), sticky="ew")

        # Age Entry
        age_lbl = ctk.CTkLabel(form_frame, text="Age (years)", font=ctk.CTkFont(size=13, weight="bold"), text_color=const.COLOR_TEXT)
        age_lbl.grid(row=3, column=0, padx=25, pady=(5, 2), sticky="w")
        self.profile_age_entry = ctk.CTkEntry(form_frame, fg_color=const.COLOR_BG, border_color=const.COLOR_BORDER, text_color=const.COLOR_TEXT, textvariable=self.age_var)
        self.profile_age_entry.grid(row=4, column=0, padx=25, pady=(0, 15), sticky="ew")

        # Gender Entry
        gender_lbl = ctk.CTkLabel(form_frame, text="Gender", font=ctk.CTkFont(size=13, weight="bold"), text_color=const.COLOR_TEXT)
        gender_lbl.grid(row=5, column=0, padx=25, pady=(5, 2), sticky="w")
        self.profile_gender_select = ctk.CTkSegmentedButton(
            form_frame,
            values=["Male", "Female", "Other"],
            selected_color=const.COLOR_ACCENT,
            selected_hover_color=const.COLOR_ACCENT_HOVER,
            fg_color=const.COLOR_BG,
            text_color=const.COLOR_TEXT
        )
        self.profile_gender_select.grid(row=6, column=0, padx=25, pady=(0, 20), sticky="ew")
        self.profile_gender_select.set("Female")

        # Create Button
        self.create_profile_btn = ctk.CTkButton(
            form_frame,
            text="Add User Profile",
            font=ctk.CTkFont(size=14, weight="bold"),
            fg_color=const.COLOR_ACCENT,
            hover_color=const.COLOR_ACCENT_HOVER,
            text_color="#FFFFFF",
            height=40,
            command=self.create_profile
        )
        self.create_profile_btn.grid(row=7, column=0, padx=25, pady=10, sticky="ew")

    def setup_right_list(self):
        list_frame = ctk.CTkFrame(
            self, 
            fg_color=const.COLOR_CARD_BG, 
            corner_radius=15, 
            border_width=1, 
            border_color=const.COLOR_BORDER
        )
        list_frame.grid(row=0, column=1, sticky="nsew", padx=(10, 0))
        list_frame.grid_columnconfigure(0, weight=1)
        list_frame.grid_rowconfigure(1, weight=1)

        list_title = ctk.CTkLabel(
            list_frame, 
            text="Existing Profiles", 
            font=ctk.CTkFont(size=20, weight="bold"),
            text_color=const.COLOR_TEXT
        )
        list_title.grid(row=0, column=0, padx=25, pady=(25, 10), sticky="w")

        # Scrollable container for profile list
        self.profiles_scroll = ctk.CTkScrollableFrame(
            list_frame, 
            fg_color="transparent"
        )
        self.profiles_scroll.grid(row=1, column=0, padx=20, pady=(0, 20), sticky="nsew")
        self.profiles_scroll.grid_columnconfigure(0, weight=1)

    def refresh_profiles_list(self):
        """Cleans and re-renders profile cards list frame."""
        for widget in self.profiles_scroll.winfo_children():
            widget.destroy()

        active_id = self.get_active_user_id_cb()

        for uid, user in self.data_manager.users.items():
            is_active = (uid == active_id)
            card = ctk.CTkFrame(
                self.profiles_scroll, 
                fg_color=const.COLOR_BG, 
                corner_radius=10,
                border_width=2 if is_active else 1,
                border_color=const.COLOR_ACCENT if is_active else const.COLOR_BORDER
            )
            card.pack(fill="x", pady=6, padx=5)
            
            # Profile Avatar Box
            icon_frame = ctk.CTkFrame(card, width=45, height=45, corner_radius=22, fg_color=const.COLOR_ACCENT)
            icon_frame.pack(side="left", padx=15, pady=12)
            icon_frame.pack_propagate(False)
            
            letter = user["name"][0].upper() if user["name"] else "U"
            icon_lbl = ctk.CTkLabel(icon_frame, text=letter, text_color="#FFFFFF", font=ctk.CTkFont(size=18, weight="bold"))
            icon_lbl.pack(fill="both", expand=True)

            # Profile Info Text
            info_frame = ctk.CTkFrame(card, fg_color="transparent")
            info_frame.pack(side="left", fill="both", expand=True, pady=10)
            
            name_lbl = ctk.CTkLabel(info_frame, text=user["name"], font=ctk.CTkFont(size=15, weight="bold"), text_color=const.COLOR_TEXT, anchor="w")
            name_lbl.pack(fill="x")
            
            meta_lbl = ctk.CTkLabel(
                info_frame, 
                text=f"Age: {user['age']}  •  Gender: {user['gender']}", 
                font=ctk.CTkFont(size=12), 
                text_color=const.COLOR_TEXT_MUTED,
                anchor="w"
            )
            meta_lbl.pack(fill="x")

            # Selection State Tag
            if is_active:
                tag_frame = ctk.CTkFrame(card, fg_color=const.COLOR_ACCENT, corner_radius=10, height=22)
                tag_frame.pack(side="right", padx=(0, 10))
                tag_lbl = ctk.CTkLabel(tag_frame, text="Active", text_color="#FFFFFF", font=ctk.CTkFont(size=10, weight="bold"), padx=8)
                tag_lbl.pack()

            # Delete Button
            delete_btn = ctk.CTkButton(
                card,
                text="Delete",
                width=60,
                height=28,
                fg_color="#E76F51",
                hover_color="#C85237",
                text_color="#FFFFFF",
                font=ctk.CTkFont(size=11, weight="bold"),
                command=lambda target_id=uid: self.delete_profile(target_id)
            )
            delete_btn.pack(side="right", padx=15)

            # Bind click events on all child elements to select profile
            for widget in [card, icon_frame, icon_lbl, info_frame, name_lbl, meta_lbl]:
                widget.bind("<Button-1>", lambda e, target_id=uid: self.activate_profile(target_id))
            if is_active:
                tag_frame.bind("<Button-1>", lambda e, target_id=uid: self.activate_profile(target_id))
                tag_lbl.bind("<Button-1>", lambda e, target_id=uid: self.activate_profile(target_id))

    def validate_name_on_type(self, *args):
        name = self.name_var.get().strip()
        if len(name) >= 2:
            self.profile_name_entry.configure(border_color=const.COLOR_BORDER)

    def validate_age_on_type(self, *args):
        age_str = self.age_var.get().strip()
        try:
            age = int(age_str)
            if 1 <= age <= 120:
                self.profile_age_entry.configure(border_color=const.COLOR_BORDER)
        except ValueError:
            pass

    def activate_profile(self, user_id):
        """Tells root application to switch active profile."""
        app = self.winfo_toplevel()
        if hasattr(app, "on_user_switch"):
            app.on_user_switch(user_id)
            self.refresh_profiles_list()

    def create_profile(self):
        """Fetches form inputs, validates, and updates outer context."""
        name = self.name_var.get().strip()
        age_str = self.age_var.get().strip()
        gender = self.profile_gender_select.get()

        valid = True
        
        # Validate name
        if len(name) < 2:
            self.profile_name_entry.configure(border_color="#E76F51") # red error border
            valid = False
        else:
            self.profile_name_entry.configure(border_color=const.COLOR_BORDER)
            
        # Validate age
        try:
            age = int(age_str)
            if age <= 0 or age > 120:
                raise ValueError
            self.profile_age_entry.configure(border_color=const.COLOR_BORDER)
        except ValueError:
            self.profile_age_entry.configure(border_color="#E76F51") # red error border
            valid = False

        if not valid:
            messagebox.showwarning("Validation Error", "Please fill in all fields with valid information.")
            return

        # Let parent handle state insertion
        self.on_user_create_cb(name, age, gender)

        # Clear entries
        self.name_var.set("")
        self.age_var.set("")
        self.profile_gender_select.set("Female")

    def delete_profile(self, user_id):
        """Triggers outer callback to delete profile."""
        self.on_user_delete_cb(user_id)
