# 🎵 MP3 Joiner

A clean, modern GUI tool for joining multiple audio files together — instantly and losslessly — powered under the hood by FFmpeg.

No re-encoding. No quality loss. No waiting.

---

## Features

- **Lossless joining** — Uses FFmpeg's `concat` with `-c copy`, so your audio is never re-encoded
- **Drag-and-drop style file list** — Add as many tracks as you need, in any order
- **Reorder tracks** — Move files up or down before joining
- **Supports multiple formats** — MP3, WAV, M4A, AAC, FLAC, OGG
- **Custom output path** — Choose exactly where your joined file gets saved
- **Background processing** — The UI stays responsive while FFmpeg runs
- **Modern dark UI** — Built with [CustomTkinter](https://github.com/TomSchimansky/CustomTkinter), not the clunky default Tkinter look

---

## Why This Exists

Most GUI audio joiners either re-encode your files (destroying quality and taking forever) or have outdated, clunky interfaces. This tool wraps FFmpeg's blazing-fast lossless concat in a clean, easy-to-use UI — ideal for joining large audiobooks, podcast episodes, or music files without any quality loss.

---

## Requirements

- Python 3.10+
- [FFmpeg](https://ffmpeg.org/download.html) installed and added to your system PATH
- CustomTkinter:
  ```
  pip install customtkinter
  ```

---

## Usage

```bash
python mp3_joiner.py
```

1. Click **+ Add Files** to add your audio tracks
2. Use **Move Up / Move Down** to set the order
3. Click **Browse** to choose your output file location
4. Hit **Join Files →**

That's it. FFmpeg does the rest in seconds.

---

## Screenshot

<img width="742" height="692" alt="MP3-Joiner_Screenshot" src="https://github.com/user-attachments/assets/9e292183-c739-41ee-a9b1-b870ac83579a" />

---

## License

MIT — do whatever you want with it.

---

## Credits

> This project was designed and developed with the assistance of [Claude](https://claude.ai), an AI assistant made by [Anthropic](https://www.anthropic.com). The UI design, FFmpeg integration logic, and project structure were all generated through a conversation with Claude AI.
