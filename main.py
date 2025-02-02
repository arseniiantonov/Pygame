import csv
import sys
from random import randint

import pygame

pygame.init()

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
FPS = 60

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (200, 200, 200)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
COLORS = [(255, 0, 0), (0, 255, 0), (0, 0, 255), (255, 255, 0), (0, 255, 255), (255, 0, 255)]

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Строим башню")

font = pygame.font.Font(None, 36)
small_font = pygame.font.Font(None, 24)
bonus_font = pygame.font.Font(None, 48)

RESULTS_FILE = "results.csv"


class Block:
    def __init__(self, x, y, width, height, color):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.color = color
        self.speed_x = 10
        self.falling = True
        self.image = pygame.image.load("assets/block.png")
        self.image = pygame.transform.scale(self.image, (self.width, self.height))

    def draw(self):
        screen.blit(self.image, (self.x, self.y))

    def move(self, dx):
        self.x += dx

    def fall(self):
        if self.falling:
            self.y += 5


def save_result(name, score):
    with open(RESULTS_FILE, mode="a", newline="") as file:
        writer = csv.writer(file)
        writer.writerow([name, score])


def load_results():
    results = []
    try:
        with open(RESULTS_FILE, mode="r") as file:
            reader = csv.reader(file)
            for row in reader:
                if len(row) == 2:
                    results.append({"name": row[0], "score": int(row[1])})
    except FileNotFoundError:
        pass
    return sorted(results, key=lambda x: x["score"], reverse=True)


