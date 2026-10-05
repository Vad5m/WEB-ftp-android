import os
import sys
import socket
import threading
import traceback
import time
from pathlib import Path

from kivy.app import App
from kivy.clock import Clock
from kivy.uix.label import Label
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.scrollview import ScrollView
from kivy.utils import platform

from flask import (
    Flask, request, redirect, url_for, send_file, send_from_directory,
    render_template_string, abort, jsonify, make_response
)

HTTP_PORT = 42005

if sys.platform == "win32":
    ROOT = "C:\\"
elif os.path.exists("/storage/emulated/0"):
    ROOT = "/storage/emulated/0"
else:
    ROOT = "/"

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MEDIA_DIR = os.path.join(BASE_DIR, "media")

SERVER_READY = False
ERRORS = []
ERROR_LOCK = threading.Lock()

LOG_FILE = os.path.join(BASE_DIR, "app.log")


def log(msg):
    try:
        with open(LOG_FILE, "a", encoding="utf-8") as f:
            f.write(str(msg) + "\n")
    except Exception:
        pass
    try:
        print(msg, file=sys.stderr)
    except Exception:
        pass


def log_error(msg):
    with ERROR_LOCK:
        ERRORS.append(msg)
        if len(ERRORS) > 50:
            ERRORS.pop(0)
    log(f"[ERROR] {msg}")


def get_errors():
    with ERROR_LOCK:
        return list(ERRORS)


def get_local_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
    except Exception:
        ip = "127.0.0.1"
    finally:
        s.close()
    return ip


sys.excepthook = lambda t, v, tb: log(
    "".join(traceback.format_exception(t, v, tb)))

try:
    threading.excepthook = lambda a: log(
        "".join(traceback.format_exception(a.exc_type, a.exc_value,
                                            a.exc_traceback)))
except Exception:
    pass


def request_android_permissions():
    if not os.path.exists("/system/build.prop"):
        return
    try:
        from jnius import autoclass

        Build = autoclass("android.os.Build$VERSION")
        if Build.SDK_INT >= 30:
            Environment = autoclass("android.os.Environment")
            if not Environment.isExternalStorageManager():
                PythonActivity = autoclass("org.kivy.android.PythonActivity")
                Settings = autoclass("android.provider.Settings")
                Intent = autoclass("android.content.Intent")
                Uri = autoclass("android.net.Uri")
                activity = PythonActivity.mActivity
                intent = Intent(Settings.ACTION_MANAGE_APP_ALL_FILES_ACCESS_PERMISSION)
                intent.setData(Uri.parse("package:" + activity.getPackageName()))
                activity.startActivity(intent)
                log("[PERM] Запрошен All files access")
            else:
                log("[PERM] All files access уже выдан")
    except Exception as e:
        log(f"[PERM] skip: {e}")


I18N = {
    "en": {
        "root": "Root",
        "up": "Up",
        "upload": "Upload",
        "choose": "Choose files",
        "no_files": "No files selected",
        "empty": "Empty",
        "errors": "Errors",
        "clear": "Clear",
        "delete_confirm": "Delete?",
        "size": "Size",
        "back": "Back to files",
        "error": "Error",
        "lang_switch": "RU",
        "yes": "Yes",
        "no": "No",
    },
    "ru": {
        "root": "Корень",
        "up": "Вверх",
        "upload": "Загрузить",
        "choose": "Выбрать файлы",
        "no_files": "Файлы не выбраны",
        "empty": "Пусто",
        "errors": "Ошибки",
        "clear": "Очистить",
        "delete_confirm": "Удалить?",
        "size": "Размер",
        "back": "Вернуться к файлам",
        "error": "Ошибка",
        "lang_switch": "EN",
        "yes": "Да",
        "no": "Нет",
    },
}


def get_lang():
    lang = request.cookies.get("lang")
    if lang in I18N:
        return lang
    lang = request.args.get("lang")
    if lang in I18N:
        return lang
    return "en"


app = Flask(__name__)

