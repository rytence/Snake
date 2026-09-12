"""A Pygame snake game. Run with: python main.py."""

import random
from pathlib import Path

import pygame


CELL = 24
COLS, ROWS = 30, 22
HEADER = 72
WIDTH, HEIGHT = COLS * CELL, ROWS * CELL + HEADER
BACKGROUND = (16, 22, 32)
TEXT = (230, 237, 245)
MUTED = (147, 164, 185)
DIRECTIONS = {
    pygame.K_UP: (0, -1), pygame.K_w: (0, -1),
    pygame.K_DOWN: (0, 1), pygame.K_s: (0, 1),
    pygame.K_LEFT: (-1, 0), pygame.K_a: (-1, 0),
    pygame.K_RIGHT: (1, 0), pygame.K_d: (1, 0),
}


class SoundEffects:
    def __init__(self):
        self.muted = False
        self.sounds = {}
        self.music_loaded = False
        if not pygame.mixer.get_init():
            return
        folder = Path(__file__).resolve().parent / "assets" / "sounds"
        for name, filename in {
            "eat": "bing_01.mp3",
            "crash": "bung_01.mp3",
            "restart": "bing_02.mp3",
            "win": "bing_02.mp3",
        }.items():
            try:
                sound = pygame.mixer.Sound(str(folder / filename))
                sound.set_volume(0.55)
                self.sounds[name] = sound
            except (pygame.error, OSError):
                # A missing sound should not prevent playing the game.
                pass
        try:
            pygame.mixer.music.load(str(folder / "gone_fishin.mp3"))
            # Keep the banjo underneath the goofy sound effects.
            pygame.mixer.music.set_volume(0.25)
            pygame.mixer.music.play(loops=-1)
            self.music_loaded = True
        except (pygame.error, OSError):
            pass

    def play(self, name):
        if not self.muted and pygame.mixer.get_init() and name in self.sounds:
            self.sounds[name].play()

    def toggle_mute(self):
        self.muted = not self.muted
        if pygame.mixer.get_init():
            if self.muted:
                pygame.mixer.stop()
            if self.music_loaded:
                if self.muted:
                    pygame.mixer.music.pause()
                else:
                    pygame.mixer.music.unpause()


