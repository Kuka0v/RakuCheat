# cheat_core.py
# Дизайн из test.py + Интеграция данных Лоадера

import glfw
import OpenGL.GL as gl
import imgui
from imgui.integrations.glfw import GlfwRenderer
import keyboard
import time
import ctypes
import sys
import threading
import winsound
import os

# ==========================================
# ДАННЫЕ ОТ ЛОАДЕРА (ИНТЕГРАЦИЯ)
# ==========================================
# Эти переменные прилетают из exe-шника
CTX_USER = globals().get("USER_LOGIN", "DevUser")
CTX_STATUS = globals().get("USER_STATUS", "Free")
CTX_AVATAR_ID = globals().get("USER_AVATAR_ID", None)

# ==========================================
# КОНФИГУРАЦИЯ
# ==========================================
config = {
    "running": True,
    "active_tab": "Lag Switch",
    "menu_open": True,
    
    # Lag Switch
    "lag_enabled": False,     
    "lag_active": False,      
    "lag_bind": "Q", 
    "lag_time": 2.0,
    "lag_start_time": 0.0,
    
    # Macro
    "macro_enabled": False,
    
    # Visuals
    "crosshair_enabled": False,
    "crosshair_color": [0.0, 1.0, 0.0, 1.0],
    "crosshair_size": 10.0,      
    "crosshair_thickness": 2.0,  
    "crosshair_gap": 0.0,        
    "crosshair_dot": False,      
    "crosshair_t_style": False,  
    
    "skinchanger_enabled": False, 
    
    "binding_mode": None 
}

# ==========================================
# ЗАГРУЗКА ШРИФТА
# ==========================================
def load_fonts(io):
    # Пытаемся загрузить Inter или Arial
    font_size = 18.0
    font_config = imgui.core.FontConfig(merge_mode=False)
    
    fonts_to_try = [
        "Inter-Medium.ttf", 
        "Inter-Regular.ttf", 
        "C:\\Windows\\Fonts\\arial.ttf",
        "arial.ttf"
    ]
    
    font_loaded = False
    for font_path in fonts_to_try:
        if os.path.exists(font_path):
            try:
                io.fonts.add_font_from_file_ttf(font_path, font_size, font_config)
                font_loaded = True
                break
            except: pass
    
    if not font_loaded:
        io.fonts.add_font_default()

# ==========================================
# ЛОГИКА
# ==========================================
def lag_logic_thread():
    while config["running"]:
        current_time = time.time()
        if config["lag_active"]:
            if (current_time - config["lag_start_time"]) > config["lag_time"]:
                config["lag_active"] = False
                try: winsound.Beep(600, 200)
                except: pass
        
        if config["lag_enabled"] and keyboard.is_pressed(config["lag_bind"]):
            config["lag_active"] = not config["lag_active"]
            if config["lag_active"]:
                config["lag_start_time"] = time.time()
                try: winsound.Beep(1000, 200)
                except: pass
            else:
                try: winsound.Beep(600, 200)
                except: pass
            time.sleep(0.3)
        time.sleep(0.01)

# ==========================================
# СТИЛИЗАЦИЯ
# ==========================================
def apply_raku_theme():
    style = imgui.get_style()
    colors = style.colors

    style.window_border_size = 0.0
    style.child_border_size = 0.0
    style.popup_border_size = 0.0
    
    style.window_rounding = 12.0
    style.child_rounding = 8.0
    style.frame_rounding = 4.0
    style.grab_rounding = 12.0
    style.popup_rounding = 8.0
    style.scrollbar_size = 0.0
    style.window_padding = (0, 0)
    
    colors[imgui.COLOR_WINDOW_BACKGROUND] = (0, 0, 0, 0) 
    colors[imgui.COLOR_CHILD_BACKGROUND]  = (0.05, 0.05, 0.05, 1.00)
    colors[imgui.COLOR_TEXT]              = (0.90, 0.90, 0.90, 1.00)
    
    colors[imgui.COLOR_BUTTON]            = (0.00, 0.00, 0.00, 0.00)
    colors[imgui.COLOR_BUTTON_HOVERED]    = (0.12, 0.12, 0.14, 1.00) 
    colors[imgui.COLOR_BUTTON_ACTIVE]     = (0.15, 0.15, 0.18, 1.00)
    
    colors[imgui.COLOR_FRAME_BACKGROUND]  = (0.10, 0.10, 0.12, 1.00) 
    colors[imgui.COLOR_FRAME_BACKGROUND_HOVERED] = (0.12, 0.12, 0.14, 1.00)
    colors[imgui.COLOR_FRAME_BACKGROUND_ACTIVE]  = (0.12, 0.12, 0.14, 1.00)
    
    blue_accent = (0.26, 0.40, 0.90, 1.00)
    colors[imgui.COLOR_SLIDER_GRAB]       = blue_accent
    colors[imgui.COLOR_SLIDER_GRAB_ACTIVE]= (0.30, 0.50, 1.00, 1.00)
    colors[imgui.COLOR_CHECK_MARK]        = blue_accent
    colors[imgui.COLOR_HEADER]            = blue_accent
    colors[imgui.COLOR_POPUP_BACKGROUND]  = (0.11, 0.11, 0.13, 1.00)
    colors[imgui.COLOR_BORDER]            = (0, 0, 0, 0)

