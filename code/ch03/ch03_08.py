import pygame, random


class Dragon:
    def __init__(self,x,y):
        self.image = pygame.image.load("dragon_right.png")
        self.rect = self.image.get_rect()
        self.rect.left = x
        self.rect.centery = y
        self.speed = 10

    def update(self,direction):
        self.rect.y += direction * self.speed
            
    def draw(self,screen):
        screen.blit(self.image,self.rect) 

class Coin:
    def __init__(self,x,y):
        self.image = pygame.image.load("coin.png")
        self.rect = self.image.get_rect()
        self.speed = 10
        self.reset(x,y)
    
    def reset(self,x,y):
        self.rect.x = x
        self.rect.y = y

    def update(self):
        self.rect.x -= self.speed 

    def draw(self,screen):
        screen.blit(self.image,self.rect) 

class Game:
    GREEN = (0, 255, 0)
    WHITE = (255, 255, 255)
    BLACK = (0, 0, 0)

    def __init__(self,width=1000, height=500):
        pygame.init()
        self.win_width = width 
        self.win_height = height 
        self.display_surface = pygame.display.set_mode((self.win_width, self.win_height))
        pygame.display.set_caption("Feed the Dragon")
        self.fps = 60
        self.clock = pygame.time.Clock()
        self.lives = 5
        self.buffer_distance = 100
        self.score = 0
        self.sound = pygame.mixer.Sound("sound_1.wav")
        self.font = pygame.font.Font('WenQuan.ttf', 32)
        self.dragon = Dragon(32,self.win_height//2)
        self.coin = Coin(x=self.win_width+self.buffer_distance, 
                         y=random.randint(64, self.win_height - 32))
        self.running = True 
        self.is_paused = False
        
    def draw_text(self,text,color,x,y):
        image = self.font.render(text, True, color)
        rect = image.get_rect()
        rect.centerx = x
        rect.centery = y
        self.display_surface.blit(image,rect)

    def coin_reset(self):
        self.coin.reset(x=self.win_width+self.buffer_distance,
                        y=random.randint(64, self.win_height - 32))

    def handle_input(self):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_UP] and self.dragon.rect.top > 64:
            self.dragon.update(-1)
        if keys[pygame.K_DOWN] and self.dragon.rect.bottom < self.win_height:
            self.dragon.update(1)
        
    def handle_coin(self):
        if self.coin.rect.x < 0:
            self.lives -= 1
            self.coin_reset()
        else:
            self.coin.update()

    def handle_collision(self):
        if self.dragon.rect.colliderect(self.coin.rect):
            self.score += 1
            self.sound.play()
            self.coin.speed += 0.5
            self.coin_reset()

    def check_gameover(self):
        if self.lives == 0:
            self.draw_text("GAME OVER",Game.GREEN,self.win_width//2,self.win_height//2)
            self.draw_text("Press any key to play again",Game.GREEN,self.win_width//2,self.win_height//2+50)
            pygame.display.update()
            self.is_paused = True
            while self.is_paused:
                for event in pygame.event.get():
                    if event.type == pygame.KEYDOWN:
                        self.score = 0
                        self.lives = 5
                        self.coin_reset()
                        self.coin.speed = 10
                        self.is_paused = False

                    if event.type == pygame.QUIT:
                        self.is_paused = False
                        self.running = False

    def draw(self):
        self.display_surface.fill(Game.BLACK)

        self.draw_text("Score: " + str(self.score),Game.GREEN,100,20)
        self.draw_text("吃金币的龙" ,Game.GREEN,self.win_width//2,20)
        self.draw_text("Lives: " + str(self.lives),Game.GREEN,self.win_width-100,20)

        pygame.draw.line(self.display_surface, Game.WHITE, (0, 64), (self.win_width, 64), 2)
        self.dragon.draw(self.display_surface)
        self.coin.draw(self.display_surface)
        pygame.display.update()

    def play(self):
        while self.running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
        
            self.handle_input()
            self.handle_coin()
            self.handle_collision()
            self.draw()
            self.check_gameover()
            self.clock.tick(self.fps)
        
        pygame.quit()

if __name__ == '__main__':
    game = Game()
    game.play()

