# 🎮 MCservermanager

> **A modern, GUI-first Minecraft server management application.**  
> *Stop wrestling with config files and terminals. Manage your server with style.*

![License](https://img.shields.io/badge/license-MIT-blue.svg)
![Python](https://img.shields.io/badge/python-3.8%2B-blue)
![Platform](https://img.shields.io/badge/platform-Windows%20%7C%20macOS%20%7C%20Linux-lightgrey)

---

## ✨ Features

- **🖥️ Dashboard**: Start/Stop/Kill server, view status, and monitor real-time CPU/RAM usage.
- **📜 Console**: View server logs and send commands directly from the app.
- **⚙️ Properties Editor**: Edit `server.properties` with a clean, validated GUI.
- **👥 Player Management**: Manage Whitelist and Bans easily (resolves UUIDs via Mojang API).
- **🎨 Modern UI**: Dark mode, rounded corners, and a clean aesthetic powered by Dear PyGui.

---

## 🚀 Getting Started

### Prerequisites

1.  **Python 3.8+** installed.
2.  **Java** installed and added to your system PATH (required for running Minecraft servers).

### Installation

1.  Clone the repository:
    ```bash
    git clone https://github.com/yourusername/MCservermanager.git
    cd MCservermanager
    ```

2.  Install dependencies:
    ```bash
    pip install -r requirements.txt
    ```

3.  **Prepare your server**:
    -   Place your server files (including the `.jar` file) in the `exampleserver/` directory.
    -   *Note: The app automatically detects the first `.jar` file it finds.*

### Running the App

```bash
python main.py
```

---

## 🛠️ Usage Guide

### Dashboard
The command center for your server.
- **Start**: Launches the server process.
- **Stop**: Sends a graceful `stop` command.
- **Kill**: Forcefully terminates the process (use as a last resort).
- **Graphs**: Monitor performance to ensure smooth gameplay.

### Properties
Forget editing text files.
- Toggle settings like `online-mode`, `pvp`, and `flight`.
- Adjust `max-players`, `view-distance`, and more.
- **Save Changes** writes directly to `server.properties`.

### Players
Manage your community.
- **Whitelist**: Add usernames (auto-fetches UUIDs).
- **Bans**: Ban troublemakers with a reason.

---

## 🤝 Contributing

Contributions are welcome! Feel free to open issues or submit pull requests.

1.  Fork the Project
2.  Create your Feature Branch (`git checkout -b feature/AmazingFeature`)
3.  Commit your Changes (`git commit -m 'Add some AmazingFeature'`)
4.  Push to the Branch (`git push origin feature/AmazingFeature`)
5.  Open a Pull Request

---

## 📄 License

Distributed under the MIT License. See `LICENSE` for more information.

---

*Built with ❤️ using [Dear PyGui](https://github.com/hoffstadt/DearPyGui).*
