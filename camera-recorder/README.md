# camera-recorder

A lightweight, reliable Windows background program that records video from a connected camera during preset time ranges and saves the output to a local folder. No GUI required — runs silently in the background.

---

## How It Works

The program uses **FFmpeg** for video capture and encoding (H.264/MP4), and a **Python scheduler** that checks the current time against your configured schedule every 10 seconds. When a recording window starts, FFmpeg is launched as a background process. When the window ends, FFmpeg is gracefully stopped and the MP4 file is finalized.

---

## Quick Start

### Step 1 — Get the files

Download or clone this repository. Your deployment folder should contain:

```
recorder.exe          ← the main program
ffmpeg.exe            ← download separately (see below)
config.json           ← your schedule and settings
list_cameras.bat      ← helper: lists available cameras
test_recording.bat    ← helper: records a 10-second test clip
install_startup.bat   ← optional: adds recorder to Windows startup
uninstall_startup.bat ← optional: removes from Windows startup
```

### Step 2 — Download FFmpeg

1. Go to [https://www.gyan.dev/ffmpeg/builds/](https://www.gyan.dev/ffmpeg/builds/)
2. Download the **ffmpeg-release-essentials.zip** (or the latest release build)
3. Extract it and copy **`ffmpeg.exe`** from the `bin/` folder into the same folder as `recorder.exe`

### Step 3 — Find your camera name

Double-click **`list_cameras.bat`**. It will print all available DirectShow video devices, for example:

```
[dshow @ ...] "Integrated Camera"
[dshow @ ...] "HD Pro Webcam C920"
```

Copy the exact name (including quotes) for use in `config.json`.

### Step 4 — Edit `config.json`

```json
{
  "camera_name": "Integrated Camera",
  "output_folder": "C:\\Videos\\Recordings",
  "schedules": [
    { "start": "12:20", "end": "13:20" },
    { "start": "18:00", "end": "19:00" }
  ],
  "video_settings": {
    "resolution": "1280x720",
    "framerate": 30,
    "crf": 23
  }
}
```

| Field | Description |
|---|---|
| `camera_name` | Exact DirectShow device name from Step 3 |
| `output_folder` | Where MP4 files are saved (created automatically) |
| `schedules` | List of `{ "start": "HH:MM", "end": "HH:MM" }` entries. 24-hour format. Overnight windows (e.g. 23:00–01:00) are supported. |
| `resolution` | Recording resolution (e.g. `1920x1080`, `1280x720`, `640x480`) |
| `framerate` | Frames per second (e.g. `30`, `25`, `15`) |
| `crf` | H.264 quality: lower = better quality, larger file. Range 18–28. Default `23` is a good balance. |

### Step 5 — Test

Double-click **`test_recording.bat`**. It will record a 10-second clip immediately and save it to your `output_folder`. Play it back to confirm the camera and settings are correct.

### Step 6 — Run

Double-click **`recorder.exe`** (or run it from the command line). It will run silently in the background. Check `recorder.log` for status and any errors.

To stop it, open Task Manager and end the `recorder.exe` process.

---

## Auto-Start at Login (Optional)

To have the recorder start automatically when you log in to Windows:

1. Double-click **`install_startup.bat`**
2. To remove it later, double-click **`uninstall_startup.bat`**

Alternatively, you can add `recorder.exe` to the Windows Task Scheduler for more control (e.g., run whether logged in or not, run as a specific user).

---

## Output Files

Each recording session produces a separate MP4 file named with a timestamp:

```
Recordings/
  recording_2025-06-01_12-20-00.mp4
  recording_2025-06-01_18-00-00.mp4
```

---

## Logs

All events are written to **`recorder.log`** in the same folder as the executable:

```
2025-06-01 12:19:50 [INFO] Scheduler started. 2 schedule(s) loaded.
2025-06-01 12:20:00 [INFO] Entering scheduled window at 12:20:00.
2025-06-01 12:20:00 [INFO] Starting recording → C:\Videos\Recordings\recording_2025-06-01_12-20-00.mp4
2025-06-01 13:20:00 [INFO] Scheduled window ended at 13:20:00.
2025-06-01 13:20:00 [INFO] Stopping recording (sending 'q' to FFmpeg)...
2025-06-01 13:20:01 [INFO] Recording stopped.
```

---

## Troubleshooting

| Problem | Solution |
|---|---|
| `ffmpeg.exe not found` | Place `ffmpeg.exe` in the same folder as `recorder.exe` |
| Camera not found / wrong name | Run `list_cameras.bat` and copy the exact device name into `config.json` |
| Black screen / no video | Try a lower resolution or framerate; check if another app is using the camera |
| File not playable | The recording was interrupted mid-write. Try `ffmpeg -i input.mp4 -c copy fixed.mp4` to repair it |
| High CPU usage | Increase the `crf` value (e.g., 28) or lower the `framerate` (e.g., 15) |

---

## Building from Source

Requirements: **Python 3.8+** on Windows, **PyInstaller**

```bat
pip install pyinstaller
build.bat
```

The compiled `recorder.exe` will be in the `dist/` folder.

---

## License

MIT License — free to use, modify, and distribute.
