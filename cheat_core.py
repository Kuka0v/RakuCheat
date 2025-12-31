# cheat_core.py
# FIX 2.1: Исправлены бинды, ПИН-код, черный экран и вкладка Crosshair

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
import pydirectinput
import requests

# ==========================================
# ДАННЫЕ ОТ ЛОАДЕРА
# ==========================================
CTX_USER = globals().get("USER_LOGIN", "DevUser")
CTX_STATUS = globals().get("USER_STATUS", "Admin") 
CTX_DATABASE = globals().get("USER_DATABASE", {})

# Заглушка для тестов (если запускаешь без лоадера)
if not CTX_DATABASE:
    CTX_DATABASE = {
        "macro": {
            "Insta_Bluetooth_Tech": {"name": "Insta Bluetooth Tech", "allow": "Admin, Tester", "pin": "1234"},
            "Insta_Hug_Tech": {"name": "Insta Hug Tech [Beta]", "allow": "Admin, Tester, Free", "pin": "none"}
        },
        "news": [
            {"title": "System Update", "content": "Fixed UI bugs and keybinding issues."}
        ]
    }

# ==========================================
# КОНФИГУРАЦИЯ
# ==========================================
config = {
    "running": True,
    "menu_open": True,
    "active_tab": "Macro",
    "binding_mode": None, # Какую кнопку сейчас биндим
    
    # --- MACRO STATES ---
    "macros": {}, 
    "pin_input": "",
    "pin_target": None,
    "pin_error": False,
    "popup_open_request": False, # Флаг для открытия попапа

    # --- INSTA BLUETOOTH TECH SETTINGS ---
    "bt_rotation": 400.0,
    "bt_long_wait": 1.83,
    "bt_short_wait": 0.40,
    "bt_bind_left": "Q",
    "bt_bind_right": "E",
    
    # Lag Switch
    "lag_enabled": False,     
    "lag_active": False,      
    "lag_bind": "Z", 
    "lag_time": 2.0,
    "lag_start_time": 0.0,
    
    # Visuals
    "crosshair_enabled": False,
    "crosshair_color": [0.0, 1.0, 0.0, 1.0],
    "crosshair_size": 10.0,      
    "crosshair_thickness": 2.0,  
    "crosshair_gap": 0.0,        
    "crosshair_dot": False,      
    "crosshair_t_style": False,  
    
    "skinchanger_enabled": False 
}

# Инициализация состояний макросов
for key in CTX_DATABASE.get("macro", {}):
    config["macros"][key] = {"enabled": False, "unlocked": False, "settings_open": False}

# ==========================================
# ЛОГИКА БИНДОВ (НОВАЯ, НЕ ВИСНЕТ)
# ==========================================
def on_key_event(e):
    # Эта функция вызывается сама при нажатии любой кнопки
    if config["binding_mode"] and e.event_type == 'down':
        if e.name != 'esc':
            print(f"Rebinding {config['binding_mode']} to {e.name}")
            config[config["binding_mode"]] = e.name.upper()
        config["binding_mode"] = None

# Запускаем прослушку клавиатуры в фоне
keyboard.hook(on_key_event)

# ==========================================
# ЛОГИКА МАКРОСОВ
# ==========================================
def perform_bt_sequence(right=True):
    rot = int(config["bt_rotation"])
    long_w = config["bt_long_wait"]
    short_w = config["bt_short_wait"]
    
    pydirectinput.mouseDown(button='right')
    time.sleep(long_w)
    
    pydirectinput.mouseDown(button='left')
    time.sleep(0.05)
    pydirectinput.mouseUp(button='left')
    
    if right:
        pydirectinput.keyDown('a'); pydirectinput.keyDown('w')
    else:
        pydirectinput.keyDown('d'); pydirectinput.keyDown('w')
        
    time.sleep(short_w)
    
    move_val = rot if right else -rot
    pydirectinput.moveRel(move_val, 0, relative=True, _pause=False)
    
    pydirectinput.mouseDown(button='left')
    time.sleep(0.05)
    pydirectinput.mouseUp(button='left')
    
    time.sleep(0.5)
    
    if right:
        pydirectinput.keyUp('a'); pydirectinput.keyUp('w')
    else:
        pydirectinput.keyUp('d'); pydirectinput.keyUp('w')
        
    pydirectinput.mouseUp(button='right')

