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

speed = [2,2]

fpsClock = pygame.time.Clock()

running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        # 键盘离散移动，常用于单次操作，例如跳跃操作
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_LEFT:
                dragon_rect.x -= speed[0]
            if event.key == pygame.K_RIGHT:
                dragon_rect.x += speed[0]
            if event.key == pygame.K_UP:
                dragon_rect.y -= speed[1]
            if event.key == pygame.K_DOWN:
                dragon_rect.y += speed[1]

    # 键盘连续移动，常用于按住操作，例如方向移动
    keys = pygame.key.get_pressed()
    if keys[pygame.K_a]:
        dragon_rect.x -= speed[0]
    if keys[pygame.K_d]:
        dragon_rect.x += speed[0]
    if keys[pygame.K_w]:
        dragon_rect.y -= speed[1]
    if keys[pygame.K_s]:
        dragon_rect.y += speed[1]

    display_surface.fill(WHITE)
    display_surface.blit(dragon_image, dragon_rect)
    display_surface.blit(text, text_rect)

    pygame.display.update()
    fpsClock.tick(60)

#End the game
pygame.quit()