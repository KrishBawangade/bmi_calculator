import tkinter as tk
import customtkinter as ctk
import src.constants as const

class CalculatorView(ctk.CTkFrame):
    def __init__(self, parent, data_manager, on_save_record, get_active_user_id_cb, on_user_switch_cb):
        super().__init__(parent, fg_color="transparent")
        
        self.data_manager = data_manager
        self.on_save_record = on_save_record
        self.get_active_user_id_cb = get_active_user_id_cb
        self.on_user_switch_cb = on_user_switch_cb
        
        self.grid_columnconfigure(0, weight=3)
        self.grid_columnconfigure(1, weight=2)
        self.grid_rowconfigure(0, weight=1)

        # Variables
        self.unit_system = tk.StringVar(value="Metric")
        self.height_var = tk.StringVar(value="168.0")
        self.weight_var = tk.StringVar(value="63.0")

        self.setup_left_inputs()
        self.setup_right_results()

        # Bind variables to trace callbacks for live-update
        self.height_var.trace_add("write", self.on_height_entry_change)
        self.weight_var.trace_add("write", self.on_weight_entry_change)
        
        # Trigger initial calculation
        self.recalculate_bmi()

    def setup_left_inputs(self):
        input_frame = ctk.CTkFrame(
            self, 
            fg_color=const.COLOR_CARD_BG, 
            corner_radius=15, 
            border_width=1, 
            border_color=const.COLOR_BORDER
        )
        input_frame.grid(row=0, column=0, sticky="nsew", padx=(0, 10))
        input_frame.grid_columnconfigure(0, weight=1)

        # Tab Title
        input_title = ctk.CTkLabel(
            input_frame, 
            text="Calculate BMI", 
            font=ctk.CTkFont(size=20, weight="bold"),
            text_color=const.COLOR_TEXT
        )
        input_title.grid(row=0, column=0, padx=25, pady=(25, 20), sticky="w")

        # Profile selection
        profile_container = ctk.CTkFrame(input_frame, fg_color="transparent")
        profile_container.grid(row=1, column=0, padx=25, pady=10, sticky="ew")
        profile_container.grid_columnconfigure(1, weight=1)

        profile_lbl = ctk.CTkLabel(
            profile_container, 
            text="User Profile:", 
            font=ctk.CTkFont(size=14),
            text_color=const.COLOR_TEXT
        )
        profile_lbl.grid(row=0, column=0, padx=(0, 10), sticky="w")

        self.user_dropdown = ctk.CTkOptionMenu(
            profile_container,
            values=[],
            command=self.on_dropdown_select,
            fg_color=const.COLOR_BG,
            text_color=const.COLOR_TEXT,
            button_color=const.COLOR_ACCENT,
            button_hover_color=const.COLOR_ACCENT_HOVER,
            dropdown_fg_color=const.COLOR_CARD_BG,
            dropdown_text_color=const.COLOR_TEXT
        )
        self.user_dropdown.grid(row=0, column=1, sticky="ew")

        # Unit selector
        unit_container = ctk.CTkFrame(input_frame, fg_color="transparent")
        unit_container.grid(row=2, column=0, padx=25, pady=10, sticky="ew")
        unit_container.grid_columnconfigure(1, weight=1)

        unit_lbl = ctk.CTkLabel(
            unit_container, 
            text="Unit System:", 
            font=ctk.CTkFont(size=14),
            text_color=const.COLOR_TEXT
        )
        unit_lbl.grid(row=0, column=0, padx=(0, 10), sticky="w")

        self.unit_toggle = ctk.CTkSegmentedButton(
            unit_container,
            values=["Metric", "Imperial"],
            command=self.toggle_units,
            selected_color=const.COLOR_ACCENT,
            selected_hover_color=const.COLOR_ACCENT_HOVER,
            fg_color=const.COLOR_BG,
            text_color=const.COLOR_TEXT
        )
        self.unit_toggle.grid(row=0, column=1, sticky="ew")
        self.unit_toggle.set("Metric")

        # Height Input Frame
        height_card = ctk.CTkFrame(input_frame, fg_color=const.COLOR_BG, corner_radius=10)
        height_card.grid(row=3, column=0, padx=25, pady=15, sticky="ew")

        height_header = ctk.CTkFrame(height_card, fg_color="transparent")
        height_header.pack(fill="x", padx=15, pady=(10, 5))
        
        self.height_label = ctk.CTkLabel(
            height_header, 
            text="Height", 
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color=const.COLOR_TEXT
        )
        self.height_label.pack(side="left")

        self.height_unit_lbl = ctk.CTkLabel(
            height_header, 
            text="cm", 
            font=ctk.CTkFont(size=12),
            text_color=const.COLOR_TEXT_MUTED
        )
        self.height_unit_lbl.pack(side="right")

        self.height_entry = ctk.CTkEntry(
            height_header, 
            width=70, 
            textvariable=self.height_var,
            fg_color=const.COLOR_CARD_BG,
            text_color=const.COLOR_TEXT,
            border_color=const.COLOR_BORDER
        )
        self.height_entry.pack(side="right", padx=(0, 10))

        self.height_slider = ctk.CTkSlider(
            height_card,
            from_=const.RANGE_METRIC["height"]["min"],
            to=const.RANGE_METRIC["height"]["max"],
            command=self.on_height_slider_move,
            button_color=const.COLOR_ACCENT,
            button_hover_color=const.COLOR_ACCENT_HOVER,
            progress_color=const.COLOR_ACCENT,
            fg_color=const.COLOR_BORDER
        )
        self.height_slider.pack(fill="x", padx=15, pady=(5, 15))
        self.height_slider.set(const.RANGE_METRIC["height"]["default"])

        # Weight Input Frame
        weight_card = ctk.CTkFrame(input_frame, fg_color=const.COLOR_BG, corner_radius=10)
        weight_card.grid(row=4, column=0, padx=25, pady=15, sticky="ew")

        weight_header = ctk.CTkFrame(weight_card, fg_color="transparent")
        weight_header.pack(fill="x", padx=15, pady=(10, 5))
        
        self.weight_label = ctk.CTkLabel(
            weight_header, 
            text="Weight", 
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color=const.COLOR_TEXT
        )
        self.weight_label.pack(side="left")

        self.weight_unit_lbl = ctk.CTkLabel(
            weight_header, 
            text="kg", 
            font=ctk.CTkFont(size=12),
            text_color=const.COLOR_TEXT_MUTED
        )
        self.weight_unit_lbl.pack(side="right")

        self.weight_entry = ctk.CTkEntry(
            weight_header, 
            width=70, 
            textvariable=self.weight_var,
            fg_color=const.COLOR_CARD_BG,
            text_color=const.COLOR_TEXT,
            border_color=const.COLOR_BORDER
        )
        self.weight_entry.pack(side="right", padx=(0, 10))

        self.weight_slider = ctk.CTkSlider(
            weight_card,
            from_=const.RANGE_METRIC["weight"]["min"],
            to=const.RANGE_METRIC["weight"]["max"],
            command=self.on_weight_slider_move,
            button_color=const.COLOR_ACCENT,
            button_hover_color=const.COLOR_ACCENT_HOVER,
            progress_color=const.COLOR_ACCENT,
            fg_color=const.COLOR_BORDER
        )
        self.weight_slider.pack(fill="x", padx=15, pady=(5, 15))
        self.weight_slider.set(const.RANGE_METRIC["weight"]["default"])

        # Calculate Button
        self.calc_btn = ctk.CTkButton(
            input_frame,
            text="Calculate BMI Score",
            font=ctk.CTkFont(size=15, weight="bold"),
            fg_color=const.COLOR_ACCENT,
            hover_color=const.COLOR_ACCENT_HOVER,
            text_color="#FFFFFF",
            height=45,
            command=self.recalculate_bmi
        )
        self.calc_btn.grid(row=5, column=0, padx=25, pady=25, sticky="ew")

    def setup_right_results(self):
        result_frame = ctk.CTkFrame(
            self, 
            fg_color=const.COLOR_CARD_BG, 
            corner_radius=15, 
            border_width=1, 
            border_color=const.COLOR_BORDER
        )
        result_frame.grid(row=0, column=1, sticky="nsew", padx=(10, 0))
        result_frame.grid_columnconfigure(0, weight=1)

        result_title = ctk.CTkLabel(
            result_frame, 
            text="Your Results", 
            font=ctk.CTkFont(size=20, weight="bold"),
            text_color=const.COLOR_TEXT
        )
        result_title.grid(row=0, column=0, padx=25, pady=(25, 20), sticky="w")

        # Score Card
        self.score_card = ctk.CTkFrame(result_frame, fg_color=const.COLOR_BG, corner_radius=10, height=130)
        self.score_card.grid(row=1, column=0, padx=25, pady=10, sticky="ew")
        self.score_card.grid_propagate(False)
        self.score_card.grid_columnconfigure(0, weight=1)
        self.score_card.grid_rowconfigure(0, weight=1)

        score_sub_frame = ctk.CTkFrame(self.score_card, fg_color="transparent")
        score_sub_frame.grid(row=0, column=0)
        
        self.score_val_lbl = ctk.CTkLabel(
            score_sub_frame, 
            text="--", 
            font=ctk.CTkFont(size=42, weight="bold"),
            text_color=const.COLOR_ACCENT
        )
        self.score_val_lbl.grid(row=0, column=0)

        self.score_status_lbl = ctk.CTkLabel(
            score_sub_frame, 
            text="--", 
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color=const.COLOR_TEXT_MUTED
        )
        self.score_status_lbl.grid(row=1, column=0)

        # Gauge Canvas
        self.gauge_container = ctk.CTkFrame(result_frame, fg_color="transparent", height=70)
        self.gauge_container.grid(row=2, column=0, padx=25, pady=10, sticky="ew")
        self.gauge_container.grid_propagate(False)

        self.gauge_canvas = ctk.CTkCanvas(
            self.gauge_container, 
            height=60, 
            highlightthickness=0
        )
        self.gauge_canvas.pack(fill="both", expand=True)
        self.gauge_canvas.bind("<Configure>", lambda e: self.draw_gauge())

        # Description
        desc_card = ctk.CTkFrame(result_frame, fg_color=const.COLOR_BG, corner_radius=10)
        desc_card.grid(row=3, column=0, padx=25, pady=15, sticky="ew")

        self.desc_lbl = ctk.CTkLabel(
            desc_card,
            text="",
            font=ctk.CTkFont(size=13),
            text_color=const.COLOR_TEXT,
            wraplength=250,
            justify="center"
        )
        self.desc_lbl.pack(padx=15, pady=15)

        # Save Button
        self.save_record_btn = ctk.CTkButton(
            result_frame,
            text="Save Record to History",
            font=ctk.CTkFont(size=14, weight="bold"),
            fg_color="transparent",
            text_color=const.COLOR_ACCENT,
            border_width=2,
            border_color=const.COLOR_ACCENT,
            hover_color=const.COLOR_BORDER,
            height=40,
            command=self.save_record
        )
        self.save_record_btn.grid(row=4, column=0, padx=25, pady=(10, 25), sticky="ew")

    def refresh_user_dropdown(self):
        """Re-reads profiles list and resets dropdown value."""
        users_list = self.data_manager.users
        names = [u["name"] for u in users_list.values()]
        self.user_dropdown.configure(values=names)
        
        active_id = self.get_active_user_id_cb()
        if active_id in users_list:
            self.user_dropdown.set(users_list[active_id]["name"])

    def set_inputs(self, height, weight):
        """Sets inputs directly."""
        self.height_var.set(f"{height:.1f}")
        self.weight_var.set(f"{weight:.1f}")
        self.height_slider.set(height)
        self.weight_slider.set(weight)
        self.recalculate_bmi()

    def toggle_units(self, new_system):
        """Converts and updates current height/weight slider bounds."""
        prev_system = "Imperial" if new_system == "Metric" else "Metric"
        if prev_system == new_system:
            return
            
        self.unit_system.set(new_system)

        try:
            h = float(self.height_var.get())
            w = float(self.weight_var.get())
        except ValueError:
            h = const.RANGE_METRIC["height"]["default"] if new_system == "Metric" else const.RANGE_IMPERIAL["height"]["default"]
            w = const.RANGE_METRIC["weight"]["default"] if new_system == "Metric" else const.RANGE_IMPERIAL["weight"]["default"]

        if new_system == "Metric":
            new_h = h * 2.54
            new_w = w * 0.45359237
            
            self.height_label.configure(text="Height")
            self.height_unit_lbl.configure(text="cm")
            self.height_slider.configure(from_=const.RANGE_METRIC["height"]["min"], to=const.RANGE_METRIC["height"]["max"])
            
            self.weight_label.configure(text="Weight")
            self.weight_unit_lbl.configure(text="kg")
            self.weight_slider.configure(from_=const.RANGE_METRIC["weight"]["min"], to=const.RANGE_METRIC["weight"]["max"])
        else:
            new_h = h / 2.54
            new_w = w / 0.45359237
            
            self.height_label.configure(text="Height")
            self.height_unit_lbl.configure(text="in")
            self.height_slider.configure(from_=const.RANGE_IMPERIAL["height"]["min"], to=const.RANGE_IMPERIAL["height"]["max"])
            
            self.weight_label.configure(text="Weight")
            self.weight_unit_lbl.configure(text="lbs")
            self.weight_slider.configure(from_=const.RANGE_IMPERIAL["weight"]["min"], to=const.RANGE_IMPERIAL["weight"]["max"])

        self.height_var.set(f"{new_h:.1f}")
        self.weight_var.set(f"{new_w:.1f}")
        self.height_slider.set(new_h)
        self.weight_slider.set(new_w)
        
        self.recalculate_bmi()

    def on_height_slider_move(self, value):
        self.height_var.set(f"{value:.1f}")
        self.recalculate_bmi()

    def on_weight_slider_move(self, value):
        self.weight_var.set(f"{value:.1f}")
        self.recalculate_bmi()

    def on_height_entry_change(self, *args):
        try:
            val = float(self.height_var.get())
            limits = const.RANGE_METRIC["height"] if self.unit_toggle.get() == "Metric" else const.RANGE_IMPERIAL["height"]
            if limits["min"] <= val <= limits["max"]:
                self.height_slider.set(val)
                self.recalculate_bmi()
        except ValueError:
            pass

    def on_weight_entry_change(self, *args):
        try:
            val = float(self.weight_var.get())
            limits = const.RANGE_METRIC["weight"] if self.unit_toggle.get() == "Metric" else const.RANGE_IMPERIAL["weight"]
            if limits["min"] <= val <= limits["max"]:
                self.weight_slider.set(val)
                self.recalculate_bmi()
        except ValueError:
            pass

    def on_dropdown_select(self, val):
        for uid, user_data in self.data_manager.users.items():
            if user_data["name"] == val:
                self.on_user_switch_cb(uid)
                break

    def recalculate_bmi(self):
        """Performs math calculation and updates output fields."""
        try:
            h = float(self.height_var.get())
            w = float(self.weight_var.get())
            
            bmi = self.data_manager.calculate_bmi(w, h, self.unit_toggle.get())
        except ValueError:
            self.score_val_lbl.configure(text="--")
            self.score_status_lbl.configure(text="INVALID INPUT", text_color="#E76F51")
            self.desc_lbl.configure(text="Please key in positive weight and height values.")
            return

        self.score_val_lbl.configure(text=f"{bmi:.1f}", text_color=const.COLOR_ACCENT)
        
        info = self.data_manager.classify_bmi(bmi)
        cat = info["category"]
        
        if cat == "Underweight":
            color = const.COLOR_UNDERWEIGHT
        elif cat == "Normal":
            color = const.COLOR_NORMAL
        elif cat == "Overweight":
            color = const.COLOR_OVERWEIGHT
        else:
            color = const.COLOR_OBESE

        self.score_status_lbl.configure(text=info["status"], text_color=color)
        self.desc_lbl.configure(text=info["advice"])
        
        self.draw_gauge(bmi)

    def draw_gauge(self, current_bmi=None):
        if current_bmi is None:
            try:
                current_bmi = float(self.score_val_lbl.cget("text"))
            except ValueError:
                current_bmi = 22.0

        canvas = self.gauge_canvas
        canvas.delete("all")

        w = canvas.winfo_width()
        h = canvas.winfo_height()
        if w < 100:
            w = 340
        if h < 20:
            h = 60

        margin_x = 15
        bar_y = h - 25
        bar_height = 12

        usable_w = w - (margin_x * 2)
        zone_w = usable_w / 4

        is_dark = ctk.get_appearance_mode() == "Dark"
        c_under = const.COLOR_UNDERWEIGHT[1] if is_dark else const.COLOR_UNDERWEIGHT[0]
        c_norm = const.COLOR_NORMAL[1] if is_dark else const.COLOR_NORMAL[0]
        c_over = const.COLOR_OVERWEIGHT[1] if is_dark else const.COLOR_OVERWEIGHT[0]
        c_obese = const.COLOR_OBESE[1] if is_dark else const.COLOR_OBESE[0]
        c_text = const.COLOR_TEXT[1] if is_dark else const.COLOR_TEXT[0]
        c_muted = const.COLOR_TEXT_MUTED[1] if is_dark else const.COLOR_TEXT_MUTED[0]

        # Draw blocks
        canvas.create_rectangle(margin_x, bar_y, margin_x + zone_w, bar_y + bar_height, fill=c_under, outline="")
        canvas.create_rectangle(margin_x + zone_w, bar_y, margin_x + (zone_w * 2), bar_y + bar_height, fill=c_norm, outline="")
        canvas.create_rectangle(margin_x + (zone_w * 2), bar_y, margin_x + (zone_w * 3), bar_y + bar_height, fill=c_over, outline="")
        canvas.create_rectangle(margin_x + (zone_w * 3), bar_y, margin_x + usable_w, bar_y + bar_height, fill=c_obese, outline="")

        # Draw labels
        canvas.create_text(margin_x, bar_y + bar_height + 10, text="15", fill=c_muted, font=("Helvetica", 9))
        canvas.create_text(margin_x + zone_w, bar_y + bar_height + 10, text="18.5", fill=c_muted, font=("Helvetica", 9))
        canvas.create_text(margin_x + (zone_w * 2), bar_y + bar_height + 10, text="25", fill=c_muted, font=("Helvetica", 9))
        canvas.create_text(margin_x + (zone_w * 3), bar_y + bar_height + 10, text="30", fill=c_muted, font=("Helvetica", 9))
        canvas.create_text(margin_x + usable_w, bar_y + bar_height + 10, text="40", fill=c_muted, font=("Helvetica", 9))

        # Needle position
        bmi = current_bmi
        if bmi <= 15:
            needle_x = margin_x
        elif bmi >= 40:
            needle_x = margin_x + usable_w
        else:
            if bmi < 18.5:
                p = (bmi - 15) / (18.5 - 15)
                needle_x = margin_x + p * zone_w
            elif bmi < 25.0:
                p = (bmi - 18.5) / (25.0 - 18.5)
                needle_x = margin_x + zone_w + p * zone_w
            elif bmi < 30.0:
                p = (bmi - 25.0) / (30.0 - 25.0)
                needle_x = margin_x + (zone_w * 2) + p * zone_w
            else:
                p = (bmi - 30.0) / (40.0 - 30.0)
                needle_x = margin_x + (zone_w * 3) + p * zone_w

        # Draw needle
        canvas.create_polygon(
            needle_x, bar_y - 2,
            needle_x - 6, bar_y - 12,
            needle_x + 6, bar_y - 12,
            fill=c_text, outline=""
        )
        canvas.create_line(needle_x, bar_y - 2, needle_x, bar_y + bar_height + 2, fill=c_text, width=2)

    def save_record(self):
        """Sends height/weight/bmi details to outer record saver."""
        try:
            h = float(self.height_var.get())
            w = float(self.weight_var.get())
            bmi = float(self.score_val_lbl.cget("text"))
        except ValueError:
            return
            
        self.on_save_record(w, h, bmi, self.score_status_lbl.cget("text").title())