PAGE = """<!doctype html><html><head><meta charset=utf-8>
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Files: {{ path }}</title>
<link rel="icon" href="/media/folder.png">
<style>
*{box-sizing:border-box}
body{font-family:system-ui,sans-serif;background:#111;color:#eee;
     margin:0;padding:24px;min-height:100vh}
a{color:#4af;text-decoration:none}
a:hover{text-decoration:underline}
.topbar{display:flex;justify-content:space-between;align-items:center;
        margin-bottom:16px;gap:10px;flex-wrap:wrap}
.lang-btn{background:#1c1c1c;border:1px solid #333;color:#eee;
          padding:6px 14px;border-radius:8px;font-size:13px;
          cursor:pointer;font-weight:600;display:inline-flex;
          align-items:center;gap:6px}
.lang-btn:hover{background:#2a2a2a}
.lang-btn img{width:16px;height:16px;display:block}
.crumbs{display:flex;flex-wrap:wrap;align-items:center;gap:4px;
        margin-bottom:16px;font-size:14px}
.crumbs a{padding:4px 6px;border-radius:6px;display:inline-flex;
          align-items:center;gap:5px}
.crumbs a:hover{background:#222;text-decoration:none}
.crumbs .sep{color:#555}
.crumbs img{width:14px;height:14px}
.toolbar{display:flex;gap:10px;align-items:center;flex-wrap:wrap;
         margin-bottom:20px}
.up{background:#1c1c1c;padding:8px 14px;border-radius:8px;display:inline-flex;
    align-items:center;gap:6px;color:#eee;font-size:14px}
.up:hover{background:#2a2a2a;text-decoration:none}
.up img{width:16px;height:16px}
.grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(130px,1fr));
      gap:14px;max-width:1100px}
.item{position:relative;display:flex;flex-direction:column;align-items:center;
      padding:14px 8px;border-radius:10px;background:#181818;
      border:1px solid #222;transition:.15s;overflow:hidden}
.item:hover{background:#222;border-color:#333;transform:translateY(-2px)}
.item .icon-wrap{width:64px;height:64px;display:flex;align-items:center;
                 justify-content:center;margin-bottom:8px;border-radius:12px;
                 background:linear-gradient(135deg,#3a2a10,#5a3a15);
                 box-shadow:0 2px 8px rgba(0,0,0,.4)}
.item .icon-wrap.thumb{background:#0d0d0d;overflow:hidden;padding:0}
.item .icon{width:52px;height:52px;object-fit:contain;
            filter:drop-shadow(0 2px 4px rgba(0,0,0,.5))}
.item .icon-wrap.thumb .icon.preview{width:100%;height:100%;
                                     object-fit:cover;border-radius:12px;
                                     filter:none}
.item .name{font-size:13px;text-align:center;color:#eee;word-break:break-word;
            overflow:hidden;display:-webkit-box;-webkit-line-clamp:2;
            -webkit-box-orient:vertical;max-width:100%}
.item .size{font-size:11px;color:#777;margin-top:4px;
            font-variant-numeric:tabular-nums}
.item a.cover{position:absolute;inset:0;z-index:1}
.item .del{position:absolute;top:6px;right:6px;z-index:2;
           background:#2a1212;color:#e77;border-radius:6px;
           padding:3px 7px;font-size:12px;opacity:0;transition:.15s;
           display:inline-flex;align-items:center;gap:4px;cursor:pointer}
.item .del img{width:12px;height:12px}
.item:hover .del{opacity:1}
.item .del:hover{background:#4a1515;color:#fff;text-decoration:none}
form.up{margin:0;display:flex;gap:10px;align-items:center;
        padding:8px 12px;background:#1c1c1c;border-radius:8px}
input[type=file]{color:#eee;font-size:13px;max-width:230px}
button{background:#4af;border:0;color:#000;padding:7px 14px;
       border-radius:6px;cursor:pointer;font-weight:600;font-size:13px;
       display:inline-flex;align-items:center;gap:6px}
button:hover{background:#69f}
button img{width:14px;height:14px}
.empty{color:#666;font-style:italic;padding:40px 0;text-align:center}
.errors{background:#2a1010;border:1px solid #5a1a1a;border-radius:8px;
        padding:14px 18px;margin-bottom:20px;color:#fbb;font-size:13px}
.errors h3{margin:0 0 8px 0;color:#f77;font-size:14px;
           display:flex;align-items:center;gap:8px}
.errors h3 img{width:16px;height:16px}
.errors pre{margin:4px 0;white-space:pre-wrap;word-break:break-word;
            font-family:monospace;font-size:12px;color:#faa}
.errors .clear{float:right;background:#4a1515;color:#fbb;border:0;
               padding:3px 10px;border-radius:5px;cursor:pointer;font-size:12px}
.errors .clear:hover{background:#5a1a1a}
.dropzone{position:fixed;inset:0;background:rgba(0,0,0,.75);
          display:none;align-items:center;justify-content:center;
          z-index:1000;pointer-events:none}
.dropzone.active{display:flex}
.dropzone .inner{border:3px dashed #fa0;border-radius:20px;
                 padding:60px 80px;color:#fa0;font-size:24px;
                 font-weight:700;text-align:center;background:rgba(30,20,5,.9)}
.overlay{position:fixed;inset:0;background:rgba(0,0,0,.8);
         display:none;align-items:center;justify-content:center;
         z-index:2000;flex-direction:column;gap:20px}
.overlay.active{display:flex}
.spinner{width:64px;height:64px;border:6px solid #333;
         border-top-color:#fa0;border-radius:50%;
         animation:spin 1s linear infinite}
@keyframes spin{to{transform:rotate(360deg)}}
.overlay .text{color:#fa0;font-size:18px;font-weight:600}
.modal{position:fixed;inset:0;background:rgba(0,0,0,.8);
       display:none;align-items:center;justify-content:center;z-index:3000}
.modal.active{display:flex}
.modal .box{background:#1c1c1c;border:1px solid #333;border-radius:14px;
            padding:28px 32px;max-width:360px;width:90%;text-align:center}
.modal .box p{font-size:16px;margin:0 0 20px 0;color:#eee}
.modal .box .name{color:#fa0;font-weight:700;word-break:break-all}
.modal .box .btns{display:flex;gap:12px;justify-content:center}
.modal .box button{padding:10px 24px;font-size:14px;border-radius:8px}
.modal .box .yes{background:#c33;color:#fff}
.modal .box .yes:hover{background:#e44}
.modal .box .no{background:#333;color:#eee}
.modal .box .no:hover{background:#444}
</style></head><body>

<div class="topbar">
  <div></div>
  <a class="lang-btn" href="?lang={{ other_lang }}">
    <img src="/media/lang.png" onerror="this.style.display='none'">
    {{ t.lang_switch }}
  </a>
</div>

{% if errors %}
<div class="errors">
  <a class="clear" href="{{ url_for('clear_err') }}">{{ t.clear }}</a>
  <h3>
    <img src="/media/error.png" onerror="this.style.display='none'">
    {{ t.errors }} ({{ errors|length }})
  </h3>
  {% for e in errors %}<pre>{{ e }}</pre>{% endfor %}
</div>
{% endif %}

<div class="crumbs">
  <a href="/">
    <img src="/media/home.png" onerror="this.style.display='none'">
    {{ t.root }}
  </a>
  {% for c in crumbs %}
    <span class="sep">›</span>
    <a href="/browse/{{ c.rel }}">
      <img src="/media/folder.png" onerror="this.style.display='none'">
      {{ c.name }}
    </a>
  {% endfor %}
</div>

<div class="toolbar">
  {% if path and path != "/" %}
    <a class="up" href="/browse/{{ parent }}">
      <img src="/media/up.png" onerror="this.style.display='none'">
      {{ t.up }}
    </a>
  {% else %}
    <a class="up" href="/">
      <img src="/media/up.png" onerror="this.style.display='none'">
      {{ t.up }}
    </a>
  {% endif %}
  <form class="up" method="post" action="{{ url_for('upload', path=path) }}"
        enctype="multipart/form-data" id="uploadForm">
    <input type="file" name="file" multiple required id="fileInput">
    <button type="submit">
      <img src="/media/upload.png" onerror="this.style.display='none'">
      {{ t.upload }}
    </button>
  </form>
</div>

{% if entries %}
<div class="grid">
  {% for e in entries %}
  <div class="item">
    <a class="cover" href="{{ e.url }}"></a>
    <div class="icon-wrap{% if e.is_img %} thumb{% endif %}">
      {% if e.is_img %}
        <img class="icon preview" src="{{ e.url }}" alt=""
             loading="lazy"
             onerror="this.parentNode.classList.remove('thumb');this.parentNode.innerHTML='<img class=\'icon\' src=\'/media/{{ e.icon }}\'>'">
      {% else %}
        <img class="icon" src="/media/{{ e.icon }}" alt=""
             onerror="this.replaceWith(document.createTextNode('{{ e.fallback }}'))">
      {% endif %}
    </div>
    <div class="name" title="{{ e.name }}">{{ e.name }}</div>
    {% if e.size %}<div class="size">{{ e.size }}</div>{% endif %}
    <a class="del" data-url="{{ e.delete_url }}" data-name="{{ e.name }}">
      <img src="/media/trash.png" onerror="this.style.display='none'">
      X
    </a>
  </div>
  {% endfor %}
</div>
{% else %}
<div class="empty">{{ t.empty }}</div>
{% endif %}

<div class="dropzone" id="dropzone">
  <div class="inner">{{ t.upload }}</div>
</div>

<div class="overlay" id="overlay">
  <div class="spinner"></div>
  <div class="text" id="overlayText">{{ t.upload }}...</div>
</div>

<div class="modal" id="modal">
  <div class="box">
    <p>{{ t.delete_confirm }}<br><span class="name" id="modalName"></span></p>
    <div class="btns">
      <button class="yes" id="modalYes">{{ t.yes }}</button>
      <button class="no" id="modalNo">{{ t.no }}</button>
    </div>
  </div>
</div>

<script>
(function(){
  var dropzone = document.getElementById('dropzone');
  var overlay = document.getElementById('overlay');
  var overlayText = document.getElementById('overlayText');
  var uploadForm = document.getElementById('uploadForm');
  var fileInput = document.getElementById('fileInput');
  var dragCounter = 0;

  document.addEventListener('dragenter', function(e){
    e.preventDefault();
    dragCounter++;
    if(dragCounter === 1) dropzone.classList.add('active');
  });
  document.addEventListener('dragleave', function(e){
    e.preventDefault();
    dragCounter--;
    if(dragCounter <= 0){ dragCounter = 0; dropzone.classList.remove('active'); }
  });
  document.addEventListener('dragover', function(e){
    e.preventDefault();
  });
  document.addEventListener('drop', function(e){
    e.preventDefault();
    dragCounter = 0;
    dropzone.classList.remove('active');
    var files = e.dataTransfer.files;
    if(!files || files.length === 0) return;
    var fd = new FormData();
    for(var i=0;i<files.length;i++) fd.append('file', files[i]);
    overlayText.textContent = '{{ t.upload }} ' + files.length + '...';
    overlay.classList.add('active');
    var xhr = new XMLHttpRequest();
    xhr.open('POST', '{{ url_for("upload", path=path) }}', true);
    xhr.onload = function(){
      overlay.classList.remove('active');
      if(xhr.status >= 200 && xhr.status < 400){
        window.location.reload();
      } else {
        alert('Error: ' + xhr.status);
      }
    };
    xhr.onerror = function(){
      overlay.classList.remove('active');
      alert('Network error');
    };
    xhr.send(fd);
  });

  uploadForm.addEventListener('submit', function(){
    if(fileInput.files && fileInput.files.length > 1){
      overlayText.textContent = '{{ t.upload }} ' + fileInput.files.length + '...';
      overlay.classList.add('active');
    }
  });

  var modal = document.getElementById('modal');
  var modalName = document.getElementById('modalName');
  var modalYes = document.getElementById('modalYes');
  var modalNo = document.getElementById('modalNo');
  var pendingUrl = null;

  document.querySelectorAll('.item .del').forEach(function(el){
    el.addEventListener('click', function(ev){
      ev.preventDefault();
      ev.stopPropagation();
      pendingUrl = el.getAttribute('data-url');
      modalName.textContent = el.getAttribute('data-name');
      modal.classList.add('active');
    });
  });

  modalNo.addEventListener('click', function(){
    modal.classList.remove('active');
    pendingUrl = null;
  });

  modalYes.addEventListener('click', function(){
    modal.classList.remove('active');
    if(pendingUrl){ window.location.href = pendingUrl; }
    pendingUrl = null;
  });

  modal.addEventListener('click', function(e){
    if(e.target === modal){ modal.classList.remove('active'); pendingUrl = null; }
  });
})();
</script>

</body></html>
"""