def logic_thread():
    while config["running"]:
        # Macro Logic
        if config["macros"].get("Insta_Bluetooth_Tech", {}).get("enabled", False):
            if keyboard.is_pressed(config["bt_bind_right"]):
                pydirectinput.moveRel(-int(config["bt_rotation"]), 0, relative=True, _pause=False)
                perform_bt_sequence(right=True)
                time.sleep(0.5)
            elif keyboard.is_pressed(config["bt_bind_left"]):
                pydirectinput.moveRel(int(config["bt_rotation"]), 0, relative=True, _pause=False)
                perform_bt_sequence(right=False)
                time.sleep(0.5)

        # Lag Switch Logic
        if config["lag_enabled"]:
            if keyboard.is_pressed(config["lag_bind"]):
                config["lag_active"] = not config["lag_active"]
                if config["lag_active"]:
                    config["lag_start_time"] = time.time()
                    try: winsound.Beep(1000, 200)
                    except: pass
                else:
                    try: winsound.Beep(600, 200)
                    except: pass
                time.sleep(0.3)
            
            if config["lag_active"]:
                if (time.time() - config["lag_start_time"]) > config["lag_time"]:
                    config["lag_active"] = False
                    try: winsound.Beep(600, 200)
                    except: pass

        time.sleep(0.01)

# ==========================================
# СТИЛИЗАЦИЯ
# ==========================================
def apply_raku_theme():
    style = imgui.get_style()
    colors = style.colors

    style.window_border_size = 0.0
    style.child_border_size = 0.0
    style.window_rounding = 8.0
    style.child_rounding = 6.0
    style.frame_rounding = 4.0
    
    colors[imgui.COLOR_WINDOW_BACKGROUND] = (0, 0, 0, 0)
    colors[imgui.COLOR_BORDER] = (0, 0, 0, 0)
    colors[imgui.COLOR_TEXT] = (0.90, 0.90, 0.90, 1.00)
    colors[imgui.COLOR_BUTTON] = (0.15, 0.15, 0.18, 1.00) # Чуть светлее
    colors[imgui.COLOR_BUTTON_HOVERED] = (0.20, 0.20, 0.24, 1.00)
    colors[imgui.COLOR_BUTTON_ACTIVE] = (0.25, 0.25, 0.30, 1.00)
    colors[imgui.COLOR_HEADER] = (0.20, 0.20, 0.25, 1.00)
    colors[imgui.COLOR_FRAME_BACKGROUND] = (0.10, 0.10, 0.12, 1.00)
    colors[imgui.COLOR_POPUP_BACKGROUND] = (0.08, 0.08, 0.10, 1.00)

# ==========================================
# UI КОМПОНЕНТЫ
# ==========================================
def render_custom_toggle(label, state):
    imgui.push_style_var(imgui.STYLE_FRAME_ROUNDING, 12.0)
    p = imgui.get_cursor_screen_pos()
    draw_list = imgui.get_window_draw_list()
    
    height = 24
    width = 45
    radius = height / 2
    
    if imgui.invisible_button(label, width, height):
        state = not state
        
    col_bg = imgui.get_color_u32_rgba(0.2, 0.2, 0.2, 1.0)
    if state:
        col_bg = imgui.get_color_u32_rgba(0.3, 0.8, 0.3, 1.0)
        
    draw_list.add_rect_filled(p.x, p.y, p.x + width, p.y + height, col_bg, radius)
    circle_x = p.x + radius if not state else p.x + width - radius
    draw_list.add_circle_filled(circle_x, p.y + radius, radius - 2, imgui.get_color_u32_rgba(1, 1, 1, 1))
    
    imgui.same_line()
    imgui.align_text_to_frame_padding()
    imgui.text(label)
    imgui.pop_style_var()
    return state

