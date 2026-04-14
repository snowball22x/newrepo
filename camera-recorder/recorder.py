"""
camera-recorder — Lightweight Windows background camera recorder
Records video from a camera during preset time ranges using FFmpeg.

Usage:
    recorder.exe            — Run the scheduler (reads config.json next to the exe)
    recorder.exe --list     — List available DirectShow video devices
    recorder.exe --test     — Record a 10-second test clip immediately
"""

import sys
import os
import json
import subprocess
import time
import logging
import signal
import threading
from datetime import datetime, date, timedelta
from pathlib import Path

# Windows-only subprocess flag to suppress console windows
_NO_WINDOW = subprocess.CREATE_NO_WINDOW if sys.platform == "win32" else 0

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------

def get_base_dir() -> Path:
    """Return the directory containing the executable (or script during dev)."""
    if getattr(sys, "frozen", False):
        return Path(sys.executable).parent
    return Path(__file__).parent


BASE_DIR = get_base_dir()
CONFIG_PATH = BASE_DIR / "config.json"
LOG_PATH = BASE_DIR / "recorder.log"
FFMPEG_PATH = BASE_DIR / "ffmpeg.exe"

# ---------------------------------------------------------------------------
# Logging
# ---------------------------------------------------------------------------

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler(LOG_PATH, encoding="utf-8"),
        logging.StreamHandler(sys.stdout),
    ],
)
log = logging.getLogger("recorder")

# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------

DEFAULT_CONFIG = {
    "camera_name": "Integrated Camera",
    "output_folder": str(BASE_DIR / "Recordings"),
    "schedules": [
        {"start": "12:20", "end": "13:20"}
    ],
    "video_settings": {
        "resolution": "1280x720",
        "framerate": 30,
        "crf": 23
    }
}


def load_config() -> dict:
    if not CONFIG_PATH.exists():
        log.warning("config.json not found — writing default config.")
        CONFIG_PATH.write_text(json.dumps(DEFAULT_CONFIG, indent=2))
    with open(CONFIG_PATH, encoding="utf-8") as f:
        cfg = json.load(f)
    # Fill in missing keys from defaults
    for key, val in DEFAULT_CONFIG.items():
        cfg.setdefault(key, val)
    cfg["video_settings"] = {**DEFAULT_CONFIG["video_settings"], **cfg.get("video_settings", {})}
    return cfg


def parse_time(t: str) -> tuple[int, int]:
    """Parse 'HH:MM' or 'H:MM' into (hour, minute)."""
    parts = t.strip().split(":")
    return int(parts[0]), int(parts[1])


def time_in_window(now: datetime, start_str: str, end_str: str) -> bool:
    sh, sm = parse_time(start_str)
    eh, em = parse_time(end_str)
    start_dt = now.replace(hour=sh, minute=sm, second=0, microsecond=0)
    end_dt = now.replace(hour=eh, minute=em, second=0, microsecond=0)
    # Handle overnight windows (e.g. 23:00 – 01:00)
    if end_dt <= start_dt:
        end_dt += timedelta(days=1)
    return start_dt <= now < end_dt


def seconds_until_next_window(now: datetime, schedules: list) -> float:
    """Return seconds until the nearest upcoming schedule window starts."""
    candidates = []
    for s in schedules:
        sh, sm = parse_time(s["start"])
        start_dt = now.replace(hour=sh, minute=sm, second=0, microsecond=0)
        if start_dt <= now:
            start_dt += timedelta(days=1)
        candidates.append((start_dt - now).total_seconds())
    return min(candidates) if candidates else 60.0

# ---------------------------------------------------------------------------
# FFmpeg helpers
# ---------------------------------------------------------------------------

def find_ffmpeg() -> str:
    """Locate ffmpeg.exe: bundled first, then PATH."""
    if FFMPEG_PATH.exists():
        return str(FFMPEG_PATH)
    # Try system PATH
    import shutil
    found = shutil.which("ffmpeg")
    if found:
        return found
    raise FileNotFoundError(
        "ffmpeg.exe not found. Place ffmpeg.exe next to recorder.exe or add it to PATH."
    )


def list_devices(ffmpeg: str):
    """Print available DirectShow video devices."""
    log.info("Listing available DirectShow video devices...")
    result = subprocess.run(
        [ffmpeg, "-list_devices", "true", "-f", "dshow", "-i", "dummy"],
        capture_output=True, text=True, creationflags=_NO_WINDOW
    )
    output = result.stderr  # FFmpeg writes device list to stderr
    print("\n--- Available DirectShow Devices ---")
    for line in output.splitlines():
        if "DirectShow" in line or "video" in line.lower() or "audio" in line.lower() or "]" in line:
            print(line)
    print("------------------------------------\n")


def build_ffmpeg_cmd(ffmpeg: str, camera_name: str, output_path: str, vs: dict) -> list:
    """Build the FFmpeg command list for recording."""
    return [
        ffmpeg,
        "-f", "dshow",
        "-video_size", vs.get("resolution", "1280x720"),
        "-framerate", str(vs.get("framerate", 30)),
        "-i", f"video={camera_name}",
        "-c:v", "libx264",
        "-preset", "veryfast",
        "-crf", str(vs.get("crf", 23)),
        "-movflags", "+faststart",
        "-y",
        output_path,
    ]


def make_output_path(output_folder: str) -> str:
    ts = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    folder = Path(output_folder)
    folder.mkdir(parents=True, exist_ok=True)
    return str(folder / f"recording_{ts}.mp4")

# ---------------------------------------------------------------------------
# Recorder state
# ---------------------------------------------------------------------------

