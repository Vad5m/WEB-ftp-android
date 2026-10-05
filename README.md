# WEB-ftp-android

# WebFTP

A simple web-based file manager for Android (and beyond), built with Python + Kivy + Flask. It runs an HTTP server directly on the device, letting you browse and manage files from any browser on the same network.

## Features

- 📂 Browse the filesystem through a browser
- ⬆️ Upload files (including **drag & drop**)
- 🗑️ Delete files and empty folders
- 🖼️ Image previews and file-type icons
- 🌐 Bilingual UI (EN / RU)
- 📱 Requests `MANAGE_EXTERNAL_STORAGE` permission on Android 11+
- 🧭 Breadcrumb navigation
- 🐞 Built-in error viewer right in the web UI

## How It Works

On launch, the app starts a Flask server on `0.0.0.0:42005` in a background thread and displays the local IP. Open that address in a browser on any device on the same network to get access to the device's files.

Default filesystem root:
- **Windows** → `C:\`
- **Android** → `/storage/emulated/0`
- **Other** → `/`

## Installation & Build

### Requirements
- Python 3.10+
- Kivy
- Flask
- Buildozer (for APK builds)

### Run on desktop

```bash
pip install kivy flask
python main.py
```

### Build Android APK

```bash
docker run --interactive --tty --rm \
                                         --volume "$HOME/.buildozer":/home/user/.buildozer \
                                         --volume "$PWD":/home/user/hostcwd \
                                         kivy/buildozer android debug
