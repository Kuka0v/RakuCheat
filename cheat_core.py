# cheat_core.py
# ЭТОТ ФАЙЛ ЗАГРУЖАЕТСЯ С GITHUB И ЗАПУСКАЕТСЯ В ОПЕРАТИВНОЙ ПАМЯТИ

import glfw
import OpenGL.GL as gl
import imgui
from imgui.integrations.glfw import GlfwRenderer
import keyboard
import mouse  # Теперь доступно, так как есть в лоадере
import time
import ctypes
import threading
import winsound
import sys

# ==========================================
# ПОЛУЧЕНИЕ ДАННЫХ ОТ ЛОАДЕРА
# ==========================================
# Лоадер передает эти переменные через globals().
# Если запустить скрипт локально (без лоадера), используются значения по умолчанию.
CTX_USER = globals().get("USER_LOGIN", "DevUser")
CTX_STATUS = globals().get("USER_STATUS", "Free")
CTX_AVATAR_ID = globals().get("USER_AVATAR_ID", None) # ID текстуры OpenGL

# ==========================================
# КОНФИГУРАЦИЯ
# ==========================================
config = {
    "running": True,
    "active_tab": "Legit",
    "menu_open": True,
    
    # Lag Switch
    "lag_enabled": False, 
    "lag_active": False, 
    "lag_bind": "Q", 
    "lag_time": 2.0, 
    "lag_start_time": 0.0,
    
    # Macro (NoRecoil)
    "macro_enabled": False,
    "recoil_x": 0,
    "recoil_y": 2, # Сила тяги вниз
    
    # Visuals
    "crosshair_enabled": False, 
    "crosshair_color": [0.0, 1.0, 0.0, 1.0], 
    "crosshair_size": 10.0,
    "crosshair_gap": 2.0,
    
    # System
    "binding_mode": None 
}

# ==========================================
# ЛОГИКА ЧИТА (ПОТОКИ)
# ==========================================
def background_logic():
    """Фоновый поток для макросов и лаг-свитча"""
    while config["running"]:
        current_time = time.time()
        
        # --- LAG SWITCH ---
        if config["lag_active"]:
            if (current_time - config["lag_start_time"]) > config["lag_time"]:
                config["lag_active"] = False
                winsound.Beep(500, 100) # Звук отключения
        
        if config["lag_enabled"] and keyboard.is_pressed(config["lag_bind"]):
            if not config["lag_active"]: # Только активация
                config["lag_active"] = True
                config["lag_start_time"] = time.time()
                winsound.Beep(1000, 100) # Звук включения
            time.sleep(0.2)

        # --- MACRO (NO RECOIL) ---
        if config["macro_enabled"]:
            if mouse.is_pressed(button='left'):
                # Тянем мышку вниз (очень простая реализация)
                mouse.move(config["recoil_x"], config["recoil_y"], absolute=False, duration=0.01)
                time.sleep(0.01)

        time.sleep(0.005)

# ==========================================
# GUI: СТИЛИ И ОТРИСОВКА
# ==========================================
def apply_raku_theme():
    style = imgui.get_style()
    colors = style.colors
    
    style.window_rounding = 10.0
    style.child_rounding = 6.0
    style.frame_rounding = 4.0
    style.grab_rounding = 4.0
    style.popup_rounding = 6.0
    style.scrollbar_size = 0.0
    style.window_padding = (0, 0)
    
    # Цветовая палитра Raku
    c_bg = (0.07, 0.07, 0.09, 1.00)
    c_child = (0.10, 0.10, 0.12, 1.00)
    c_accent = (0.35, 0.45, 0.90, 1.00) # Синий акцент
    
    colors[imgui.COLOR_WINDOW_BACKGROUND] = c_bg
    colors[imgui.COLOR_CHILD_BACKGROUND]  = c_child
    colors[imgui.COLOR_TEXT]              = (0.90, 0.90, 0.90, 1.00)
    colors[imgui.COLOR_BUTTON]            = (0.00, 0.00, 0.00, 0.00) # Прозрачные кнопки
    colors[imgui.COLOR_BUTTON_HOVERED]    = (0.15, 0.15, 0.18, 1.00)
    colors[imgui.COLOR_BUTTON_ACTIVE]     = (0.20, 0.20, 0.23, 1.00)
    colors[imgui.COLOR_FRAME_BACKGROUND]  = (0.15, 0.15, 0.18, 1.00)
    colors[imgui.COLOR_HEADER]            = c_accent
    colors[imgui.COLOR_CHECK_MARK]        = c_accent
    colors[imgui.COLOR_SLIDER_GRAB]       = c_accent
    colors[imgui.COLOR_SLIDER_GRAB_ACTIVE]= (0.40, 0.50, 1.00, 1.00)