# ==========================================
# ИКОНКИ
# ==========================================
def draw_icon(draw_list, x, y, icon_type, color):
    c = imgui.get_color_u32_rgba(*color)
    if icon_type == "macro": 
        draw_list.add_line(x+5, y+2, x-2, y+10, c, 2.0)
        draw_list.add_line(x-2, y+10, x+4, y+10, c, 2.0)
        draw_list.add_line(x+4, y+10, x-1, y+18, c, 2.0)
    elif icon_type == "lag":
        draw_list.add_rect(x-4, y, x+6, y+16, c, rounding=4.0, thickness=2.0)
        draw_list.add_line(x-4, y+6, x+6, y+6, c, 2.0)
        draw_list.add_line(x+1, y, x+1, y+6, c, 2.0)
    elif icon_type == "crosshair":
        cx, cy = x+1, y+8
        draw_list.add_circle(cx, cy, 7, c, thickness=2.0)
        draw_list.add_line(cx, cy-9, cx, cy-4, c, 2.0)
        draw_list.add_line(cx, cy+4, cx, cy+9, c, 2.0)
        draw_list.add_line(cx-9, cy, cx-4, cy, c, 2.0)
        draw_list.add_line(cx+4, cy, cx+9, cy, c, 2.0)
    elif icon_type == "skin": 
        draw_list.add_line(x-6, y, x-2, y-4, c, 2.0)
        draw_list.add_line(x+6, y, x+2, y-4, c, 2.0)
        draw_list.add_line(x-2, y-4, x+2, y-4, c, 2.0)
        draw_list.add_rect(x-6, y, x+6, y+14, c, rounding=2.0, thickness=2.0)
    elif icon_type == "info":
        cx, cy = x+1, y+8
        draw_list.add_circle(cx, cy, 8, c, thickness=2.0)
        draw_list.add_line(cx, cy-4, cx, cy-2, c, 2.0)
        draw_list.add_line(cx, cy, cx, cy+4, c, 2.0)

def draw_sidebar_button(icon_type, label, active):
    imgui.push_style_var(imgui.STYLE_BUTTON_TEXT_ALIGN, (0.0, 0.5))
    if active:
        imgui.push_style_color(imgui.COLOR_BUTTON, 0.15, 0.16, 0.18, 1.0)
        text_col = (1.0, 1.0, 1.0, 1.0)
        icon_col = (0.26, 0.40, 0.90, 1.0) 
    else:
        imgui.push_style_color(imgui.COLOR_BUTTON, 0.0, 0.0, 0.0, 0.0)
        text_col = (0.6, 0.6, 0.6, 1.0)
        icon_col = (0.5, 0.5, 0.5, 1.0)

    imgui.push_style_color(imgui.COLOR_TEXT, *text_col)
    clicked = imgui.button(f"       {label}###{label}", width=190, height=40)
    p_min = imgui.get_item_rect_min()
    draw_list = imgui.get_window_draw_list()
    draw_icon(draw_list, p_min.x + 15, p_min.y + 10, icon_type, icon_col)
    
    imgui.pop_style_color(2)
    imgui.pop_style_var()
    return clicked

