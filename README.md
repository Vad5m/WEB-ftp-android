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
