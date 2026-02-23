import pygame
import time
import random
import os

pygame.init()

# Screen size
WIDTH, HEIGHT = 600, 400
TOP_MARGIN = 40  # Space reserved at the top for score/level display

# Setup display (start windowed)
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Snake Master Deluxe")

# Audio state
is_muted = False

# Load button images (after setting video mode)
try:
    mute_img = pygame.image.load("mute.png").convert_alpha()
    volume_img = pygame.image.load("volume.png").convert_alpha()
except pygame.error:
    print("Audio button images not found. Using default rectangles.")
    mute_img = pygame.Surface((30, 30))
    volume_img = pygame.Surface((30, 30))
    mute_img.fill((100, 100, 100))
    volume_img.fill((200, 200, 200))

# Scale the images
mute_img = pygame.transform.scale(mute_img, (30, 30))
volume_img = pygame.transform.scale(volume_img, (30, 30))

# Colors - modern vibrant palette
COLORS = {
    "backgrounds": [(30, 30, 30), (245, 245, 245), (20, 60, 20), (10, 40, 80), (60, 20, 70), (255, 140, 0)],
    "snake_levels": [(100, 200, 100), (50, 150, 50), (0, 100, 0), (0, 180, 180), (180, 0, 180), (255, 120, 0)],
    "food": (255, 215, 0),  # Gold
    "obstacle": (180, 0, 50),  # Dark red
    "button_bg": (50, 50, 50),
    "button_hover": (80, 80, 80),
    "button_text": (200, 200, 200),
    "text": (220, 220, 220),
    "red": (255, 80, 80)
}

clock = pygame.time.Clock()

# Fonts
font_small = pygame.font.SysFont("comicsansms", 20)
font_big = pygame.font.SysFont("comicsansms", 30)

# Game constants
BLOCK_SIZE = 20

# High score file
HS_FILE = "highscore.txt"

# Load high score from file
def load_high_score():
    if not os.path.isfile(HS_FILE):
        with open(HS_FILE, 'w') as f:
            f.write("0")
        return 0
    with open(HS_FILE, 'r') as f:
        try:
            return int(f.read())
        except:
            return 0

# Game state variables
high_score = load_high_score()
level = 1
is_muted = False # controls whether music is on/off

# Load background music
if not is_muted:
    pygame.mixer.music.load("background_music.mp3")
    pygame.mixer.music.play(-1)

# Save high score to file
def save_high_score(score):
    with open(HS_FILE, 'w') as f:
        f.write(str(score))

# Obstacles for level 3
OBSTACLES = [
    pygame.Rect(200, 150, BLOCK_SIZE*3, BLOCK_SIZE),
    pygame.Rect(400, 100, BLOCK_SIZE, BLOCK_SIZE*4),
    pygame.Rect(100, 300, BLOCK_SIZE*5, BLOCK_SIZE),
]

# Button helper
def draw_button(text, x, y, w, h, mouse_pos, mouse_click):
    rect = pygame.Rect(x, y, w, h)
    color = COLORS["button_hover"] if rect.collidepoint(mouse_pos) else COLORS["button_bg"]
    pygame.draw.rect(screen, color, rect, border_radius=5)
    label = font_small.render(text, True, COLORS["button_text"])
    label_rect = label.get_rect(center=rect.center)
    screen.blit(label, label_rect)
    clicked = False
    if rect.collidepoint(mouse_pos) and mouse_click[0]:
        clicked = True
    return clicked

