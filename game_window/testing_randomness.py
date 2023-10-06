from clock import Clock
import pygame
import time

# Initialize Pygame
pygame.init()

# Colors
WHITE = (255, 255, 255)

# Clock Colors
CLOCK_TEXT_COLOR = "black"
CLOCK_BORDER_COLOR = "black"
CLOCK_BG_COLOR = "darkGray"

# Screen dimensions
WIDTH, HEIGHT = 800, 600

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption('StockGame')

# Initialize the Clock object with the desired colors
clock_instance = Clock(10, 10, text_color=CLOCK_TEXT_COLOR, border_color=CLOCK_BORDER_COLOR, bg_color=CLOCK_BG_COLOR)

# Main loop
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    screen.fill(WHITE)
    clock_instance.display(screen)  # Using the Clock class's display method
    pygame.display.flip()

    time.sleep(1)

pygame.quit()