def render_keybind(label, bind_key_key):
    is_binding = config["binding_mode"] == bind_key_key
    current_key = config[bind_key_key]
    btn_text = "..." if is_binding else f"[{current_key}]"
    
    if imgui.button(f"{btn_text}##{bind_key_key}", 80, 24):
        config["binding_mode"] = bind_key_key
        
    imgui.same_line()
    imgui.text(label)

def render_sidebar_btn(label, tab_name):
    active = config["active_tab"] == tab_name
    if active:
        imgui.push_style_color(imgui.COLOR_BUTTON, 0.18, 0.18, 0.22, 1.0)
        imgui.push_style_color(imgui.COLOR_TEXT, 1.0, 1.0, 1.0, 1.0)
    else:
        imgui.push_style_color(imgui.COLOR_BUTTON, 0,0,0,0)
        imgui.push_style_color(imgui.COLOR_TEXT, 0.6, 0.6, 0.6, 1.0)
        
    if imgui.button(f"  {label}##sidebar", 180, 35):
        config["active_tab"] = tab_name
    imgui.pop_style_color(2)

def render_custom_slider(label, val, v_min, v_max):
    imgui.text(label)
    imgui.same_line(120)
    imgui.push_item_width(200)
    changed, new_val = imgui.slider_float(f"##{label}", val, v_min, v_max)
    imgui.pop_item_width()
    return new_val