ERROR_PAGE = """<!doctype html><html><head><meta charset=utf-8>
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{{ t.error }}</title>
<link rel="icon" href="/media/error.png">
<style>
body{font-family:system-ui,sans-serif;background:#111;color:#eee;
     padding:24px;margin:0}
.card{background:#2a1010;border:1px solid #5a1a1a;border-radius:10px;
      padding:20px;max-width:700px;margin:40px auto}
h1{color:#f77;margin-top:0;font-size:20px}
pre{white-space:pre-wrap;word-break:break-word;color:#faa;
    font-size:12px;background:#1a0808;padding:12px;border-radius:6px}
a{color:#4af}
</style></head><body>
<div class="card">
  <h1>{{ t.error }} {{ code }}</h1>
  <p>{{ message }}</p>
  {% if details %}<pre>{{ details }}</pre>{% endif %}
  <p><a href="/">{{ t.back }}</a></p>
</div>
</body></html>
"""


def safe_path(rel):
    try:
        p = (Path(ROOT) / rel.lstrip("/")).resolve()
        root = Path(ROOT).resolve()
        if root not in p.parents and p != root:
            abort(403)
        return p
    except Exception as e:
        abort(400, f"Некорректный путь: {e}")


def human_size(n):
    for unit in ("B", "K", "M", "G", "T"):
        if n < 1024:
            return f"{n:.0f}{unit}" if unit == "B" else f"{n:.1f}{unit}"
        n /= 1024
    return f"{n:.1f}P"


