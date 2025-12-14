# cheat_core.py
# Updated Design: Dark/Blue Theme (Raku Style)

import glfw
import OpenGL.GL as gl
import imgui
from imgui.integrations.glfw import GlfwRenderer
import keyboard
import mouse
import time
import ctypes
import threading
import winsound
import math

# ==========================================
# ДАННЫЕ ОТ ЛОАДЕРА
# ==========================================
CTX_USER = globals().get("USER_LOGIN", "DevMode")
CTX_STATUS = globals().get("USER_STATUS", "Admin")
CTX_AVATAR_ID = globals().get("USER_AVATAR_ID", None)

# ==========================================
# КОНФИГУРАЦИЯ
# ==========================================
config = {
    "running": True,
    "menu_open": True,
    "active_tab": "MISC", # По умолчанию как на скрине
    
    # Lag Switch
    "lag_enabled": False,     
    "lag_active": False,      
    "lag_bind": "Q", 
    "lag_time": 2.0,
    "lag_start_time": 0.0,
    
    # Macro (NoRecoil)
    "macro_enabled": False,
    "recoil_y": 5,
    
    # Visuals
    "crosshair_enabled": False,
    "crosshair_color": [0.4, 0.6, 1.0, 1.0], # Blue default
    "crosshair_size": 10.0,      
    "crosshair_thickness": 2.0,  
    "crosshair_gap": 0.0,        
    
    "binding_mode": None 
}

# ==========================================
# ЛОГИКА (В ФОНЕ)
# ==========================================
def background_logic():
    while config["running"]:
        current_time = time.time()
        
        # --- LAG SWITCH ---
        if config["lag_active"]:
            if (current_time - config["lag_start_time"]) > config["lag_time"]:
                config["lag_active"] = False
                try: winsound.Beep(500, 100)
                except: pass
        
        # Обработка бинда Лаг-свитча
        if config["lag_enabled"] and config["lag_bind"] and keyboard.is_pressed(config["lag_bind"]):
            if not config["lag_active"]:
                config["lag_active"] = True
                config["lag_start_time"] = time.time()
                try: winsound.Beep(1000, 100)
                except: pass
            time.sleep(0.2)

        # --- MACRO ---
        if config["macro_enabled"] and mouse.is_pressed(button='left'):
            mouse.move(0, config["recoil_y"], absolute=False, duration=0.01)
            time.sleep(0.01)

        time.sleep(0.005)

# ==========================================
# GUI: СТИЛИ И ЭЛЕМЕНТЫ
# ==========================================
def apply_theme():
    style = imgui.get_style()
    colors = style.colors

    # Размеры и скругления (как на скрине)
    style.window_padding = (0, 0)
    style.window_rounding = 0.0 # Окно без скругления (мы рисуем фон сами)
    style.child_rounding = 6.0
    style.frame_rounding = 4.0
    style.grab_rounding = 4.0
    style.item_spacing = (8, 12)
    
    # ЦВЕТОВАЯ ПАЛИТРА (Dark & Blue)
    c_bg = (0.07, 0.07, 0.09, 1.00)      # Темный фон
    c_sidebar = (0.05, 0.05, 0.07, 1.00) # Сайдбар чуть темнее
    c_accent = (0.40, 0.55, 1.00, 1.00)  # Синий акцент (Blurple)
    c_text = (0.90, 0.90, 0.95, 1.00)
    c_text_dim = (0.50, 0.50, 0.55, 1.00)
    
    colors[imgui.COLOR_WINDOW_BACKGROUND] = (0,0,0,0) # Прозрачный (рисуем сами)
    colors[imgui.COLOR_TEXT] = c_text
    
    # Кнопки (в меню они как текст)
    colors[imgui.COLOR_BUTTON] = (0, 0, 0, 0)
    colors[imgui.COLOR_BUTTON_HOVERED] = (0.1, 0.1, 0.12, 0.5)
    colors[imgui.COLOR_BUTTON_ACTIVE] = (0.1, 0.1, 0.12, 1.0)
    
    # Слайдеры (Стиль "Capsule" как на скрине)
    colors[imgui.COLOR_FRAME_BACKGROUND] = (0.15, 0.15, 0.18, 1.0)
    colors[imgui.COLOR_FRAME_BACKGROUND_HOVERED] = (0.2, 0.2, 0.25, 1.0)
    colors[imgui.COLOR_SLIDER_GRAB] = c_accent
    colors[imgui.COLOR_SLIDER_GRAB_ACTIVE] = (0.5, 0.65, 1.0, 1.0)
    
    # Чекбоксы
    colors[imgui.COLOR_CHECK_MARK] = c_accent