# ==========================================
# ОТРИСОВКА МЕНЮ
# ==========================================
def render_menu(w_screen, h_screen):
    menu_w, menu_h = 750, 500
    imgui.set_next_window_size(menu_w, menu_h)
    imgui.set_next_window_position((w_screen - menu_w)/2, (h_screen - menu_h)/2, condition=imgui.FIRST_USE_EVER)
    
    flags = imgui.WINDOW_NO_TITLE_BAR | imgui.WINDOW_NO_RESIZE | imgui.WINDOW_NO_SCROLLBAR
    imgui.begin("Main", True, flags)
    
    # Фон меню
    p_min = imgui.get_window_position()
    p_max = (p_min.x + menu_w, p_min.y + menu_h)
    draw_list = imgui.get_window_draw_list()
    draw_list.add_rect_filled(p_min.x, p_min.y, p_max[0], p_max[1], imgui.get_color_u32_rgba(0.05, 0.05, 0.07, 1.0), 10.0)
    draw_list.add_rect_filled(p_min.x, p_min.y, p_min.x + 200, p_max[1], imgui.get_color_u32_rgba(0.03, 0.03, 0.04, 1.0), 10.0, flags=imgui.DRAW_CORNER_TOP_LEFT | imgui.DRAW_CORNER_BOTTOM_LEFT)
    draw_list.add_line(p_min.x + 200, p_min.y, p_min.x + 200, p_max[1], imgui.get_color_u32_rgba(0.15, 0.15, 0.18, 1.0))
    
    # --- SIDEBAR ---
    imgui.begin_group()
    imgui.dummy(0, 30)
    imgui.indent(10)
    imgui.text_colored("Raku", 1, 1, 1, 1)
    imgui.dummy(0, 30)
    
    imgui.text_colored("Game", 0.3, 0.3, 0.3, 1.0)
    render_sidebar_btn("Macro", "Macro")
    render_sidebar_btn("Lag Switch", "Lag Switch")
    imgui.dummy(0, 10)
    imgui.text_colored("Visuals", 0.3, 0.3, 0.3, 1.0)
    render_sidebar_btn("Crosshair", "Crosshair")
    render_sidebar_btn("Changer", "Changer")
    imgui.dummy(0, 10)
    imgui.text_colored("Other", 0.3, 0.3, 0.3, 1.0)
    render_sidebar_btn("Info / News", "Info")
    
    # Профиль
    y_space = menu_h - imgui.get_cursor_pos_y() - 50
    imgui.dummy(0, y_space)
    imgui.separator()
    imgui.dummy(0, 5)
    imgui.text(f"User: {CTX_USER}")
    status_col = (0, 1, 0, 1) if CTX_STATUS == "Admin" else (0.4, 0.6, 1, 1)
    imgui.text_colored(f"Status: {CTX_STATUS}", *status_col)
    
    imgui.unindent(10)
    imgui.end_group()
    imgui.same_line()
    
    # --- CONTENT ---
    imgui.begin_group()
    imgui.dummy(0, 20)
    imgui.indent(20)
    
    if config["active_tab"] == "Macro":
        imgui.text_colored("Available Macros", 0.8, 0.8, 0.8, 1.0)
        imgui.dummy(0, 10)
        
        for key, data in CTX_DATABASE.get("macro", {}).items():
            name = data.get("name", key)
            allow_list = data.get("allow", "")
            pin = data.get("pin", "none")
            
            # Проверка прав
            is_allowed = any(role.strip() == CTX_STATUS for role in allow_list.split(","))
            
            imgui.push_style_color(imgui.COLOR_CHILD_BACKGROUND, 0.1, 0.1, 0.12, 1.0)
            imgui.begin_child(f"card_{key}", 500, 60, True)
            
            imgui.set_cursor_pos((15, 12))
            imgui.text(name)
            imgui.set_cursor_pos((15, 32))
            
            if is_allowed:
                m_state = config["macros"][key]
                
                # Логика ПИНа
                if pin != "none" and not m_state["unlocked"]:
                    if imgui.button(f"UNLOCK (PIN)##{key}"):
                        config["pin_target"] = key
                        config["popup_open_request"] = True # Просим открыть попап
                else:
                    # Логика Включения
                    imgui.set_cursor_pos_y(15)
                    imgui.dummy(380, 0); imgui.same_line()
                    new_state = render_custom_toggle(f"##tgl_{key}", m_state["enabled"])
                    if new_state != m_state["enabled"]:
                        m_state["enabled"] = new_state
                        
                    # Кнопка настроек
                    if key == "Insta_Bluetooth_Tech":
                        imgui.same_line()
                        if imgui.button("Settings"):
                            m_state["settings_open"] = not m_state["settings_open"]
            else:
                imgui.text_colored("NO ACCESS", 1, 0, 0, 1)

            imgui.end_child()
            imgui.pop_style_color()
            
            # Выпадающее меню настроек
            if key == "Insta_Bluetooth_Tech" and config["macros"][key]["settings_open"]:
                imgui.indent(20)
                imgui.push_style_color(imgui.COLOR_CHILD_BACKGROUND, 0.08, 0.08, 0.09, 1.0)
                imgui.begin_child("settings_bt", 460, 180, True)
                imgui.dummy(0,5)
                imgui.text_colored("Settings: Bluetooth Tech", 0.4, 0.6, 1.0, 1.0)
                imgui.separator()
                imgui.dummy(0,10)
                
                render_keybind("Left Bind (Q)", "bt_bind_left")
                render_keybind("Right Bind (E)", "bt_bind_right")
                imgui.dummy(0,10)
                
                config["bt_rotation"] = render_custom_slider("Rotation", config["bt_rotation"], 100, 1000)
                config["bt_long_wait"] = render_custom_slider("Long Wait", config["bt_long_wait"], 0.1, 5.0)
                config["bt_short_wait"] = render_custom_slider("Short Wait", config["bt_short_wait"], 0.1, 2.0)
                
                imgui.end_child()
