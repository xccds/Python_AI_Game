import pygame
import random
import math

pygame.init()
clock = pygame.time.Clock()

display_surface = pygame.display.set_mode((520, 550))
pygame.display.set_caption("Monte Carlo")
font = pygame.font.Font(None, 32)

WHITE = (255, 255, 255)
BLUE = (137, 207, 240)
RED = (238, 75, 43)
BLACK = (0,0,0)
total = 0
in_circle = 0

running = True
display_surface.fill(WHITE)

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
            
    pygame.draw.rect(display_surface, BLACK, (10, 40, 500, 500),width=1)
    pygame.draw.circle(display_surface, BLACK, (260, 290), 250,width=1)

    x = random.randint(10,510)
    y = random.randint(40,540)
    radius = math.sqrt((x - 260)**2 + (y - 290)**2)
    if radius <= 250:
        point_color = RED 
        in_circle += 1
    else :
        point_color = BLUE
    pygame.draw.circle(display_surface, point_color, (x, y), 1)
    total += 1
    pi = 4 * in_circle/total

    total_str = "total: {}".format(total)
    in_circle_str = "red points: {}".format(in_circle)
    pi_str = "PI: {:.5f}".format(pi)
    total_text = font.render(total_str, True, BLACK, WHITE)
    in_circle_text = font.render(in_circle_str, True, BLACK, WHITE)
    pi_text = font.render(pi_str, True, BLACK, WHITE)

    pygame.draw.rect(display_surface, WHITE, (10,5,500,30))
    display_surface.blit(total_text, (10,5))
    display_surface.blit(in_circle_text, (150,5))
    display_surface.blit(pi_text, (350,5))

    pygame.display.update()
    clock.tick(60)

pygame.quit()
