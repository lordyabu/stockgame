import json
import pygame
from core.graph import Graph
from menu.main_menu import Menu
from menu.menu_button import MenuButton
from analysis.slider import Slider
from analysis.range_slider import RangeSlider
from core.clock import Clock
from analysis.table import DataTable
from core.dayswitch import DaySwitch
import os
from analysis.range_slider import RangeSlider

def save_preset(projections, filename='presets/preset.json'):
    """
    Save a list of projections to a JSON file.

    Args:
        projections (list): A list of projection objects.
        filename (str, optional): The name of the JSON file to save. Default is 'presets/preset.json'.
    """
    with open(filename, 'w') as f:
        json.dump([proj.serialize() for proj in projections], f)

def load_preset(filename='presets/preset.json', font=None):
    """
    Load a list of projections from a JSON file.

    Args:
        filename (str, optional): The name of the JSON file to load. Default is 'presets/preset.json'.
        font (pygame.Font, optional): The font to use for rendering. Default is None.

    Returns:
        list: A list of loaded projection objects.
    """
    Graph.current_x_offset = 0  # Reset the offset

    with open(filename, 'r') as f:
        data = json.load(f)

    projections = []
    loaded_graphs = []
    loaded_slider = None
    loaded_day_switch = None
    loaded_data_table = None

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


        elif proj_data['type'] in ['MenuButton', 'SwitchButton', 'Menu', 'Clock']:
            proj_class = globals().get(proj_data['type'])
            if proj_class:
                projections.append(proj_class.deserialize(proj_data))

        elif proj_data['type'] == 'DaySwitch':
            loaded_day_switch = DaySwitch.deserialize(proj_data)
            projections.append(loaded_day_switch)

        elif proj_data['type'] == 'RangeSlider':
            loaded_range_slider = RangeSlider.deserialize(proj_data)
            projections.append(loaded_range_slider)

    if font is None:
        font = pygame.font.SysFont('arial', 14)  # Or any default you'd like

    loaded_data_table = next((DataTable.deserialize(proj_data, loaded_graphs, font) for proj_data in data if proj_data['type'] == 'DataTable'), None)
    if loaded_data_table:
        projections.append(loaded_data_table)

    # Connect Slider to Graphs and DataTable
    if loaded_slider:
        for graph in loaded_graphs:
            graph.add_observer(loaded_slider)
            loaded_slider.add_observer(graph)

        if loaded_data_table:
            loaded_slider.add_observer(loaded_data_table)

    # Connect DaySwitch to Graphs
    if loaded_day_switch:
        loaded_day_switch.add_graphs(loaded_graphs)

    # Update menu position
    menu_button_proj = next((proj for proj in projections if isinstance(proj, MenuButton)), None)
    loaded_menu = next((proj for proj in projections if isinstance(proj, Menu)), None)

    if loaded_menu and menu_button_proj:
        loaded_menu.update_position(menu_button_proj.rect.x, menu_button_proj.rect.y + menu_button_proj.rect.height)

    return projections

def load_project_state(projections):
    """
    Load a saved project state.

    Args:
        projections (list): A list of projection objects.

    Returns:
        tuple: A tuple containing the loaded components (Slider, RangeSlider, MenuButton, Menu, DataTable, DaySwitch, Graphs).
    """
    # Load the saved state
    loaded_projections = load_preset()

    # Clear the current projections and add loaded ones
    projections.clear()
    projections.extend(loaded_projections)

    # Extracting and updating the necessary components
    slider = next((proj for proj in projections if isinstance(proj, Slider)), None)
    menu_button = next((proj for proj in projections if isinstance(proj, MenuButton)), None)
    menu = next((proj for proj in projections if isinstance(proj, Menu)), None)
    data_table = next((proj for proj in projections if isinstance(proj, DataTable)), None)
    day_switch = next((proj for proj in projections if isinstance(proj, DaySwitch)), None)
    graphs = [proj for proj in projections if isinstance(proj, Graph)]
    range_slider = next((proj for proj in projections if isinstance(proj, RangeSlider)), None)

    # Reconnecting the observers
    if slider and data_table:
        slider.add_observer(data_table)
    if slider and graphs:
        for graph in graphs:
            graph.add_observer(slider)
            slider.add_observer(graph)

    # Reconnect the DaySwitch object to the loaded graphs
    if day_switch and graphs:
        day_switch.add_graphs(graphs)

    if range_slider and graphs:
        for graph in graphs:
            range_slider.add_observer(graph)

    return slider, range_slider, menu_button, menu, data_table, day_switch, graphs
