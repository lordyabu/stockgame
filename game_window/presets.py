import json
import pygame
from clock import Clock
from stock_graph import Graph
from menuObjects.switch_button import SwitchButton
from menuObjects.menu import Menu
from menuObjects.menu_button import MenuButton
def save_preset(projections, filename='preset.json'):
    with open(filename, 'w') as f:
        json.dump([proj.serialize() for proj in projections], f)


def load_preset(filename='preset.json'):
    Graph.current_x_offset = 0  # Reset the offset
    with open(filename, 'r') as f:
        data = json.load(f)

    projections = []
    for proj_data in data:
        if proj_data['type'] == 'Graph':
            projections.append(
                Graph(x=proj_data['x'], y=proj_data['y'], width=proj_data['width'], height=proj_data['height'],
                      data_file=proj_data['data_file'], size_multiplier=proj_data.get('size_multiplier', 1.0)))

        elif proj_data['type'] == 'Clock':
            projections.append(
                Clock(x=proj_data['x'], y=proj_data['y'], width=proj_data.get('width'), height=proj_data.get('height')))

        elif proj_data['type'] == 'MenuButton':
            projections.append(
                MenuButton(proj_data["x"], proj_data["y"], proj_data["width"], proj_data["height"], proj_data["text"]))

        elif proj_data['type'] == 'Menu':
            menu = Menu(proj_data['x'], proj_data['y'])
            menu.is_active = proj_data['is_active']
            for child_data in proj_data.get('children', []):
                if child_data['type'] == 'SwitchButton':
                    switch_btn = SwitchButton(child_data['x'], child_data['y'], child_data['width'],
                                              child_data['height'], child_data['text_on'], child_data['text_off'])
                    switch_btn.is_on = child_data['is_on']
                    menu.lock_button = switch_btn
                elif child_data['type'] == 'MenuButton':
                    if child_data['text'] == 'Save':
                        menu.save_button = MenuButton(child_data["x"], child_data["y"], child_data["width"],
                                                      child_data["height"], child_data["text"])
                    elif child_data['text'] == 'Load':
                        menu.load_button = MenuButton(child_data["x"], child_data["y"], child_data["width"],
                                                      child_data["height"], child_data["text"])
            projections.append(menu)

    return projections