from datetime import datetime
import customtkinter as ctk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt
import src.constants as const

class HistoryView(ctk.CTkFrame):
    def __init__(self, parent, data_manager, get_active_user_id_cb, on_delete_record_cb, get_unit_system_cb):
        super().__init__(parent, fg_color="transparent")
        
        self.data_manager = data_manager
        self.get_active_user_id_cb = get_active_user_id_cb
        self.on_delete_record_cb = on_delete_record_cb
        self.get_unit_system_cb = get_unit_system_cb
        self.canvas_widget = None

        self.grid_columnconfigure(0, weight=5)
        self.grid_columnconfigure(1, weight=4)
        self.grid_rowconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        self.setup_left_panels()
        self.setup_right_plot()

    def setup_left_panels(self):
        left_side_container = ctk.CTkFrame(self, fg_color="transparent")
        left_side_container.grid(row=0, column=0, rowspan=2, sticky="nsew", padx=(0, 10))
        left_side_container.grid_columnconfigure(0, weight=1)
        left_side_container.grid_rowconfigure(1, weight=1)

        # Stats Card
        stats_card = ctk.CTkFrame(
            left_side_container, 
            fg_color=const.COLOR_CARD_BG, 
            corner_radius=15, 
            border_width=1, 
            border_color=const.COLOR_BORDER
        )
        stats_card.grid(row=0, column=0, sticky="ew", pady=(0, 15))
        stats_card.grid_columnconfigure((0, 1, 2), weight=1)

        stats_title = ctk.CTkLabel(
            stats_card, 
            text="User Health Metrics", 
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color=const.COLOR_TEXT
        )
        stats_title.grid(row=0, column=0, columnspan=3, padx=20, pady=(15, 10), sticky="w")

        # Stats Items
        self.stat_min_lbl = self.create_stat_widget(stats_card, "Min BMI", "--", 1, 0)
        self.stat_avg_lbl = self.create_stat_widget(stats_card, "Avg BMI", "--", 1, 1)
        self.stat_max_lbl = self.create_stat_widget(stats_card, "Max BMI", "--", 1, 2)

        # Records Table Frame
        records_frame = ctk.CTkFrame(
            left_side_container, 
            fg_color=const.COLOR_CARD_BG, 
            corner_radius=15, 
            border_width=1, 
            border_color=const.COLOR_BORDER
        )
        records_frame.grid(row=1, column=0, sticky="nsew")
        records_frame.grid_columnconfigure(0, weight=1)
        records_frame.grid_rowconfigure(2, weight=1) # Row 0: title, Row 1: header, Row 2: scrollable frame

        table_title = ctk.CTkLabel(
            records_frame, 
            text="Historical Records", 
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color=const.COLOR_TEXT
        )
        table_title.grid(row=0, column=0, padx=20, pady=(15, 5), sticky="w")

        # Static Table Header Row
        self.header_frame = ctk.CTkFrame(records_frame, fg_color="transparent", height=25)
        self.header_frame.grid(row=1, column=0, padx=20, pady=(5, 5), sticky="ew")
        self.header_frame.grid_columnconfigure(0, weight=4)
        self.header_frame.grid_columnconfigure(1, weight=3)
        self.header_frame.grid_columnconfigure(2, weight=2)
        self.header_frame.grid_columnconfigure(3, weight=4)
        self.header_frame.grid_columnconfigure(4, weight=2)

        headers = ["Date", "Weight", "BMI Score", "Category", ""]
        for col, text in enumerate(headers):
            lbl = ctk.CTkLabel(
                self.header_frame, 
                text=text, 
                font=ctk.CTkFont(size=12, weight="bold"),
                text_color=const.COLOR_TEXT_MUTED,
                anchor="w" if col == 0 else "center"
            )
            lbl.grid(row=0, column=col, padx=(15, 5) if col == 0 else 5, sticky="ew")

        # Scrollable table container
        self.records_scroll = ctk.CTkScrollableFrame(
            records_frame, 
            fg_color="transparent"
        )
        self.records_scroll.grid(row=2, column=0, padx=15, pady=(0, 15), sticky="nsew")

    def setup_right_plot(self):
        chart_card = ctk.CTkFrame(
            self, 
            fg_color=const.COLOR_CARD_BG, 
            corner_radius=15, 
            border_width=1, 
            border_color=const.COLOR_BORDER
        )
        chart_card.grid(row=0, column=1, rowspan=2, sticky="nsew", padx=(10, 0))
        chart_card.grid_columnconfigure(0, weight=1)
        chart_card.grid_rowconfigure(1, weight=1)

        chart_title = ctk.CTkLabel(
            chart_card, 
            text="BMI History & Progression", 
            font=ctk.CTkFont(size=18, weight="bold"),
            text_color=const.COLOR_TEXT
        )
        chart_title.grid(row=0, column=0, padx=25, pady=(25, 5), sticky="w")

        # Container for matplotlib canvas
        self.plot_container = ctk.CTkFrame(chart_card, fg_color="transparent")
        self.plot_container.grid(row=1, column=0, padx=20, pady=20, sticky="nsew")
        self.plot_container.grid_columnconfigure(0, weight=1)
        self.plot_container.grid_rowconfigure(0, weight=1)

    def create_stat_widget(self, parent, label_text, default_value, row, col):
        frame = ctk.CTkFrame(parent, fg_color=const.COLOR_BG, corner_radius=8)
        frame.grid(row=row, column=col, padx=10, pady=(0, 15), sticky="nsew")
        
        lbl = ctk.CTkLabel(frame, text=label_text, font=ctk.CTkFont(size=11), text_color=const.COLOR_TEXT_MUTED)
        lbl.pack(pady=(8, 2))
        
        val_lbl = ctk.CTkLabel(frame, text=default_value, font=ctk.CTkFont(size=18, weight="bold"), text_color=const.COLOR_ACCENT)
        val_lbl.pack(pady=(0, 8))
        return val_lbl

    def refresh_history_tab(self):
        """Re-renders stats cards, scroll logs, and graph."""
        self.refresh_stats_cards()
        self.refresh_history_table()
        self.refresh_matplotlib_chart()

    def refresh_stats_cards(self):
        active_id = self.get_active_user_id_cb()
        stats = self.data_manager.get_user_stats(active_id)
        
        if stats["min"] is None:
            self.stat_min_lbl.configure(text="--")
            self.stat_avg_lbl.configure(text="--")
            self.stat_max_lbl.configure(text="--")
        else:
            self.stat_min_lbl.configure(text=f"{stats['min']:.1f}")
            self.stat_avg_lbl.configure(text=f"{stats['avg']:.1f}")
            self.stat_max_lbl.configure(text=f"{stats['max']:.1f}")

    def refresh_history_table(self):
        for widget in self.records_scroll.winfo_children():
            widget.destroy()

        active_id = self.get_active_user_id_cb()
        records = self.data_manager.get_user_history(active_id)
        unit_system = self.get_unit_system_cb()

        if not records:
            empty_lbl = ctk.CTkLabel(
                self.records_scroll,
                text="No weight records saved yet.",
                font=ctk.CTkFont(size=13),
                text_color=const.COLOR_TEXT_MUTED
            )
            empty_lbl.pack(pady=30)
            return

        # Rows
        for rec in records:
            if unit_system == "Imperial":
                weight_val = rec["weight"] / 0.45359237
                weight_text = f"{weight_val:.1f} lbs"
            else:
                weight_text = f"{rec['weight']:.1f} kg"

            cat = rec["category"]
            if cat == "Underweight":
                cat_color = const.COLOR_UNDERWEIGHT
            elif cat == "Normal":
                cat_color = const.COLOR_NORMAL
            elif cat == "Overweight":
                cat_color = const.COLOR_OVERWEIGHT
            else:
                cat_color = const.COLOR_OBESE

            card = ctk.CTkFrame(
                self.records_scroll, 
                fg_color=const.COLOR_BG, 
                corner_radius=10,
                border_width=1,
                border_color=const.COLOR_BORDER
            )
            card.pack(fill="x", pady=5, padx=(5, 12))

            card.grid_columnconfigure(0, weight=4)
            card.grid_columnconfigure(1, weight=3)
            card.grid_columnconfigure(2, weight=2)
            card.grid_columnconfigure(3, weight=4)
            card.grid_columnconfigure(4, weight=2)

            date_lbl = ctk.CTkLabel(card, text=rec["date"], font=ctk.CTkFont(size=12), text_color=const.COLOR_TEXT, anchor="w")
            date_lbl.grid(row=0, column=0, padx=(15, 5), pady=8, sticky="w")

            weight_lbl = ctk.CTkLabel(card, text=weight_text, font=ctk.CTkFont(size=12), text_color=const.COLOR_TEXT, anchor="center")
            weight_lbl.grid(row=0, column=1, padx=5, pady=8, sticky="ew")

            bmi_lbl = ctk.CTkLabel(card, text=f"{rec['bmi']:.1f}", font=ctk.CTkFont(size=12, weight="bold"), text_color=const.COLOR_TEXT, anchor="center")
            bmi_lbl.grid(row=0, column=2, padx=5, pady=8, sticky="ew")

            badge = ctk.CTkFrame(card, fg_color=cat_color, corner_radius=6, height=20)
            badge.grid(row=0, column=3, padx=5, pady=8)
            badge_lbl = ctk.CTkLabel(badge, text=cat, font=ctk.CTkFont(size=10, weight="bold"), text_color="#FFFFFF", padx=8)
            badge_lbl.pack()

            # Delete Button
            delete_btn = ctk.CTkButton(
                card,
                text="🗑",
                width=24,
                height=24,
                fg_color="transparent",
                hover_color=const.COLOR_BORDER,
                text_color="#E76F51",
                font=ctk.CTkFont(size=14),
                command=lambda r_id=rec["id"]: self.delete_record(r_id)
            )
            delete_btn.grid(row=0, column=4, padx=5, pady=8)

            # Hover animations
            card.bind("<Enter>", lambda e, c=card: c.configure(border_color=const.COLOR_ACCENT))
            card.bind("<Leave>", lambda e, c=card: c.configure(border_color=const.COLOR_BORDER))
            
            # Bind clicks to load record into calculator
            for widget in [card, date_lbl, weight_lbl, bmi_lbl, badge, badge_lbl]:
                widget.bind("<Button-1>", lambda e, r=rec: self.load_record_to_calculator(r))

    def delete_record(self, record_id):
        """Displays confirmation dialog and deletes a record."""
        from tkinter import messagebox
        confirm = messagebox.askyesno("Confirm Delete", "Are you sure you want to delete this historical log entry?")
        if confirm:
            self.on_delete_record_cb(record_id)

    def load_record_to_calculator(self, record):
        """Loads record values back into the Calculator view and switches tabs."""
        app = self.winfo_toplevel()
        if hasattr(app, "calculator_view") and hasattr(app, "select_tab"):
            h = record["height"]
            w = record["weight"]
            
            unit_system = app.calculator_view.unit_toggle.get()
            if unit_system == "Metric":
                app.calculator_view.set_inputs(h, w)
            else:
                h_in = h / 2.54
                w_lb = w / 0.45359237
                app.calculator_view.set_inputs(h_in, w_lb)
                
            app.select_tab("calculator")

    def refresh_matplotlib_chart(self):
        """Plots the historical progression graph, styling it for active theme."""
        if self.canvas_widget:
            self.canvas_widget.destroy()
            self.canvas_widget = None

        active_id = self.get_active_user_id_cb()
        user_name = self.data_manager.users[active_id]["name"]
        
        records = sorted(
            [r for r in self.data_manager.history if r["user_id"] == active_id],
            key=lambda r: r["date"]
        )

        is_dark = ctk.get_appearance_mode() == "Dark"
        fig_bg = "#202A28" if is_dark else "#FFFFFF"
        ax_bg = "#141A18" if is_dark else "#F4F7F6"
        text_color = "#ECF2F0" if is_dark else "#2B3A36"
        grid_color = "#324340" if is_dark else "#E1E8E6"
        line_color = "#6FB5BD" if is_dark else "#4E878C"

        fig, ax = plt.subplots(figsize=(6, 3.8), dpi=100)
        fig.patch.set_facecolor(fig_bg)
        ax.set_facecolor(ax_bg)

        ax.set_title(f"BMI Progress Log - {user_name}", color=text_color, fontsize=12, weight="bold", pad=15)
        ax.set_ylabel("BMI Score", color=text_color, fontsize=10, labelpad=8)
        
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.spines['left'].set_color(grid_color)
        ax.spines['bottom'].set_color(grid_color)
        
        ax.tick_params(colors=text_color, labelsize=9)
        ax.grid(True, linestyle="--", alpha=0.5, color=grid_color)

        if not records:
            ax.text(0.5, 0.5, "No weight records saved yet.\nGo to 'Calculator' tab to save BMI logs.",
                    horizontalalignment='center', verticalalignment='center',
                    transform=ax.transAxes, color=const.COLOR_TEXT_MUTED[0] if not is_dark else const.COLOR_TEXT_MUTED[1], fontsize=11)
            ax.set_xticks([])
            ax.set_yticks([])
        else:
            dates = [datetime.strptime(r["date"], "%Y-%m-%d").strftime("%d %b") for r in records]
            bmis = [r["bmi"] for r in records]

            ax.plot(dates, bmis, marker='o', color=line_color, linewidth=2.5, markersize=6, markerfacecolor='#FFFFFF', markeredgewidth=2)
            
            if len(dates) > 6:
                every_n = len(dates) // 4
                ax.set_xticks(dates[::every_n])
            
            # Highlight target zone
            ax.axhspan(18.5, 25.0, color='#76C893', alpha=0.1, label="Healthy Zone")
            ax.legend(facecolor=fig_bg, edgecolor=grid_color, labelcolor=text_color, loc="upper right", framealpha=0.8, fontsize=9)

        plt.tight_layout()

        canvas = FigureCanvasTkAgg(fig, master=self.plot_container)
        self.canvas_widget = canvas.get_tk_widget()
        self.canvas_widget.pack(fill="both", expand=True)
        canvas.draw()
        
        plt.close(fig)
