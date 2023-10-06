import pygame
from clock import Clock
from stock_graph import Graph
# Pygame Setup and Main Loop
# Initialize Pygame
pygame.init()

WHITE = (255, 255, 255)

# Initial window dimensions
width, height = 800, 600
screen = pygame.display.set_mode((width, height), pygame.RESIZABLE)
pygame.display.set_caption("Resizable Window with Clock and Graphs")

# Initialize the Clock and Graph objects
clock_instance = Clock(10, 10, text_color="black", border_color="black", bg_color="darkGray")
main_graph = Graph(is_main=True, is_live=False, data_file='./data/PriceDay.csv', size_multiplier=1.5)

# Create side (auxiliary) graphs
side_graph1 = Graph(is_main=False, is_live=False, data_file='./data/PriceDay2.csv', size_multiplier=.9)
side_graph2 = Graph(is_main=False, is_live=False, data_file='./data/PriceDay3.csv', size_multiplier=.9)

running = True
dragging = False  # Track if we're dragging an object
dragged_object = None  # The object being dragged

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.VIDEORESIZE:
            width, height = event.w, event.h
            screen = pygame.display.set_mode((width, height), pygame.RESIZABLE)
        elif event.type == pygame.MOUSEBUTTONDOWN:
            # Check if the mouse is over the clock or one of the graphs
            if clock_instance.rect.collidepoint(event.pos):  # Assuming your Clock class has a rect attribute
                dragging = True
                dragged_object = clock_instance
            elif main_graph.rect.collidepoint(event.pos):  # Assuming your Graph class has a rect attribute
                dragging = True
                dragged_object = main_graph
            # Add checks for other graphs...
        elif event.type == pygame.MOUSEBUTTONUP:
            dragging = False
            dragged_object = None
        elif event.type == pygame.MOUSEMOTION and dragging:
            dx, dy = event.rel  # Relative mouse movement
            dragged_object.update_position(dx, dy)
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_PLUS:
                # Increase size (You need to define how to do this in your classes)
                dragged_object.increase_size()
            elif event.key == pygame.K_MINUS:
                # Decrease size
                dragged_object.decrease_size()

    # Clear the screen with a color (e.g., white)
    screen.fill(WHITE)

    # Display the clock and graphs
    clock_instance.display(screen)
    main_graph.display(screen)
    side_graph1.display(screen)
    side_graph2.display(screen)

    pygame.display.flip()

pygame.quit()