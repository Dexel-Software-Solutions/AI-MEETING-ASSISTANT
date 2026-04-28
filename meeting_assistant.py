"""
╔══════════════════════════════════════════════════════════════════╗
║       AI MEETING ASSISTANT — Compact Overlay Edition             ║
║              Developer: Demiyan Dissanayake                      ║
║         Perplexity-style floating notification widget            ║
╚══════════════════════════════════════════════════════════════════╝

INSTALL:
  pip install SpeechRecognition pyaudio requests

SYSTEM AUDIO (Windows):
  Control Panel → Sound → Recording → Enable "Stereo Mix"
  Then select "Stereo Mix" in Settings → Audio Device
"""

import tkinter as tk
from tkinter import ttk
import threading, time, json, os, queue, datetime, math, requests
import speech_recognition as sr
from typing import Optional

# ── CONFIG ────────────────────────────────────────────────────────
CFG = {
    "API_KEY":         "",                   # ← Your OpenRouter key
    "MODEL":           "openai/gpt-4o",
    "MAX_TOKENS":      900,
    "PAUSE_THRESHOLD": 1.2,
    "ENERGY":          300,
    "DEVELOPER":       "Demiyan Dissanayake",
    "VERSION":         "3.0",
}

SYSTEM_PROMPT = """You are a brilliant academic AI helping an undergrad student in an online meeting.
Answer every question like a professor would — clear, authoritative, structured.
Format: 1-3 short paragraphs. Lead with the core answer. Be concise but complete.
If the input is NOT a question, reply only with: [SKIP]"""

# ── COLORS ───────────────────────────────────────────────────────
C = {
    "bg":       "#0E0F13",
    "surface":  "#17191F",
    "surface2": "#1E2028",
    "border":   "#2A2D38",
    "accent":   "#4F8EF7",
    "accent2":  "#7C5CFC",
    "green":    "#22C55E",
    "amber":    "#F59E0B",
    "red":      "#EF4444",
    "txt":      "#E8ECFF",
    "txt2":     "#7A8099",
    "txt3":     "#454960",
}

# ── OPENROUTER ───────────────────────────────────────────────────
class AI:
    def __init__(self, key):
        self.key = key
        self.url = "https://openrouter.ai/api/v1/chat/completions"
        self.headers = {
            "Authorization": f"Bearer {key}",
            "Content-Type":  "application/json",
            "HTTP-Referer":  "https://meeting-assistant.local",
            "X-Title":       "AI Meeting Assistant",
        }

    def ask(self, question: str, history: list, on_chunk) -> str:
        msgs = [{"role": "system", "content": SYSTEM_PROMPT}]
        for h in history[-6:]:
            msgs += [{"role": "user",      "content": h["q"]},
                     {"role": "assistant", "content": h["a"]}]
        msgs.append({"role": "user", "content": question})
        payload = {
            "model":       CFG["MODEL"],
            "messages":    msgs,
            "max_tokens":  CFG["MAX_TOKENS"],
            "temperature": 0.65,
            "stream":      True,
        }
        full = ""
        try:
            with requests.post(self.url, headers=self.headers,
                               json=payload, stream=True, timeout=25) as r:
                r.raise_for_status()
                for line in r.iter_lines():
                    if not line:
                        continue
                    line = line.decode()
                    if line.startswith("data: "):
                        s = line[6:]
                        if s == "[DONE]":
                            break
                        try:
                            d     = json.loads(s)
                            chunk = d["choices"][0]["delta"].get("content", "")
                            if chunk:
                                full += chunk
                                on_chunk(chunk)
                        except Exception:
                            pass
        except requests.exceptions.ConnectionError:
            msg = "⚠ No internet connection."
            on_chunk(msg)
            return msg
        except requests.exceptions.HTTPError as e:
            msg = f"⚠ API error ({e.response.status_code})"
            on_chunk(msg)
            return msg
        except Exception as e:
            msg = f"⚠ {str(e)[:60]}"
            on_chunk(msg)
            return msg
        return full


