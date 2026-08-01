#!/usr/bin/env python3
import sys
import subprocess

try:
    import customtkinter as ctk
    from PIL import Image, ImageTk, ImageDraw, ImageFont, ImageSequence
    import requests
    import xlsxwriter
    import urllib3
except ImportError:
    subprocess.check_call([sys.executable, "-m", "pip", "install", "customtkinter", "Pillow", "requests", "urllib3", "xlsxwriter", "--break-system-packages"])
    import customtkinter as ctk
    from PIL import Image, ImageTk, ImageDraw, ImageFont, ImageSequence
    import requests
    import xlsxwriter
    import urllib3

import os
import threading
from io import BytesIO
import shutil
import time
import re
import socket
import ssl
from tkinter import filedialog
from urllib3.exceptions import InsecureRequestWarning
import signal
import webbrowser
import math
import random
import tempfile
import concurrent.futures

requests.packages.urllib3.disable_warnings(category=InsecureRequestWarning)

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("green")

KATEGORILER = {
    "YÖNETİM & PLATFORM": ["admin", "dashboard", "panel", "manage", "adminpanel", "adm", "cms", "wordpress", "wp-admin", "joomla", "drupal", "ghost", "content", "portal", "myaccount", "account", "profile", "login", "auth", "sso", "oauth", "control", "controlpanel", "whm", "cpanel", "plesk", "directadmin", "webmin"],
    "API & GELİŞTİRME": ["api", "api-v1", "api-v2", "rest", "graphql", "api-gateway", "backend", "dev", "development", "staging", "test", "beta", "sandbox", "uat", "qa", "develop", "testing", "docs", "documentation", "swagger", "api-docs", "developer", "devportal", "reference", "webhook", "webhooks", "callback", "hook", "notification", "gql", "playground", "graphiql"],
    "VERİ & DEPOLAMA": ["db", "database", "mysql", "postgres", "mongodb", "redis", "sql", "storage", "files", "upload", "s3", "bucket", "blob", "static-assets", "backup", "backup-server", "backup01", "archive", "vault", "dump", "cdn", "static", "assets", "img", "images", "media", "resources", "cache", "caching", "varnish", "memcached", "redis-cache", "search", "elastic", "elasticsearch", "solr", "algolia", "meilisearch"],
    "AĞ & ALTYAPI": ["ns1", "ns2", "dns", "dns1", "dns2", "resolver", "nameserver", "mail", "smtp", "imap", "pop3", "webmail", "email", "mx", "mailserver", "proxy", "proxy01", "relay", "forward", "reverse-proxy", "nginx", "lb", "loadbalancer", "balancer", "haproxy", "nlb", "alb", "nagios", "zabbix", "prometheus", "grafana", "munin", "observability", "logs", "log", "logstash", "fluentd", "syslog", "graylog"],
    "DOSYA & MEDYA": ["media", "video", "audio", "podcast", "stream", "live", "download", "dl", "files", "releases", "binary", "dist", "upload", "uploads", "drop", "submit", "file-upload", "img", "images", "photos", "gallery", "thumb", "thumbs"],
    "YEDEK & KURTARMA": ["backup", "yedek", "bkp", "snapshot", "restore", "recovery", "replica", "slave", "secondary", "standby", "mirror", "dr", "disaster-recovery", "failover", "redundancy", "archive", "old", "legacy", "deprecated", "historical"]
}

KATEGORI_RENKLERI = {
    "YÖNETİM & PLATFORM": "#ffaa00",
    "API & GELİŞTİRME": "#66ccff",
    "VERİ & DEPOLAMA": "#cc88ff",
    "AĞ & ALTYAPI": "#00ff88",
    "DOSYA & MEDYA": "#ff4444",
    "YEDEK & KURTARMA": "#ff8844",
    "DİĞER": "#ffffff"
}

def kategori_bul(domain):
    parts = domain.lower().split('.')
    for p in parts:
        for kat, kelimeler in KATEGORILER.items():
            if p in kelimeler:
                return kat
    for kat, kelimeler in KATEGORILER.items():
        for k in kelimeler:
            if k in domain.lower():
                return kat
    return "DİĞER"

class AccordionPanel(ctk.CTkFrame):
    def __init__(self, master, title, color, items, **kwargs):
        super().__init__(master, **kwargs)
        self.is_open = False
        self.items = list(items)
        self.title = title
        self.color = color

        self.btn = ctk.CTkButton(self, text=f"▶ {title} ({len(items)})", fg_color="#1a1a1a", hover_color="#2a2a2a", text_color=color, anchor="w", command=self.toggle)
        self.btn.pack(fill="x", padx=2, pady=2)

        self.content_frame = ctk.CTkFrame(self, fg_color="#0a0a0a")

        self.textbox = ctk.CTkTextbox(self.content_frame, font=ctk.CTkFont(family="Consolas", size=12), fg_color="#0a0a0a", text_color="#ffffff", height=150)
        self.textbox.pack(fill="both", expand=True, padx=2, pady=2)
        self.textbox.insert("1.0", "\n".join(self.items))
        self.textbox.configure(state="disabled")

    def toggle(self):
        if self.is_open:
            self.content_frame.pack_forget()
            self.btn.configure(text=f"▶ {self.title} ({len(self.items)})")
            self.is_open = False
        else:
            self.content_frame.pack(fill="x", padx=5, pady=2)
            self.btn.configure(text=f"▼ {self.title} ({len(self.items)})")
            self.is_open = True

    def add_item(self, text):
        self.items.append(text)
        self.btn.configure(text=f"{'▼' if self.is_open else '▶'} {self.title} ({len(self.items)})")
        self.textbox.configure(state="normal")
        if len(self.items) == 1:
            self.textbox.delete("1.0", "end")
            self.textbox.insert("end", text)
        else:
            self.textbox.insert("end", "\n" + text)
        self.textbox.see("end")
        self.textbox.configure(state="disabled")

