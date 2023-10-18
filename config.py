# config.py

# Fonts
font_graph_name = 'arial'
font_graph_size = 14
font_name = "arial"
font_size = 14

# Object configurations
object_configs = [
    {"class_name": "Clock", "args": (10, 10, 100, 50),
     "kwargs": {"text_color": "black", "border_color": "black", "bg_color": "darkGray"}},
    {"class_name": "Graph",
     "kwargs": {"is_live": False, "column": 'Price1',
                "size_multiplier": 1.5, "color": (100, 100, 100), "title": "Price 1", "original_title": "Price 1", "strategy_active": False, 'prof_coloring': False, 'bar_chart': 2}},
    # ... continue for other Graph instances
]

# Positions and dimensions
slider_position = (50, 450)
slider_width = 350
data_table_position = (650, 50)
menu_button_position = (700, 10)
menu_button_size = (80, 40)
menu_position = (700, 60)
day_switch_position = (650, 10)
range_slider_position = (50, 500)