def custom_toggle(label, active):
    # Кастомный чекбокс (если нужно) или стандартный
    clicked, state = imgui.checkbox(label, active)
    return state

def render_sidebar():
    # Фон сайдбара
    draw_list = imgui.get_window_draw_list()
    p = imgui.get_window_position()
    h = imgui.get_window_height()
    w_sidebar = 200
    
    # Рисуем темную колонку слева
    draw_list.add_rect_filled(p.x, p.y, p.x + w_sidebar, p.y + h, imgui.get_color_u32_rgba(0.05, 0.05, 0.07, 1.0), rounding=12.0, flags=imgui.DRAW_CORNER_TOP_LEFT | imgui.DRAW_CORNER_BOTTOM_LEFT)
    
    imgui.begin_child("Sidebar", width=w_sidebar, height=0, border=False)
    imgui.dummy(0, 30)
    
    # LOGO
    imgui.indent(25)
    imgui.set_window_font_scale(1.3)
    imgui.text_colored("RAKU CHEAT", 0.4, 0.55, 1.0, 1.0) # Синий логотип
    imgui.set_window_font_scale(1.0)
    imgui.unindent(25)
    
    imgui.dummy(0, 50)
    
    # MENU ITEMS
    tabs = ["LEGIT", "VISUALS", "MISC"]
    
    for tab in tabs:
        is_active = (config["active_tab"] == tab)
        
        imgui.set_cursor_pos_x(0)
        
        # Если активна вкладка - рисуем полоску слева
        if is_active:
            cur_y = imgui.get_cursor_pos_y()
            dl = imgui.get_window_draw_list()
            wp = imgui.get_window_position()
            # Синяя полоска
            dl.add_rect_filled(wp.x, wp.y + cur_y, wp.x + 3, wp.y + cur_y + 40, imgui.get_color_u32_rgba(0.4, 0.55, 1.0, 1.0))
            
            # Подсветка фона кнопки
            imgui.push_style_color(imgui.COLOR_BUTTON, 0.08, 0.08, 0.1, 1.0)
            imgui.push_style_color(imgui.COLOR_TEXT, 1.0, 1.0, 1.0, 1.0)
        else:
            imgui.push_style_color(imgui.COLOR_BUTTON, 0.0, 0.0, 0.0, 0.0)
            imgui.push_style_color(imgui.COLOR_TEXT, 0.6, 0.6, 0.6, 1.0)
            
        if imgui.button(f"     {tab}", width=200, height=40):
            config["active_tab"] = tab
            
        imgui.pop_style_color(2)
        imgui.dummy(0, 5)

    # USER PROFILE (BOTTOM)
    h_win = imgui.get_window_height()
    imgui.set_cursor_pos_y(h_win - 70)
    imgui.indent(15)
    
    # Рисуем карточку профиля
    dl = imgui.get_window_draw_list()
    cp = imgui.get_cursor_screen_pos()
    
    # Фон карточки
    dl.add_rect_filled(cp.x, cp.y, cp.x + 170, cp.y + 55, imgui.get_color_u32_rgba(0.08, 0.08, 0.1, 1.0), rounding=8.0)
    dl.add_rect(cp.x, cp.y, cp.x + 170, cp.y + 55, imgui.get_color_u32_rgba(0.2, 0.2, 0.25, 1.0), rounding=8.0)
    
    # Аватар
    imgui.set_cursor_pos((25, h_win - 60))
    if CTX_AVATAR_ID:
        imgui.image(CTX_AVATAR_ID, 35, 35, border_color=(0,0,0,0))
    else:
        dl.add_circle_filled(cp.x + 28, cp.y + 27, 18, imgui.get_color_u32_rgba(0.3, 0.3, 0.35, 1.0))
    
    # Текст
    imgui.set_cursor_pos((70, h_win - 62))
    imgui.text(str(CTX_USER))
    
    imgui.set_cursor_pos((70, h_win - 45))
    s_col = (1.0, 1.0, 1.0, 0.7)
    if "Admin" in CTX_STATUS: s_col = (1.0, 0.4, 0.4, 1.0)
    elif "Premium" in CTX_STATUS: s_col = (0.4, 0.6, 1.0, 1.0)
    imgui.text_colored(str(CTX_STATUS), *s_col)
    
    imgui.unindent(15)
    imgui.end_child()

