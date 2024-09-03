import pygame
import random
pygame.init()

WINDOW_WIDTH = 600
WINDOW_HEIGHT = 300
display_surface = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
pygame.display.set_caption("Blitting Images!")

WHITE = (255, 255, 255)
GRAY = (127, 127, 127)

font = pygame.font.Font('WenQuan.ttf', 32)
text = font.render("飞龙在天", True, GRAY, WHITE)
text_rect = text.get_rect()
text_rect.center = (WINDOW_WIDTH//2, text_rect.height//2)

dragon_image = pygame.image.load("dragon_right.png")
dragon_rect = dragon_image.get_rect()
dragon_rect.center = (WINDOW_WIDTH//2, WINDOW_HEIGHT//2)

coin_image = pygame.image.load("coin.png")
coin_rect = coin_image.get_rect()
coin_rect.x = random.randint(0, WINDOW_WIDTH - 32)
coin_rect.y = random.randint(0, WINDOW_HEIGHT - 32)

speed = [3,3]
fpsClock = pygame.time.Clock()

running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
    # 键盘连续移动
    keys = pygame.key.get_pressed()
    if keys[pygame.K_a]:
        dragon_rect.x -= speed[0]
    if keys[pygame.K_d]:
        dragon_rect.x += speed[0]
    if keys[pygame.K_w]:
        dragon_rect.y -= speed[1]
    if keys[pygame.K_s]:
        dragon_rect.y += speed[1]

    #Check for collision between two rects
    if dragon_rect.colliderect(coin_rect):
        print("HIT")
        coin_rect.x = random.randint(0, WINDOW_WIDTH - 32)
        coin_rect.y = random.randint(0, WINDOW_HEIGHT - 32)

    display_surface.fill(WHITE)
    display_surface.blit(text, text_rect)
    display_surface.blit(dragon_image, dragon_rect)
    display_surface.blit(coin_image, coin_rect)
    pygame.draw.rect(display_surface, GRAY, dragon_rect, 1)
    pygame.draw.rect(display_surface, GRAY, coin_rect, 1)

    pygame.display.update()
    fpsClock.tick(60)

#End the game
pygame.quit()