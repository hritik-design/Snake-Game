import pygame
import random
import sys

# --- Constants ---
CELL_SIZE = 25
GRID_WIDTH = 32
GRID_HEIGHT = 24
SCREEN_WIDTH = CELL_SIZE * GRID_WIDTH
SCREEN_HEIGHT = CELL_SIZE * GRID_HEIGHT
FPS = 10

WHITE = (255, 255, 255)
BLACK = (15, 15, 15)
GREEN = (0, 200, 70)
DARK_GREEN = (0, 130, 40)
RED = (230, 0, 0)
GOLD = (255, 215, 0)
BG_COLOR = (10, 10, 10)
HIGHSCORE_FILE = "highscore.txt"

pygame.init()
pygame.mixer.init()

# --- Button Class ---
class Button:
    def __init__(self, text, x, y, width, height, color, hover_color, action=None):
        self.text = text
        self.rect = pygame.Rect(x, y, width, height)
        self.color = color
        self.hover_color = hover_color
        self.action = action
        self.font = pygame.font.Font(pygame.font.match_font('arialblack'), 30)

    def draw(self, screen):
        mouse_pos = pygame.mouse.get_pos()
        click = pygame.mouse.get_pressed()
        if self.rect.collidepoint(mouse_pos):
            pygame.draw.rect(screen, self.hover_color, self.rect, border_radius=12)
            if click[0] == 1 and self.action:
                self.action()
        else:
            pygame.draw.rect(screen, self.color, self.rect, border_radius=12)

        text_surf = self.font.render(self.text, True, WHITE)
        text_rect = text_surf.get_rect(center=self.rect.center)
        screen.blit(text_surf, text_rect)

