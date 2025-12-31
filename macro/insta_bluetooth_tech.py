
import pydirectinput
import time
import threading
from pynput import keyboard

# --- НАСТРОЙКИ ---
ROTATION = 400
ROTATION_AMOUNT = 400
LONG_WAIT = 1.83
SHORT_WAIT = 0.40
CLICK_DURATION = 0.05  # Длительность "зажатия" ЛКМ в секундах.

pressed_keys = set()

def perform_manual_click_sequence(right=True):
    """
    Выполняет последовательность с ручным, более надежным кликом.
    right=True  -> версия для 'E'
    right=False -> зеркальная версия для 'Q'
    """
    print("Последовательность начата: Зажимаю ПКМ...")
    pydirectinput.mouseDown(button='right')
    
    print(f"ПКМ зажата. Жду {LONG_WAIT} сек...")
    time.sleep(LONG_WAIT)
    
    # --- Первый "ручной" клик ЛКМ ---
    print("Первый клик ЛКМ (ручной режим)...")
    pydirectinput.mouseDown(button='left')
    time.sleep(CLICK_DURATION)
    pydirectinput.mouseUp(button='left')
    # ------------------------------------
    
    # --- Зажимаем A+W (для E) или D+W (для Q) ---
    if right:
        print("Зажимаю клавиши 'A' и 'W'...")
        pydirectinput.keyDown('a')
        pydirectinput.keyDown('w')
    else:
        print("Зажимаю клавиши 'D' и 'W'...")
        pydirectinput.keyDown('d')
        pydirectinput.keyDown('w')
    # ---------------------------------------------
    
    print(f"Жду {SHORT_WAIT} сек перед поворотом...")
    time.sleep(SHORT_WAIT)
    
    # --- Двигаем мышь ---
    move_value = ROTATION_AMOUNT if right else -ROTATION_AMOUNT
    print(f"Двигаю мышь на {move_value}...")
    pydirectinput.moveRel(move_value, 0, relative=True, _pause=False)
    
    # --- Второй "ручной" клик ЛКМ ---
    print("Второй клик ЛКМ (ручной режим)...")
    pydirectinput.mouseDown(button='left')
    time.sleep(CLICK_DURATION)
    pydirectinput.mouseUp(button='left')
    # ---------------------------------
    
    # --- Держим клавиши ещё 2 секунды ---
    print("Держу клавиши ещё 2 секунды...")
    time.sleep(2)
    if right:
        print("Отпускаю 'A' и 'W'...")
        pydirectinput.keyUp('a')
        pydirectinput.keyUp('w')
    else:
        print("Отпускаю 'D' и 'W'...")
        pydirectinput.keyUp('d')
        pydirectinput.keyUp('w')
    # ------------------------------------
    
    print("Отпускаю ПКМ. Последовательность завершена.")
    pydirectinput.mouseUp(button='right')


def on_press(key):
    try:
        key_char = key.char
    except AttributeError:
        key_char = key.name

    # --- E: обычная версия ---
    if key_char == 'e' and key_char not in pressed_keys:
        print("Нажата 'E'. Запускаю последовательность (вправо).")
        pydirectinput.moveRel(-ROTATION, 0, relative=True, _pause=False)
        sequence_thread = threading.Thread(target=perform_manual_click_sequence, args=(True,))
        sequence_thread.start()

    # --- Q: зеркальная версия ---
    if key_char == 'q' and key_char not in pressed_keys:
        print("Нажата 'Q'. Запускаю зеркальную последовательность (влево).")
        pydirectinput.moveRel(ROTATION, 0, relative=True, _pause=False)
        sequence_thread = threading.Thread(target=perform_manual_click_sequence, args=(False,))
        sequence_thread.start()
    
    pressed_keys.add(key_char)


def on_release(key):
    try:
        key_char = key.char
    except AttributeError:
        key_char = key.name

    if key_char in pressed_keys:
        pressed_keys.remove(key_char)
    
    if key == keyboard.Key.esc:
        return False


# --- Основная часть скрипта ---
pydirectinput.PAUSE = 0
print("--- Скрипт с РУЧНЫМ кликом для лучшей совместимости ---")
print("У вас есть 3 секунды, чтобы переключиться в окно игры...")
time.sleep(3)
print("Готово. Нажимайте 'E' (вправо) или 'Q' (влево). Для выхода нажмите 'Esc'.")

with keyboard.Listener(on_press=on_press, on_release=on_release) as listener:
    listener.join()
print("Скрипт остановлен.")