def render_custom_slider(label, val, v_min, v_max, format_str):
    imgui.text(label)
    imgui.same_line(100)
    imgui.push_item_width(200)
    changed, new_val = imgui.slider_float(f"##{label}", val, v_min, v_max, format="")
    imgui.pop_item_width()
    imgui.same_line()
    imgui.text(format_str % new_val)
    return changed, new_val

def render_keybind(label, bind_key):
    imgui.text(label)
    imgui.same_line(100)
    is_binding = config["binding_mode"] == label
    btn_text = "?" if is_binding else f"[{bind_key}]"
    imgui.push_style_color(imgui.COLOR_BUTTON, 0.08, 0.08, 0.08, 1.0)
    if imgui.button(f"{btn_text}##{label}", width=50, height=20):
        config["binding_mode"] = label
    imgui.pop_style_color()

def draw_circle_image(draw_list, x, y, radius, color):
    draw_list.add_circle_filled(x, y, radius, imgui.get_color_u32_rgba(*color))

# ==========================================
# ОТРИСОВКА МЕНЮ
# ==========================================
def render_sidebar():
    imgui.push_style_color(imgui.COLOR_CHILD_BACKGROUND, 0.05, 0.05, 0.05, 1.0)
    imgui.begin_child("Sidebar", width=220, height=0, border=False)
    draw_list = imgui.get_window_draw_list()
    
    imgui.dummy(0, 30)
    imgui.set_cursor_pos_x(30)
    
    # Заголовок
    imgui.set_window_font_scale(1.5) 
    imgui.text_colored("Raku", 1, 1, 1, 1)
    imgui.set_window_font_scale(1.0)
    
    imgui.dummy(0, 30)
    imgui.indent(15) 
    
    # Вкладки
    imgui.text_colored("Game", 0.3, 0.3, 0.3, 1.0); imgui.dummy(0, 5)
    if draw_sidebar_button("macro", "Macro", config["active_tab"] == "Macro"): config["active_tab"] = "Macro"
    imgui.dummy(0, 2)
    lag_label = "Lag Switch" + (" (ON)" if config["lag_active"] else "")
    if draw_sidebar_button("lag", lag_label, config["active_tab"] == "Lag Switch"): config["active_tab"] = "Lag Switch"

    imgui.dummy(0, 10)
    imgui.text_colored("Visuals", 0.3, 0.3, 0.3, 1.0); imgui.dummy(0, 5)
    if draw_sidebar_button("crosshair", "Crosshair", config["active_tab"] == "Crosshair"): config["active_tab"] = "Crosshair"
    imgui.dummy(0, 2)
    if draw_sidebar_button("skin", "Changer", config["active_tab"] == "Changer"): config["active_tab"] = "Changer"

    imgui.dummy(0, 10)
    imgui.text_colored("Other", 0.3, 0.3, 0.3, 1.0); imgui.dummy(0, 5)
    if draw_sidebar_button("info", "Info", config["active_tab"] == "Info"): config["active_tab"] = "Info"
        
    imgui.unindent(15)
    
    # === ПРОФИЛЬ ПОЛЬЗОВАТЕЛЯ (ИЗ GITHUB) ===
    y_bottom = imgui.get_window_height() - 70
    imgui.set_cursor_pos_y(y_bottom)
    win_pos = imgui.get_window_position()
    cursor_x = win_pos.x + 30
    cursor_y = win_pos.y + y_bottom + 15
    
    # АВАТАРКА
    if CTX_AVATAR_ID:
        # Если есть аватарка от лоадера - рисуем её
        imgui.set_cursor_screen_pos((cursor_x - 18, cursor_y - 18))
        imgui.image(CTX_AVATAR_ID, 36, 36)
    else:
        # Иначе рисуем кружок
        draw_circle_image(draw_list, cursor_x, cursor_y, 18, (0.3, 0.3, 0.35, 1.0))
    
    # НИКНЕЙМ
    imgui.set_cursor_pos((60, y_bottom + 10))
    imgui.text(str(CTX_USER))
    
    # СТАТУС
    imgui.set_cursor_pos((60, y_bottom + 25))
    imgui.text_colored("Status:", 0.5, 0.5, 0.5, 1.0)
    imgui.same_line(0)
    
    # Цвет статуса
    s_col = (0.6, 0.6, 0.6, 1.0)
    if "Admin" in CTX_STATUS: s_col = (1.0, 0.3, 0.3, 1.0)
    elif "Premium" in CTX_STATUS: s_col = (0.4, 0.6, 1.0, 1.0)
    
    imgui.text_colored(str(CTX_STATUS), *s_col)

    imgui.end_child()
    imgui.pop_style_color()