# --- Main Game Class ---
class SnakeGame:
    def __init__(self):
        pygame.display.set_caption("Snake Evolution")
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font(pygame.font.match_font('arial'), 28)
        self.big_font = pygame.font.Font(pygame.font.match_font('arialblack'), 60)
        self.highscore = self.load_highscore()
        self.state = "menu"
        self.squares = self.generate_bg_squares()
        self.reset()

        # Buttons
        self.start_btn = Button("Start Game", SCREEN_WIDTH//2 - 120, SCREEN_HEIGHT//2 - 40, 240, 60, GREEN, DARK_GREEN, self.start_game)
        self.highscore_btn = Button("High Score", SCREEN_WIDTH//2 - 120, SCREEN_HEIGHT//2 + 40, 240, 60, (80,80,200), (120,120,255), self.show_highscore)
        self.quit_btn = Button("Quit", SCREEN_WIDTH//2 - 120, SCREEN_HEIGHT//2 + 120, 240, 60, RED, (255,80,80), self.quit_game)

    def generate_bg_squares(self):
        return [[random.randint(0, SCREEN_WIDTH), random.randint(0, SCREEN_HEIGHT), random.randint(2, 5)] for _ in range(40)]

    def animate_bg(self):
        for s in self.squares:
            pygame.draw.rect(self.screen, (40, 40, 40), (s[0], s[1], s[2], s[2]))
            s[1] += s[2] * 0.3
            if s[1] > SCREEN_HEIGHT:
                s[0] = random.randint(0, SCREEN_WIDTH)
                s[1] = 0

    def load_highscore(self):
        try:
            with open(HIGHSCORE_FILE, "r") as f:
                return int(f.read().strip() or 0)
        except:
            return 0

    def save_highscore(self):
        with open(HIGHSCORE_FILE, "w") as f:
            f.write(str(self.highscore))

    def reset(self):
        self.direction = (1, 0)
        mid_x, mid_y = GRID_WIDTH // 2, GRID_HEIGHT // 2
        self.snake = [(mid_x - 1, mid_y), (mid_x, mid_y), (mid_x + 1, mid_y)]
        self.spawn_food()
        self.score = 0
        self.game_over = False
        self.paused = False
        self.speed = FPS

    def spawn_food(self):
        while True:
            x, y = random.randint(0, GRID_WIDTH - 1), random.randint(0, GRID_HEIGHT - 1)
            if (x, y) not in self.snake:
                self.food = (x, y)
                break

    def start_game(self):
        self.state = "game"
        self.reset()

    def show_highscore(self):
        self.state = "highscore"

    def quit_game(self):
        pygame.quit()
        sys.exit()

    def handle_keys(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.quit_game()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.state = "menu"

                # Game controls
                if self.state == "game" and not self.game_over and not self.paused:
                    if event.key in (pygame.K_UP, pygame.K_w) and self.direction != (0, 1):
                        self.direction = (0, -1)
                    elif event.key in (pygame.K_DOWN, pygame.K_s) and self.direction != (0, -1):
                        self.direction = (0, 1)
                    elif event.key in (pygame.K_LEFT, pygame.K_a) and self.direction != (1, 0):
                        self.direction = (-1, 0)
                    elif event.key in (pygame.K_RIGHT, pygame.K_d) and self.direction != (-1, 0):
                        self.direction = (1, 0)
                if self.state == "game" and event.key == pygame.K_p:
                    self.paused = not self.paused
                if self.state == "game" and self.game_over and event.key == pygame.K_r:
                    if self.score > self.highscore:
                        self.highscore = self.score
                        self.save_highscore()
                    self.reset()

    def update(self):
        if self.state != "game" or self.game_over or self.paused:
            return
        head_x, head_y = self.snake[-1]
        dx, dy = self.direction
        new_head = ((head_x + dx) % GRID_WIDTH, (head_y + dy) % GRID_HEIGHT)
        if new_head in self.snake:
            self.game_over = True
            if self.score > self.highscore:
                self.highscore = self.score
                self.save_highscore()
            return
        self.snake.append(new_head)
        if new_head == self.food:
            self.score += 1
            if self.score % 5 == 0:
                self.speed += 1
            self.spawn_food()
        else:
            self.snake.pop(0)

    def draw_snake(self):
        for i, (x, y) in enumerate(self.snake):
            rect = pygame.Rect(x * CELL_SIZE + 2, y * CELL_SIZE + 2, CELL_SIZE - 4, CELL_SIZE - 4)
            color = DARK_GREEN if i == len(self.snake) - 1 else GREEN
            pygame.draw.rect(self.screen, color, rect, border_radius=4)

    def draw_food(self):
        fx, fy = self.food
        pygame.draw.circle(self.screen, GOLD, (fx * CELL_SIZE + CELL_SIZE // 2, fy * CELL_SIZE + CELL_SIZE // 2), CELL_SIZE // 2 - 2)

    def draw_menu(self):
        self.screen.fill(BG_COLOR)
        self.animate_bg()
        title = self.big_font.render("SNAKE EVOLUTION", True, random.choice([GREEN, GOLD, WHITE]))
        self.screen.blit(title, title.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//3)))
        self.start_btn.draw(self.screen)
        self.highscore_btn.draw(self.screen)
        self.quit_btn.draw(self.screen)
        pygame.display.flip()

    def draw_highscore_screen(self):
        self.screen.fill(BG_COLOR)
        self.animate_bg()
        title = self.big_font.render("HIGH SCORE", True, GOLD)
        score_text = self.font.render(f"{self.highscore}", True, WHITE)
        back_text = self.font.render("Press ESC to go back", True, (180,180,180))
        self.screen.blit(title, title.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//3)))
        self.screen.blit(score_text, score_text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2)))
        self.screen.blit(back_text, back_text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT - 60)))
        pygame.display.flip()

    def draw_game(self):
        self.screen.fill(BG_COLOR)
        self.draw_snake()
        self.draw_food()
        pygame.draw.rect(self.screen, WHITE, (0, 0, SCREEN_WIDTH, SCREEN_HEIGHT), 2)
        self.screen.blit(self.font.render(f"Score: {self.score}", True, WHITE), (10, 10))
        self.screen.blit(self.font.render(f"High: {self.highscore}", True, WHITE), (SCREEN_WIDTH - 120, 10))
        if self.paused:
            pause = self.big_font.render("Paused", True, WHITE)
            self.screen.blit(pause, pause.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2)))
        if self.game_over:
            over = self.big_font.render("GAME OVER", True, RED)
            retry = self.font.render("Press R to Restart", True, WHITE)
            self.screen.blit(over, over.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 - 40)))
            self.screen.blit(retry, retry.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 + 20)))
        pygame.display.flip()

    def run(self):
        while True:
            self.handle_keys()
            if self.state == "menu":
                self.draw_menu()
            elif self.state == "highscore":
                self.draw_highscore_screen()
            elif self.state == "game":
                self.update()
                self.draw_game()
            self.clock.tick(self.speed if self.state == "game" else 30)

if __name__ == "__main__":
    SnakeGame().run()
