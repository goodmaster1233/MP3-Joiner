"""
MP3 Joiner — Lossless audio joining via FFmpeg
Requires: pip install customtkinter
Also requires FFmpeg installed and in PATH (https://ffmpeg.org)
"""

import customtkinter as ctk
import subprocess
import os
import threading
from tkinter import filedialog, messagebox

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

ACCENT   = "#4C9BE8"
SUCCESS  = "#4CAF82"
DANGER   = "#E85D5D"
BG_CARD  = "#1E2028"
BG_ROW   = "#252830"
BG_ROW_S = "#2A3A52"
TEXT_DIM = "#7A8090"


class FileRow(ctk.CTkFrame):
    def __init__(self, master, index, path, on_select, **kwargs):
        super().__init__(master, height=48, fg_color=BG_ROW, corner_radius=8, **kwargs)
        self.pack_propagate(False)
        self.index = index
        self.path = path
        self.on_select = on_select
        self.selected = False

        self.num = ctk.CTkLabel(self, text=f"{index + 1}", width=28,
                                font=ctk.CTkFont("Courier New", 12, "bold"),
                                text_color=TEXT_DIM)
        self.num.pack(side="left", padx=(12, 4))

        # Icon label (unicode music note)
        ctk.CTkLabel(self, text="♪", font=ctk.CTkFont(size=14),
                     text_color=ACCENT, width=20).pack(side="left", padx=(0, 8))

        self.name_lbl = ctk.CTkLabel(self, text=os.path.basename(path),
                                     anchor="w", font=ctk.CTkFont(size=13),
                                     text_color="#D0D8E8")
        self.name_lbl.pack(side="left", fill="x", expand=True)

        size_str = self._file_size(path)
        ctk.CTkLabel(self, text=size_str, font=ctk.CTkFont(size=11),
                     text_color=TEXT_DIM, width=60).pack(side="right", padx=12)

        for w in [self, self.num, self.name_lbl]:
            w.bind("<Button-1>", lambda e: self.on_select(self.index))

    def _file_size(self, path):
        try:
            b = os.path.getsize(path)
            if b >= 1_000_000:
                return f"{b/1_000_000:.1f} MB"
            return f"{b/1_000:.0f} KB"
        except Exception:
            return ""

    def set_selected(self, sel: bool):
        self.selected = sel
        color = BG_ROW_S if sel else BG_ROW
        self.configure(fg_color=color)

    def update_num(self, index):
        self.index = index
        self.num.configure(text=f"{index + 1}")