def render_content():
    imgui.same_line()
    imgui.begin_child("Content", width=0, height=0, border=False)
    
    imgui.dummy(0, 50)
    imgui.indent(30)
    
    # Карточка настроек
    imgui.push_style_color(imgui.COLOR_CHILD_BACKGROUND, 0.08, 0.08, 0.10, 1.0)
    imgui.begin_child("SettingsCard", width=380, height=280, border=False)
    
    imgui.dummy(0, 10)
    imgui.indent(15)
    imgui.text_colored(f"Settings {config['active_tab']}", 0.9, 0.9, 0.9, 1.0)
    imgui.dummy(0, 15)
    
    if config["active_tab"] == "Lag Switch":
        _, config["lag_enabled"] = imgui.checkbox("Enable LagSwitch", config["lag_enabled"])
        imgui.dummy(0, 10)
        _, config["lag_time"] = render_custom_slider("Time", config["lag_time"], 1.0, 20.0, "%.0f s")
        imgui.dummy(0, 10)
        render_keybind("Input", config["lag_bind"])
        imgui.dummy(0, 10)
        if config["lag_active"]:
            remaining = max(0, config["lag_time"] - (time.time() - config["lag_start_time"]))
            imgui.text_colored(f"ACTIVE: {remaining:.1f}s", 0.26, 0.40, 0.90, 1.0)
        
    elif config["active_tab"] == "Macro":
        imgui.text("Macro Settings")
        imgui.dummy(0, 10)
        _, config["macro_enabled"] = imgui.checkbox("Enabled", config["macro_enabled"])
        
    elif config["active_tab"] == "Crosshair":
        _, config["crosshair_enabled"] = imgui.checkbox("Enable Crosshair", config["crosshair_enabled"])
        imgui.dummy(0, 10)
        imgui.text("Color"); imgui.same_line(100); _, config["crosshair_color"] = imgui.color_edit4("##color", *config["crosshair_color"], flags=imgui.COLOR_EDIT_NO_INPUTS)
        imgui.dummy(0, 5)
        _, config["crosshair_size"] = render_custom_slider("Size", config["crosshair_size"], 1.0, 50.0, "%.0f px")
        _, config["crosshair_thickness"] = render_custom_slider("Width", config["crosshair_thickness"], 1.0, 10.0, "%.0f px")
        _, config["crosshair_gap"] = render_custom_slider("Gap", config["crosshair_gap"], 0.0, 20.0, "%.0f px")
        imgui.dummy(0, 5)
        _, config["crosshair_dot"] = imgui.checkbox("Dot", config["crosshair_dot"])
        imgui.same_line(150)
        _, config["crosshair_t_style"] = imgui.checkbox("T-Style", config["crosshair_t_style"])

    elif config["active_tab"] == "Changer":
        imgui.text("Skinchanger Settings")
        imgui.dummy(0, 10)
        _, config["skinchanger_enabled"] = imgui.checkbox("Active", config["skinchanger_enabled"])
        imgui.dummy(0, 5)
        imgui.text_colored("Inventory loading...", 0.5, 0.5, 0.5, 1.0)
        
    else:
        imgui.text("Information")
        imgui.dummy(0, 5)
        imgui.text("Status:")
        imgui.same_line()
        imgui.text_colored("Undetected", 0, 1, 0, 1)

    imgui.unindent(15)
    imgui.end_child()
    imgui.pop_style_color()
    imgui.unindent(30)
    imgui.end_child()

def handle_input():
    if config["binding_mode"]:
        e = keyboard.read_event(suppress=True)
        if e.event_type == 'down':
            if e.name != 'esc':
                if config["binding_mode"] == "Input":
                    config["lag_bind"] = e.name.upper()
            config["binding_mode"] = None
            time.sleep(0.2)