IMAGE_EXTS = {"jpg", "jpeg", "png", "gif", "webp", "bmp", "svg", "ico",
              "heic", "avif"}

ICON_MAP = [
    (IMAGE_EXTS, "image.png", "[img]"),
    ({"mp4", "mkv", "avi", "mov", "webm", "flv", "m4v", "3gp"},
     "video.png", "[vid]"),
    ({"mp3", "wav", "flac", "ogg", "m4a", "aac", "opus", "wma"},
     "audio.png", "[aud]"),
    ({"zip", "rar", "7z", "tar", "gz", "bz2", "xz", "iso"},
     "archive.png", "[arc]"),
    ({"pdf", "doc", "docx", "txt", "rtf", "odt", "md"},
     "doc.png", "[doc]"),
    ({"xls", "xlsx", "csv", "ods"}, "sheet.png", "[xls]"),
    ({"ppt", "pptx", "odp"}, "slide.png", "[ppt]"),
    ({"py", "js", "ts", "html", "css", "json", "xml", "yml", "yaml",
      "c", "cpp", "h", "java", "go", "rs", "sh", "php", "rb", "sql",
      "ini", "cfg", "toml"}, "code.png", "[src]"),
    ({"apk", "exe", "msi", "dmg", "deb", "rpm", "appimage"},
     "apk.png", "[bin]"),
]