def draw_sidebar_button(label, active):
    """Рисует кнопку в сайдбаре"""
    imgui.push_style_var(imgui.STYLE_BUTTON_TEXT_ALIGN, (0.0, 0.5))
    
    if active:
        imgui.push_style_color(imgui.COLOR_BUTTON, 0.15, 0.16, 0.18, 1.0)
        imgui.push_style_color(imgui.COLOR_TEXT, 1.0, 1.0, 1.0, 1.0)
        # Вертикальная полоска активной вкладки
        draw_list = imgui.get_window_draw_list()
        p = imgui.get_cursor_screen_pos()
        draw_list.add_rect_filled(p.x, p.y + 5, p.x + 3, p.y + 35, imgui.get_color_u32_rgba(0.35, 0.45, 0.90, 1.0))
    else:
        imgui.push_style_color(imgui.COLOR_BUTTON, 0.0, 0.0, 0.0, 0.0)
        imgui.push_style_color(imgui.COLOR_TEXT, 0.6, 0.6, 0.6, 1.0)
        
    clicked = imgui.button(f"    {label}", width=190, height=40)
    
    imgui.pop_style_color(2)
    imgui.pop_style_var()
    return clicked

def render_sidebar():
    imgui.begin_child("Sidebar", width=200, height=0, border=False)
    
    # Лого
    imgui.dummy(0, 20)
    imgui.set_cursor_pos_x(20)
    imgui.set_window_font_scale(1.4)
    imgui.text_colored("RAKU CHEAT", 0.35, 0.45, 0.90, 1.0)
    imgui.set_window_font_scale(1.0)
    imgui.dummy(0, 30)
    
    # Меню
    if draw_sidebar_button("LEGIT", config["active_tab"] == "Legit"): config["active_tab"] = "Legit"
    imgui.dummy(0, 5)
    if draw_sidebar_button("VISUALS", config["active_tab"] == "Visuals"): config["active_tab"] = "Visuals"
    imgui.dummy(0, 5)
    if draw_sidebar_button("MISC", config["active_tab"] == "Misc"): config["active_tab"] = "Misc"
    
    # Профиль пользователя (внизу)
    h = imgui.get_window_height()
    imgui.set_cursor_pos_y(h - 80)
    
    imgui.push_style_color(imgui.COLOR_CHILD_BACKGROUND, 0.08, 0.08, 0.10, 1.0)
    imgui.begin_child("UserCard", width=180, height=60, border=True)
    
    # Аватар
    imgui.set_cursor_pos((10, 10))
    if CTX_AVATAR_ID:
        imgui.image(CTX_AVATAR_ID, 40, 40)
    else:
        # Если аватарки нет, рисуем кружок
        dl = imgui.get_window_draw_list()
        p = imgui.get_cursor_screen_pos()
        dl.add_circle_filled(p.x + 20, p.y + 20, 20, imgui.get_color_u32_rgba(0.3, 0.3, 0.3, 1.0))
    
    # Имя и статус
    imgui.set_cursor_pos((60, 12))
    imgui.text(str(CTX_USER))
    imgui.set_cursor_pos((60, 28))
    
    # Цвет статуса
    s_col = (0.5, 0.5, 0.5, 1.0)
    if "Admin" in CTX_STATUS: s_col = (1.0, 0.3, 0.3, 1.0)
    elif "Premium" in CTX_STATUS: s_col = (1.0, 0.8, 0.2, 1.0)
    
    imgui.text_colored(str(CTX_STATUS), *s_col)
    
    imgui.end_child()
    imgui.pop_style_color()
    
    imgui.end_child()

def render_content():
    imgui.same_line()
    imgui.begin_child("Content", width=0, height=0, border=False)
    imgui.dummy(0, 10)
    
    imgui.indent(20)
    imgui.text_colored(f"Settings > {config['active_tab']}", 0.5, 0.5, 0.5, 1.0)
    imgui.dummy(0, 20)
    
    if config["active_tab"] == "Legit":
        imgui.text("Macro Settings")
        imgui.separator()
        imgui.dummy(0, 10)
        _, config["macro_enabled"] = imgui.checkbox("Enable NoRecoil", config["macro_enabled"])
        imgui.text("Vertical Pull")
        _, config["recoil_y"] = imgui.slider_int("##pull", config["recoil_y"], 1, 20)
    
    elif config["active_tab"] == "Visuals":
        imgui.text("Overlay Settings")
        imgui.separator()
        imgui.dummy(0, 10)
        _, config["crosshair_enabled"] = imgui.checkbox("Draw Crosshair", config["crosshair_enabled"])
        
        imgui.dummy(0, 5)
        imgui.text("Size")
        _, config["crosshair_size"] = imgui.slider_float("##size", config["crosshair_size"], 1.0, 50.0)
        imgui.text("Gap")
        _, config["crosshair_gap"] = imgui.slider_float("##gap", config["crosshair_gap"], 0.0, 20.0)
        imgui.text("Color")
        _, config["crosshair_color"] = imgui.color_edit4("##col", *config["crosshair_color"])
        
    elif config["active_tab"] == "Misc":
        imgui.text("Network Manipulation")
        imgui.separator()
        imgui.dummy(0, 10)
        _, config["lag_enabled"] = imgui.checkbox("Enable Lag Switch", config["lag_enabled"])
        
        # Биндинг клавиши
        imgui.dummy(0, 5)
        imgui.text("Bind Key: ")
        imgui.same_line()
        btn_txt = "PRESS KEY" if config["binding_mode"] == "LAG" else f"[{config['lag_bind']}]"
        if imgui.button(btn_txt, width=100):
            config["binding_mode"] = "LAG"
            
        imgui.text("Duration (sec)")
        _, config["lag_time"] = imgui.slider_float("##dur", config["lag_time"], 0.1, 5.0)
        
        if config["lag_active"]:
            imgui.dummy(0, 20)
            imgui.text_colored("!!! LAG ACTIVE !!!", 1.0, 0.0, 0.0, 1.0)

    imgui.end_child()

