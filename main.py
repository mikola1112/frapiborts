import pygame
from random import randint
import sys  # Потрібен для коректного виходу

pygame.init()
window_size = 1200, 800
window = pygame.display.set_mode(window_size)
pygame.display.set_caption("Flappy Square")
clock = pygame.time.Clock()

player_rect = pygame.Rect(150, window_size[1]//2-100, 100, 100)

# Додали параметр start_pos, щоб нові труби з'являлися після останніх
def generate_pipes(count, start_pos=None, pipe_width=140, gap=280, distance=650):
    pipes = []
    # Якщо позиція не вказана, починаємо за краєм екрана
    start_x = start_pos if start_pos is not None else window_size[0]
    
    for i in range(count):
        height = randint(50, 440)
        top_pipe = pygame.Rect(start_x, 0, pipe_width, height)
        bottom_pipe = pygame.Rect(start_x, height + gap, pipe_width, window_size[1] - (height + gap))
        pipes.extend([top_pipe, bottom_pipe])
        start_x += distance
    return pipes

# Початкові налаштування
pipes = generate_pipes(20) # Для старту достатньо 20
main_font = pygame.font.Font(None, 100)
score = 0
lose = False
y_vel = 2

# Головний цикл
while True:
    # 1. ОБРОБКА ПОДІЙ
    for e in pygame.event.get():
        if e.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

    # 2. ЛОГІКА ГРИ
    if not lose:
        keys = pygame.key.get_pressed()
        if keys[pygame.K_w]: player_rect.y -= 10
        if keys[pygame.K_s]: player_rect.y += 10
        
        # Обробка руху труб та зіткнень
        for pipe in pipes[:]:
            pipe.x -= 8
            if pipe.x <= -pipe.width:
                pipes.remove(pipe)
                score += 0.5 # Оскільки труб дві (верхня і нижня), за пару отримаємо +1
            
            if player_rect.colliderect(pipe):
                lose = True

        # Нескінченна генерація: якщо труб мало, додаємо нові в кінець останньої
        if len(pipes) < 10:
            last_pipe_x = pipes[-1].x
            pipes += generate_pipes(20, start_pos=last_pipe_x + 650)

        # Перевірка виходу за межі екрана
        if player_rect.top <= 0 or player_rect.bottom >= window_size[1]:
            lose = True
    else:
        # Логіка програшу (падіння)
        if player_rect.y < window_size[1]:
            player_rect.y += y_vel
            y_vel *= 1.1 # Прискорення падіння
        
        # Рестарт
        keys = pygame.key.get_pressed()
        if keys[pygame.K_r]:
            lose = False
            score = 0
            y_vel = 2
            player_rect.y = window_size[1]//2-100
            pipes = generate_pipes(20)

    # 3. МАЛЮВАННЯ
    window.fill('sky blue')
    
    # Малюємо труби
    for pipe in pipes:
        pygame.draw.rect(window, 'green', pipe)
    
    # Малюємо гравця
    pygame.draw.rect(window, 'red', player_rect)
    
    # Малюємо рахунок
    score_text = main_font.render(f'Score: {int(score)}', True, 'black')
    window.blit(score_text, (window_size[0]//2 - score_text.get_width()//2, 40))

    if lose:
        lose_text = main_font.render('PRESS R TO RESTART', True, 'red')
        window.blit(lose_text, (window_size[0]//2 - lose_text.get_width()//2, window_size[1]//2))

    pygame.display.update()
    clock.tick(60)