def draw_text_center(text, y, font, color):
    label = font.render(text, True, color)
    rect = label.get_rect(center=(WIDTH//2, y))
    screen.blit(label, rect)

def draw_snake(snake_list, level):
    # Different snake colors & head shape per level
    snake_colors = COLORS["snake_levels"]
    color = snake_colors[level - 1] if level <= len(snake_colors) else (255, 255, 255)

    for i, seg in enumerate(snake_list):
        rect = pygame.Rect(seg[0], seg[1], BLOCK_SIZE, BLOCK_SIZE)
        pygame.draw.rect(screen, color, rect, border_radius=4)

        # Head - curved face / eyes / tongue
        if i == len(snake_list) - 1:
            eye_radius = 3
            eye_y = seg[1] + 6

            # Eye positions by level
            if level == 1:
                eye_x1 = seg[0] + 5
                eye_x2 = seg[0] + 15
            elif level == 2:
                eye_x1 = seg[0] + 4
                eye_x2 = seg[0] + 16
            else:
                eye_x1 = seg[0] + 6
                eye_x2 = seg[0] + 14

            pygame.draw.circle(screen, (0, 0, 0), (eye_x1, eye_y), eye_radius)
            pygame.draw.circle(screen, (0, 0, 0), (eye_x2, eye_y), eye_radius)

            # Tongue (small rectangle below head)
            tongue_color = (255, 50, 50)  # Red-pink tongue
            tongue_width = 4
            tongue_height = 8
            tongue_x = seg[0] + BLOCK_SIZE // 2 - tongue_width // 2
            tongue_y = seg[1] + BLOCK_SIZE
            tongue_rect = pygame.Rect(tongue_x, tongue_y, tongue_width, tongue_height)
            pygame.draw.rect(screen, tongue_color, tongue_rect)

def draw_food(x, y):
    pygame.draw.circle(screen, COLORS["food"], (x + BLOCK_SIZE//2, y + BLOCK_SIZE//2), BLOCK_SIZE//2)

def draw_mute_button(is_muted):
    button_rect = pygame.Rect(WIDTH - 40, 10, 24, 24)
    icon = mute_img if is_muted else volume_img

    # Draw button background depending on hover
    mouse_pos = pygame.mouse.get_pos()
    if button_rect.collidepoint(mouse_pos):
        pygame.draw.rect(screen, COLORS["button_hover"], button_rect, border_radius=6)
    else:
        pygame.draw.rect(screen, COLORS["button_bg"], button_rect, border_radius=6)

    # Draw the icon on top
    screen.blit(icon, (WIDTH - 40, 10))

    return button_rect

def draw_obstacles():
    for obs in OBSTACLES:
        pygame.draw.rect(screen, COLORS["obstacle"], obs, border_radius=4)

def game_intro():
    global snake_speed
    intro = True
    while intro:
        mouse_pos = pygame.mouse.get_pos()
        mouse_click = pygame.mouse.get_pressed()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()

        screen.fill(COLORS["backgrounds"][0])
        draw_text_center("Snake Master Deluxe", HEIGHT//6, font_big, COLORS["text"])

        if draw_button("EASY", 100, 200, 120, 40, mouse_pos, mouse_click):
            snake_speed = 8
            intro = False
            gameLoop()

        if draw_button("MEDIUM", 240, 200, 120, 40, mouse_pos, mouse_click):
            snake_speed = 12
            intro = False
            gameLoop()

        if draw_button("HARD", 380, 200, 120, 40, mouse_pos, mouse_click):
            snake_speed = 18
            intro = False
            gameLoop()

        if draw_button("QUIT", 240, 260, 120, 40, mouse_pos, mouse_click):
            pygame.quit()
            quit()

        pygame.display.update()
        clock.tick(15)

def pause_menu():
    paused = True
    while paused:
        mouse_pos = pygame.mouse.get_pos()
        mouse_click = pygame.mouse.get_pressed()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_p:
                    paused = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_F11:
                    toggle_fullscreen()

        screen.fill(COLORS["backgrounds"][0])
        draw_text_center("Paused", HEIGHT//3, font_big, COLORS["text"])
        if draw_button("Resume (P)", 180, 180, 240, 50, mouse_pos, mouse_click):
            paused = False
        if draw_button("Restart", 180, 250, 240, 50, mouse_pos, mouse_click):
            return "restart"
        if draw_button("Quit", 180, 320, 240, 50, mouse_pos, mouse_click):
            pygame.quit()
            quit()

        pygame.display.update()
        clock.tick(15)
    return "resume"

def game_over_screen(score):
    global high_score
    while True:
        mouse_pos = pygame.mouse.get_pos()
        mouse_click = pygame.mouse.get_pressed()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()

        screen.fill(COLORS["backgrounds"][0])
        draw_text_center(f"Game Over! Score: {score} High Score: {high_score}", HEIGHT//3, font_big, COLORS["red"])

        if draw_button("RESTART", 150, 220, 140, 50, mouse_pos, mouse_click):
            return "restart"
        if draw_button("QUIT", 310, 220, 140, 50, mouse_pos, mouse_click):
            pygame.quit()
            quit()

        pygame.display.update()
        clock.tick(15)

def toggle_fullscreen():
    current_flags = pygame.display.get_surface().get_flags()
    is_fullscreen = current_flags & pygame.FULLSCREEN
    if is_fullscreen:
        pygame.display.set_mode((WIDTH, HEIGHT))
    else:
        pygame.display.set_mode((WIDTH, HEIGHT), pygame.FULLSCREEN)

def gameLoop():
    global high_score, level, snake_speed, is_muted

    x = WIDTH // 2
    y = HEIGHT // 2
    dx = BLOCK_SIZE
    dy = 0

    snake_list = []
    snake_length = 1

    food_x = round(random.randrange(0, WIDTH - BLOCK_SIZE) / BLOCK_SIZE) * BLOCK_SIZE
    food_y = round(random.randrange(TOP_MARGIN, HEIGHT - BLOCK_SIZE) / BLOCK_SIZE) * BLOCK_SIZE

    score = 0
    level = 1

    paused = False

    while True:
        mouse_pos = pygame.mouse.get_pos()
        mouse_click = pygame.mouse.get_pressed()
        mute_button_rect = draw_mute_button(is_muted)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                save_high_score(high_score)
                pygame.quit()
                quit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT and dx == 0:
                    dx = -BLOCK_SIZE
                    dy = 0
                elif event.key == pygame.K_RIGHT and dx == 0:
                    dx = BLOCK_SIZE
                    dy = 0
                elif event.key == pygame.K_UP and dy == 0:
                    dx = 0
                    dy = -BLOCK_SIZE
                elif event.key == pygame.K_DOWN and dy == 0:
                    dx = 0
                    dy = BLOCK_SIZE
                elif event.key == pygame.K_p:
                    paused = True
                elif event.key == pygame.K_F11:
                    toggle_fullscreen()

            # this must be OUTSIDE of the KEYDOWN section!
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1 and mute_button_rect.collidepoint(event.pos):
                            is_muted = not is_muted
                            if is_muted:
                                pygame.mixer.music.pause()
                            else:
                                pygame.mixer.music.unpause()
                 
        if paused:
            action = pause_menu()
            if action == "restart":
                return gameLoop()
            elif action == "resume":
                paused = False

        x += dx
        y += dy

        # Wrap around screen
        if x >= WIDTH:
            x = 0
        elif x < 0:
            x = WIDTH - BLOCK_SIZE
        if y >= HEIGHT:
            y = TOP_MARGIN
        elif y < TOP_MARGIN:
            y = HEIGHT - BLOCK_SIZE

        # Background by level
        screen.fill(COLORS["backgrounds"][level-1])

        # Display Score and Level
        score_text = font_small.render(f"Score: {score}  Level: {level}", True, COLORS["text"])
        screen.blit(score_text, (10, 10))


        # Draw obstacles on level 3
        if level == 3:
            draw_obstacles()

        # Draw food
        draw_food(food_x, food_y)

        # Update snake
        snake_head = [x, y]
        snake_list.append(snake_head)

        if len(snake_list) > snake_length:
            del snake_list[0]

        # Check collisions with self
        for segment in snake_list[:-1]:
            if segment == snake_head:
                save_high_score(high_score)
                action = game_over_screen(score)
                if action == "restart":
                    return gameLoop()

        # Check collision with obstacles
        if level == 3:
            head_rect = pygame.Rect(x, y, BLOCK_SIZE, BLOCK_SIZE)
            for obs in OBSTACLES:
                if head_rect.colliderect(obs):
                    save_high_score(high_score)
                    action = game_over_screen(score)
                    if action == "restart":
                        return gameLoop()

        draw_snake(snake_list, level)
        mute_button_rect = draw_mute_button(is_muted)
        pygame.display.update()

        # Check food eaten
        if x == food_x and y == food_y:
            food_x = round(random.randrange(0, WIDTH - BLOCK_SIZE) / BLOCK_SIZE) * BLOCK_SIZE
            food_y = round(random.randrange(TOP_MARGIN, HEIGHT - BLOCK_SIZE) / BLOCK_SIZE) * BLOCK_SIZE
            snake_length += 1
            score += 1
            if score > high_score:
                high_score = score
            # Level progression
            if score >= 100:
                level = 6
                snake_speed = 18
            elif score >= 80:
                level = 5
                snake_speed = 16
            elif score >= 60:
                level = 4
                snake_speed = 14
            elif score >= 40:
                level = 3
                snake_speed = 12
            elif score >= 25:
                level = 2
                snake_speed = 10
            else:
                level = 1
                snake_speed = 8

        clock.tick(snake_speed)


# Main launcher
if __name__ == "__main__":
    game_intro()
