# Soothing Color Palette Definitions
# Format: (Light Mode Color, Dark Mode Color)
COLOR_BG = ("#F4F7F6", "#141A18")
COLOR_SIDEBAR_BG = ("#E5EBE9", "#0F1413")
COLOR_CARD_BG = ("#FFFFFF", "#202A28")
COLOR_TEXT = ("#2B3A36", "#ECF2F0")
COLOR_TEXT_MUTED = ("#5A6E6A", "#9CB0AB")
COLOR_ACCENT = ("#4E878C", "#6FB5BD")
COLOR_ACCENT_HOVER = ("#3B6B6F", "#52979F")
COLOR_BORDER = ("#D1DCDA", "#324340")

# Soothing Health Category Colors
COLOR_UNDERWEIGHT = ("#5C9EAD", "#73BCCB")
COLOR_NORMAL = ("#76C893", "#90E3AC")
COLOR_OVERWEIGHT = ("#E9C46A", "#F4D35E")
COLOR_OBESE = ("#E76F51", "#EE964B")

# Range Limits
RANGE_METRIC = {
    "height": {"min": 100.0, "max": 250.0, "default": 170.0, "unit": "cm"},
    "weight": {"min": 30.0, "max": 200.0, "default": 70.0, "unit": "kg"}
}

RANGE_IMPERIAL = {
    "height": {"min": 36.0, "max": 96.0, "default": 68.0, "unit": "in"},
    "weight": {"min": 60.0, "max": 550.0, "default": 150.0, "unit": "lbs"}
}
