import pygame

#Initialize pygame
pygame.init()

#Create a display surface
WINDOW_WIDTH = 600
WINDOW_HEIGHT = 300
display_surface = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
pygame.display.set_caption("Blitting Images!")

#Define colors as RGB tuples
WHITE = (255, 255, 255)
GRAY = (127, 127, 127)

#Give a background color to the display
display_surface.fill(WHITE)

#Create images...returns a Surface object with the image drawon on it.
#We can then get the rect of the surface and use the rect to position the image.
dragon_image = pygame.image.load("dragon_right.png")
dragon_rect = dragon_image.get_rect()
dragon_rect.center = (WINDOW_WIDTH//2, WINDOW_HEIGHT//2)

font = pygame.font.Font('WenQuan.ttf', 32)
text = font.render("飞龙在天", True, GRAY, WHITE)
text_rect = text.get_rect()
text_rect.center = (WINDOW_WIDTH//2, text_rect.height//2)

#The main game loop
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    #Blit (copy) a surface object at the given coordinates to our display
    display_surface.blit(dragon_image, dragon_rect)
    pygame.draw.rect(display_surface, GRAY,dragon_rect, 4)
    display_surface.blit(text, text_rect)

    #Update the display
    pygame.display.update()

#End the game
pygame.quit()