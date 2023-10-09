import json
import pygame
from core.clock import Clock
from core.graph import Graph
from menu.switch_button import SwitchButton
from menu.main_menu import Menu
from menu.menu_button import MenuButton
from analysis.slider import Slider
from analysis.table import DataTable
import os
def save_preset(projections, filename='presets/preset.json'):
    with open(filename, 'w') as f:
        json.dump([proj.serialize() for proj in projections], f)


def load_preset(filename='presets/preset.json', font=None):
    Graph.current_x_offset = 0  # Reset the offset
    with open(filename, 'r') as f:
        data = json.load(f)

    projections = []
    loaded_slider = None  # Initialize loaded_slider
    loaded_graphs = []

    for proj_data in data:
        if proj_data['type'] == 'Graph':
            if not os.path.exists(proj_data['data_file']):
                print(f"Error: Data file {proj_data['data_file']} not found. Skipping this graph.")
                continue

            graph = Graph.deserialize(proj_data)
            projections.append(graph)
            loaded_graphs.append(graph)

        elif proj_data['type'] == 'Slider':
            loaded_slider = Slider.deserialize(proj_data)
            projections.append(loaded_slider)

        elif proj_data['type'] == 'MenuButton':
            projections.append(MenuButton.deserialize(proj_data))

        elif proj_data['type'] == 'SwitchButton':
            projections.append(SwitchButton.deserialize(proj_data))

        elif proj_data['type'] == 'Menu':
            loaded_menu = Menu.deserialize(proj_data)
            projections.append(loaded_menu)

        elif proj_data['type'] == 'Clock':
            projections.append(Clock.deserialize(proj_data))

    if font is None:
        font = pygame.font.SysFont(None, 24)  # Or any default you'd like

    for proj_data in data:
        if proj_data['type'] == 'DataTable':
            loaded_data_table = DataTable.deserialize(proj_data, loaded_graphs, font)
            projections.append(loaded_data_table)

    if loaded_slider:
        # Re-establish the slider's interaction with graphs and data table
        loaded_graphs = [proj for proj in projections if isinstance(proj, Graph)]
        loaded_data_table = next((proj for proj in projections if isinstance(proj, DataTable)), None)

        for graph in loaded_graphs:
            loaded_slider.add_observer(graph)

        if loaded_data_table:
            loaded_slider.add_observer(loaded_data_table)

        # Ensure that the slider's current_value is within its range
        loaded_slider.current_value = max(loaded_slider.min_value, min(loaded_slider.max_value, loaded_slider.current_value))

    # Ensure menu position is based on the loaded MenuButton position
    menu_button_proj = next((proj for proj in projections if isinstance(proj, MenuButton)), None)
    loaded_menu = next((proj for proj in projections if isinstance(proj, Menu)), None)

    if loaded_menu and menu_button_proj:
        loaded_menu.update_position(menu_button_proj.rect.x, menu_button_proj.rect.y + menu_button_proj.rect.height)

    return projections