def main():
    if not glfw.init(): return
    
    glfw.window_hint(glfw.FLOATING, True)
    glfw.window_hint(glfw.DECORATED, False)
    glfw.window_hint(glfw.TRANSPARENT_FRAMEBUFFER, True)
    glfw.window_hint(glfw.SAMPLES, 4)
    
    user32 = ctypes.windll.user32
    w_screen, h_screen = user32.GetSystemMetrics(0), user32.GetSystemMetrics(1)
    
    window = glfw.create_window(w_screen, h_screen, "Raku Overlay", None, None)
    glfw.make_context_current(window)
    glfw.swap_interval(1)

    imgui.create_context()
    impl = GlfwRenderer(window)
    apply_raku_theme()
    
    io = imgui.get_io()
    io.config_windows_move_from_title_bar_only = False
    load_fonts(io)
    impl.refresh_font_texture()

    threading.Thread(target=lag_logic_thread, daemon=True).start()

    last_ins = False

    while not glfw.window_should_close(window):
        glfw.poll_events()
        handle_input()
        
        if keyboard.is_pressed('insert'):
            if not last_ins:
                config["menu_open"] = not config["menu_open"]
                glfw.set_window_attrib(window, glfw.MOUSE_PASSTHROUGH, not config["menu_open"])
            last_ins = True
        else:
            last_ins = False

        impl.process_inputs()
        imgui.new_frame()
        
        # Crosshair logic
        if config["crosshair_enabled"]:
            dl = imgui.get_background_draw_list()
            cx, cy = w_screen / 2, h_screen / 2
            col = imgui.get_color_u32_rgba(*config["crosshair_color"])
            size = config["crosshair_size"]
            thick = config["crosshair_thickness"]
            gap = config["crosshair_gap"]
            dl.add_line(cx - size - gap, cy, cx - gap, cy, col, thick)
            dl.add_line(cx + gap, cy, cx + size + gap, cy, col, thick)
            dl.add_line(cx, cy + gap, cx, cy + size + gap, col, thick)
            if not config["crosshair_t_style"]:
                dl.add_line(cx, cy - size - gap, cx, cy - gap, col, thick)
            if config["crosshair_dot"]:
                dl.add_rect_filled(cx - thick/2, cy - thick/2, cx + thick/2, cy + thick/2, col)

        if config["menu_open"]:
            menu_w, menu_h = 800, 550
            imgui.set_next_window_size(menu_w, menu_h, condition=imgui.ALWAYS)
            imgui.set_next_window_position((w_screen - menu_w)/2, (h_screen - menu_h)/2, condition=imgui.FIRST_USE_EVER)
            
            flags = imgui.WINDOW_NO_TITLE_BAR | imgui.WINDOW_NO_RESIZE | imgui.WINDOW_NO_SCROLLBAR | imgui.WINDOW_NO_COLLAPSE | imgui.WINDOW_NO_BACKGROUND
            imgui.begin("RakuMenu", True, flags=flags)
            
            p_min = imgui.get_window_position()
            p_max = (p_min.x + menu_w, p_min.y + menu_h)
            
            bg_list = imgui.get_window_draw_list()
            bg_list.add_rect_filled(p_min.x, p_min.y, p_max[0], p_max[1], imgui.get_color_u32_rgba(0.02, 0.02, 0.02, 1.0), rounding=12.0)
            border_col = imgui.get_color_u32_rgba(0.2, 0.2, 0.25, 1.0)
            bg_list.add_rect(p_min.x, p_min.y, p_max[0], p_max[1], border_col, rounding=12.0, thickness=1.0)
            
            render_sidebar()
            render_content()
            imgui.end()

        gl.glClearColor(0, 0, 0, 0)
        gl.glClear(gl.GL_COLOR_BUFFER_BIT)
        imgui.render()
        impl.render(imgui.get_draw_data())
        glfw.swap_buffers(window)

    config["running"] = False
    impl.shutdown()
    glfw.terminate()

# В самом конце файла:
if __name__ == "__main__":
    main()
else:
    # Этот блок сработает при запуске через exec() из лоадера
    # Запускаем в отдельном потоке, чтобы GUI лоадера (если он еще жив) не вис,
    # или просто запускаем main, если лоадер уже скрыт.
    main()
