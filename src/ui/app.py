import dearpygui.dearpygui as dpg
import threading
import time
from src.backend.server_manager import ServerManager
from src.backend.config_manager import ConfigManager
from src.backend.player_manager import PlayerManager
import os

class App:
    def __init__(self):
        self.server_dir = "exampleserver" # Hardcoded for MVP
        
        # Auto-detect jar
        jar_name = "server.jar"
        if os.path.exists(self.server_dir):
            for f in os.listdir(self.server_dir):
                if f.endswith(".jar"):
                    jar_name = f
                    break
        
        self.server_manager = ServerManager(self.server_dir, jar_name=jar_name)
        self.config_manager = ConfigManager(self.server_dir)
        self.player_manager = PlayerManager(self.server_dir)
        
        self.console_log = ""
        self.update_interval = 0.5
        
        dpg.create_context()
        self.setup_font()
        self.setup_ui()
        self.setup_theme()
        
    def setup_font(self):
        # Try to load a system font for a better look
        font_path = "C:/Windows/Fonts/segoeui.ttf"
        if os.path.exists(font_path):
            with dpg.font_registry():
                with dpg.font(font_path, 18) as default_font:
                    dpg.add_font_range_hint(dpg.mvFontRangeHint_Default)
                dpg.bind_font(default_font)

    def setup_theme(self):
        with dpg.theme() as global_theme:
            with dpg.theme_component(dpg.mvAll):
                dpg.add_theme_style(dpg.mvStyleVar_WindowRounding, 10)
                dpg.add_theme_style(dpg.mvStyleVar_FrameRounding, 6)
                dpg.add_theme_style(dpg.mvStyleVar_GrabRounding, 6)
                dpg.add_theme_style(dpg.mvStyleVar_TabRounding, 6)
                dpg.add_theme_style(dpg.mvStyleVar_ChildRounding, 8)
                dpg.add_theme_style(dpg.mvStyleVar_PopupRounding, 8)
                dpg.add_theme_style(dpg.mvStyleVar_ScrollbarRounding, 8)
                
                # Modern Dark Theme Colors (Apple-ish Dark Mode)
                dpg.add_theme_color(dpg.mvThemeCol_WindowBg, (30, 30, 30))
                dpg.add_theme_color(dpg.mvThemeCol_ChildBg, (40, 40, 40))
                dpg.add_theme_color(dpg.mvThemeCol_Border, (60, 60, 60))
                dpg.add_theme_color(dpg.mvThemeCol_Button, (50, 50, 50))
                dpg.add_theme_color(dpg.mvThemeCol_ButtonHovered, (70, 70, 70))
                dpg.add_theme_color(dpg.mvThemeCol_ButtonActive, (90, 90, 90))
                dpg.add_theme_color(dpg.mvThemeCol_TitleBg, (40, 40, 40))
                dpg.add_theme_color(dpg.mvThemeCol_TitleBgActive, (50, 50, 50))
                dpg.add_theme_color(dpg.mvThemeCol_Tab, (40, 40, 40))
                dpg.add_theme_color(dpg.mvThemeCol_TabHovered, (60, 60, 60))
                dpg.add_theme_color(dpg.mvThemeCol_TabActive, (80, 80, 80))
                dpg.add_theme_color(dpg.mvThemeCol_Header, (50, 50, 50))
                dpg.add_theme_color(dpg.mvThemeCol_HeaderHovered, (70, 70, 70))
                dpg.add_theme_color(dpg.mvThemeCol_HeaderActive, (90, 90, 90))
                dpg.add_theme_color(dpg.mvThemeCol_FrameBg, (20, 20, 20))
                dpg.add_theme_color(dpg.mvThemeCol_FrameBgHovered, (40, 40, 40))
                dpg.add_theme_color(dpg.mvThemeCol_FrameBgActive, (60, 60, 60))
                dpg.add_theme_color(dpg.mvThemeCol_Text, (240, 240, 240))
                
        dpg.bind_theme(global_theme)

    def setup_ui(self):
        dpg.create_viewport(title='MCservermanager', width=1000, height=700)
        
        with dpg.window(tag="Primary Window"):
            with dpg.group(horizontal=True):
                # Sidebar
                with dpg.child_window(width=200, tag="Sidebar"):
                    dpg.add_text("MC Server Manager", color=(0, 255, 0))
                    dpg.add_separator()
                    dpg.add_button(label="Dashboard", width=-1, callback=lambda: self.show_tab("Dashboard"))
                    dpg.add_button(label="Console", width=-1, callback=lambda: self.show_tab("Console"))
                    dpg.add_button(label="Properties", width=-1, callback=lambda: self.show_tab("Properties"))
                    dpg.add_button(label="Players", width=-1, callback=lambda: self.show_tab("Players"))
                
                # Main Content Area
                with dpg.child_window(tag="Content", border=False):
                    # Dashboard Tab
                    with dpg.group(tag="Dashboard_Group"):
                        dpg.add_text("Server Status")
                        dpg.add_text("Offline", tag="status_text", color=(255, 0, 0))
                        dpg.add_separator()
                        
                        with dpg.group(horizontal=True):
                            dpg.add_button(label="Start Server", tag="btn_start", callback=self.start_server, width=100, height=50)
                            dpg.add_button(label="Stop Server", tag="btn_stop", callback=self.stop_server, width=100, height=50, show=False)
                            dpg.add_button(label="Kill Server", tag="btn_kill", callback=self.kill_server, width=100, height=50, show=False)
                        
                        dpg.add_spacer(height=20)
                        dpg.add_text("Performance")
                        with dpg.plot(label="CPU Usage", height=200, width=-1):
                            dpg.add_plot_legend()
                            dpg.add_plot_axis(dpg.mvXAxis, label="Time", no_tick_labels=True, tag="cpu_x_axis")
                            with dpg.plot_axis(dpg.mvYAxis, label="%", tag="cpu_y_axis"):
                                dpg.set_axis_limits(dpg.last_item(), 0, 100)
                                dpg.add_line_series([], [], label="CPU", tag="cpu_series")
                                
                        with dpg.plot(label="RAM Usage (MB)", height=200, width=-1):
                            dpg.add_plot_legend()
                            dpg.add_plot_axis(dpg.mvXAxis, label="Time", no_tick_labels=True, tag="ram_x_axis")
                            with dpg.plot_axis(dpg.mvYAxis, label="MB", tag="ram_y_axis"):
                                dpg.add_line_series([], [], label="RAM", tag="ram_series")

                    # Console Tab
                    with dpg.group(tag="Console_Group", show=False):
                        dpg.add_text("Server Console")
                        dpg.add_input_text(multiline=True, readonly=True, tag="console_output", width=-1, height=-50)
                        with dpg.group(horizontal=True):
                            dpg.add_input_text(tag="console_input", width=-100, on_enter=True, callback=self.send_console_command)
                            dpg.add_button(label="Send", width=90, callback=self.send_console_command)

                    # Properties Tab
                    with dpg.group(tag="Properties_Group", show=False):
                        dpg.add_text("Server Properties")
                        dpg.add_button(label="Save Changes", callback=self.save_properties)
                        dpg.add_separator()
                        with dpg.child_window(tag="Properties_List", border=False):
                            pass # Will be populated dynamically

                    # Players Tab
                    with dpg.group(tag="Players_Group", show=False):
                        with dpg.tab_bar():
                            with dpg.tab(label="Whitelist"):
                                dpg.add_input_text(label="Username", tag="whitelist_input")
                                dpg.add_button(label="Add to Whitelist", callback=self.add_whitelist)
                                dpg.add_separator()
                                dpg.add_listbox(tag="whitelist_list", width=-1, num_items=10)
                                dpg.add_button(label="Remove Selected", callback=self.remove_whitelist)
                            
                            with dpg.tab(label="Bans"):
                                dpg.add_input_text(label="Username", tag="ban_input")
                                dpg.add_input_text(label="Reason", tag="ban_reason", default_value="Banned by operator")
                                dpg.add_button(label="Ban Player", callback=self.ban_player)
                                dpg.add_separator()
                                dpg.add_listbox(tag="ban_list", width=-1, num_items=10)
                                dpg.add_button(label="Unban Selected", callback=self.unban_player)

        dpg.setup_dearpygui()
        dpg.show_viewport()
        dpg.set_primary_window("Primary Window", True)

        # Initial Data Load
        self.refresh_properties()
        self.refresh_players()

        # Start update loop
        self.cpu_data_x = []
        self.cpu_data_y = []
        self.ram_data_x = []
        self.ram_data_y = []
        self.tick_count = 0
        
        while dpg.is_dearpygui_running():
            self.update_loop()
            dpg.render_dearpygui_frame()

        dpg.destroy_context()

    def show_tab(self, tab_name):
        dpg.hide_item("Dashboard_Group")
        dpg.hide_item("Console_Group")
        dpg.hide_item("Properties_Group")
        dpg.hide_item("Players_Group")
        
        dpg.show_item(f"{tab_name}_Group")

    def update_loop(self):
        # Update Status
        status = self.server_manager.get_status()
        dpg.set_value("status_text", status)
        if status == "Online":
            dpg.configure_item("status_text", color=(0, 255, 0))
            dpg.hide_item("btn_start")
            dpg.show_item("btn_stop")
            dpg.show_item("btn_kill")
        else:
            dpg.configure_item("status_text", color=(255, 0, 0))
            dpg.show_item("btn_start")
            dpg.hide_item("btn_stop")
            dpg.hide_item("btn_kill")

        # Update Console
        new_lines = self.server_manager.get_console_output()
        if new_lines:
            current_text = dpg.get_value("console_output")
            for line in new_lines:
                current_text += line + "\n"
            # Keep only last 1000 lines to prevent lag
            lines = current_text.split('\n')
            if len(lines) > 1000:
                current_text = '\n'.join(lines[-1000:])
            dpg.set_value("console_output", current_text)
            
            # Auto scroll? DPG doesn't have easy auto-scroll for input_text, 
            # but we can try to set y_scroll if we used a child window.
            # For now, input_text is okay.

        # Update Performance
        if self.tick_count % 10 == 0: # Every ~10 frames
            stats = self.server_manager.get_performance_stats()
            self.cpu_data_y.append(stats['cpu'])
            self.ram_data_y.append(stats['ram'])
            self.cpu_data_x.append(self.tick_count)
            self.ram_data_x.append(self.tick_count)
            
            if len(self.cpu_data_x) > 100:
                self.cpu_data_x.pop(0)
                self.cpu_data_y.pop(0)
                self.ram_data_x.pop(0)
                self.ram_data_y.pop(0)
                
            dpg.set_value("cpu_series", [self.cpu_data_x, self.cpu_data_y])
            dpg.set_value("ram_series", [self.ram_data_x, self.ram_data_y])
            
            # Auto-fit axes
            dpg.fit_axis_data("cpu_x_axis")
            dpg.fit_axis_data("ram_x_axis")
            dpg.fit_axis_data("ram_y_axis")

        self.tick_count += 1

    def start_server(self):
        self.server_manager.start_server()

    def stop_server(self):
        self.server_manager.stop_server()

    def kill_server(self):
        self.server_manager.kill_server()

    def send_console_command(self):
        cmd = dpg.get_value("console_input")
        if cmd:
            self.server_manager.send_command(cmd)
            dpg.set_value("console_input", "")

    def refresh_properties(self):
        dpg.delete_item("Properties_List", children_only=True)
        props = self.config_manager.load_config()
        
        # Sort keys
        sorted_keys = sorted(props.keys())
        
        for key in sorted_keys:
            val = props[key]
            with dpg.group(horizontal=True, parent="Properties_List"):
                dpg.add_text(f"{key}:")
                # Determine type? For now just text input
                if val.lower() in ['true', 'false']:
                    dpg.add_checkbox(default_value=val.lower() == 'true', tag=f"prop_{key}")
                elif val.isdigit():
                    dpg.add_input_int(default_value=int(val), width=200, tag=f"prop_{key}")
                else:
                    dpg.add_input_text(default_value=val, width=200, tag=f"prop_{key}")

    def save_properties(self):
        props = self.config_manager.load_config() # Get current keys
        new_props = {}
        for key in props:
            # Check if tag exists (it should)
            tag = f"prop_{key}"
            if dpg.does_item_exist(tag):
                val = dpg.get_value(tag)
                new_props[key] = str(val).lower() if isinstance(val, bool) else str(val)
        
        self.config_manager.save_config(new_props)
        # Show notification?

    def refresh_players(self):
        # Whitelist
        whitelist = self.player_manager.get_whitelist()
        names = [p['name'] for p in whitelist]
        dpg.configure_item("whitelist_list", items=names)
        
        # Bans
        bans = self.player_manager.get_banned_players()
        ban_names = [f"{p['name']} ({p.get('reason', 'No reason')})" for p in bans]
        dpg.configure_item("ban_list", items=ban_names)

    def add_whitelist(self):
        name = dpg.get_value("whitelist_input")
        if name:
            success, msg = self.player_manager.add_to_whitelist(name)
            if success:
                dpg.set_value("whitelist_input", "")
                self.refresh_players()
            else:
                print(msg) # TODO: Show in UI

    def remove_whitelist(self):
        selected = dpg.get_value("whitelist_list")
        if selected:
            success, msg = self.player_manager.remove_from_whitelist(selected)
            if success:
                self.refresh_players()

    def ban_player(self):
        name = dpg.get_value("ban_input")
        reason = dpg.get_value("ban_reason")
        if name:
            success, msg = self.player_manager.ban_player(name, reason)
            if success:
                dpg.set_value("ban_input", "")
                self.refresh_players()

    def unban_player(self):
        selected = dpg.get_value("ban_list")
        if selected:
            # Extract name from "Name (Reason)"
            name = selected.split(' (')[0]
            success, msg = self.player_manager.unban_player(name)
            if success:
                self.refresh_players()

if __name__ == "__main__":
    app = App()
