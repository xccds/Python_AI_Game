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
GRAY = (127, 127, 127)

#Give a background color to the display
display_surface.fill(WHITE)
circle_color = rect_color = BLUE

#The main game loop
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
            
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_b:
                circle_color = BLUE
            elif event.key == pygame.K_g:
                circle_color = GRAY

        if event.type == pygame.MOUSEBUTTONDOWN:
            if rect_color == BLUE:
                rect_color = GRAY
            else:
                rect_color = BLUE

    #Circle(surface, color, center, radius, thickness...0 for fill)
    pygame.draw.circle(display_surface, circle_color, (WINDOW_WIDTH//2, WINDOW_HEIGHT//2), 150)

    #Rectangle(surface, color, (top-left x, top-left y, width, height))
    pygame.draw.rect(display_surface, rect_color, (0, 0, 100, 100))

    #Update the display
    pygame.display.update()

#End the game
pygame.quit()