class MP3Joiner(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("MP3 Joiner")
        self.geometry("740x660")
        self.minsize(620, 520)
        self.configure(fg_color="#13151A")

        self.files: list[str] = []
        self.file_rows: list[FileRow] = []
        self.selected_index: int | None = None

        self._build_ui()

    # ── UI Construction ──────────────────────────────────────────────

    def _build_ui(self):
        # ── Header ──
        hdr = ctk.CTkFrame(self, fg_color="transparent")
        hdr.pack(fill="x", padx=28, pady=(22, 6))

        ctk.CTkLabel(hdr, text="MP3 Joiner",
                     font=ctk.CTkFont("Trebuchet MS", 26, "bold"),
                     text_color="#EEF2FF").pack(side="left")

        badge = ctk.CTkLabel(hdr, text="  lossless via FFmpeg  ",
                             font=ctk.CTkFont(size=11),
                             fg_color="#22263A", corner_radius=20,
                             text_color=ACCENT)
        badge.pack(side="left", padx=12, pady=4)

        # ── Files Card ──
        card = ctk.CTkFrame(self, fg_color=BG_CARD, corner_radius=14)
        card.pack(fill="both", expand=True, padx=22, pady=(6, 8))

        # card toolbar
        tb = ctk.CTkFrame(card, fg_color="transparent")
        tb.pack(fill="x", padx=16, pady=(14, 8))

        ctk.CTkLabel(tb, text="Tracks",
                     font=ctk.CTkFont(size=14, weight="bold"),
                     text_color="#C8D0E0").pack(side="left")

        self.count_lbl = ctk.CTkLabel(tb, text="0 files",
                                       font=ctk.CTkFont(size=12),
                                       text_color=TEXT_DIM)
        self.count_lbl.pack(side="left", padx=10)

        # right-side buttons
        for label, cmd, primary in [
            ("+ Add Files", self.add_files, True),
            ("Remove",      self.remove_selected, False),
            ("Clear All",   self.clear_files, False),
        ]:
            ctk.CTkButton(tb, text=label, width=90, height=30,
                          corner_radius=8,
                          fg_color=ACCENT if primary else "transparent",
                          hover_color="#3A7ACC" if primary else "#2A2D38",
                          border_width=0 if primary else 1,
                          border_color="#3A3F50",
                          font=ctk.CTkFont(size=12),
                          command=cmd).pack(side="right", padx=3)

        # scrollable list
        self.scroll = ctk.CTkScrollableFrame(card, fg_color="transparent",
                                              scrollbar_button_color="#2E3240",
                                              scrollbar_button_hover_color=ACCENT)
        self.scroll.pack(fill="both", expand=True, padx=12, pady=(0, 6))

        self.empty_lbl = ctk.CTkLabel(self.scroll,
                                       text="No files added yet\nClick  + Add Files  to get started",
                                       font=ctk.CTkFont(size=13),
                                       text_color=TEXT_DIM, justify="center")
        self.empty_lbl.pack(expand=True, pady=60)

        # order controls
        ctrl = ctk.CTkFrame(card, fg_color="transparent")
        ctrl.pack(fill="x", padx=16, pady=(2, 14))

        for label, cmd in [("▲  Move Up", self.move_up), ("▼  Move Down", self.move_down)]:
            ctk.CTkButton(ctrl, text=label, width=108, height=28,
                          corner_radius=8, fg_color="transparent",
                          border_width=1, border_color="#3A3F50",
                          font=ctk.CTkFont(size=12),
                          hover_color="#2A2D38",
                          command=cmd).pack(side="left", padx=3)

        # ── Output Card ──
        out_card = ctk.CTkFrame(self, fg_color=BG_CARD, corner_radius=14)
        out_card.pack(fill="x", padx=22, pady=(0, 8))

        out_inner = ctk.CTkFrame(out_card, fg_color="transparent")
        out_inner.pack(fill="x", padx=16, pady=14)

        ctk.CTkLabel(out_inner, text="Output File",
                     font=ctk.CTkFont(size=13, weight="bold"),
                     text_color="#C8D0E0").pack(anchor="w", pady=(0, 8))

        row = ctk.CTkFrame(out_inner, fg_color="transparent")
        row.pack(fill="x")

        self.out_entry = ctk.CTkEntry(row, placeholder_text="Choose where to save the joined file…",
                                       height=36, corner_radius=8,
                                       fg_color="#0F1116", border_color="#3A3F50",
                                       font=ctk.CTkFont(size=12))
        self.out_entry.pack(side="left", fill="x", expand=True, padx=(0, 8))

        ctk.CTkButton(row, text="Browse", width=80, height=36,
                      corner_radius=8, fg_color="#252830",
                      hover_color="#2E3240", border_width=1,
                      border_color="#3A3F50",
                      font=ctk.CTkFont(size=12),
                      command=self.browse_output).pack(side="right")

        # ── Footer / Join ──
        foot = ctk.CTkFrame(self, fg_color="transparent")
        foot.pack(fill="x", padx=22, pady=(0, 20))

        self.status_lbl = ctk.CTkLabel(foot, text="", font=ctk.CTkFont(size=12),
                                        text_color=TEXT_DIM)
        self.status_lbl.pack(side="left")

        self.join_btn = ctk.CTkButton(foot, text="Join Files  →",
                                       width=148, height=42,
                                       corner_radius=10,
                                       fg_color=ACCENT,
                                       hover_color="#3A7ACC",
                                       font=ctk.CTkFont(size=14, weight="bold"),
                                       command=self.join_files)
        self.join_btn.pack(side="right")

    # ── File Management ──────────────────────────────────────────────

    def add_files(self):
        paths = filedialog.askopenfilenames(
            title="Select Audio Files",
            filetypes=[
                ("MP3 files", "*.mp3"),
                ("All audio", "*.mp3 *.wav *.m4a *.aac *.flac *.ogg"),
                ("All files", "*.*"),
            ],
        )
        added = 0
        for p in paths:
            if p not in self.files:
                self.files.append(p)
                added += 1
        if added:
            self._refresh()

    def remove_selected(self):
        if self.selected_index is not None:
            self.files.pop(self.selected_index)
            self.selected_index = None
            self._refresh()

    def clear_files(self):
        self.files.clear()
        self.selected_index = None
        self._refresh()

    def move_up(self):
        i = self.selected_index
        if i is not None and i > 0:
            self.files[i], self.files[i - 1] = self.files[i - 1], self.files[i]
            self._refresh()
            self._select(i - 1)

    def move_down(self):
        i = self.selected_index
        if i is not None and i < len(self.files) - 1:
            self.files[i], self.files[i + 1] = self.files[i + 1], self.files[i]
            self._refresh()
            self._select(i + 1)

    def _select(self, idx):
        self.selected_index = idx
        for row in self.file_rows:
            row.set_selected(row.index == idx)

    def _refresh(self):
        for row in self.file_rows:
            row.destroy()
        self.file_rows.clear()
        self.selected_index = None

        n = len(self.files)
        self.count_lbl.configure(text=f"{n} file{'s' if n != 1 else ''}")

        if not self.files:
            self.empty_lbl.pack(expand=True, pady=60)
            return

        self.empty_lbl.pack_forget()

        for i, path in enumerate(self.files):
            row = FileRow(self.scroll, i, path, on_select=self._select)
            row.pack(fill="x", pady=3)
            self.file_rows.append(row)

    # ── Output & Join ────────────────────────────────────────────────

    def browse_output(self):
        path = filedialog.asksaveasfilename(
            title="Save Joined File As",
            defaultextension=".mp3",
            filetypes=[("MP3 file", "*.mp3"), ("All files", "*.*")],
        )
        if path:
            self.out_entry.delete(0, "end")
            self.out_entry.insert(0, path)

    def join_files(self):
        if len(self.files) < 2:
            messagebox.showwarning("Not enough files",
                                   "Add at least 2 files to join.")
            return
        output = self.out_entry.get().strip()
        if not output:
            messagebox.showwarning("No output path",
                                   "Please choose a save location first.")
            return

        self.join_btn.configure(state="disabled", text="Joining…")
        self.status_lbl.configure(text="⏳  Running FFmpeg…", text_color=TEXT_DIM)
        threading.Thread(target=self._run_ffmpeg, args=(output,), daemon=True).start()

    def _run_ffmpeg(self, output):
        list_path = os.path.join(os.path.dirname(output) or ".", "_ffmpeg_concat_list.txt")
        try:
            with open(list_path, "w", encoding="utf-8") as f:
                for p in self.files:
                    # FFmpeg concat list uses forward slashes and needs special chars escaped
                    safe = p.replace("'", "\\'")
                    f.write(f"file '{safe}'\n")

            cmd = [
                "ffmpeg", "-y",
                "-f", "concat",
                "-safe", "0",
                "-i", list_path,
                "-c", "copy",
                output,
            ]
            result = subprocess.run(cmd, capture_output=True, text=True)

            if result.returncode == 0:
                self.after(0, self._on_success, output)
            else:
                self.after(0, self._on_error, result.stderr[-800:])

        except FileNotFoundError:
            self.after(0, self._on_error,
                       "FFmpeg not found.\n\nMake sure FFmpeg is installed and added to your PATH.\n"
                       "Download: https://ffmpeg.org/download.html")
        except Exception as exc:
            self.after(0, self._on_error, str(exc))
        finally:
            try:
                os.remove(list_path)
            except Exception:
                pass

    def _on_success(self, output):
        self.join_btn.configure(state="normal", text="Join Files  →")
        self.status_lbl.configure(text="✓  Done!", text_color=SUCCESS)
        messagebox.showinfo("Success",
                            f"Files joined successfully!\n\nSaved to:\n{output}")

    def _on_error(self, msg):
        self.join_btn.configure(state="normal", text="Join Files  →")
        self.status_lbl.configure(text="✗  Error — see dialog", text_color=DANGER)
        messagebox.showerror("FFmpeg Error", msg)


if __name__ == "__main__":
    app = MP3Joiner()
    app.mainloop()