class Recorder:
    def __init__(self, cfg: dict, ffmpeg: str):
        self.cfg = cfg
        self.ffmpeg = ffmpeg
        self.proc: subprocess.Popen | None = None
        self._lock = threading.Lock()

    def is_recording(self) -> bool:
        with self._lock:
            return self.proc is not None and self.proc.poll() is None

    def start(self):
        with self._lock:
            if self.proc is not None and self.proc.poll() is None:
                log.warning("Start called but recording already in progress.")
                return
            out = make_output_path(self.cfg["output_folder"])
            cmd = build_ffmpeg_cmd(
                self.ffmpeg,
                self.cfg["camera_name"],
                out,
                self.cfg["video_settings"],
            )
            log.info(f"Starting recording → {out}")
            log.debug("FFmpeg command: " + " ".join(cmd))
            try:
                self.proc = subprocess.Popen(
                    cmd,
                    stdin=subprocess.PIPE,
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.PIPE,
                    creationflags=_NO_WINDOW,
                )
                # Start a thread to drain stderr so the pipe doesn't block
                threading.Thread(target=self._drain_stderr, daemon=True).start()
            except Exception as e:
                log.error(f"Failed to start FFmpeg: {e}")
                self.proc = None

    def stop(self):
        with self._lock:
            if self.proc is None or self.proc.poll() is not None:
                return
            log.info("Stopping recording (sending 'q' to FFmpeg)...")
            try:
                self.proc.stdin.write(b"q")
                self.proc.stdin.flush()
            except Exception:
                pass
            try:
                self.proc.wait(timeout=15)
            except subprocess.TimeoutExpired:
                log.warning("FFmpeg did not exit in time — terminating.")
                self.proc.terminate()
                try:
                    self.proc.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    self.proc.kill()
            log.info("Recording stopped.")
            self.proc = None

    def _drain_stderr(self):
        """Read and log FFmpeg stderr output."""
        try:
            for line in self.proc.stderr:
                decoded = line.decode("utf-8", errors="replace").rstrip()
                if decoded:
                    log.debug(f"[ffmpeg] {decoded}")
        except Exception:
            pass

    def test_record(self, duration: int = 10):
        """Record a short test clip immediately."""
        out = make_output_path(self.cfg["output_folder"])
        cmd = build_ffmpeg_cmd(
            self.ffmpeg,
            self.cfg["camera_name"],
            out,
            self.cfg["video_settings"],
        )
        # Insert -t duration after the input
        cmd = cmd[:cmd.index("-c:v")] + ["-t", str(duration)] + cmd[cmd.index("-c:v"):]
        log.info(f"Test recording for {duration}s → {out}")
        result = subprocess.run(
            cmd,
            capture_output=True,
            creationflags=_NO_WINDOW,
        )
        if result.returncode == 0:
            log.info(f"Test recording saved: {out}")
            print(f"\nTest recording saved: {out}\n")
        else:
            err = result.stderr.decode("utf-8", errors="replace")
            log.error(f"Test recording failed:\n{err}")
            print(f"\nTest recording FAILED. Check recorder.log for details.\n")

# ---------------------------------------------------------------------------
# Main scheduler loop
# ---------------------------------------------------------------------------

def run_scheduler(cfg: dict, ffmpeg: str):
    recorder = Recorder(cfg, ffmpeg)
    schedules = cfg.get("schedules", [])

    if not schedules:
        log.error("No schedules defined in config.json. Exiting.")
        return

    log.info(f"Scheduler started. {len(schedules)} schedule(s) loaded.")
    for s in schedules:
        log.info(f"  Schedule: {s['start']} → {s['end']}")
    log.info(f"Output folder: {cfg['output_folder']}")
    log.info(f"Camera: {cfg['camera_name']}")

    # Handle graceful shutdown
    def shutdown(signum, frame):
        log.info("Shutdown signal received.")
        recorder.stop()
        sys.exit(0)

    signal.signal(signal.SIGTERM, shutdown)
    signal.signal(signal.SIGINT, shutdown)

    CHECK_INTERVAL = 10  # seconds between schedule checks

    while True:
        now = datetime.now()
        in_window = any(time_in_window(now, s["start"], s["end"]) for s in schedules)

        if in_window and not recorder.is_recording():
            log.info(f"Entering scheduled window at {now.strftime('%H:%M:%S')}.")
            recorder.start()

        elif not in_window and recorder.is_recording():
            log.info(f"Scheduled window ended at {now.strftime('%H:%M:%S')}.")
            recorder.stop()

        elif not in_window and not recorder.is_recording():
            secs = seconds_until_next_window(now, schedules)
            if secs > 60:
                log.info(
                    f"Idle. Next window in {int(secs // 3600)}h "
                    f"{int((secs % 3600) // 60)}m. Sleeping {CHECK_INTERVAL}s."
                )

        # Check if FFmpeg crashed mid-recording and restart if still in window
        if in_window and not recorder.is_recording():
            log.warning("FFmpeg process ended unexpectedly during window — restarting.")
            time.sleep(3)
            recorder.start()

        time.sleep(CHECK_INTERVAL)

# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

def main():
    args = sys.argv[1:]

    try:
        ffmpeg = find_ffmpeg()
    except FileNotFoundError as e:
        log.error(str(e))
        sys.exit(1)

    if "--list" in args:
        list_devices(ffmpeg)
        return

    cfg = load_config()

    if "--test" in args:
        r = Recorder(cfg, ffmpeg)
        r.test_record(duration=10)
        return

    run_scheduler(cfg, ffmpeg)


if __name__ == "__main__":
    main()