# ==========================================
# ОСНОВНАЯ ФУНКЦИЯ (ВЫЗЫВАЕТСЯ ЛОАДЕРОМ)
# ==========================================
def main():
    if not glfw.init():
        return

    # Настройки окна оверлея
    glfw.window_hint(glfw.FLOATING, True) # Поверх всех окон
    glfw.window_hint(glfw.DECORATED, False) # Без рамок
    glfw.window_hint(glfw.TRANSPARENT_FRAMEBUFFER, True) # Прозрачный
    glfw.window_hint(glfw.SAMPLES, 4)
    
    # Получаем разрешение экрана
    w_screen, h_screen = ctypes.windll.user32.GetSystemMetrics(0), ctypes.windll.user32.GetSystemMetrics(1)
    window = glfw.create_window(w_screen, h_screen, "Raku Overlay", None, None)
    
    # Прозрачность для мыши (чтобы кликать сквозь меню, когда оно закрыто)
    glfw.set_window_attrib(window, glfw.MOUSE_PASSTHROUGH, False)
    
    glfw.make_context_current(window)
    glfw.swap_interval(1)

    imgui.create_context()
    impl = GlfwRenderer(window)
    apply_raku_theme()
    
    # Запуск логики в отдельном потоке
    logic_thread = threading.Thread(target=background_logic, daemon=True)
    logic_thread.start()
    
    last_insert_state = False

    while not glfw.window_should_close(window):
        glfw.poll_events()
        
        # --- ОБРАБОТКА INPUT (Insert menu) ---
        if keyboard.is_pressed('insert'):
            if not last_insert_state:
                config["menu_open"] = not config["menu_open"]
                # Если меню открыто - мышь перехватывается окном, если закрыто - проходит насквозь в игру
                glfw.set_window_attrib(window, glfw.MOUSE_PASSTHROUGH, not config["menu_open"])
            last_insert_state = True
        else:
            last_insert_state = False
            
        # --- ОБРАБОТКА БИНДОВ ---
        if config["binding_mode"]:
            # Ждем нажатия любой клавиши
            key = keyboard.read_key()
            if key and key != "esc":
                if config["binding_mode"] == "LAG":
                    config["lag_bind"] = key.upper()
                config["binding_mode"] = None
                time.sleep(0.3) # Анти-дребезг

        impl.process_inputs()
        imgui.new_frame()

        # --- ОТРИСОВКА CROSSHAIR ---
        if config["crosshair_enabled"]:
            dl = imgui.get_background_draw_list()
            cx, cy = w_screen / 2, h_screen / 2
            col = imgui.get_color_u32_rgba(*config["crosshair_color"])
            s = config["crosshair_size"]
            g = config["crosshair_gap"]
            
            # Крестик
            dl.add_line(cx - s - g, cy, cx - g, cy, col, 2.0)
            dl.add_line(cx + g, cy, cx + s + g, cy, col, 2.0)
            dl.add_line(cx, cy - s - g, cx, cy - g, col, 2.0)
            dl.add_line(cx, cy + g, cx, cy + s + g, col, 2.0)

        # --- ОТРИСОВКА МЕНЮ ---
        if config["menu_open"]:
            menu_w, menu_h = 750, 500
            
            # Центрируем меню
            imgui.set_next_window_size(menu_w, menu_h)
            imgui.set_next_window_position((w_screen - menu_w)/2, (h_screen - menu_h)/2, condition=imgui.FIRST_USE_EVER)
            
            imgui.begin("RakuMenu", flags=imgui.WINDOW_NO_TITLE_BAR | imgui.WINDOW_NO_RESIZE | imgui.WINDOW_NO_SCROLLBAR)
            
            # Делим на две части: Сайдбар и Контент
            render_sidebar()
            render_content()
            
            imgui.end()

        # Рендер
        gl.glClearColor(0, 0, 0, 0)
        gl.glClear(gl.GL_COLOR_BUFFER_BIT)
        imgui.render()
        impl.render(imgui.get_draw_data())
        glfw.swap_buffers(window)
        
    config["running"] = False
    impl.shutdown()
    glfw.terminate()

# Если этот файл запущен напрямую (для тестов), вызываем main
# Но в лоадере он будет вызван через exec() -> main()
if __name__ == "__main__":
    main()