class SnakeGame:
    def __init__(self):
        self.best = 0
        self.reset()

    def reset(self):
        x, y = COLS // 2, ROWS // 2
        self.snake = [(x, y), (x - 1, y), (x - 2, y)]
        self.direction = (1, 0)
        self.next_direction = self.direction
        self.turn_pending = False
        self.score = 0
        self.paused = self.game_over = self.won = False
        self.food = self.spawn_food()

    def spawn_food(self):
        occupied = set(self.snake)
        empty = [(x, y) for y in range(ROWS) for x in range(COLS)
                 if (x, y) not in occupied]
        return random.choice(empty) if empty else None

    @property
    def step_interval(self):
        return 1 / min(10 + self.score // 3, 20)

    def turn(self, direction):
        if self.paused or self.game_over or self.turn_pending:
            return
        reverse = (-self.direction[0], -self.direction[1])
        if direction != reverse and direction != self.direction:
            self.next_direction = direction
            self.turn_pending = True

    def step(self):
        if self.paused or self.game_over:
            return
        self.direction = self.next_direction
        self.turn_pending = False
        x, y = self.snake[0]
        dx, dy = self.direction
        head = (x + dx, y + dy)
        eating = head == self.food
        # Moving into the tail is legal when it vacates its cell.
        body = self.snake if eating else self.snake[:-1]
        if not (0 <= head[0] < COLS and 0 <= head[1] < ROWS) or head in body:
            self.game_over = True
            return "crash"
        self.snake.insert(0, head)
        if eating:
            self.score += 1
            self.best = max(self.best, self.score)
            self.food = self.spawn_food()
            if self.food is None:
                self.won = self.game_over = True
                return "win"
            return "eat"
        else:
            self.snake.pop()


def cell_rect(position):
    x, y = position
    return pygame.Rect(x * CELL, HEADER + y * CELL, CELL, CELL)


def draw(screen, game, font, small_font, title_font, sounds=None):
    screen.fill(BACKGROUND)
    label = font.render(f"SNAKE    Score: {game.score}    Best: {game.best}", True, TEXT)
    screen.blit(label, (16, 10))
    audio_available = sounds is not None and (sounds.sounds or sounds.music_loaded)
    audio_status = "off" if not audio_available else "muted" if sounds.muted else "on"
    label = small_font.render(
        f"Arrows/WASD: move   Space: pause   R: restart   M: sound {audio_status}   Esc: quit",
        True, MUTED)
    screen.blit(label, (16, 43))
    pygame.draw.rect(screen, (21, 30, 42), (0, HEADER, WIDTH, ROWS * CELL))
    for x in range(0, WIDTH, CELL):
        pygame.draw.line(screen, (28, 39, 53), (x, HEADER), (x, HEIGHT))
    for y in range(HEADER, HEIGHT, CELL):
        pygame.draw.line(screen, (28, 39, 53), (0, y), (WIDTH, y))
    if game.food is not None:
        pygame.draw.circle(screen, (255, 102, 120), cell_rect(game.food).center, CELL // 2 - 3)
    for index, position in enumerate(game.snake):
        color = (113, 240, 171) if index == 0 else (64, 211, 135)
        pygame.draw.rect(screen, color, cell_rect(position).inflate(-3, -3), border_radius=5)
    center_x, center_y = cell_rect(game.snake[0]).center
    dx, dy = game.direction
    for offset in (-4, 4):
        eye = (center_x + dx * 5 - dy * offset, center_y + dy * 5 + dx * offset)
        pygame.draw.circle(screen, BACKGROUND, eye, 2)
    if game.paused or game.game_over:
        overlay = pygame.Surface((WIDTH, HEIGHT - HEADER), pygame.SRCALPHA)
        overlay.fill((8, 12, 20, 205))
        screen.blit(overlay, (0, HEADER))
        title = "YOU WIN!" if game.won else "GAME OVER" if game.game_over else "PAUSED"
        hint = "Press R to play again" if game.game_over else "Press Space to continue"
        center = (WIDTH // 2, HEADER + ROWS * CELL // 2)
        label = title_font.render(title, True, TEXT)
        screen.blit(label, label.get_rect(center=(center[0], center[1] - 25)))
        label = font.render(hint, True, MUTED)
        screen.blit(label, label.get_rect(center=(center[0], center[1] + 25)))


def main():
    pygame.mixer.pre_init(44100, -16, 2, 512)
    pygame.init()
    try:
        screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("Snake")
        clock = pygame.time.Clock()
        font = pygame.font.Font(None, 28)
        small_font = pygame.font.Font(None, 22)
        title_font = pygame.font.Font(None, 58)
        game = SnakeGame()
        sounds = SoundEffects()
        elapsed = 0.0
        running = True
        while running:
            elapsed += min(clock.tick(60) / 1000, 0.1)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.WINDOWFOCUSLOST and not game.game_over:
                    game.paused = True
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        running = False
                    elif event.key == pygame.K_r:
                        game.reset()
                        if pygame.mixer.get_init():
                            pygame.mixer.stop()
                        sounds.play("restart")
                        elapsed = 0.0
                    elif event.key == pygame.K_m:
                        sounds.toggle_mute()
                    elif event.key == pygame.K_SPACE and not game.game_over:
                        game.paused = not game.paused
                        elapsed = 0.0
                    elif event.key in DIRECTIONS:
                        game.turn(DIRECTIONS[event.key])
            if not running:
                break
            if game.paused or game.game_over:
                elapsed = 0.0
            elif elapsed >= game.step_interval:
                elapsed -= game.step_interval
                sound_event = game.step()
                if sound_event is not None:
                    sounds.play(sound_event)
            draw(screen, game, font, small_font, title_font, sounds)
            pygame.display.flip()
    finally:
        pygame.quit()


if __name__ == "__main__":
    main()
