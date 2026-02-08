import sounddevice as sd
import numpy as np
from pygame import *
from random import randint

# ====== НАЛАШТУВАННЯ АУДІО ======
sr = 16000
block = 256
mic_level = 0.0

def audio_cb(indata, frames, time, status):
    global mic_level
    if status:
        return
    # Рахуємо RMS (середньоквадратичну гучність)
    rms = float(np.sqrt(np.mean(indata**2)))
    mic_level = 0.85 * mic_level + 0.15 * rms

# ====== НАЛАШТУВАННЯ ГРИ ======
init()
window_size = 1200, 800
window = display.set_mode(window_size)
display.set_caption("Voice Bird")
clock = time.Clock()

# Фізика та параметри
THRESH = 0.005      # Поріг чутливості мікрофона (підлаштуй під себе)
IMPULSE = -9.0     # Сила стрибка вгору
GRAVITY = 0.6       # Сила падіння вниз

player_rect = Rect(150, window_size[1]//2-100, 70, 70)
y_vel = 0.0
score = 0
lose = False
main_font = font.Font(None, 100)

def generate_pipes(count, pipe_width=140, gap=260, min_height=50, max_height=450, distance=600):
    pipes = []
    start_x = window_size[0]
    for i in range(count):
        height = randint(min_height, max_height)
        top_pipe = Rect(start_x, 0, pipe_width, height)
        bottom_pipe = Rect(start_x, height + gap, pipe_width, window_size[1] - (height + gap))
        pipes.extend([top_pipe, bottom_pipe])
        start_x += distance
    return pipes

pipes = generate_pipes(150)

# ====== ГОЛОВНИЙ ЦИКЛ ======
with sd.InputStream(samplerate=sr, channels=1, blocksize=block, callback=audio_cb):
    while True:
        for e in event.get():
            if e.type == QUIT:
                quit()
                exit()

        window.fill('sky blue')

        # Обробка натискань клавіш
        keys = key.get_pressed()

        if not lose:
            # Стрибок (Голос або Клавіша W)
            if mic_level > THRESH or keys[K_w]:
                y_vel = IMPULSE
            
            # Застосування гравітації
            y_vel += GRAVITY
            player_rect.y += int(y_vel)

            # Перевірка меж екрана
            if player_rect.top <= 0:
                player_rect.top = 0
                y_vel = 0
            if player_rect.bottom >= window_size[1]:
                lose = True

        # Малювання та рух труб
        for pipe in pipes[:]:
            if not lose:
                pipe.x -= 8  # швидкість руху труб
            
            draw.rect(window, 'green', pipe)

            # Видалення труб та нарахування очок
            if pipe.x <= -pipe.width:
                pipes.remove(pipe)
                score += 0.5 # 0.5 бо дві труби (верхня і нижня) складають один прохід

            # Перевірка зіткнень
            if player_rect.colliderect(pipe):
                lose = True

        # Малювання гравця
        draw.rect(window, 'red', player_rect)

        # Додавання нових труб, якщо вони закінчуються
        if len(pipes) < 10:
            pipes += generate_pipes(50)

        # Відображення рахунку
        score_text = main_font.render(f'Score: {int(score)}', True, 'black')
        window.blit(score_text, (window_size[0]//2 - score_text.get_width()//2, 50))

        # Екран програшу
        if lose:
            lose_text = main_font.render('GAME OVER! Press R', True, 'darkred')
            window.blit(lose_text, (window_size[0]//2 - lose_text.get_width()//2, window_size[1]//2))
            
            if keys[K_r]:
                # Скидання гри
                lose = False
                score = 0
                y_vel = 0
                player_rect.y = window_size[1]//2-100
                pipes = generate_pipes(150)

        display.update()
        clock.tick(60)
