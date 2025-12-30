import subprocess
import threading
import queue
import psutil
import os
import time

class ServerManager:
    def __init__(self, server_dir, jar_name="server.jar", java_path="java"):
        self.server_dir = server_dir
        self.jar_name = jar_name
        self.java_path = java_path
        self.process = None
        self.output_queue = queue.Queue()
        self.is_running = False
        self.stop_event = threading.Event()
        self.monitor_thread = None

    def start_server(self):
        if self.is_running:
            return False

        jar_path = os.path.join(self.server_dir, self.jar_name)
        if not os.path.exists(jar_path):
            self.output_queue.put(f"Error: {self.jar_name} not found in {self.server_dir}")
            return False

        try:
            # Start the process
            self.process = subprocess.Popen(
                [self.java_path, "-Xmx1024M", "-Xms1024M", "-jar", self.jar_name, "nogui"],
                cwd=self.server_dir,
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1,
                creationflags=subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0
            )
            self.is_running = True
            self.stop_event.clear()
            
            # Start monitoring thread
            self.monitor_thread = threading.Thread(target=self._monitor_output, daemon=True)
            self.monitor_thread.start()
            return True
        except Exception as e:
            self.output_queue.put(f"Failed to start server: {str(e)}")
            return False

    def _monitor_output(self):
        while not self.stop_event.is_set() and self.process and self.process.poll() is None:
            line = self.process.stdout.readline()
            if line:
                self.output_queue.put(line.strip())
        
        if self.process and self.process.poll() is not None:
            self.is_running = False
            self.output_queue.put("Server stopped.")

    def stop_server(self):
        if self.is_running and self.process:
            self.send_command("stop")
            # Wait a bit for graceful shutdown
            time.sleep(5)
            if self.process.poll() is None:
                self.kill_server()
            self.is_running = False

    def kill_server(self):
        if self.process:
            try:
                parent = psutil.Process(self.process.pid)
                for child in parent.children(recursive=True):
                    child.kill()
                parent.kill()
            except psutil.NoSuchProcess:
                pass
            self.is_running = False
            self.output_queue.put("Server killed.")

    def send_command(self, command):
        if self.is_running and self.process:
            try:
                self.process.stdin.write(command + "\n")
                self.process.stdin.flush()
            except Exception as e:
                self.output_queue.put(f"Error sending command: {str(e)}")

    def get_console_output(self):
        lines = []
        while not self.output_queue.empty():
            lines.append(self.output_queue.get())
        return lines

    def get_status(self):
        if self.is_running:
            return "Online"
        return "Offline"

    def get_performance_stats(self):
        if not self.is_running or not self.process:
            return {"cpu": 0, "ram": 0}
        
        try:
            proc = psutil.Process(self.process.pid)
            with proc.oneshot():
                cpu_percent = proc.cpu_percent(interval=None)
                memory_info = proc.memory_info()
                ram_mb = memory_info.rss / 1024 / 1024
            return {"cpu": cpu_percent, "ram": ram_mb}
        except psutil.NoSuchProcess:
            return {"cpu": 0, "ram": 0}