def file_icon(path, is_dir):
    try:
        if is_dir:
            return "folder.png", "[dir]", False
        ext = path.suffix.lower().lstrip(".")
        is_img = ext in IMAGE_EXTS
        for exts, icon, emoji in ICON_MAP:
            if ext in exts:
                return icon, emoji, is_img
        return "file.png", "[file]", is_img
    except Exception:
        return "file.png", "[file]", False


def _err_page(code, message, details=None):
    try:
        lang = get_lang()
        return render_template_string(
            ERROR_PAGE, code=code, message=message, details=details,
            t=I18N[lang]), code
    except Exception:
        return f"<h1>Error {code}</h1><pre>{message}\n{details or ''}</pre>", code


@app.errorhandler(400)
def err_400(e):
    return _err_page(400, getattr(e, "description", str(e)))


@app.errorhandler(403)
def err_403(e):
    return _err_page(403, "Forbidden / Доступ запрещён",
                     getattr(e, "description", None))


@app.errorhandler(404)
def err_404(e):
    return _err_page(404, "Not found / Не найдено")


@app.errorhandler(500)
def err_500(e):
    tb = traceback.format_exc()
    log_error(f"500: {e}\n{tb}")
    return _err_page(500, "Internal error", tb)


@app.errorhandler(Exception)
def err_any(e):
    tb = traceback.format_exc()
    log_error(f"{type(e).__name__}: {e}\n{tb}")
    return _err_page(500, f"{type(e).__name__}: {e}", tb)