def get_player_name():
    name = ""
    input_active = True
    input_rect = pygame.Rect(SCREEN_WIDTH // 2 - 150, 300, 300, 50)
    color_active = BLUE
    color_inactive = GRAY
    color = color_inactive

    while input_active:
        screen.fill(WHITE)
        prompt_text = font.render("Введите ваше имя:", True, BLACK)
        instruction_text = small_font.render("Нажмите Enter для сохранения", True, BLACK)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    input_active = False
                elif event.key == pygame.K_BACKSPACE:
                    name = name[:-1]
                else:
                    name += event.unicode

        screen.blit(prompt_text, (SCREEN_WIDTH // 2 - prompt_text.get_width() // 2, 200))
        screen.blit(instruction_text, (SCREEN_WIDTH // 2 - instruction_text.get_width() // 2, 400))
        pygame.draw.rect(screen, color, input_rect, 2)
        name_surface = font.render(name, True, BLACK)
        screen.blit(name_surface, (input_rect.x + 10, input_rect.y + 10))

        pygame.display.flip()

    return name.strip()


def draw_bonus_text(text, x, y, duration=1.0):
    start_time = pygame.time.get_ticks()
    while pygame.time.get_ticks() - start_time < duration * 1000:
        bonus_text = bonus_font.render(text, True, RED)
        screen.blit(bonus_text, (x, y))
        pygame.display.flip()


def play_game(level=1):
    clock = pygame.time.Clock()
    running = True
    paused = False
    score = 0
    start_time = pygame.time.get_ticks()

    blocks = []
    base_y = SCREEN_HEIGHT - 30

    if level == 1:
        fall_speed = 5
        block_width = 100
        block_height = 30
    elif level == 2:
        fall_speed = 10
        block_width = 80
        block_height = 25
        time_limit = 60

    current_block = Block(randint(0, SCREEN_WIDTH - block_width), 50, block_width, block_height,
                          COLORS[randint(0, len(COLORS) - 1)])
    blocks.append(current_block)

    while running:
        screen.fill(WHITE)
        keys = pygame.key.get_pressed()

        if level == 2:
            elapsed_time = (pygame.time.get_ticks() - start_time) // 1000
            remaining_time = max(time_limit - elapsed_time, 0)
            timer_text = font.render(f"Время: {remaining_time} сек", True, RED)
            screen.blit(timer_text, (SCREEN_WIDTH - 200, 10))

            if remaining_time <= 0:
                running = False
                break

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return score
                if event.key == pygame.K_p:
                    paused = not paused

        if not paused:
            if keys[pygame.K_LEFT] or keys[pygame.K_a]:
                current_block.move(-current_block.speed_x)
            if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
                current_block.move(current_block.speed_x)

            current_block.fall()

            if level == 2 and randint(0, 10) > 8:
                current_block.move(randint(-5, 5))

            if current_block.y + current_block.height >= base_y or (
                    len(blocks) > 1 and current_block.y + current_block.height >= blocks[-2].y
            ):
                current_block.falling = False

                if len(blocks) > 1:
                    prev_block = blocks[-2]
                    if current_block.x + current_block.width < prev_block.x or current_block.x > prev_block.x + prev_block.width:
                        running = False
                        break

                if len(blocks) > 1 and abs(current_block.x - blocks[-2].x) <= 5:
                    score += 20
                    draw_bonus_text("Бонус!", current_block.x + current_block.width // 2, current_block.y - 30)
                else:
                    score += 10

                current_block = Block(randint(0, SCREEN_WIDTH - block_width), 50, block_width, block_height,
                                      COLORS[randint(0, len(COLORS) - 1)])
                blocks.append(current_block)

        for block in blocks:
            block.draw()

        score_text = font.render(f"Очки: {score}", True, BLACK)
        screen.blit(score_text, (10, 10))

        hint_pause = small_font.render("P: Пауза", True, BLACK)
        hint_exit = small_font.render("ESC: Выход", True, BLACK)
        screen.blit(hint_pause, (SCREEN_WIDTH - 150, 10))
        screen.blit(hint_exit, (SCREEN_WIDTH - 150, 40))

        if paused:
            pause_text = font.render("Игра на паузе. Нажмите P для продолжения.", True, BLACK)
            screen.blit(pause_text, (SCREEN_WIDTH // 2 - pause_text.get_width() // 2, SCREEN_HEIGHT // 2))

        pygame.display.flip()
        clock.tick(FPS)

    game_over_text = font.render("Игра окончена! Нажмите ESC для выхода.", True, RED)
    screen.blit(game_over_text, (SCREEN_WIDTH // 2 - game_over_text.get_width() // 2, SCREEN_HEIGHT // 2))
    pygame.display.flip()
    wait_for_escape()
    return score


def wait_for_escape():
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                return


def show_menu():
    while True:
        screen.fill(WHITE)
        mouse_pos = pygame.mouse.get_pos()

        if draw_button("Играть", 300, 200, 200, 50, GRAY, (150, 150, 150), mouse_pos):
            return "level_select"

        if draw_button("Результаты", 300, 300, 200, 50, GRAY, (150, 150, 150), mouse_pos):
            return "results"

        if draw_button("Выход", 300, 400, 200, 50, GRAY, (150, 150, 150), mouse_pos):
            quit_game()

        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                quit_game()


def show_level_select():
    while True:
        screen.fill(WHITE)
        mouse_pos = pygame.mouse.get_pos()

        if draw_button("1 Уровень", 300, 200, 200, 50, GRAY, (150, 150, 150), mouse_pos):
            return "level_1"

        if draw_button("2 Уровень", 300, 300, 200, 50, GRAY, (150, 150, 150), mouse_pos):
            return "level_2"

        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                quit_game()


def play_level_2():
    return 0


def start_game(level):
    score = play_game(level)
    name = get_player_name()
    save_result(name, score)


def draw_button(text, x, y, width, height, color, hover_color, mouse_pos):
    rect = pygame.Rect(x, y, width, height)
    is_hovered = rect.collidepoint(mouse_pos)

    pygame.draw.rect(screen, hover_color if is_hovered else color, rect)

    text_surf = font.render(text, True, BLACK)
    text_rect = text_surf.get_rect(center=(x + width // 2, y + height // 2))
    screen.blit(text_surf, text_rect)

    for event in pygame.event.get():
        if event.type == pygame.MOUSEBUTTONUP and is_hovered:
            return True

    return False


def quit_game():
    pygame.quit()
    sys.exit()


def show_results():
    screen.fill(WHITE)
    results = load_results()
    title_text = font.render("Результаты:", True, BLACK)
    screen.blit(title_text, (SCREEN_WIDTH // 2 - title_text.get_width() // 2, 50))

    for i, result in enumerate(results[:10]):
        result_text = font.render(f"{i + 1}. {result['name']} - {result['score']} очков", True, BLACK)
        screen.blit(result_text, (100, 100 + i * 40))

    back_text = font.render("Нажмите ESC для выхода в меню", True, BLACK)
    screen.blit(back_text, (SCREEN_WIDTH // 2 - back_text.get_width() // 2, SCREEN_HEIGHT - 50))
    pygame.display.flip()

    waiting = True
    while waiting:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                waiting = False


def main():
    clock = pygame.time.Clock()
    running = True
    current_screen = "menu"

    while running:
        if current_screen == "menu":
            current_screen = show_menu()

        elif current_screen == "level_select":
            current_screen = show_level_select()

        elif current_screen == "level_1":
            score = play_game(level=1)
            name = get_player_name()
            save_result(name, score)
            current_screen = "menu"

        elif current_screen == "level_2":
            score = play_game(level=2)
            name = get_player_name()
            save_result(name, score)
            current_screen = "menu"

        elif current_screen == "results":
            show_results()
            current_screen = "menu"

        clock.tick(FPS)

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()