# ── AUDIO ENGINE ─────────────────────────────────────────────────
class AudioEngine:
    def __init__(self, on_text, on_status):
        self.on_text   = on_text
        self.on_status = on_status
        self.r = sr.Recognizer()
        self.r.energy_threshold = CFG["ENERGY"]
        self.r.pause_threshold  = CFG["PAUSE_THRESHOLD"]
        self.running   = False
        self._dev_idx  = None

    def start(self, device_index=None):
        self._dev_idx = device_index
        self.running  = True
        threading.Thread(target=self._loop, daemon=True).start()

    def stop(self):
        self.running = False

    def _loop(self):
        try:
            mic = sr.Microphone(device_index=self._dev_idx)
        except Exception as e:
            self.on_status("err", f"Mic error: {e}")
            return

        self.on_status("cal", "Calibrating...")
        with mic as src:
            try:
                self.r.adjust_for_ambient_noise(src, duration=1.5)
            except Exception:
                pass

        self.on_status("ok", "Listening")
        while self.running:
            try:
                with mic as src:
                    audio = self.r.listen(src, timeout=4, phrase_time_limit=14)
                self.on_status("rec", "Recognizing...")
                try:
                    text = self.r.recognize_google(audio, language="en-US")
                    if text.strip():
                        self.on_text(text.strip())
                except sr.UnknownValueError:
                    self.on_status("ok", "Listening")
                except sr.RequestError as e:
                    self.on_status("err", f"Speech API: {e}")
                    time.sleep(2)
            except sr.WaitTimeoutError:
                self.on_status("ok", "Listening")
            except Exception as e:
                if self.running:
                    self.on_status("err", str(e)[:40])
                    time.sleep(1)