@app.route("/media/<path:fname>")
def media(fname):
    try:
        safe = os.path.normpath(fname).lstrip("/\\")
        if ".." in safe.split(os.sep):
            abort(403)
        full = os.path.join(MEDIA_DIR, safe)
        if not os.path.isfile(full):
            abort(404)
        resp = make_response(send_from_directory(MEDIA_DIR, safe))
        resp.headers["Cache-Control"] = "public, max-age=86400"
        return resp
    except Exception as e:
        log_error(f"media({fname}): {e}")
        abort(404)


@app.route("/lang/<code>")
def set_lang(code):
    back = request.args.get("back", "/")
    if code not in I18N:
        code = "en"
    resp = make_response(redirect(back))
    resp.set_cookie("lang", code, max_age=60 * 60 * 24 * 365)
    return resp


@app.route("/errors/clear")
def clear_err():
    try:
        with ERROR_LOCK:
            ERRORS.clear()
        return redirect("/")
    except Exception as e:
        log_error(f"clear_err: {e}")
        return _err_page(500, str(e))


@app.route("/errors")
def show_errors():
    return jsonify(errors=get_errors())


@app.route("/")
def index_root():
    return _index("")


@app.route("/browse/")
def index_browse_empty():
    return _index("")


@app.route("/browse/<path:path>")
def index_browse(path):
    return _index(path)


def _index(path=""):
    try:
        lang = get_lang()
        t = I18N[lang]
        other = "ru" if lang == "en" else "en"

        target = safe_path(path)
        if not target.is_dir():
            return redirect(url_for("download", path=path))

        entries = []
        try:
            for child in sorted(target.iterdir(),
                                key=lambda c: (not c.is_dir(),
                                               c.name.lower())):
                try:
                    rel = str(child.relative_to(Path(ROOT).resolve())
                              ).replace(os.sep, "/")
                    is_dir = child.is_dir()
                    try:
                        size = child.stat().st_size if child.is_file() else 0
                    except OSError:
                        size = None
                    icon_name, emoji, is_img = file_icon(child, is_dir)
                    entries.append({
                        "name": child.name,
                        "is_dir": is_dir,
                        "icon": icon_name,
                        "fallback": emoji,
                        "is_img": is_img,
                        "size": human_size(size) if size else "",
                        "url": url_for("index_browse", path=rel) if is_dir
                               else url_for("download", path=rel),
                        "delete_url": url_for("delete", path=rel),
                    })
                except Exception as e:
                    log_error(f"обработка {child}: {e}")
        except PermissionError as e:
            log_error(f"нет доступа к {target}: {e}")
            abort(403, f"Нет доступа: {target}")

        parts = [p for p in path.strip("/").split("/") if p]
        crumbs = []
        acc = ""
        for p in parts:
            acc = f"{acc}/{p}" if acc else p
            crumbs.append({"name": p, "rel": acc})

        parent = "/".join(parts[:-1]) if parts else ""

        return render_template_string(
            PAGE,
            path="/" + path.strip("/") if path.strip("/") else "/",
            parent=parent,
            crumbs=crumbs,
            entries=entries,
            errors=get_errors(),
            t=t,
            other_lang=other,
        )
    except Exception as e:
        tb = traceback.format_exc()
        log_error(f"_index({path}): {e}\n{tb}")
        return _err_page(500, f"{type(e).__name__}: {e}", tb)


@app.route("/download/<path:path>")
def download(path):
    try:
        target = safe_path(path)
        if not target.is_file() or not os.access(str(target), os.R_OK):
            abort(404, f"Файл не найден: {target}")
        try:
            if target.stat().st_size == 0:
                abort(404, f"Файл пуст или недоступен: {target}")
        except OSError as e:
            abort(404, f"Файл недоступен: {target} ({e})")
        return send_file(str(target), as_attachment=False,
                         download_name=target.name)
    except Exception as e:
        tb = traceback.format_exc()
        log_error(f"download({path}): {e}\n{tb}")
        return _err_page(500, f"{type(e).__name__}: {e}", tb)


@app.route("/upload/", methods=["POST"])
@app.route("/upload/<path:path>", methods=["POST"])
def upload(path=""):
    try:
        target_dir = safe_path(path)
        if not target_dir.is_dir():
            abort(400, f"Не папка: {target_dir}")
        for f in request.files.getlist("file"):
            if not f.filename:
                continue
            name = os.path.basename(f.filename)
            try:
                f.save(target_dir / name)
            except Exception as e:
                log_error(f"сохранить {name}: {e}")
        return redirect(f"/browse/{path}" if path else "/")
    except Exception as e:
        tb = traceback.format_exc()
        log_error(f"upload({path}): {e}\n{tb}")
        return _err_page(500, f"{type(e).__name__}: {e}", tb)