def render_content():
    imgui.same_line()
    imgui.begin_child("Content", width=0, height=0, border=False)
    
    imgui.dummy(0, 40)
    imgui.indent(30)
    
    # Breadcrumbs (Settings > Tab)
    imgui.text_colored(f"Settings > {config['active_tab']}", 0.4, 0.4, 0.45, 1.0)
    imgui.dummy(0, 20)
    
    if config["active_tab"] == "MISC":
        imgui.text("Network Manipulation")
        imgui.separator()
        imgui.dummy(0, 20)
        
        _, config["lag_enabled"] = imgui.checkbox("Enable Lag Switch", config["lag_enabled"])
        
        imgui.dummy(0, 10)
        
        # Биндинг клавиши
        imgui.text("Bind Key:")
        imgui.same_line(150)
        key_lbl = f"[{config['lag_bind']}]" if config['binding_mode'] != 'LAG' else "[ ... ]"
        if imgui.button(key_lbl, width=80):
             config["binding_mode"] = "LAG"
        
        imgui.dummy(0, 10)
        
        # Слайдер как на скрине
        imgui.text("Duration (sec)")
        # Делаем слайдер толстым и красивым
        imgui.push_style_var(imgui.STYLE_FRAME_ROUNDING, 6.0)
        imgui.push_style_var(imgui.STYLE_GRAB_ROUNDING, 6.0)
        imgui.push_style_color(imgui.COLOR_FRAME_BACKGROUND, 0.15, 0.15, 0.20, 1.0)
        
        imgui.push_item_width(300)
        _, config["lag_time"] = imgui.slider_float("##lagtime", config["lag_time"], 0.1, 5.0, format="%.3f")
        imgui.pop_item_width()
        
        imgui.pop_style_color()
        imgui.pop_style_var(2)
        
        # Индикатор активности
        if config["lag_active"]:
            imgui.dummy(0, 20)
            imgui.text_colored("Status:", 0.5, 0.5, 0.5, 1.0)
            imgui.same_line()
            imgui.text_colored("LAG ACTIVE", 1.0, 0.2, 0.2, 1.0)
            
    elif config["active_tab"] == "LEGIT":
        imgui.text("Weapon Settings")
        imgui.separator()
        imgui.dummy(0, 20)
        _, config["macro_enabled"] = imgui.checkbox("Enable NoRecoil", config["macro_enabled"])
        imgui.dummy(0, 10)
        imgui.text("Vertical Force")
        imgui.push_item_width(300)
        _, config["recoil_y"] = imgui.slider_int("##recoil", config["recoil_y"], 0, 20)
        imgui.pop_item_width()
        
    elif config["active_tab"] == "VISUALS":
        imgui.text("Overlay Settings")
        imgui.separator()
        imgui.dummy(0, 20)
        _, config["crosshair_enabled"] = imgui.checkbox("Active Crosshair", config["crosshair_enabled"])
        imgui.dummy(0, 10)
        imgui.text("Size"); imgui.same_line(100); imgui.push_item_width(200); _, config["crosshair_size"] = imgui.slider_float("##s", config["crosshair_size"], 1, 50); imgui.pop_item_width()
        imgui.text("Gap"); imgui.same_line(100); imgui.push_item_width(200); _, config["crosshair_gap"] = imgui.slider_float("##g", config["crosshair_gap"], 0, 20); imgui.pop_item_width()
        
    imgui.end_child()