# ── MAIN APP ─────────────────────────────────────────────────────
class App:
    W_COMPACT  = 340
    W_EXPANDED = 380
    H_COMPACT  = 52
    H_EXPANDED = 460

    def __init__(self):
        self.root = tk.Tk()
        self.root.overrideredirect(True)
        self.root.attributes("-topmost", True)
        self.root.attributes("-alpha", 0.97)
        self.root.configure(bg=C["bg"])

        # State
        self.q         = queue.Queue()
        self.ai        = None
        self.audio     = None
        self.history   = []
        self.listening = False
        self.streaming = False
        self.full_resp = ""
        self.expanded  = False
        self._phase    = 0.0
        self._drag_x   = 0
        self._drag_y   = 0

        self.api_key   = tk.StringVar()
        self.model_var = tk.StringVar(value=CFG["MODEL"])
        self.dev_var   = tk.StringVar(value="Default")

        self._load_cfg()
        self._set_pos(self.W_COMPACT, self.H_COMPACT)
        self._build()
        self._bind_keys()
        self._tick()
        self._pulse_tick()

    # ── GEOMETRY ─────────────────────────────
    def _set_pos(self, w, h):
        sw = self.root.winfo_screenwidth()
        self.root.geometry(f"{w}x{h}+{sw - w - 16}+16")

    def _expand(self):
        if self.expanded:
            return
        self.expanded = True
        self._set_pos(self.W_EXPANDED, self.H_EXPANDED)
        self.resp_frame.pack(fill=tk.BOTH, expand=True)
        self.foot_frame.pack(fill=tk.X)

    def _collapse(self):
        if not self.expanded:
            return
        self.expanded = False
        self.resp_frame.pack_forget()
        self.foot_frame.pack_forget()
        self._set_pos(self.W_COMPACT, self.H_COMPACT)

    # ── BUILD ────────────────────────────────
    def _build(self):
        self.outer = tk.Frame(self.root, bg=C["accent2"], padx=1, pady=1)
        self.outer.pack(fill=tk.BOTH, expand=True)

        self.inner = tk.Frame(self.outer, bg=C["bg"])
        self.inner.pack(fill=tk.BOTH, expand=True)

        self._build_topbar()
        self._build_response()
        self._build_footer()

    def _build_topbar(self):
        bar = tk.Frame(self.inner, bg=C["surface"], height=52)
        bar.pack(fill=tk.X)
        bar.pack_propagate(False)

        for w in [bar]:
            w.bind("<ButtonPress-1>", self._drag_start)
            w.bind("<B1-Motion>",     self._drag_move)

        # Pulse
        left = tk.Frame(bar, bg=C["surface"])
        left.pack(side=tk.LEFT, padx=10, fill=tk.Y)
        left.bind("<ButtonPress-1>", self._drag_start)
        left.bind("<B1-Motion>",     self._drag_move)

        self.pulse_c = tk.Canvas(left, width=28, height=28,
                                 bg=C["surface"], highlightthickness=0)
        self.pulse_c.pack(side=tk.LEFT, pady=12)

        lf = tk.Frame(left, bg=C["surface"])
        lf.pack(side=tk.LEFT, padx=(6, 0))
        lf.bind("<ButtonPress-1>", self._drag_start)
        lf.bind("<B1-Motion>",     self._drag_move)

        self.title_lbl = tk.Label(lf, text="AI Assistant",
                                   font=("Helvetica", 11, "bold"),
                                   fg=C["txt"], bg=C["surface"])
        self.title_lbl.pack(anchor="w")
        self.title_lbl.bind("<ButtonPress-1>", self._drag_start)
        self.title_lbl.bind("<B1-Motion>",     self._drag_move)

        self.sub_lbl = tk.Label(lf, text="Ready  ·  F2 to start",
                                 font=("Helvetica", 8), fg=C["txt3"],
                                 bg=C["surface"])
        self.sub_lbl.pack(anchor="w")
        self.sub_lbl.bind("<ButtonPress-1>", self._drag_start)
        self.sub_lbl.bind("<B1-Motion>",     self._drag_move)

        # Right controls
        right = tk.Frame(bar, bg=C["surface"])
        right.pack(side=tk.RIGHT, padx=8)

        self.listen_btn = self._pill(right, "▶", C["accent"], self._toggle_listen)
        self.listen_btn.pack(side=tk.LEFT, padx=2)
        self._pill(right, "⚙", C["surface2"], self._open_settings).pack(side=tk.LEFT, padx=2)
        self._pill(right, "✕", C["surface2"], self.root.destroy, hover=C["red"]).pack(side=tk.LEFT, padx=2)

    def _build_response(self):
        self.resp_frame = tk.Frame(self.inner, bg=C["bg"])
        # packed on demand

        tk.Frame(self.resp_frame, bg=C["border"], height=1).pack(fill=tk.X)

        # Question bar
        qb = tk.Frame(self.resp_frame, bg=C["surface"], pady=6)
        qb.pack(fill=tk.X)
        tk.Label(qb, text="Q", font=("Helvetica", 8, "bold"),
                 fg=C["accent"], bg=C["surface"], width=2).pack(side=tk.LEFT, padx=(10, 4))
        self.q_lbl = tk.Label(qb, text="Waiting for question...",
                               font=("Helvetica", 9), fg=C["txt2"],
                               bg=C["surface"], anchor="w",
                               wraplength=290, justify=tk.LEFT)
        self.q_lbl.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 8))

        # Text area
        tf = tk.Frame(self.resp_frame, bg=C["bg"], pady=4)
        tf.pack(fill=tk.BOTH, expand=True, padx=10)

        self.resp_text = tk.Text(
            tf, wrap=tk.WORD, bg=C["bg"], fg=C["txt"],
            font=("Georgia", 10), relief=tk.FLAT,
            selectbackground=C["accent"],
            insertbackground=C["accent"],
            padx=4, pady=6,
            spacing1=3, spacing3=3,
            cursor="arrow",
        )
        self.resp_text.pack(fill=tk.BOTH, expand=True)
        self.resp_text.config(state=tk.DISABLED)

        self.resp_text.tag_config("stream", foreground=C["amber"])
        self.resp_text.tag_config("done",   foreground=C["txt"])
        self.resp_text.tag_config("dim",    foreground=C["txt3"])
        self.resp_text.tag_config("cursor", foreground=C["accent"])

    def _build_footer(self):
        self.foot_frame = tk.Frame(self.inner, bg=C["surface"], height=38)
        self.foot_frame.pack_propagate(False)
        # packed on demand

        tk.Frame(self.foot_frame, bg=C["border"], height=1).pack(fill=tk.X)
        ff = tk.Frame(self.foot_frame, bg=C["surface"])
        ff.pack(fill=tk.X, padx=10, pady=5)

        self.manual = tk.Entry(ff, bg=C["surface2"], fg=C["txt3"],
                               insertbackground=C["accent"], relief=tk.FLAT,
                               font=("Helvetica", 9), width=22)
        self.manual.pack(side=tk.LEFT, fill=tk.X, expand=True, ipady=4, padx=(0, 6))
        self.manual.insert(0, "Type a question...")
        self.manual.bind("<FocusIn>",  lambda e: self._ph_clear())
        self.manual.bind("<FocusOut>", lambda e: self._ph_restore())
        self.manual.bind("<Return>",   lambda e: self._submit_manual())

        self._pill(ff, "↵ Ask", C["accent"],   self._submit_manual, small=True).pack(side=tk.LEFT)
        self._pill(ff, "⎘",     C["surface2"], self._copy,    small=True).pack(side=tk.LEFT, padx=(4, 0))
        self._pill(ff, "↙",     C["surface2"], self._collapse, small=True).pack(side=tk.LEFT, padx=(4, 0))

    # ── WIDGETS ──────────────────────────────
    def _pill(self, parent, text, bg, cmd, hover=None, small=False):
        f  = ("Helvetica", 8) if small else ("Helvetica", 9, "bold")
        px = 7 if small else 9
        py = 2 if small else 3
        b  = tk.Label(parent, text=text, bg=bg, fg=C["txt"],
                      font=f, cursor="hand2", padx=px, pady=py)
        hc = hover or self._dk(bg)
        b.bind("<Button-1>", lambda e: cmd())
        b.bind("<Enter>",    lambda e: b.config(bg=hc))
        b.bind("<Leave>",    lambda e: b.config(bg=bg))
        return b

    def _dk(self, h):
        try:
            r = max(0, int(h[1:3], 16) - 30)
            g = max(0, int(h[3:5], 16) - 30)
            b = max(0, int(h[5:7], 16) - 30)
            return f"#{r:02x}{g:02x}{b:02x}"
        except Exception:
            return h

    # ── DRAG ─────────────────────────────────
    def _drag_start(self, e):
        self._drag_x = e.x_root - self.root.winfo_x()
        self._drag_y = e.y_root - self.root.winfo_y()

    def _drag_move(self, e):
        self.root.geometry(f"+{e.x_root - self._drag_x}+{e.y_root - self._drag_y}")

    # ── PULSE ────────────────────────────────
    def _pulse_tick(self):
        c  = self.pulse_c
        sz = 28
        c.delete("all")
        cx = cy = sz // 2

        if self.listening and not self.streaming:
            # Green ripple
            for i in range(3):
                p  = self._phase - i * 0.9
                s  = max(0.0, math.sin(p))
                r  = 5 + i * 5 * s
                op = int(s * 180)
                col = f"#{0:02x}{min(255,34+op):02x}{0:02x}"
                if r > 1:
                    c.create_oval(cx - r, cy - r, cx + r, cy + r,
                                  outline=C["green"], width=1)
            c.create_oval(cx-5, cy-5, cx+5, cy+5, fill=C["green"], outline="")
            self._phase += 0.12

        elif self.streaming:
            # Spinning arc
            angle = (self._phase * 220) % 360
            c.create_arc(4, 4, 24, 24, start=angle, extent=260,
                         outline=C["accent"], width=2, style=tk.ARC)
            c.create_oval(cx-3, cy-3, cx+3, cy+3, fill=C["accent2"], outline="")
            self._phase += 0.15

        else:
            c.create_oval(cx-4, cy-4, cx+4, cy+4, fill=C["txt3"], outline="")

        self.root.after(55, self._pulse_tick)

    # ── LISTEN ───────────────────────────────
    def _toggle_listen(self):
        if self.listening:
            self._stop()
        else:
            self._start()

    def _start(self):
        key = self.api_key.get().strip()
        if not key:
            self._expand()
            self._show_resp("⚙ Open Settings (⚙) and enter your OpenRouter API key.")
            return
        self.ai = AI(key)
        dev_idx = self._dev_index()
        self.audio = AudioEngine(
            on_text=lambda t: self.q.put(("speech", t)),
            on_status=lambda s, m: self.q.put(("status", s, m)),
        )
        self.audio.start(device_index=dev_idx)
        self.listening = True
        self.listen_btn.config(bg=C["red"], text="⏹")
        self._sub("Listening  ·  F2 to stop")

    def _stop(self):
        if self.audio:
            self.audio.stop()
            self.audio = None
        self.listening = False
        self.listen_btn.config(bg=C["accent"], text="▶")
        self._sub("Stopped  ·  F2 to start")

    def _dev_index(self):
        val = self.dev_var.get()
        if val.startswith("["):
            try:
                return int(val.split("]")[0].replace("[", ""))
            except Exception:
                pass
        return None

    # ── SPEECH ───────────────────────────────
    def _on_speech(self, text: str):
        self.q_lbl.config(text=text[:110], fg=C["txt2"])
        self._expand()
        self._begin_stream(text)
        threading.Thread(target=self._ask_ai, args=(text,), daemon=True).start()

    def _ask_ai(self, text: str):
        if not self.ai:
            return
        self.streaming = True
        answer = self.ai.ask(text, self.history,
                             on_chunk=lambda c: self.q.put(("chunk", c)))
        self.q.put(("done", text, answer))

    def _submit_manual(self):
        text = self.manual.get().strip()
        if not text or text == "Type a question...":
            return
        self.manual.delete(0, tk.END)
        self.q_lbl.config(text=text[:110], fg=C["txt2"])
        self._expand()
        self._begin_stream(text)
        key = self.api_key.get().strip()
        if not key:
            self._show_resp("⚙ Add API key in Settings first.")
            return
        if not self.ai:
            self.ai = AI(key)
        threading.Thread(target=self._ask_ai, args=(text,), daemon=True).start()

    # ── DISPLAY ──────────────────────────────
    def _begin_stream(self, _q):
        self.full_resp = ""
        self.streaming = True
        self.resp_text.config(state=tk.NORMAL)
        self.resp_text.delete("1.0", tk.END)
        self.resp_text.insert(tk.END, "▌", "cursor")
        self.resp_text.config(state=tk.DISABLED)
        self._sub("Thinking...")

    def _append_chunk(self, chunk: str):
        self.full_resp += chunk
        self.resp_text.config(state=tk.NORMAL)
        try:
            idx = self.resp_text.search("▌", "1.0", tk.END)
            if idx:
                self.resp_text.delete(idx, f"{idx}+1c")
        except Exception:
            pass
        self.resp_text.insert(tk.END, chunk, "stream")
        self.resp_text.insert(tk.END, "▌", "cursor")
        self.resp_text.see(tk.END)
        self.resp_text.config(state=tk.DISABLED)

    def _finish_stream(self, question: str, answer: str):
        self.streaming = False
        self.resp_text.config(state=tk.NORMAL)
        try:
            idx = self.resp_text.search("▌", "1.0", tk.END)
            if idx:
                self.resp_text.delete(idx, f"{idx}+1c")
        except Exception:
            pass
        self.resp_text.tag_remove("stream", "1.0", tk.END)
        self.resp_text.tag_add("done", "1.0", tk.END)
        self.resp_text.config(state=tk.DISABLED)

        if "[SKIP]" not in answer:
            self.history.append({"q": question, "a": answer})
            if len(self.history) > 20:
                self.history.pop(0)

        self._sub(f"Done  ·  {datetime.datetime.now().strftime('%H:%M')}")
        self._flash_border()

    def _show_resp(self, text: str):
        self.resp_text.config(state=tk.NORMAL)
        self.resp_text.delete("1.0", tk.END)
        self.resp_text.insert(tk.END, text, "dim")
        self.resp_text.config(state=tk.DISABLED)

    def _flash_border(self):
        seq = [C["green"], C["accent2"], C["border"], C["accent2"], C["border"]]
        def step(i=0):
            if i < len(seq):
                self.outer.config(bg=seq[i])
                self.root.after(110, lambda: step(i + 1))
        step()

    # ── QUEUE ────────────────────────────────
    def _tick(self):
        try:
            while True:
                item = self.q.get_nowait()
                cmd  = item[0]
                if cmd == "speech":
                    self._on_speech(item[1])
                elif cmd == "status":
                    icons = {"ok": "●", "rec": "◉", "cal": "◈", "err": "✕"}
                    self._sub(f"{icons.get(item[1], '·')} {item[2]}")
                elif cmd == "chunk":
                    if "[SKIP]" not in item[1]:
                        self._append_chunk(item[1])
                elif cmd == "done":
                    _, q, a = item
                    if "[SKIP]" in a:
                        self._show_resp("ℹ Not a question — still listening...")
                        self.streaming = False
                    else:
                        self._finish_stream(q, a)
        except queue.Empty:
            pass
        finally:
            self.root.after(40, self._tick)

    # ── HELPERS ──────────────────────────────
    def _sub(self, t: str):
        self.sub_lbl.config(text=t[:52])

    def _copy(self):
        self.root.clipboard_clear()
        self.root.clipboard_append(self.full_resp)
        self._sub("Copied ✓")
        self.root.after(2000, lambda: self._sub("Ready"))

    def _ph_clear(self):
        if self.manual.get() == "Type a question...":
            self.manual.delete(0, tk.END)
            self.manual.config(fg=C["txt"])

    def _ph_restore(self):
        if not self.manual.get():
            self.manual.insert(0, "Type a question...")
            self.manual.config(fg=C["txt3"])

    # ── SETTINGS ─────────────────────────────
    def _open_settings(self):
        win = tk.Toplevel(self.root)
        win.title("Settings")
        win.geometry("420x340")
        win.configure(bg=C["bg"])
        win.attributes("-topmost", True)
        win.overrideredirect(False)
        win.grab_set()

        hdr = tk.Frame(win, bg=C["surface"], pady=10)
        hdr.pack(fill=tk.X)
        tk.Label(hdr, text="⚙  Settings", font=("Helvetica", 12, "bold"),
                 fg=C["txt"], bg=C["surface"]).pack(side=tk.LEFT, padx=16)
        tk.Label(hdr, text=f"by {CFG['DEVELOPER']}",
                 font=("Helvetica", 8, "italic"),
                 fg=C["txt3"], bg=C["surface"]).pack(side=tk.RIGHT, padx=16)

        def field(lbl, var, show=None):
            f = tk.Frame(win, bg=C["bg"])
            f.pack(fill=tk.X, padx=16, pady=6)
            tk.Label(f, text=lbl, fg=C["txt2"], bg=C["bg"],
                     font=("Helvetica", 9), width=16, anchor="w").pack(side=tk.LEFT)
            kw = {"show": show} if show else {}
            e = tk.Entry(f, textvariable=var, bg=C["surface2"], fg=C["txt"],
                         insertbackground=C["accent"], relief=tk.FLAT,
                         font=("Helvetica", 10), **kw)
            e.pack(side=tk.LEFT, fill=tk.X, expand=True, ipady=5, padx=(8, 0))
            return e

        key_e = field("OpenRouter API Key", self.api_key, show="●")

        show_v = tk.BooleanVar()
        def toggle():
            key_e.config(show="" if show_v.get() else "●")
        tk.Checkbutton(win, text="Show key", variable=show_v, command=toggle,
                       fg=C["txt2"], bg=C["bg"], selectcolor=C["surface2"],
                       activebackground=C["bg"], font=("Helvetica", 9),
                       cursor="hand2").pack(anchor="e", padx=16)

        # Model
        mf = tk.Frame(win, bg=C["bg"])
        mf.pack(fill=tk.X, padx=16, pady=6)
        tk.Label(mf, text="Model", fg=C["txt2"], bg=C["bg"],
                 font=("Helvetica", 9), width=16, anchor="w").pack(side=tk.LEFT)
        models = ["openai/gpt-4o", "openai/gpt-4o-mini",
                  "anthropic/claude-3.5-sonnet", "anthropic/claude-3-haiku",
                  "google/gemini-pro", "mistralai/mixtral-8x7b-instruct"]
        ttk.Combobox(mf, textvariable=self.model_var, values=models,
                     font=("Helvetica", 9)).pack(side=tk.LEFT, fill=tk.X,
                                                  expand=True, padx=(8, 0))

        # Audio device
        af = tk.Frame(win, bg=C["bg"])
        af.pack(fill=tk.X, padx=16, pady=6)
        tk.Label(af, text="Audio Device", fg=C["txt2"], bg=C["bg"],
                 font=("Helvetica", 9), width=16, anchor="w").pack(side=tk.LEFT)
        try:
            devs = ["Default"] + [f"[{i}] {n}" for i, n
                                   in enumerate(sr.Microphone.list_microphone_names())]
        except Exception:
            devs = ["Default"]
        ttk.Combobox(af, textvariable=self.dev_var, values=devs,
                     font=("Helvetica", 9)).pack(side=tk.LEFT, fill=tk.X,
                                                  expand=True, padx=(8, 0))

        tk.Label(win,
                 text="💡 Windows: Enable 'Stereo Mix' in Sound → Recording\n"
                      "   to capture Zoom / Meet / Teams audio directly.",
                 fg=C["txt3"], bg=C["bg"], font=("Helvetica", 8),
                 justify=tk.LEFT).pack(padx=16, pady=(6, 0), anchor="w")

        def save():
            CFG["API_KEY"] = self.api_key.get().strip()
            CFG["MODEL"]   = self.model_var.get()
            if CFG["API_KEY"]:
                self.ai = AI(CFG["API_KEY"])
            self._save_cfg()
            win.destroy()

        tk.Button(win, text="  Save  ", command=save,
                  bg=C["accent"], fg="white", relief=tk.FLAT,
                  font=("Helvetica", 10, "bold"), cursor="hand2",
                  pady=7).pack(fill=tk.X, padx=16, pady=14)

    # ── PERSISTENCE ──────────────────────────
    def _save_cfg(self):
        p = os.path.join(os.path.expanduser("~"), ".ma_cfg.json")
        try:
            with open(p, "w") as f:
                json.dump({"key": self.api_key.get(),
                           "model": self.model_var.get(),
                           "device": self.dev_var.get()}, f)
        except Exception:
            pass

    def _load_cfg(self):
        p = os.path.join(os.path.expanduser("~"), ".ma_cfg.json")
        try:
            with open(p) as f:
                d = json.load(f)
            self.api_key.set(d.get("key", ""))
            self.model_var.set(d.get("model", CFG["MODEL"]))
            self.dev_var.set(d.get("device", "Default"))
            if d.get("key"):
                self.ai = AI(d["key"])
        except Exception:
            pass

    # ── HOTKEYS ──────────────────────────────
    def _bind_keys(self):
        self.root.bind("<F2>",     lambda e: self._toggle_listen())
        self.root.bind("<F3>",     lambda e: self._collapse())
        self.root.bind("<F4>",     lambda e: self._copy())
        self.root.bind("<Escape>", lambda e: self._stop())

    def run(self):
        self.root.mainloop()


# ── ENTRY ─────────────────────────────────────────────────────────
if __name__ == "__main__":
    print(f"""
  AI Meeting Assistant  v{CFG['VERSION']}
  Developer : {CFG['DEVELOPER']}
  ─────────────────────────────────
  pip install SpeechRecognition pyaudio requests

  Hotkeys:
    F2  =  Start / Stop listening
    F3  =  Collapse widget
    F4  =  Copy last answer
    Esc =  Stop listening

  Drag the top bar to reposition anywhere on screen.
""")
    App().run()