class CyberAnkaTerminal:
    def __init__(self):
        self.root = ctk.CTk()
        self.root.title("CyberAnka - Alt Alan Adı Tarayıcı")
        self.root.configure(fg_color="#0a0a0a")
        self._set_window_icon()

        self.screen_w = self.root.winfo_screenwidth()
        self.screen_h = self.root.winfo_screenheight()
        w = int(self.screen_w * 0.90)
        h = int(self.screen_h * 0.85)
        if w < 1000: w = 1000
        if h < 650: h = 650
        x = (self.screen_w - w) // 2
        y = (self.screen_h - h) // 2
        self.root.geometry(f"{w}x{h}+{x}+{y}")
        self.root.minsize(950, 600)
        self.root.resizable(False, False)  # Pencere boyutu sabit
        self.root.attributes("-alpha", 0)

        self.subfinder_path = self.find_binary("subfinder")
        self.subfinder_available = self.subfinder_path is not None

        self.subdomains = []
        self.probe_results = []
        self.current_operation = "bekliyor"
        self.paused = False
        self.stopped = False
        self.pause_event = threading.Event()
        self.pause_event.set()
        self.total_found = 0
        self.scan_start_time = 0

        self._active_proc = None
        self._proc_lock = threading.Lock()
        self._probe_stop = threading.Event()
        self._probe_pause = threading.Event()
        self._probe_pause.set()

        self.thread_count = ctk.IntVar(value=200)
        self.timeout_value = ctk.IntVar(value=3)
        self.maxtime_value = ctk.IntVar(value=25)

        self._session_id = int(time.time() * 1000) % 1000000

        self.logo_img_pil = None
        self.bg_logo_img_pil = None
        self.live_accordion_panels = {}
        self._dns_cache = {}  # DNS çözümleme önbelleği
        self.accordion_visible = False

        self.gif_frames = []
        self.gif_delay = 50
        self.gif_frame_idx = 0
        self.bird_x = -150
        self.bird_y = 0
        self.bird_dx = 0
        self.bird_wave_phase = 0
        self.splash_bg = None
        self.splash_phase = 0
        self.bg_solid_color = "#000000"

        self.root.after(50, self.start_splash)

    def _safe_kill_proc(self, proc):
        if proc is None or proc.poll() is not None:
            return
        try:
            if sys.platform == "win32":
                proc.kill()
            else:
                os.killpg(os.getpgid(proc.pid), signal.SIGKILL)
        except Exception:
            try:
                proc.kill()
            except Exception:
                pass
        proc.wait(timeout=2)

    def find_binary(self, name):
        path = shutil.which(name)
        if path:
            return path
        home = os.path.expanduser("~")
        extra = {
            "subfinder": [
                os.path.join(home, "go", "bin", "subfinder"),
                "/usr/local/bin/subfinder",
                "/usr/bin/subfinder",
                os.path.join(home, "go", "bin", "subfinder.exe"),
                "C:\\Go\\bin\\subfinder.exe",
            ],
        }
        for p in extra.get(name, []):
            if os.path.isfile(p):
                return p
        return None

    def _set_window_icon(self):
        try:
            r = requests.get(
                "https://i.hizliresim.com/7fh9ayg.png",
                timeout=10,
                headers={"User-Agent": "Mozilla/5.0"},
            )
            r.raise_for_status()
            icon_img = Image.open(BytesIO(r.content))
            self._icon_pil = icon_img.copy()
            icon_sizes = [(16, 16), (32, 32), (48, 48), (64, 64)]
            icon_photo = ImageTk.PhotoImage(icon_img.resize((64, 64), Image.LANCZOS))
            self._icon_ref = icon_photo
            self.root.wm_iconphoto(True, icon_photo)
            if sys.platform == "win32":
                try:
                    import ctypes
                    import tempfile
                    ico_path = os.path.join(tempfile.gettempdir(), "cyberanka_icon.ico")
                    icon_img.save(ico_path, format="ICO", sizes=icon_sizes)
                    self.root.iconbitmap(ico_path)
                    myappid = "cyberanka.subdomain.scanner.1"
                    ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)
                except Exception:
                    pass
        except Exception:
            pass

    def download_logo(self):
        try:
            r = requests.get(
                "https://cyberanka.com/assets/images/subflame.png",
                timeout=10,
                headers={"User-Agent": "Mozilla/5.0"},
            )
            r.raise_for_status()
            img = Image.open(BytesIO(r.content))
            return img
        except Exception:
            return None

    def download_bg_logo(self):
        try:
            r = requests.get(
                "https://i.hizliresim.com/e9rbpzb.png",
                timeout=10,
                headers={"User-Agent": "Mozilla/5.0"},
            )
            r.raise_for_status()
            img = Image.open(BytesIO(r.content))
            return img
        except Exception:
            return None

    def download_gif_frames(self):
        try:
            r = requests.get(
                "https://downloadwap.com/thumbs3/screensavers/d/new/fantasy/phoenix-285306.gif",
                timeout=15,
                headers={"User-Agent": "Mozilla/5.0"},
                stream=True
            )
            r.raise_for_status()
            gif_data = BytesIO(r.content)
            gif = Image.open(gif_data)
            frames = []
            durations = []
            for frame in ImageSequence.Iterator(gif):
                frame_rgba = frame.copy().convert('RGBA')
                frames.append(frame_rgba)
                dur = frame.info.get('duration', 50)
                durations.append(dur)
            avg_dur = sum(durations) // len(durations) if durations else 50
            return frames, avg_dur
        except Exception as e:
            return None, 50

    def create_hacker_bg(self, w, h):
        bg = Image.new('RGBA', (w, h), (0, 0, 0, 255))
        draw = ImageDraw.Draw(bg)
        try:
            font_tiny = ImageFont.truetype("Consolas", 8)
            font_small = ImageFont.truetype("Consolas", 10)
            font_med = ImageFont.truetype("Consolas", 12)
        except Exception:
            font_tiny = ImageFont.load_default()
            font_small = ImageFont.load_default()
            font_med = ImageFont.load_default()

        rng = random.Random(42)

        # Dikey ışık çizgileri - soluk neon
        for col in range(0, w, 25):
            alpha = rng.randint(4, 12)
            draw.line([(col, 0), (col, h)], fill=(0, 255, 65, alpha), width=1)

        # Yatay grid çizgileri - çok soluk
        for row in range(0, h, 40):
            alpha = rng.randint(3, 8)
            draw.line([(0, row), (w, row)], fill=(0, 200, 50, alpha), width=1)

        # Köşe parantezleri [ ] { } - hacker terminal görünümü
        corner_positions = [
            (15, 15, "[", "#00ff41"),
            (w-25, 15, "]", "#00ff41"),
            (15, h-30, "{", "#ff4444"),
            (w-25, h-30, "}", "#ff4444"),
        ]
        for cx, cy, char, color in corner_positions:
            draw.text((cx, cy), char, fill=color, font=font_med)

        # Yanlarda dikey hacker kodu sütunları
        hex_chars = "0123456789ABCDEF"
        symbols = "!@#$%^&*_+-=[]{}|;':\",./<>?~"
        code_lines = "root@subflame:~$ ./scan.sh --target=* --verbose"

        # Sol sütun - dikey kod
        for i in range(30):
            y = i * 18 + 40
            if y < h - 40:
                char = rng.choice(hex_chars + symbols)
                alpha = rng.randint(8, 25)
                draw.text((8, y), char, fill=(0, 255, 65, alpha), font=font_tiny)

        # Sağ sütun - dikey kod
        for i in range(30):
            y = i * 18 + 40
            if y < h - 40:
                char = rng.choice(hex_chars + symbols)
                alpha = rng.randint(8, 25)
                draw.text((w-18, y), char, fill=(0, 255, 65, alpha), font=font_tiny)

        # Merkezde büyük neon "subflame" yazısı (çok soluk)
        try:
            font_big = ImageFont.truetype("Consolas", 60)
        except Exception:
            font_big = ImageFont.load_default()
        draw.text((w//2, h//2 - 60), "subflame", fill=(0, 255, 65, 6), font=font_big, anchor="mm")
        draw.text((w//2, h//2 + 10), "v1.0", fill=(0, 200, 50, 8), font=font_med, anchor="mm")

        # Saçılmış hex değerleri - çok soluk
        for _ in range(150):
            x = rng.randint(20, w-30)
            y = rng.randint(10, h-20)
            char = rng.choice(hex_chars)
            alpha = rng.randint(3, 12)
            green_val = rng.randint(100, 220)
            draw.text((x, y), char, fill=(0, green_val, 0, alpha), font=font_tiny)

        # Kırmızı uyarı sembolleri > ! $
        for i in range(20):
            x = rng.randint(30, w-40)
            y = rng.randint(20, h-30)
            char = rng.choice([">", "!", "$", "#"])
            alpha = rng.randint(8, 20)
            draw.text((x, y), char, fill=(255, 40, 40, alpha), font=font_small)

        # Alt kısımda status bar benzeri çizgi
        draw.line([(0, h-22), (w, h-22)], fill=(0, 255, 65, 10), width=1)
        status_text = f"CYBERANKA | SUBFLAME v1.0 // {time.strftime('%H:%M:%S')} UTC"
        draw.text((10, h-18), status_text, fill=(0, 255, 65, 12), font=font_tiny)

        # Sağ alt köşede küçük versiyon bilgisi
        draw.text((w-80, h-18), "encrypted", fill=(0, 200, 50, 10), font=font_tiny)

        # Noktalı border efekti - çerçeve
        for i in range(0, w, 6):
            alpha = rng.randint(3, 8)
            draw.point((i, 0), fill=(0, 255, 65, alpha))
            draw.point((i, h-1), fill=(0, 255, 65, alpha))
        for i in range(0, h, 6):
            alpha = rng.randint(3, 8)
            draw.point((0, i), fill=(0, 255, 65, alpha))
            draw.point((w-1, i), fill=(0, 255, 65, alpha))

        return bg

    def start_splash(self):
        gif_raw, self.gif_delay = self.download_gif_frames()
        if not gif_raw:
            self.splash_phase = 2
            self.root.attributes("-alpha", 1)
            self._final_setup()
            return

        target_size = 160
        self.gif_frames = []
        for frame in gif_raw:
            w, h = frame.size
            ratio = target_size / max(w, h)
            nw = int(w * ratio)
            nh = int(h * ratio)
            resized = frame.resize((nw, nh), Image.LANCZOS)
            self.gif_frames.append(resized)

        screen_w = self.root.winfo_screenwidth()
        screen_h = self.root.winfo_screenheight()

        self.splash_bg = ctk.CTkFrame(self.root, fg_color=self.bg_solid_color, corner_radius=0)
        self.splash_bg.place(relx=0, rely=0, relwidth=1, relheight=1)

        self.hacker_bg_pil = self.create_hacker_bg(screen_w, screen_h)
        self.hacker_bg_tk = ImageTk.PhotoImage(self.hacker_bg_pil)
        self.hacker_bg_label = ctk.CTkLabel(self.splash_bg, text="", image=self.hacker_bg_tk, fg_color="transparent")
        self.hacker_bg_label.place(relx=0, rely=0, relwidth=1, relheight=1)

        self.bird_x = -160
        self.bird_y = screen_h // 2 - 60
        mid_x = screen_w // 2
        travel_dist = mid_x + 300
        self.bird_dx = travel_dist / 125
        self.bird_wave_phase = 0

        self.bird_label = ctk.CTkLabel(self.splash_bg, text="", fg_color="transparent")
        self.bird_label.place(x=self.bird_x, y=self.bird_y)

        brand_frame = ctk.CTkFrame(self.splash_bg, fg_color="transparent")
        brand_frame.place(relx=0.5, rely=0.42, anchor="center")

        sub_label = ctk.CTkLabel(
            brand_frame,
            text="Sub",
            font=ctk.CTkFont(family="Montserrat", size=64, weight="bold"),
            text_color="#ff4444",
            fg_color="transparent"
        )
        sub_label.pack(side=ctk.LEFT)

        flame_label = ctk.CTkLabel(
            brand_frame,
            text="flame",
            font=ctk.CTkFont(family="Montserrat", size=64, weight="normal"),
            text_color="#ff4444",
            fg_color="transparent"
        )
        flame_label.pack(side=ctk.LEFT)

        tagline = ctk.CTkLabel(
            self.splash_bg,
            text="Gelişmiş alt alan adı keşif ve tarama aracı",
            font=ctk.CTkFont(family="Montserrat", size=16),
            text_color="#ff8888",
            fg_color="transparent"
        )
        tagline.place(relx=0.5, rely=0.52, anchor="center")

        self.countdown_label = ctk.CTkLabel(
            self.splash_bg,
            text="",
            font=ctk.CTkFont(family="Consolas", size=56, weight="bold"),
            text_color="#00ff41",
            fg_color="transparent"
        )
        self.countdown_label.place(relx=0.5, rely=0.65, anchor="center")

        self.countdown_sub = ctk.CTkLabel(
            self.splash_bg,
            text="Arayüz açılıyor",
            font=ctk.CTkFont(family="Consolas", size=18),
            text_color="#00cc33",
            fg_color="transparent"
        )
        self.countdown_sub.place(relx=0.5, rely=0.60, anchor="center")

        self.countdown_remaining = 5
        self.root.attributes("-alpha", 1)
        self.animate_gif_frame()

    def animate_gif_frame(self):
        if self.splash_phase == 2:
            return
        if not hasattr(self, 'splash_bg') or self.splash_bg is None:
            return
        try:
            if not self.splash_bg.winfo_exists():
                return
        except Exception:
            return

        sw = self.root.winfo_width() if self.root.winfo_width() > 100 else self.root.winfo_screenwidth()
        sh = self.root.winfo_height() if self.root.winfo_height() > 100 else self.root.winfo_screenheight()

        self.bird_x += self.bird_dx
        self.bird_wave_phase += 0.1
        self.bird_y = sh // 2 - 60 + math.sin(self.bird_wave_phase) * 35

        if self.bird_x > sw + 200:
            self.bird_x = -160
            self.bird_y = sh // 2 - 60
            self.bird_wave_phase = 0

        if self.bird_label and self.bird_label.winfo_exists() and self.gif_frames:
            frame = self.gif_frames[self.gif_frame_idx]
            self.gif_frame_idx = (self.gif_frame_idx + 1) % len(self.gif_frames)
            self.current_gif_photo = ImageTk.PhotoImage(frame)
            self.bird_label.configure(image=self.current_gif_photo)
            self.bird_label.place(x=int(self.bird_x), y=int(self.bird_y))

        self.root.after(max(30, int(self.gif_delay * 0.8)), self.animate_gif_frame)

    def do_countdown(self):
        if self.splash_phase == 2:
            return
        if self.countdown_remaining > 0:
            num_str = str(self.countdown_remaining)
            dots = "." * (6 - self.countdown_remaining)
            self.countdown_label.configure(text=num_str)
            self.countdown_sub.configure(text=f"Arayüz açılıyor{dots}")
            self.countdown_remaining -= 1
            self.root.after(1000, self.do_countdown)
        else:
            self.countdown_label.configure(text="0")
            self.countdown_sub.configure(text="Arayüz açılıyor...")
            self.splash_phase = 2
            if self.splash_bg and self.splash_bg.winfo_exists():
                self.splash_bg.destroy()
            self.splash_bg = None
            self._final_setup()

    def _final_setup(self):
        self.splash_phase = 2
        self.logo_img_pil = self.download_logo()
        self.bg_logo_img_pil = self.download_bg_logo()
        self._build_gui()

    def _build_gui(self):
        for w in self.root.winfo_children():
            w.destroy()

        main = ctk.CTkFrame(self.root, fg_color="#0a0a0a", corner_radius=0)
        main.pack(fill=ctk.BOTH, expand=True)

        top_bar = ctk.CTkFrame(main, fg_color="#661111", height=4, corner_radius=0)
        top_bar.pack(fill=ctk.X, side=ctk.TOP)

        header = ctk.CTkFrame(main, fg_color="#111111", height=80, corner_radius=0)
        header.pack(fill=ctk.X, side=ctk.TOP)
        header.pack_propagate(False)

        brand_left = ctk.CTkFrame(header, fg_color="transparent")
        brand_left.pack(side=ctk.LEFT, padx=(10, 3))
        if self.logo_img_pil:
            try:
                sm_logo = self.logo_img_pil.copy()
                sm_logo.thumbnail((60, 60), Image.LANCZOS)
                self.logo_small = ImageTk.PhotoImage(sm_logo)
                ctk.CTkLabel(
                    brand_left, text="", image=self.logo_small, fg_color="transparent"
                ).pack(side=ctk.LEFT, padx=(0, 6))
            except Exception:
                pass

        brand_text = ctk.CTkFrame(brand_left, fg_color="transparent")
        brand_text.pack(side=ctk.LEFT)

        title_row = ctk.CTkFrame(brand_text, fg_color="transparent")
        title_row.pack(anchor="w")
        ctk.CTkLabel(
            title_row, text="Sub",
            font=ctk.CTkFont(family="Montserrat", size=22, weight="bold"),
            text_color="#ff6666", fg_color="transparent"
        ).pack(side=ctk.LEFT)
        ctk.CTkLabel(
            title_row, text="flame",
            font=ctk.CTkFont(family="Montserrat", size=22, weight="normal"),
            text_color="#ff6666", fg_color="transparent"
        ).pack(side=ctk.LEFT)

        self.brand_desc = ctk.CTkLabel(
            brand_text, text="Gelişmiş alt alan adı keşif ve tarama aracı",
            font=ctk.CTkFont(family="Montserrat", size=11),
            text_color="#aaaaaa", fg_color="transparent"
        )
        self.brand_desc.pack(anchor="w")

        self.status_label = ctk.CTkLabel(
            header, text="[ HAZIR ]",
            font=ctk.CTkFont(family="Consolas", size=13, weight="bold"),
            text_color="#ff6666", fg_color="transparent"
        )
        self.status_label.pack(side=ctk.LEFT, padx=(15, 0))

        kurulum_tab = ctk.CTkFrame(header, fg_color="#1a0a0a", corner_radius=6)
        kurulum_tab.pack(side=ctk.LEFT, padx=(15, 0))
        kurulum_btn = ctk.CTkButton(
            kurulum_tab, text="⚙ KURULUM",
            font=ctk.CTkFont(family="Consolas", size=10, weight="bold"),
            fg_color="#661111", hover_color="#882222",
            text_color="#ffffff", height=28, width=90, corner_radius=4,
            command=self.show_kurulum_rehberi
        )
        kurulum_btn.pack(padx=4, pady=4)

        counter_frame = ctk.CTkFrame(header, fg_color="transparent")
        counter_frame.pack(side=ctk.RIGHT, padx=(0, 15))

        self.live_counter = ctk.CTkLabel(
            counter_frame, text="[ 0 ]",
            font=ctk.CTkFont(family="Consolas", size=18, weight="bold"),
            text_color="#ff6666", fg_color="transparent"
        )
        self.live_counter.pack(side=ctk.RIGHT, padx=(0, 8))

        self.time_counter = ctk.CTkLabel(
            counter_frame, text="( 0.0s )",
            font=ctk.CTkFont(family="Consolas", size=12),
            text_color="#66aaff", fg_color="transparent"
        )
        self.time_counter.pack(side=ctk.RIGHT, padx=(0, 5))

        self.term_container = ctk.CTkFrame(main, fg_color="#0a0a0a", corner_radius=0)
        self.term_container.pack(fill=ctk.BOTH, expand=True, padx=0, pady=(0, 0))

        self.term_frame = ctk.CTkFrame(self.term_container, fg_color="#000000", corner_radius=0)
        self.term_frame.pack(fill=ctk.BOTH, expand=True, padx=0, pady=0)

        bg_frame = ctk.CTkFrame(self.term_frame, fg_color="#000000", corner_radius=0)
        bg_frame.place(relx=0.5, rely=0.5, anchor="center", relwidth=1, relheight=1)
        bg_frame.lower()

        if self.bg_logo_img_pil:
            try:
                big_logo = self.bg_logo_img_pil.copy()
                tw = self.term_frame.winfo_width() if self.term_frame.winfo_width() > 100 else 900
                th = self.term_frame.winfo_height() if self.term_frame.winfo_height() > 100 else 600
                big_logo.thumbnail((int(tw*1.5), int(th*1.5)), Image.LANCZOS)
                if big_logo.mode == 'RGBA':
                    r, g, b, a = big_logo.split()
                    a = a.point(lambda i: max(0, int(i * 0.08)))
                    big_logo = Image.merge('RGBA', (r, g, b, a))
                else:
                    big_logo = big_logo.convert('RGBA')
                    datas = big_logo.getdata()
                    new_data = [(r, g, b, 20) for (r, g, b, a) in datas]
                    big_logo.putdata(new_data)
                self.bg_logo_big = ImageTk.PhotoImage(big_logo)
                ctk.CTkLabel(
                    bg_frame, text="", image=self.bg_logo_big, fg_color="transparent"
                ).place(relx=0.5, rely=0.5, anchor="center")
            except Exception:
                pass

        self._place_cyber_text_bg(bg_frame)

        if self.logo_img_pil:
            try:
                anka_logo = self.logo_img_pil.copy()
                anka_logo.thumbnail((350, 100), Image.LANCZOS)
                if anka_logo.mode == 'RGBA':
                    r, g, b, a = anka_logo.split()
                    a = a.point(lambda i: max(0, int(i * 0.06)))
                    anka_logo = Image.merge('RGBA', (r, g, b, a))
                else:
                    anka_logo = anka_logo.convert('RGBA')
                    datas = anka_logo.getdata()
                    new_data = [(r, g, b, 15) for (r, g, b, a) in datas]
                    anka_logo.putdata(new_data)
                self.anka_bg = ImageTk.PhotoImage(anka_logo)
                ctk.CTkLabel(
                    bg_frame, text="", image=self.anka_bg, fg_color="transparent"
                ).place(relx=0.5, rely=0.25, anchor="center")
            except Exception:
                pass

        term_title = ctk.CTkFrame(self.term_frame, fg_color="#111111", height=26, corner_radius=0)
        term_title.pack(fill=ctk.X, side=ctk.TOP)
        term_title.pack_propagate(False)

        for i, color in enumerate(["#ff4444", "#ffaa00", "#ff6666"]):
            ctk.CTkLabel(
                term_title, text="●", font=ctk.CTkFont(size=10),
                text_color=color, fg_color="transparent"
            ).pack(side=ctk.LEFT, padx=(4 if i == 0 else 2, 1))

        ctk.CTkLabel(
            term_title, text="root@subflame:~$",
            font=ctk.CTkFont(family="Consolas", size=11, weight="bold"),
            text_color="#ff6666", fg_color="transparent"
        ).pack(side=ctk.LEFT, padx=(10, 0))

        # Konsol ve accordion için içerik alanı - term_title altında kalır
        self.content_area = ctk.CTkFrame(self.term_frame, fg_color="#000000", corner_radius=0)
        self.content_area.pack(fill=ctk.BOTH, expand=True)

        self.terminal = ctk.CTkTextbox(
            self.content_area,
            font=ctk.CTkFont(family="Consolas", size=13),
            fg_color="#000000", text_color="#ffffff",
            border_color="#111111", border_width=1,
            corner_radius=0, wrap="word", activate_scrollbars=True
        )
        self.terminal.pack(fill=ctk.BOTH, expand=True)

        for tag, color in [
            ("green", "#ff8888"), ("cyan", "#66ccff"), ("red", "#ff4444"),
            ("yellow", "#ffcc44"), ("purple", "#cc88ff"), ("dim", "#666666"),
            ("orange", "#ff8844"), ("sub", "#44ddaa"), ("white", "#ffffff"),
        ]:
            self.terminal.tag_config(tag, foreground=color)
            
        for k, color in KATEGORI_RENKLERI.items():
            self.terminal.tag_config(f"kat_{k}", foreground=color)

        self.progress = ctk.CTkProgressBar(
            self.content_area, fg_color="#111111", progress_color="#ff6666",
            height=4, corner_radius=0
        )
        self.progress.pack(fill=ctk.X, padx=0, pady=0)
        self.progress.set(0)

        filter_frame = ctk.CTkFrame(main, fg_color="#111111", height=34, corner_radius=0)
        filter_frame.pack(fill=ctk.X, side=ctk.TOP, padx=0, pady=(1, 1))
        filter_frame.pack_propagate(False)

        ctk.CTkLabel(
            filter_frame, text="🔍", font=ctk.CTkFont(family="Segoe UI", size=14),
            text_color="#555555", fg_color="transparent"
        ).pack(side=ctk.LEFT, padx=(10, 3))

        self.filter_entry = ctk.CTkEntry(
            filter_frame, placeholder_text="api, admin, port 80...",
            font=ctk.CTkFont(family="Consolas", size=12),
            fg_color="#1a0a0a", text_color="#ffffff",
            placeholder_text_color="#555555", border_color="#661111",
            border_width=1, corner_radius=3, height=26
        )
        self.filter_entry.pack(side=ctk.LEFT, fill=ctk.X, expand=True, padx=(3, 3))
        self.filter_entry.bind("<Return>", self.on_filter_search)

        self.btn_filter = ctk.CTkButton(
            filter_frame, text="ARA",
            font=ctk.CTkFont(family="Consolas", size=10, weight="bold"),
            fg_color="#661111", hover_color="#882222",
            text_color="#ffffff", height=26, width=50, corner_radius=3,
            command=self.on_filter_search
        )
        self.btn_filter.pack(side=ctk.LEFT, padx=(0, 3))

        self.btn_filter_clear = ctk.CTkButton(
            filter_frame, text="X",
            font=ctk.CTkFont(family="Consolas", size=10, weight="bold"),
            fg_color="#882222", hover_color="#993333",
            text_color="#ffffff", height=26, width=26, corner_radius=3,
            command=self.on_filter_clear
        )
        self.btn_filter_clear.pack(side=ctk.LEFT, padx=(0, 5))

        self.filter_count_label = ctk.CTkLabel(
            filter_frame, text="[ 0 / 0 ]",
            font=ctk.CTkFont(family="Consolas", size=12, weight="bold"),
            text_color="#ff8888", fg_color="transparent", width=80
        )
        self.filter_count_label.pack(side=ctk.RIGHT, padx=(0, 10))

        ctk.CTkLabel(
            filter_frame, text="subflame",
            font=ctk.CTkFont(family="Segoe UI", size=9),
            text_color="#333333", fg_color="transparent"
        ).pack(side=ctk.RIGHT, padx=(0, 5))

        cmd_frame = ctk.CTkFrame(main, fg_color="#111111", height=52, corner_radius=0)
        cmd_frame.pack(fill=ctk.X, side=ctk.BOTTOM, padx=0, pady=(1, 2))
        cmd_frame.pack_propagate(False)

        ctk.CTkLabel(
            cmd_frame, text="root@subflame:~$",
            font=ctk.CTkFont(family="Consolas", size=14, weight="bold"),
            text_color="#ff6666", fg_color="transparent"
        ).pack(side=ctk.LEFT, padx=(12, 6))

        self.entry = ctk.CTkEntry(
            cmd_frame, placeholder_text="ornek.com (veya alan_adlari.txt)",
            font=ctk.CTkFont(family="Consolas", size=13),
            fg_color="#1a0a0a", text_color="#ffffff",
            placeholder_text_color="#555555", border_color="#661111",
            border_width=1, corner_radius=4, height=34
        )
        self.entry.pack(side=ctk.LEFT, fill=ctk.X, expand=True, padx=(3, 6))
        self.entry.bind("<Return>", lambda e: self.start_scan())

        btn_frame = ctk.CTkFrame(cmd_frame, fg_color="transparent")
        btn_frame.pack(side=ctk.RIGHT, padx=(0, 6))

        bs = {"font": ctk.CTkFont(family="Consolas", size=10, weight="bold"), "height": 32, "corner_radius": 4}

        self.btn_scan = ctk.CTkButton(btn_frame, text="▶ BAŞLAT", fg_color="#661111", hover_color="#882222", text_color="#ffffff", width=80, command=self.start_scan, **bs)
        self.btn_scan.pack(side=ctk.LEFT, padx=2)

        self.btn_pause = ctk.CTkButton(btn_frame, text="⏸ DURAKLAT", fg_color="#884422", hover_color="#995533", text_color="#ffffff", width=100, command=self.toggle_pause, state=ctk.DISABLED, **bs)
        self.btn_pause.pack(side=ctk.LEFT, padx=2)

        self.btn_stop = ctk.CTkButton(btn_frame, text="⏹ DURDUR", fg_color="#882222", hover_color="#993333", text_color="#ffffff", width=85, command=self.stop_operation, state=ctk.DISABLED, **bs)
        self.btn_stop.pack(side=ctk.LEFT, padx=2)

        self.btn_probe = ctk.CTkButton(btn_frame, text="🔍 CANLI DOMAİN TARA", fg_color="#662288", hover_color="#773399", text_color="#ffffff", width=150, command=self.probe_subdomains, state=ctk.DISABLED, **bs)
        self.btn_probe.pack(side=ctk.LEFT, padx=2)

        self.btn_copy = ctk.CTkButton(btn_frame, text="📋 KOPYALA", fg_color="#886600", hover_color="#997700", text_color="#ffffff", width=90, command=self.copy_results, state=ctk.DISABLED, **bs)
        self.btn_copy.pack(side=ctk.LEFT, padx=2)

        self.btn_save = ctk.CTkButton(btn_frame, text="💾 KAYDET", fg_color="#661111", hover_color="#882222", text_color="#ffffff", width=85, command=self.save_results, state=ctk.DISABLED, **bs)
        self.btn_save.pack(side=ctk.LEFT, padx=2)

        self.btn_save_probe = ctk.CTkButton(btn_frame, text="📊 CANLI DOMAİNLERİ KAYDET", fg_color="#662288", hover_color="#773399", text_color="#ffffff", width=190, command=self.save_probe_results, state=ctk.DISABLED, **bs)
        self.btn_save_probe.pack(side=ctk.LEFT, padx=2)

        self.btn_clear = ctk.CTkButton(btn_frame, text="🗑 TEMİZLE", fg_color="#444444", hover_color="#555555", text_color="#ffffff", width=90, command=self.clear_terminal, **bs)
        self.btn_clear.pack(side=ctk.LEFT, padx=2)

        if sys.platform == "win32":
            self.btn_select_subfinder = ctk.CTkButton(btn_frame, text="⚙ SUBFINDER SEÇ", fg_color="#552288", hover_color="#663399", text_color="#ffffff", width=110, command=self.select_subfinder, **bs)
            self.btn_select_subfinder.pack(side=ctk.LEFT, padx=2)

        settings_frame = ctk.CTkFrame(main, fg_color="#111111", height=32, corner_radius=0)
        settings_frame.pack(fill=ctk.X, side=ctk.BOTTOM, padx=0, pady=(0, 0))
        settings_frame.pack_propagate(False)

        ctk.CTkLabel(settings_frame, text="İş Parçacığı:", font=ctk.CTkFont(family="Consolas", size=10), text_color="#777777", fg_color="transparent").pack(side=ctk.LEFT, padx=(10, 3))
        ts = ctk.CTkSlider(settings_frame, from_=10, to=500, number_of_steps=49, variable=self.thread_count, fg_color="#222222", progress_color="#ff6666", button_color="#ff6666", button_hover_color="#ff8888", width=110, height=12, command=self.on_thread_change)
        ts.pack(side=ctk.LEFT, padx=(1, 3))
        self.thread_label = ctk.CTkLabel(settings_frame, text="200", font=ctk.CTkFont(family="Consolas", size=11, weight="bold"), text_color="#ff6666", fg_color="transparent", width=30)
        self.thread_label.pack(side=ctk.LEFT, padx=(0, 5))
        for v, l in [(50, "Yavaş"), (200, "Normal"), (500, "Hızlı")]:
            ctk.CTkButton(settings_frame, text=l, font=ctk.CTkFont(family="Consolas", size=8), fg_color="#222222", hover_color="#333333", text_color="#999999", height=20, width=45, corner_radius=2, command=lambda val=v: self.set_thread_preset(val)).pack(side=ctk.LEFT, padx=2)

        ctk.CTkLabel(settings_frame, text="Zaman Aşımı:", font=ctk.CTkFont(family="Consolas", size=10), text_color="#777777", fg_color="transparent").pack(side=ctk.LEFT, padx=(5, 3))
        ts2 = ctk.CTkSlider(settings_frame, from_=1, to=10, number_of_steps=9, variable=self.timeout_value, fg_color="#222222", progress_color="#884422", button_color="#884422", button_hover_color="#995533", width=70, height=12, command=self.on_timeout_change)
        ts2.pack(side=ctk.LEFT, padx=(1, 3))
        self.timeout_label = ctk.CTkLabel(settings_frame, text="3s", font=ctk.CTkFont(family="Consolas", size=11, weight="bold"), text_color="#884422", fg_color="transparent", width=25)
        self.timeout_label.pack(side=ctk.LEFT, padx=(0, 5))

        ctk.CTkLabel(settings_frame, text="Maks:", font=ctk.CTkFont(family="Consolas", size=10), text_color="#777777", fg_color="transparent").pack(side=ctk.LEFT, padx=(5, 3))
        ts3 = ctk.CTkSlider(settings_frame, from_=5, to=120, number_of_steps=23, variable=self.maxtime_value, fg_color="#222222", progress_color="#882222", button_color="#882222", button_hover_color="#993333", width=70, height=12, command=self.on_maxtime_change)
        ts3.pack(side=ctk.LEFT, padx=(1, 3))
        self.maxtime_label = ctk.CTkLabel(settings_frame, text="25s", font=ctk.CTkFont(family="Consolas", size=11, weight="bold"), text_color="#882222", fg_color="transparent", width=25)
        self.maxtime_label.pack(side=ctk.LEFT, padx=(0, 5))

        ctk.CTkLabel(
            settings_frame, text="https://cyberanka.com",
            font=ctk.CTkFont(family="Consolas", size=9),
            text_color="#333333", fg_color="transparent"
        ).pack(side=ctk.RIGHT, padx=(0, 10))

        self._print_banner()
        self._print("", "dim")
        if not self.subfinder_available:
            self._print("HATA: subfinder bulunamadı!", "red")
            self._print("Kurulum: Üstteki KURULUM sekmesine tıklayın.", "yellow")
        else:
            self._print(f"[TAMAM] subfinder: {self.subfinder_path}", "green")
        self._print("", "dim")
        self._print("root@subflame:~$ Hedef alan adı girin ve ENTER tuşuna basın", "green")
        self._print("root@subflame:~$ Örnek: ornek.com | Çoklu: alan_adlari.txt", "dim")
        self._print("─" * 60, "dim")
        self.root.bind("<F11>", lambda e: self.toggle_fullscreen())

    def show_kurulum_rehberi(self):
        kurulum_win = ctk.CTkToplevel(self.root)
        kurulum_win.title("Kurulum Rehberi")
        kurulum_win.configure(fg_color="#0a0a0a")
        kurulum_win.geometry("700x480")
        kurulum_win.resizable(True, True)
        kurulum_win.transient(self.root)
        
        def set_icon():
            try:
                if hasattr(self, '_icon_ref'):
                    kurulum_win.wm_iconphoto(True, self._icon_ref)
                if sys.platform == "win32":
                    import tempfile
                    ico_path = os.path.join(tempfile.gettempdir(), "cyberanka_icon.ico")
                    if os.path.exists(ico_path):
                        kurulum_win.iconbitmap(ico_path)
            except Exception:
                pass
        self.root.after(100, set_icon)
        
        header_frame = ctk.CTkFrame(kurulum_win, fg_color="transparent")
        header_frame.pack(pady=(15, 5))
        
        if hasattr(self, 'logo_img_pil') and self.logo_img_pil:
            try:
                k_logo_pil = self.logo_img_pil.resize((40, 40), Image.LANCZOS)
                k_logo = ctk.CTkImage(light_image=k_logo_pil, dark_image=k_logo_pil, size=(40, 40))
                l_icon = ctk.CTkLabel(header_frame, text="", image=k_logo)
                l_icon.image = k_logo
                l_icon.pack(side=ctk.LEFT, padx=(0, 10))
            except Exception:
                pass

        ctk.CTkLabel(
            header_frame, text="subflame - Kurulum Rehberi",
            font=ctk.CTkFont(family="Consolas", size=16, weight="bold"),
            text_color="#ff6666", fg_color="transparent"
        ).pack(side=ctk.LEFT)
        
        ctk.CTkLabel(
            kurulum_win, text="Go ile subfinder kurulumu",
            font=ctk.CTkFont(family="Consolas", size=12),
            text_color="#aaaaaa", fg_color="transparent"
        ).pack(pady=(0, 10))

        metin_kutusu = ctk.CTkTextbox(
            kurulum_win,
            font=ctk.CTkFont(family="Consolas", size=12),
            fg_color="#0a0a0a", text_color="#ffffff",
            border_color="#661111", border_width=1,
            corner_radius=4
        )
        metin_kutusu.pack(fill=ctk.BOTH, expand=True, padx=15, pady=(0, 10))
        
        kurulum_metni = """# subfinder Kurulum Rehberi

## Linux / macOS
1. Go'yu kurun (https://go.dev/dl/)
2. Terminali açın ve şu komutu çalıştırın:

   go install -v github.com/projectdiscovery/subfinder/v2/cmd/subfinder@latest

3. $HOME/go/bin/subfinder yoluna eklendi.
   Eğer PATH'te değilse şunu ekleyin:
   export PATH=$PATH:$HOME/go/bin

## Windows
1. Go'yu kurun (https://go.dev/dl/)
2. CMD veya PowerShell'i yönetici olarak açın:

   go install -v github.com/projectdiscovery/subfinder/v2/cmd/subfinder@latest

3. %USERPROFILE%\\go\\bin\\subfinder.exe yoluna kurulur.

## Alternatif: Sistem Paket Yöneticisi
- Debian/Ubuntu: sudo apt install subfinder
- Arch Linux: yay -S subfinder
- macOS: brew install subfinder

## Doğrulama
subfinder -version

Not: Subfinder kurulu değilse, Windows'ta ⚙ SUBFINDER SEÇ
butonu ile manuel olarak exe dosyasını seçebilirsiniz."""

        metin_kutusu.insert("1.0", kurulum_metni)
        metin_kutusu.configure(state="disabled")

        def github_link():
            webbrowser.open("https://github.com/projectdiscovery/subfinder")
        
        ctk.CTkButton(
            kurulum_win, text="🔗 GitHub Sayfasını Aç",
            font=ctk.CTkFont(family="Consolas", size=11, weight="bold"),
            fg_color="#661111", hover_color="#882222",
            text_color="#ffffff", height=32, corner_radius=4,
            command=github_link
        ).pack(pady=(0, 15))

    def _place_cyber_text_bg(self, parent):
        try:
            font_size = 44
            handwriting_fonts = ["Segoe Script", "Comic Sans MS", "Bradley Hand ITC", "Lucida Handwriting", "Monotype Corsiva", "Palace Script MT"]
            chosen_font = "Segoe UI"
            for f in handwriting_fonts:
                try:
                    test_font = ImageFont.truetype(f, font_size)
                    chosen_font = f
                    break
                except Exception:
                    continue
            img = Image.new('RGBA', (500, 70), (0, 0, 0, 0))
            draw = ImageDraw.Draw(img)
            try:
                font = ImageFont.truetype(chosen_font, font_size)
            except Exception:
                font = ImageFont.load_default()
            draw.text((250, 35), "Cyber Anka", fill=(255, 102, 102, 12), font=font, anchor="mm")
            self.cyber_bg = ImageTk.PhotoImage(img)
            ctk.CTkLabel(parent, text="", image=self.cyber_bg, fg_color="transparent").place(relx=0.5, rely=0.88, anchor="center")
        except Exception:
            pass

    def _get_handwriting_font(self):
        fonts = ["Segoe Script", "Comic Sans MS", "Bradley Hand ITC", "Lucida Handwriting", "Monotype Corsiva", "Palace Script MT"]
        for f in fonts:
            try:
                from tkinter import font
                test = font.Font(family=f, size=10)
                available = test.actual()["family"]
                if available == f:
                    return f
            except Exception:
                continue
        return "Segoe UI"

    def _apply_split_layout(self):
        # Mevcut layout'ları temizle
        self.terminal.pack_forget()
        self.terminal.place_forget()
        self.progress.pack_forget()
        self.progress.place_forget()
        if hasattr(self, 'accordion_frame'):
            self.accordion_frame.pack_forget()
            self.accordion_frame.place_forget()

        # Place kullanarak kesin %40 üst - %60 alt oranlaması
        self.terminal.place(relx=0, rely=0, relwidth=1, relheight=0.40)
        self.progress.configure(height=4)
        self.progress.place(relx=0, rely=0.40, relwidth=1)
        if hasattr(self, 'accordion_frame'):
            self.accordion_frame.place(relx=0, rely=0.41, relwidth=1, relheight=0.59)
        self.accordion_visible = True

    def _restore_full_layout(self):
        if hasattr(self, 'accordion_frame'):
            self.accordion_frame.place_forget()
            self.accordion_frame.pack_forget()
        self.accordion_visible = False
        self.live_accordion_panels = {}
        self.terminal.place_forget()
        self.terminal.pack_forget()
        self.progress.place_forget()
        self.progress.pack_forget()
        self.terminal.configure(height=300)
        self.terminal.pack(fill=ctk.BOTH, expand=True)
        self.progress.pack(fill=ctk.X, padx=0, pady=0)

    def start_scan(self):
        target_input = self.entry.get().strip()
        if not target_input:
            self._print("HATA: Alan adı girilmedi!", "red")
            return
        if target_input.lower() in ("exit", "quit"):
            self.root.destroy()
            return
        if not self.subfinder_available:
            self._print("HATA: subfinder bulunamadı!", "red")
            return
        if self.current_operation != "bekliyor":
            self._print("UYARI: Zaten bir işlem devam ediyor!", "yellow")
            return

        if self.is_file_target(target_input):
            domains = self.read_domains_from_file(target_input)
            if not domains:
                self._print("HATA: Dosyada alan adı bulunamadı!", "red")
                return
            self._print(f"{len(domains)} alan adı yüklendi: {target_input}", "cyan")
            for d in domains[:5]: self._print(f"  - {d}", "dim")
            if len(domains) > 5: self._print(f"  ... ve {len(domains)-5} alan adı daha", "dim")
        else:
            domains = [target_input]

        tv = self.thread_count.get()
        tiv = self.timeout_value.get()
        mv = self.maxtime_value.get()

        self.scan_start_time = time.time()
        self.total_found = 0
        self.subdomains = []
        self.probe_results = []
        self.live_counter.configure(text="[ 0 ]")
        self.time_counter.configure(text="( 0.0s )")
        self.progress.set(0)
        self.filter_count_label.configure(text="[ 0 / 0 ]")
        self.operation_started("tarama")

        self.live_accordion_panels = {}
        if not hasattr(self, "accordion_frame"):
            self.accordion_frame = ctk.CTkScrollableFrame(self.content_area, fg_color="#000000", corner_radius=0)
        else:
            for widget in self.accordion_frame.winfo_children():
                widget.destroy()

        # Layout: Konsol %40 üst, Accordion %60 alt
        self._apply_split_layout()

        for kat in list(KATEGORILER.keys()) + ["DİĞER"]:
            panel = AccordionPanel(self.accordion_frame, kat, KATEGORI_RENKLERI.get(kat, "#ffffff"), [])
            panel.pack(fill="x", pady=2, padx=5)
            self.live_accordion_panels[kat] = panel

        self._print("+" + "-" * 58 + "+", "cyan")
        self._print(f"| HEDEF: {target_input}", "cyan")
        self._print(f"| BAŞLANGIÇ: {time.strftime('%H:%M:%S')}", "cyan")
        self._print(f"| ALAN ADI: {len(domains)} | İŞ PARÇACIĞI: {tv} | ZAMAN AŞIMI: {tiv}s | MAKS: {mv}s", "cyan")
        self._print("+" + "-" * 58 + "+", "cyan")
        self._print("subfinder çalıştırılıyor...", "yellow")
        self._print("", "dim")

        self.update_time_counter()
        t = threading.Thread(target=self._run_subfinder, args=(domains, tv, tiv, mv), daemon=True)
        t.start()

    def _run_subfinder(self, domains, threads, timeout, maxtime):
        total = len(domains)
        
        lock = threading.Lock()
        
        def flush_batch_main(batch):
            for cat, text in batch:
                self._live_accordion_add(cat, text)
            self.live_counter.configure(text=f"[ {self.total_found} ]")

        def scan_domain(idx, domain):
            if not self._check_continue():
                return
            self.root.after(0, self._print, f"[{idx+1}/{total}] Taranıyor: {domain}", "cyan")
            batch_queue = []
            last_flush = [time.time()]

            def flush():
                if batch_queue:
                    b = list(batch_queue)
                    batch_queue.clear()
                    self.root.after(0, flush_batch_main, b)

            try:
                cmd = [
                    self.subfinder_path, "-d", domain, "-silent", "-duc",
                    "-timeout", str(timeout), "-t", str(threads), "-max-time", str(maxtime),
                    "-r", "8.8.8.8,1.1.1.1,9.9.9.9,208.67.222.222"
                ]
                if sys.platform != "win32":
                    cmd = ["stdbuf", "-oL"] + cmd
                env = os.environ.copy()
                env["PYTHONUNBUFFERED"] = "1"
                si = None
                if sys.platform == "win32":
                    si = subprocess.STARTUPINFO()
                    si.dwFlags |= subprocess.STARTF_USESHOWWINDOW
                proc = subprocess.Popen(
                    cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                    text=True, bufsize=1, env=env, startupinfo=si,
                    preexec_fn=os.setsid if sys.platform != "win32" else None
                )
                with self._proc_lock:
                    self._active_proc = proc

                for line in iter(proc.stdout.readline, ""):
                    if not self._check_continue():
                        self._safe_kill_proc(proc)
                        return
                    line = line.strip()
                    if not line:
                        continue
                    url = f"https://{line}" if not line.startswith("http") else line
                    cat = kategori_bul(line)
                    with lock:
                        self.total_found += 1
                        self.subdomains.append({"url": url, "domain": line, "category": cat})
                    display = f"{line} [{cat}]"
                    batch_queue.append((cat, display))
                    if len(batch_queue) > 15 or time.time() - last_flush[0] > 0.3:
                        flush()
                        last_flush[0] = time.time()

                proc.stdout.close()
                proc.wait()
            except Exception as e:
                self.root.after(0, self._print, f"[{idx+1}/{total}] {domain} HATA: {str(e)[:50]}", "red")
            finally:
                with self._proc_lock:
                    if self._active_proc and self._active_proc.returncode is None:
                        self._safe_kill_proc(self._active_proc)
                    self._active_proc = None
            flush()
            self.root.after(0, self.progress.set, (idx + 1) / total)

        if total == 1:
            scan_domain(0, domains[0])
        else:
            parallel = min(total, 5) # Maksimum 5 paralel işlemle sınırlandırdık (hızlandırma/kilitlenmeme için)
            with concurrent.futures.ThreadPoolExecutor(max_workers=parallel) as ex:
                fts = [ex.submit(scan_domain, i, d) for i, d in enumerate(domains)]
                for ft in concurrent.futures.as_completed(fts):
                    if not self._check_continue():
                        ex.shutdown(wait=False, cancel_futures=True)
                        break

        if not self.stopped:
            elapsed = time.time() - self.scan_start_time
            self.root.after(0, self._scan_done, self.total_found, elapsed, domains)

    def _live_accordion_add(self, cat, text):
        if cat in self.live_accordion_panels:
            self.live_accordion_panels[cat].add_item(text)
        elif "DİĞER" in self.live_accordion_panels:
            self.live_accordion_panels["DİĞER"].add_item(text)

    def _scan_done(self, count, elapsed, domains):
        self.progress.set(1)
        self.filter_count_label.configure(text=f"[ {count} / {count} ]")
        self._print("+" + "-" * 58 + "+", "cyan")
        self._print(f"| TARAMA TAMAMLANDI! {count} alt alan adı bulundu", "cyan")
        self._print(f"| Süre: {self.format_duration(elapsed)}", "cyan")
        self._print("+" + "-" * 58 + "+", "cyan")
        if count > 0:
            self._print(f"Kullan: CANLI DOMAİN TARA | ARAMA/FİLTRE", "purple")
        self._print("─" * 60, "dim")
        self.operation_finished()

    def probe_subdomains(self):
        if not self.subdomains:
            self._print("Taranacak alt alan adı yok!", "yellow")
            return
        if self.current_operation != "bekliyor":
            self._print("UYARI: Zaten bir işlem devam ediyor!", "yellow")
            return
        self.probe_results = []
        self.operation_started("canlı_domain_tara")
        self.progress.set(0)

        self.live_accordion_panels = {}
        if not hasattr(self, "accordion_frame"):
            self.accordion_frame = ctk.CTkScrollableFrame(self.content_area, fg_color="#000000", corner_radius=0)
        else:
            for widget in self.accordion_frame.winfo_children():
                widget.destroy()

        self._apply_split_layout()

        for kat in list(KATEGORILER.keys()) + ["DİĞER"]:
            panel = AccordionPanel(self.accordion_frame, kat, KATEGORI_RENKLERI.get(kat, "#ffffff"), [])
            panel.pack(fill="x", pady=2, padx=5)
            self.live_accordion_panels[kat] = panel

        self._print("+" + "-" * 58 + "+", "cyan")
        self._print("| CANLILIK KONTROLÜ (BAĞLANTI)", "cyan")
        self._print("+" + "-" * 58 + "+", "cyan")

        total = len(self.subdomains)
        completed, live_count = [0], [0]

        def probe_single(item):
            url = item["url"]
            if not self._check_probe_continue():
                return
            domain = url.replace("https://", "").replace("http://", "").split("/")[0]
            cat = kategori_bul(domain)
            for use_ssl in [True, False]:
                if not self._check_probe_continue():
                    return
                port, protocol = (443, "HTTPS") if use_ssl else (80, "HTTP")
                # Fast DNS check and caching
                if domain not in self._dns_cache:
                    try:
                        self._dns_cache[domain] = socket.gethostbyname(domain)
                    except socket.gaierror:
                        self._dns_cache[domain] = None
                
                if not self._dns_cache[domain]:
                    continue # Atla, çözülemedi

                try:
                    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    sock.settimeout(1.5)
                    if not self._check_probe_continue():
                        sock.close()
                        return
                    try:
                        sock.connect((domain, port))
                    except Exception:
                        sock.close()
                        continue
                    if not self._check_probe_continue():
                        sock.close()
                        return
                    if use_ssl:
                        try:
                            ctx = ssl.create_default_context()
                            ctx.check_hostname = False
                            ctx.verify_mode = ssl.CERT_NONE
                            sock = ctx.wrap_socket(sock, server_hostname=domain)
                        except Exception:
                            sock.close()
                            continue
                    if not self._check_probe_continue():
                        sock.close()
                        return
                    sock.sendall(f"GET / HTTP/1.1\r\nHost: {domain}\r\nUser-Agent: Mozilla/5.0\r\nConnection: close\r\n\r\n".encode())
                    if not self._check_probe_continue():
                        sock.close()
                        return
                    sock.settimeout(1.5)
                    resp = b""
                    try:
                        while True:
                            c = sock.recv(4096)
                            if not c:
                                break
                            resp += c
                            if len(resp) > 16384 or b"</html>" in resp.lower():
                                break
                            if not self._check_probe_continue():
                                sock.close()
                                return
                    except socket.timeout:
                        pass
                    except Exception:
                        sock.close()
                        continue
                    sock.close()
                    if not self._check_probe_continue():
                        return
                    try:
                        rt = resp.decode('utf-8', errors='replace')
                        sc = 0
                        m = re.search(r'HTTP/\d\.\d\s+(\d+)', rt)
                        if m:
                            sc = int(m.group(1))
                    except Exception:
                        sc = 0
                    sv = "?"
                    m = re.search(r'Server:\s*(.+?)\r\n', rt, re.I)
                    if m:
                        sv = m.group(1).strip()
                    ti = "?"
                    m = re.search(r'<title>(.*?)</title>', rt, re.I | re.DOTALL)
                    if m:
                        ti = m.group(1).strip()[:60]
                    live_count[0] += 1
                    status = "AKTİF" if sc in [200, 301, 302, 307, 308, 401, 403] else "PASİF"
                    if status == "PASİF":
                        return

                    self.probe_results.append({
                        "domain": domain, "port": port, "protocol": protocol,
                        "status_code": sc, "server": sv, "title": ti, "status": status,
                        "category": cat
                    })

                    probe_display = f"[{sc}][{protocol}] {domain} | {sv} | {ti}"
                    self.root.after(0, lambda d=probe_display, ct=cat: self._live_accordion_add(ct, d))
                    return
                except Exception:
                    if not self._check_probe_continue():
                        return
                    continue
            if not self._check_probe_continue():
                return
            # PASIFLERI YUKSAYIYORUZ (Ne arayüze ne de excel listesine ekliyoruz)

        def worker():
            mt = min(self.thread_count.get(), total)
            mt = max(5, mt)
            
            with concurrent.futures.ThreadPoolExecutor(max_workers=mt) as executor:
                futures = []
                for item in self.subdomains:
                    if self._probe_stop.is_set():
                        break
                    futures.append(executor.submit(probe_single, item))
                
                for future in concurrent.futures.as_completed(futures):
                    if self._probe_stop.is_set() or self.stopped:
                        executor.shutdown(wait=False, cancel_futures=True)
                        break
                    completed[0] += 1
                    if completed[0] % max(1, total // 100) == 0 or completed[0] == total:
                        self.root.after(0, self.progress.set, min(completed[0] / total, 1.0))

            if not self._probe_stop.is_set() and not self.stopped:
                self.root.after(0, self.progress.set, 1.0)
                self.root.after(0, self._print, f"Aktif: {live_count[0]} | Toplam Tarama: {total}", "green")
                self.root.after(0, self._print, "Canlı domain taraması tamamlandı.", "green")
                self.root.after(0, self._print, f"Sonuçlar kaydedildi. ({len(self.probe_results)} kayıt)", "purple")
                self.root.after(0, self._print, "Kullan: CANLI DOMAİNLERİ KAYDET butonu ile dosyaya kaydedin.", "yellow")
                self.root.after(0, self._print, "─" * 60, "dim")
                self.root.after(0, lambda: self.btn_save_probe.configure(state=ctk.NORMAL))
            self.root.after(0, self.operation_finished)

        t = threading.Thread(target=worker, daemon=True)
        t.start()

    def save_probe_results(self):
        if not self.probe_results:
            self._print("Kaydedilecek sonuç yok! Önce CANLI DOMAİN TARA çalıştırın.", "yellow")
            return
        fp = filedialog.asksaveasfilename(
            defaultextension=".xls",
            filetypes=[("Excel Dosyaları","*.xls"), ("Metin Dosyası", "*.txt")],
            initialfile=f"cyberanka_subflame_probe_{time.strftime('%Y%m%d_%H%M%S')}"
        )
        if not fp:
            return
        try:
            up_count = sum(1 for r in self.probe_results if r["status"] == "AKTİF")
            down_count = sum(1 for r in self.probe_results if r["status"] == "PASİF")

            if fp.endswith(".txt"):
                with open(fp, "w", encoding="utf-8") as f:
                    for r in self.probe_results:
                        f.write(r['domain'] + "\n")
                self._print(f"Canlı domain sonuçları TXT olarak kaydedildi: {fp}", "green")
                self._print(f"  AKTİF: {up_count} | PASİF: {down_count} | Toplam: {len(self.probe_results)}", "cyan")
            else:
                if not fp.endswith(".xls"):
                    fp += ".xls"
                workbook = xlsxwriter.Workbook(fp)
                worksheet = workbook.add_worksheet("Tarama Sonuçları")

                header_fmt = workbook.add_format({
                    'bold': True, 'bg_color': '#661111', 'font_color': '#ffffff',
                    'border': 1, 'align': 'center', 'valign': 'vcenter',
                    'font_size': 11
                })
                data_fmt = workbook.add_format({
                    'border': 1, 'align': 'left', 'valign': 'vcenter',
                    'font_size': 10, 'text_wrap': True
                })
                up_fmt = workbook.add_format({
                    'border': 1, 'align': 'left', 'valign': 'vcenter',
                    'font_size': 10, 'bg_color': '#441111', 'font_color': '#ff8888'
                })
                down_fmt = workbook.add_format({
                    'border': 1, 'align': 'left', 'valign': 'vcenter',
                    'font_size': 10, 'bg_color': '#1a0a0a', 'font_color': '#ff6666'
                })
                info_fmt = workbook.add_format({
                    'bold': True, 'font_size': 12, 'font_color': '#ff6666'
                })

                worksheet.merge_range('A1:G1', f'CyberAnka Tarama Sonuçları - {time.strftime("%Y-%m-%d %H:%M:%S")}', info_fmt)
                worksheet.merge_range('A2:G2', f'Toplam: {len(self.probe_results)} | AKTİF: {up_count} | PASİF: {down_count}', info_fmt)

                headers = ['Alan Adı', 'Kategori', 'Port', 'Protokol', 'Kod', 'Sunucu', 'Başlık']
                for col, h in enumerate(headers):
                    worksheet.write(3, col, h, header_fmt)

                for row_idx, r in enumerate(self.probe_results):
                    row = row_idx + 4
                    fmt = up_fmt if r["status"] == "AKTİF" else down_fmt
                    worksheet.write(row, 0, r['domain'], fmt)
                    worksheet.write(row, 1, r.get('category', 'DİĞER'), fmt)
                    worksheet.write(row, 2, r['port'], fmt)
                    worksheet.write(row, 3, r['protocol'], fmt)
                    worksheet.write(row, 4, r['status_code'], fmt)
                    worksheet.write(row, 5, r['server'], fmt)
                    worksheet.write(row, 6, r['title'], fmt)

                worksheet.set_column('A:A', 35)
                worksheet.set_column('B:B', 25)
                worksheet.set_column('C:C', 8)
                worksheet.set_column('D:D', 8)
                worksheet.set_column('E:E', 8)
                worksheet.set_column('F:F', 22)
                worksheet.set_column('G:G', 45)

                workbook.close()

                self._print(f"Canlı domain sonuçları Excel olarak kaydedildi: {fp}", "green")
                self._print(f"  AKTİF: {up_count} | PASİF: {down_count} | Toplam: {len(self.probe_results)}", "cyan")
        except Exception as e:
            self._print(f"KAYIT HATASI: {e}", "red")

    def save_results(self):
        if not self.subdomains:
            self._print("Kaydedilecek alan adı yok!", "red")
            return
            
        veri = []
        if hasattr(self, "current_filtered_results") and hasattr(self, "accordion_frame") and self.accordion_frame.winfo_ismapped():
            for cat, items in self.current_filtered_results.items():
                for item in items:
                    domain = item.split(' ')[0]
                    veri.append({"domain": domain, "category": cat, "full_text": item})
        else:
            for item in self.subdomains:
                veri.append({"domain": item["domain"], "category": item["category"], "full_text": item["domain"]})
                
        if not veri:
            self._print("Kaydedilecek uygun veri bulunamadı!", "red")
            return

        fp = filedialog.asksaveasfilename(
            defaultextension=".xls",
            filetypes=[("Excel Dosyaları","*.xls"), ("Metin Dosyası", "*.txt")],
            initialfile=f"cyberanka_subflame_{time.strftime('%Y%m%d_%H%M%S')}"
        )
        if not fp:
            return
            
        try:
            if fp.endswith(".txt"):
                with open(fp, "w", encoding="utf-8") as f:
                    for r in veri:
                        f.write(r['domain'] + "\n")
                self._print(f"TXT olarak kaydedildi: {fp}", "green")
                self._print(f"  Toplam: {len(veri)} alan adı", "cyan")
            else:
                if not fp.endswith(".xls"):
                    fp += ".xls"
                workbook = xlsxwriter.Workbook(fp)
                worksheet = workbook.add_worksheet("Alt Alan Adları")

                header_fmt = workbook.add_format({
                    'bold': True, 'bg_color': '#661111', 'font_color': '#ffffff',
                    'border': 1, 'align': 'center', 'valign': 'vcenter',
                    'font_size': 11
                })
                data_fmt = workbook.add_format({
                    'border': 1, 'align': 'left', 'valign': 'vcenter',
                    'font_size': 10
                })
                info_fmt = workbook.add_format({
                    'bold': True, 'font_size': 12, 'font_color': '#ff6666'
                })

                worksheet.merge_range('A1:C1', f'CyberAnka - {time.strftime("%Y-%m-%d %H:%M:%S")}', info_fmt)
                worksheet.merge_range('A2:C2', f'Toplam Kayıt: {len(veri)}', info_fmt)

                worksheet.write(3, 0, 'Alan Adı', header_fmt)
                worksheet.write(3, 1, 'Kategori', header_fmt)
                worksheet.write(3, 2, 'Detay', header_fmt)

                for row_idx, r in enumerate(veri):
                    worksheet.write(row_idx + 4, 0, r['domain'], data_fmt)
                    worksheet.write(row_idx + 4, 1, r['category'], data_fmt)
                    worksheet.write(row_idx + 4, 2, r['full_text'], data_fmt)

                worksheet.set_column('A:A', 40)
                worksheet.set_column('B:B', 25)
                worksheet.set_column('C:C', 60)

                workbook.close()

                self._print(f"Excel olarak kaydedildi: {fp}", "green")
                self._print(f"  Toplam: {len(veri)} alan adı", "cyan")
        except Exception as e:
            self._print(f"KAYIT HATASI: {e}", "red")

    def on_thread_change(self, v):
        val = int(v)
        self.thread_count.set(val)
        self.thread_label.configure(text=str(val))

    def on_timeout_change(self, v):
        val = int(v)
        self.timeout_value.set(val)
        self.timeout_label.configure(text=f"{val}s")

    def on_maxtime_change(self, v):
        val = int(v)
        self.maxtime_value.set(val)
        self.maxtime_label.configure(text=f"{val}s")

    def _match_query(self, domain, cat, queries):
        domain_lower = domain.lower()
        cat_lower = cat.lower()
        for q in queries:
            q = q.strip()
            if not q:
                continue
            if q in domain_lower or q in cat_lower:
                return True
            for p_item in self.probe_results:
                if p_item["domain"] == domain:
                    if q == str(p_item["port"]) or q in str(p_item["status_code"]) or q in str(p_item["title"]).lower() or q in str(p_item["server"]).lower():
                        return True
        return False

    def on_filter_search(self, event=None):
        raw = self.filter_entry.get().strip().lower()
        if not self.subdomains:
            self._print("Önce tarama yapın!", "yellow")
            return

        queries = [q.strip() for q in raw.split(",") if q.strip()]

        self.live_accordion_panels = {}
        if not hasattr(self, "accordion_frame"):
            self.accordion_frame = ctk.CTkScrollableFrame(self.content_area, fg_color="#000000", corner_radius=0)
        else:
            for widget in self.accordion_frame.winfo_children():
                widget.destroy()

        self._apply_split_layout()

        kategori_sonuclari = {k: [] for k in KATEGORILER.keys()}
        kategori_sonuclari["DİĞER"] = []

        for item in self.subdomains:
            domain = item["domain"]
            cat = item["category"]

            if queries:
                if not self._match_query(domain, cat, queries):
                    continue

            display_text = f"{domain} [{cat}]"
            ek_bilgi = []
            for p_item in self.probe_results:
                if p_item["domain"] == domain:
                    ek_bilgi.append(f"Kod: {p_item['status_code']} | Port: {p_item['port']} | Sunucu: {p_item['server']} | {p_item['title']}")
            if ek_bilgi:
                display_text += " -> " + " | ".join(ek_bilgi)
            kategori_sonuclari[cat].append(display_text)

        total_matches = sum(len(lst) for lst in kategori_sonuclari.values())
        self.filter_count_label.configure(text=f"[ {total_matches} / {len(self.subdomains)} ]")

        self.current_filtered_results = kategori_sonuclari

        if total_matches == 0:
            lbl = ctk.CTkLabel(self.accordion_frame, text="Eşleşme bulunamadı.", text_color="yellow", font=ctk.CTkFont(family="Consolas", size=14))
            lbl.pack(pady=20)
        else:
            for cat, items in kategori_sonuclari.items():
                if items:
                    AccordionPanel(self.accordion_frame, cat, KATEGORI_RENKLERI.get(cat, "#ffffff"), items).pack(fill="x", pady=5, padx=5)

    def on_filter_clear(self):
        self.filter_entry.delete(0, ctk.END)
        if not self.subdomains:
            self._restore_full_layout()
            return
        self.on_filter_search()

    def set_thread_preset(self, v):
        self.thread_count.set(v)
        self.thread_label.configure(text=str(v))

    def toggle_fullscreen(self):
        c = self.root.attributes("-fullscreen")
        self.root.attributes("-fullscreen", not c)

    def _print_banner(self):
        self._print("subflame", "cyan")

    def _print(self, msg, tag="green"):
        self.terminal.insert(ctk.END, msg + "\n", tag)
        self.terminal.see(ctk.END)

    def format_duration(self, seconds):
        if seconds >= 60:
            m = int(seconds // 60)
            s = int(seconds % 60)
            return f"{m}dk {s:02d}s"
        return f"{seconds:.1f}s"

    def update_time_counter(self):
        if hasattr(self, '_time_job') and self._time_job:
            self.root.after_cancel(self._time_job)
            self._time_job = None

        if self.current_operation != "bekliyor" and self.scan_start_time > 0:
            elapsed = time.time() - self.scan_start_time
            self.time_counter.configure(text=f"( {self.format_duration(elapsed)} )")
            self._time_job = self.root.after(100, self.update_time_counter)

    def is_file_target(self, t):
        return os.path.isfile(t)

    def read_domains_from_file(self, fp):
        domains = []
        try:
            with open(fp, "r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith("#"):
                        d = re.sub(r'^https?://', '', line).split('/')[0].strip()
                        if d:
                            domains.append(d)
        except Exception as e:
            self._print(f"DOSYA HATASI: {e}", "red")
            return None
        return domains

    def copy_results(self):
        if self.subdomains:
            lines = [u["domain"] for u in self.subdomains]
            self.root.clipboard_clear()
            self.root.clipboard_append("\n".join(lines))
            self._print(f"{len(lines)} alan adı panoya kopyalandı!", "green")
        else:
            self._print("Kopyalanacak alan adı yok!", "red")

    def clear_terminal(self):
        if self.current_operation != "bekliyor":
            self.stop_operation()
            time.sleep(0.3)

        self._restore_full_layout()

        self.terminal.delete("1.0", ctk.END)
        self.subdomains = []
        self.total_found = 0
        self.probe_results = []
        self.scan_start_time = 0
        self.paused = False
        self.stopped = False
        self.pause_event.set()
        self._probe_stop.set()
        self._probe_pause.set()
        self.current_operation = "bekliyor"
        self.live_counter.configure(text="[ 0 ]")
        self.time_counter.configure(text="( 0.0s )")
        self.progress.set(0)
        self.filter_count_label.configure(text="[ 0 / 0 ]")
        self.btn_pause.configure(state=ctk.DISABLED, text="⏸ DURAKLAT")
        self.btn_stop.configure(state=ctk.DISABLED)
        self.operation_finished()
        self._print_banner()
        self._print("root@subflame:~$ Hedef alan adı girin ve ENTER tuşuna basın", "green")
        self._print("root@subflame:~$ Örnek: ornek.com", "dim")
        self._print("─" * 60, "dim")

    def select_subfinder(self):
        fp = filedialog.askopenfilename(
            title="Subfinder Aracını Seçin",
            filetypes=[("Executable", "*.exe"), ("All Files", "*.*")]
        )
        if fp:
            self.subfinder_path = fp
            self.subfinder_available = True
            self._print(f"Subfinder yolu güncellendi: {fp}", "green")

    def operation_started(self, op):
        self.current_operation = op
        self.stopped = False
        self.paused = False
        self._probe_stop.clear()
        self.pause_event.set()
        self.status_label.configure(text=f"[ {op.upper()} ]")
        self.btn_scan.configure(state=ctk.DISABLED)
        self.btn_pause.configure(state=ctk.NORMAL, text="⏸ DURAKLAT")
        self.btn_stop.configure(state=ctk.NORMAL)
        self.btn_probe.configure(state=ctk.DISABLED)
        self.btn_copy.configure(state=ctk.DISABLED)
        self.btn_save.configure(state=ctk.DISABLED)
        self.btn_save_probe.configure(state=ctk.DISABLED)

    def operation_finished(self):
        self.current_operation = "bekliyor"
        self.paused = False
        self.stopped = False
        self.status_label.configure(text="[ HAZIR ]")
        self.btn_scan.configure(state=ctk.NORMAL)
        self.btn_pause.configure(state=ctk.DISABLED, text="⏸ DURAKLAT")
        self.btn_stop.configure(state=ctk.DISABLED)
        if self.subdomains:
            self.btn_probe.configure(state=ctk.NORMAL)
            self.btn_copy.configure(state=ctk.NORMAL)
            self.btn_save.configure(state=ctk.NORMAL)
        if self.probe_results:
            self.btn_save_probe.configure(state=ctk.NORMAL)

    def toggle_pause(self):
        if self.stopped:
            return
        if self.paused:
            self.paused = False
            self.pause_event.set()
            self._probe_pause.set()
            self.btn_pause.configure(text="⏸ DURAKLAT")
            self.status_label.configure(text=f"[ {self.current_operation.upper()} ]")
        else:
            self.paused = True
            self.pause_event.clear()
            self._probe_pause.clear()
            self.btn_pause.configure(text="▶ DEVAM ET")
            self.status_label.configure(text="[ DURAKLATILDI ]")

    def stop_operation(self):
        self.stopped = True
        self.pause_event.set()
        self._probe_stop.set()
        self._probe_pause.set()
        self.status_label.configure(text="[ DURDURULDU ]")
        with self._proc_lock:
            if self._active_proc:
                self._safe_kill_proc(self._active_proc)
                self._active_proc = None
        self._print("İşlem durduruldu!", "red")
        self.operation_finished()

    def _check_continue(self):
        if self.stopped:
            return False
        self.pause_event.wait()
        return not self.stopped

    def _check_probe_continue(self):
        if self._probe_stop.is_set() or self.stopped:
            return False
        self._probe_pause.wait()
        return not self._probe_stop.is_set() and not self.stopped

    def run(self):
        self.root.after(500, self.do_countdown)
        self.root.update_idletasks()
        self.root.mainloop()

if __name__ == "__main__":
    app = CyberAnkaTerminal()
    app.run()