@app.route("/delete/<path:path>", methods=["GET", "POST"])
def delete(path):
    try:
        target = safe_path(path)
        if target.is_dir():
            try:
                target.rmdir()
            except OSError as e:
                log_error(f"папка не пустая: {target} — {e}")
                abort(400, "Папка не пустая")
        else:
            target.unlink(missing_ok=True)
        parent = "/".join(path.rstrip("/").split("/")[:-1])
        return redirect(f"/browse/{parent}" if parent else "/")
    except Exception as e:
        tb = traceback.format_exc()
        log_error(f"delete({path}): {e}\n{tb}")
        return _err_page(500, f"{type(e).__name__}: {e}", tb)


def start_server():
    global SERVER_READY
    try:
        log(f"[HTTP] ROOT={ROOT} PORT={HTTP_PORT} MEDIA={MEDIA_DIR}")

        try:
            request_android_permissions()
        except Exception as e:
            log_error(f"perm: {e}\n{traceback.format_exc()}")

        try:
            if not Path(ROOT).exists():
                log_error(f"ROOT не существует: {ROOT}")
            else:
                list(Path(ROOT).iterdir())
                log(f"[ROOT] OK, доступен")
        except PermissionError as e:
            log_error(f"Нет доступа к ROOT {ROOT}: {e}")
        except Exception as e:
            log_error(f"Ошибка проверки ROOT: {e}\n{traceback.format_exc()}")

        if not os.path.isdir(MEDIA_DIR):
            log(f"[MEDIA] папка не найдена: {MEDIA_DIR}")

        SERVER_READY = True
        log(f"[HTTP] слушаю 0.0.0.0:{HTTP_PORT}")
        app.run(host="0.0.0.0", port=HTTP_PORT, debug=False, threaded=True)
    except Exception as e:
        tb = traceback.format_exc()
        log_error(f"server: {e}\n{tb}")


class FileServerApp(App):
    def build(self):
        self.title = "WebFTP"
        root = BoxLayout(orientation="vertical", padding=15, spacing=10)

        self.status = Label(text="Starting server...",
                            size_hint_y=None, height=50, font_size="14sp")
        self.btn = Button(text="Open files / Открыть файлы",
                          size_hint_y=None, height=60, disabled=True)
        self.btn.bind(on_release=self.open_browser)

        self.log_label = Label(text="", size_hint_y=None, halign="left",
                               valign="top", font_size="11sp",
                               text_size=(400, None))
        self.log_label.bind(
            texture_size=lambda *a: setattr(self.log_label, "height",
                                            self.log_label.texture_size[1]))

        scroll = ScrollView()
        scroll.add_widget(self.log_label)

        root.add_widget(self.status)
        root.add_widget(self.btn)
        root.add_widget(scroll)

        threading.Thread(target=start_server, daemon=True).start()
        Clock.schedule_interval(self.check, 0.5)
        return root

    def check(self, dt):
        if SERVER_READY:
            ip = get_local_ip()
            self.status.text = f"http://{ip}:{HTTP_PORT}/"
            self.btn.disabled = False
            return False
        try:
            with open(LOG_FILE, "r", encoding="utf-8") as f:
                self.log_label.text = f.read()[-3000:]
        except Exception:
            pass
        return True

    def open_browser(self, *a):
        url = f"http://{get_local_ip()}:{HTTP_PORT}/"
        try:
            if platform == "android":
                from jnius import autoclass
                Intent = autoclass("android.content.Intent")
                Uri = autoclass("android.net.Uri")
                PythonActivity = autoclass("org.kivy.android.PythonActivity")
                intent = Intent(Intent.ACTION_VIEW, Uri.parse(url))
                PythonActivity.mActivity.startActivity(intent)
            else:
                import webbrowser
                webbrowser.open(url)
        except Exception as e:
            log(f"browser: {e}")


if __name__ == "__main__":
    try:
        FileServerApp().run()
    except Exception as e:
        log(f"[FATAL] {e}\n{traceback.format_exc()}")
        time.sleep(10)
