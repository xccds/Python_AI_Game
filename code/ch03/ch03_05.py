import pygame
pygame.init()

WINDOW_WIDTH = 600
WINDOW_HEIGHT = 300
display_surface = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
pygame.display.set_caption("Blitting Images!")

WHITE = (255, 255, 255)
GRAY = (127, 127, 127)

dragon_image = pygame.image.load("dragon_right.png")
dragon_rect = dragon_image.get_rect()
dragon_rect.center = (WINDOW_WIDTH//2, WINDOW_HEIGHT//2)


font = pygame.font.Font('WenQuan.ttf', 32)
text = font.render("飞龙在天", True, GRAY, WHITE)
text_rect = text.get_rect()
text_rect.center = (WINDOW_WIDTH//2, text_rect.height//2)

sound_1 = pygame.mixer.Sound('sound_1.wav')

speed = [2,2]

fpsClock = pygame.time.Clock()

running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    dragon_rect.x += speed[0]
    dragon_rect.y += speed[1]

    if dragon_rect.left < 0 or dragon_rect.right > WINDOW_WIDTH:
        speed[0] = -speed[0]
        sound_1.play()
    if dragon_rect.top < 0 or dragon_rect.bottom > WINDOW_HEIGHT:
        speed[1] = -speed[1]
        sound_1.play()

    display_surface.fill(WHITE)
    display_surface.blit(dragon_image, dragon_rect)
    display_surface.blit(text, text_rect)

    pygame.display.update()
    fpsClock.tick(60)

#End the game
pygame.quit()