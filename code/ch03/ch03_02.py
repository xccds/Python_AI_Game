import pygame

#Intiailize Pygame
pygame.init()

#Create a display surface and set its caption
WINDOW_WIDTH = 600
WINDOW_HEIGHT = 300
display_surface = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
pygame.display.set_caption("Hello World!")

#Define colors as RGB tuples
WHITE = (255, 255, 255)
BLUE = (0, 0, 255)

#Give a background color to the display
display_surface.fill(WHITE)

#Circle(surface, color, center, radius, thickness...0 for fill)
pygame.draw.circle(display_surface, BLUE, (WINDOW_WIDTH//2, WINDOW_HEIGHT//2), 150)

#Rectangle(surface, color, (top-left x, top-left y, width, height))
pygame.draw.rect(display_surface, BLUE, (0, 0, 100, 100))

#Update the display
pygame.display.update()
    
#The main game loop
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

#End the game
pygame.quit()