import pygame

class Paddle:
    COLOR = (255, 255, 255)
    VEL = 4

    def __init__(self, surface, x, y, width, height):
        self.original_x = x
        self.original_y = y
        self.rect = pygame.draw.rect(surface, self.COLOR, (x, y, width, height))

    def draw(self, surface):
        pygame.draw.rect(surface, self.COLOR, self.rect)

    def move(self, up=True):
        if up:
            self.rect.y -= self.VEL
        else:
            self.rect.y += self.VEL

    def reset(self):
        self.rect.x = self.original_x
        self.rect.y = self.original_y


class Ball:
    MAX_VEL = 8
    COLOR = (255, 255, 255)

    def __init__(self, surface, x, y, radius):
        self.original_x = x
        self.original_y = y
        self.radius = radius
        self.x_vel = self.MAX_VEL
        self.y_vel = 0
        self.rect = pygame.draw.circle(surface, self.COLOR, (x, y), radius)

    def draw(self, surface):
        pygame.draw.circle(surface, self.COLOR, (self.rect.centerx, self.rect.centery), self.radius)

    def move(self):
        self.rect.x += self.x_vel
        self.rect.y += self.y_vel

    def reset(self):
        self.rect.centerx = self.original_x
        self.rect.centery = self.original_y
        self.y_vel = 0
        self.x_vel *= -1


class Game:
    WHITE = (255, 255, 255)
    BLACK = (0, 0, 0)
    
    def __init__(self, Width=800,Height=600):
        pygame.init()
        self.Win_width , self.Win_height = (Width, Height)
        self.surface = pygame.display.set_mode((self.Win_width, self.Win_height))
        self.paddle_width = 10
        self.paddle_height = 100
        self.ball_radius = 7
        self.win_score = 10
        self.ball = Ball(self.surface,self.Win_width // 2, self.Win_height // 2, self.ball_radius )
        self.left_paddle = Paddle(self.surface,10, self.Win_height//2 - self.paddle_height//2, 
                                    self.paddle_width, self.paddle_height)
        self.right_paddle = Paddle(self.surface,self.Win_width - 10 - self.paddle_width, 
                                    self.Win_height//2 - self.paddle_height//2, 
                                    self.paddle_width, self.paddle_height)
        self.left_score = 0
        self.right_score = 0
        self.fpsClock = pygame.time.Clock()
        self.font = pygame.font.SysFont("comicsans", 40)
        pygame.display.set_caption('Pong')

    def draw(self):
        self.surface.fill(self.BLACK)
        left_score_text = self.font.render(f"{self.left_score}", 1, self.WHITE)
        right_score_text = self.font.render(f"{self.right_score}", 1, self.WHITE)
        self.surface.blit(left_score_text, (self.Win_width//4 - left_score_text.get_width()//2, 20))
        self.surface.blit(right_score_text, (self.Win_width * (3/4) -
                                    right_score_text.get_width()//2, 20))
        self.left_paddle.draw(self.surface)
        self.right_paddle.draw(self.surface)
        pygame.draw.line(self.surface, self.WHITE,(self.Win_width//2,0),
                        (self.Win_width//2,self.Win_height),width=4)
        self.ball.draw(self.surface)
        pygame.display.update()

    def paddle_collision(self,paddle):
        if (self.ball.rect.centery >= paddle.rect.top and 
            self.ball.rect.centery <= paddle.rect.bottom):
            if self.ball.rect.colliderect(paddle.rect):
                self.ball.x_vel *= -1

                difference_in_y = paddle.rect.centery - self.ball.rect.centery
                reduction_factor = (paddle.rect.height / 2) / self.ball.MAX_VEL
                y_vel = difference_in_y / reduction_factor
                self.ball.y_vel = -1 * y_vel

    def handle_collision(self):
        if self.ball.rect.bottom >= self.Win_height:
            self.ball.y_vel *= -1
        elif self.ball.rect.top <= 0:
            self.ball.y_vel *= -1

        if self.ball.rect.left < 0:
            self.right_score += 1
            self.ball.reset()
        elif self.ball.rect.right > self.Win_width:
            self.left_score += 1
            self.ball.reset()

        if self.ball.x_vel < 0:
            self.paddle_collision(self.left_paddle)
        else:
            self.paddle_collision(self.right_paddle)


    def handle_paddle_movement(self):
        keys = pygame.key.get_pressed()
        if (keys[pygame.K_w] and 
            self.left_paddle.rect.top - self.left_paddle.VEL >= 0):
            self.left_paddle.move(up=True)
        if (keys[pygame.K_s] and 
            self.left_paddle.rect.bottom + self.left_paddle.VEL <= self.Win_height):
            self.left_paddle.move(up=False)
        if (keys[pygame.K_UP] and 
            self.right_paddle.rect.top - self.right_paddle.VEL >= 0):
            self.right_paddle.move(up=True)
        if (keys[pygame.K_DOWN] and 
            self.right_paddle.rect.bottom  + self.right_paddle.VEL <= self.Win_height):
            self.right_paddle.move(up=False)

    def game_is_win(self):
        won = False 
        if self.left_score >= self.win_score:
            won = True
            win_text = "Left Player Won!"
        if self.right_score >= self.win_score:
            won = True
            win_text = "Right Player Won!"
        if won:
            text = self.font.render(win_text, 1, self.WHITE)
            self.surface.blit(text, (self.Win_width//2 - text.get_width() //
                            2, self.Win_height//2 - text.get_height()//2))
            pygame.display.update()
            pygame.time.delay(5000)
            self.ball.reset()
            self.left_paddle.reset()
            self.right_paddle.reset()
            self.left_score = 0
            self.right_score = 0

    def play_step(self):
        game_over = False
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                game_over = True
        
        self.handle_paddle_movement()
        self.ball.move()
        self.handle_collision()
        self.game_is_win()
        self.draw()
        self.fpsClock.tick(60)
        return game_over


if __name__ == '__main__':
    game = Game()
    while True:
        game_over = game.play_step()
        if game_over:
            break
    pygame.quit()