# ==========================================
# MAIN
# ==========================================
def main():
    if not glfw.init(): return
    
    # Прозрачное окно без рамок
    glfw.window_hint(glfw.FLOATING, True)
    glfw.window_hint(glfw.DECORATED, False)
    glfw.window_hint(glfw.TRANSPARENT_FRAMEBUFFER, True)
    glfw.window_hint(glfw.SAMPLES, 4)
    
    w_scr, h_scr = ctypes.windll.user32.GetSystemMetrics(0), ctypes.windll.user32.GetSystemMetrics(1)
    window = glfw.create_window(w_scr, h_scr, "Raku Overlay", None, None)
    
    glfw.make_context_current(window)
    glfw.swap_interval(1)

    imgui.create_context()
    impl = GlfwRenderer(window)
    apply_theme()
    
    # Запускаем логику в фоне
    threading.Thread(target=background_logic, daemon=True).start()

    menu_w, menu_h = 750, 450
    last_ins = False

    while not glfw.window_should_close(window):
        glfw.poll_events()
        
        # Меню на Insert
        if keyboard.is_pressed('insert'):
            if not last_ins:
                config["menu_open"] = not config["menu_open"]
                glfw.set_window_attrib(window, glfw.MOUSE_PASSTHROUGH, not config["menu_open"])
            last_ins = True
        else: last_ins = False
        
        # Биндинг
        if config["binding_mode"]:
            k = keyboard.read_key()
            if k and k != "esc":
                if config["binding_mode"] == "LAG": config["lag_bind"] = k.upper()
                config["binding_mode"] = None
                time.sleep(0.3)

        impl.process_inputs()
        imgui.new_frame()

        # Crosshair
        if config["crosshair_enabled"]:
            dl = imgui.get_background_draw_list()
            cx, cy = w_scr/2, h_scr/2
            col = imgui.get_color_u32_rgba(*config["crosshair_color"])
            s, g = config["crosshair_size"], config["crosshair_gap"]
            t = config["crosshair_thickness"]
            dl.add_line(cx-s-g, cy, cx-g, cy, col, t)
            dl.add_line(cx+g, cy, cx+s+g, cy, col, t)
            dl.add_line(cx, cy-s-g, cx, cy-g, col, t)
            dl.add_line(cx, cy+g, cx, cy+s+g, col, t)

        # Menu
        if config["menu_open"]:
            imgui.set_next_window_size(menu_w, menu_h)
            imgui.set_next_window_position((w_scr-menu_w)/2, (h_scr-menu_h)/2, condition=imgui.FIRST_USE_EVER)
            
            # Окно без стандартного фона (рисуем свой)
            imgui.begin("RakuMain", flags=imgui.WINDOW_NO_TITLE_BAR | imgui.WINDOW_NO_RESIZE | imgui.WINDOW_NO_SCROLLBAR)
            
            # Custom Background
            p = imgui.get_window_position()
            dl = imgui.get_window_draw_list()
            # Темный фон
            dl.add_rect_filled(p.x, p.y, p.x+menu_w, p.y+menu_h, imgui.get_color_u32_rgba(0.07, 0.07, 0.09, 1.0), rounding=12.0)
            # Тонкая обводка
            dl.add_rect(p.x, p.y, p.x+menu_w, p.y+menu_h, imgui.get_color_u32_rgba(0.2, 0.2, 0.25, 1.0), rounding=12.0)
            
            render_sidebar()
            render_content()
            
            imgui.end()

        gl.glClearColor(0,0,0,0)
        gl.glClear(gl.GL_COLOR_BUFFER_BIT)
        imgui.render()
        impl.render(imgui.get_draw_data())
        glfw.swap_buffers(window)
        
    impl.shutdown()
    glfw.terminate()

if __name__ == "__main__":
    main()