```

The resulting APK will be in the `bin/` folder.

## Project Structure

```
.
├── main.py            # entry point: Kivy UI + Flask server
├── buildozer.spec     # Android build config
├── media/             # UI icons (folder.png, file.png, ...)
├── data/              # presplash.png, icon.png
└── app.log            # app log (created at runtime)
```

<pre>
                              _______
                    _.----'`.____.'`-,_
               _.-'/  ,---.    ,---.   `,_
            .-' `-'  :    /    \_   \   \ `._
        _.-'\    ___  `--'  __   `--' __ `---`,
     _.'    /  ,'   `-.    /  `.    ,'  `.   _ `.
   .' `__,-'  (        )  |    |   (     /  (  \ `.
  /      ___   `-.___,'    `--'     `---'    `-'  (\
 /`   ,-'    \     ____,---.    ,-----.    ,-.     `:
:  |  \      /   ,'         )  (       \  ,   \   __ \
|_,    `----'    `._______.'    `._    /  \   / ,'  \ :
|  __,.-----._______.__________ ___`--'    `-'  \___, |
l-'___.---''_ ,|\_'.     _     /  ,'-.__________.____.J
 \'      ,-' / \_ \ \   (_)   |  /  /  _,7 !  .  .__  /
  `-.__,___|,__,'| | |  ___   | /  |  / /.  `._` ___.'
           |   | | |/ ,' | `.  \\  ___ | `"-----'
      `    | ` \_` / /.-.|.-.\  ||'_ _`\
         `[_]  |_| ||: _ v _ :| |||_|_| \
      `        |_| /|'._)!(_.'| |||_|_| |        -%
          `    !_|/ |   o|o   | |||_|_| \    %-
              /""/ /|    |    |  / '"""  \
             /  | / | `` | `` | /  /  \  ||    0
    0  __.-,' /'| \ \.___!___ /    ' \ \  \-._`|/
   \|-' ` [__0_.-._/-_-_-_-_-[____.0'-.-_-'`    '-.
  (   ``  `.\|/ `` _-_-_-_-  `  ``\|/,    ``` `` __)
   `"'mozz________ -_-_____``__________ ``__.--''
                  ""''     "'          ""'
-----------------------------------------------------

</pre>









```markdown
# WEB-ftp-android

<img width="1920" height="1080" alt="screenshot 1" src="https://github.com/user-attachments/assets/9c9ff972-2588-4b34-964d-bd5773ca050d" />
<img width="1920" height="1080" alt="screenshot 2" src="https://github.com/user-attachments/assets/bf6f810b-6b03-478b-9810-3e3e6b8edfc7" />

# WebFTP

A simple web-based file manager for Android (and beyond), built with Python + Kivy + Flask. It runs an HTTP server directly on the device, letting you browse and manage files from any browser on the same network.

## ✨ Features

- 📂 **Browse the filesystem** — navigate folders through a browser
- ⬆️ **Upload files** — including **drag & drop** support
- 🗑️ **Delete** — remove files and empty folders
- 🖼️ **Image previews** — thumbnails and file-type icons
- 🌐 **Bilingual UI** — English / Russian
- 📱 **Android 11+ support** — requests `MANAGE_EXTERNAL_STORAGE`
- 🧭 **Breadcrumb navigation** — quick jump through the tree
- 🐞 **Built-in error viewer** — see app errors right in the web UI

## 📋 Requirements

- **Python 3.10+**
- **Kivy** (UI)
- **Flask** (web framework)
- **Buildozer** (for APK builds)
- **Web browser** (Firefox, Chrome, Yandex...)

## 🚀 Installation

### 1. Clone the repository
```bash
git clone https://github.com/Vad5m/WEB-ftp-android.git
cd WEB-ftp-android
```

### 2. Install dependencies
```bash
pip install kivy flask
```

### 3. Create required directories
```bash
mkdir -p media data
```

## 🎮 Usage

### Quick Start (desktop)
```bash
python3 main.py
```

On launch, the app starts a Flask server on `0.0.0.0:42005` in a background thread and shows the local IP. Open that address in a browser on any device on the same network.

### Default filesystem root

| Platform | Root path |
|----------|-----------|
| **Windows** | `C:\` |
| **Android** | `/storage/emulated/0` |
| **Other** | `/` |

### Access the file manager
```
http://<your-local-ip>:42005/
```

## 📦 Build Android APK

```bash
docker run --interactive --tty --rm \
  --volume "$HOME/.buildozer":/home/user/.buildozer \
  --volume "$PWD":/home/user/hostcwd \
  kivy/buildozer android debug
```

The resulting APK will be in the `bin/` folder.

## 🗂️ Project Structure

```
WEB-ftp-android/
├── main.py            # entry point: Kivy UI + Flask server
├── buildozer.spec     # Android build config
├── media/             # UI icons (folder.png, file.png, ...)
├── data/              # presplash.png, icon.png
└── app.log            # app log (created at runtime)
```

## 🔐 Permissions (Android)

Already declared in `buildozer.spec`:

```
INTERNET, ACCESS_NETWORK_STATE, ACCESS_WIFI_STATE, CHANGE_WIFI_STATE,
CHANGE_NETWORK_STATE, WRITE_EXTERNAL_STORAGE, READ_EXTERNAL_STORAGE,
MANAGE_EXTERNAL_STORAGE, FOREGROUND_SERVICE, WAKE_LOCK, POST_NOTIFICATIONS
```

On Android 11+, the app will request **All files access** on startup — without it, access to `/storage/emulated/0` will be restricted.

## ⚠️ Security

The server has **no authentication** and exposes full file access. Use it only on a trusted local network. Do not expose port `42005` to the internet.

## 📄 License

MIT — do whatever you want, no warranty.

<pre>
                              _______
                    _.----'`.____.'`-,_
               _.-'/  ,---.    ,---.   `,_
            .-' `-'  :    /    \_   \   \ `._
        _.-'\    ___  `--'  __   `--' __ `---`,
     _.'    /  ,'   `-.    /  `.    ,'  `.   _ `.
   .' `__,-'  (        )  |    |   (     /  (  \ `.
  /      ___   `-.___,'    `--'     `---'    `-'  (\
 /`   ,-'    \     ____,---.    ,-----.    ,-.     `:
:  |  \      /   ,'         )  (       \  ,   \   __ \
|_,    `----'    `._______.'    `._    /  \   / ,'  \ :
|  __,.-----._______.__________ ___`--'    `-'  \___, |
l-'___.---''_ ,|\_'.     _     /  ,'-.__________.____.J
 \'      ,-' / \_ \ \   (_)   |  /  /  _,7 !  .  .__  /
  `-.__,___|,__,'| | |  ___   | /  |  / /.  `._` ___.'
           |   | | |/ ,' | `.  \\  ___ | `"-----'
      `    | ` \_` / /.-.|.-.\  ||'_ _`\
         `[_]  |_| ||: _ v _ :| |||_|_| \
      `        |_| /|'._)!(_.'| |||_|_| |        -%
          `    !_|/ |   o|o   | |||_|_| \    %-
              /""/ /|    |    |  / '"""  \
             /  | / | `` | `` | /  /  \  ||    0
    0  __.-,' /'| \ \.___!___ /    ' \ \  \-._`|/
   \|-' ` [__0_.-._/-_-_-_-_-[____.0'-.-_-'`    '-.
  (   ``  `.\|/ `` _-_-_-_-  `  ``\|/,    ``` `` __)
   `"'mozz________ -_-_____``__________ ``__.--''
                  ""''     "'          ""'
-----------------------------------------------------
</pre>
```

---

