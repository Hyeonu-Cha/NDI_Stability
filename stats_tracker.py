import threading
import time
import matplotlib.pyplot as plt
from datetime import datetime
import tkinter.messagebox as messagebox

class StatsTracker:
    def __init__(self, receiver):
        self.receiver = receiver
        self.running = False
        self.frame_rates = []
        self.timestamps = []
        self.codecs = []
        self.thread = None
        self.log_file = f"ndi_framerate_log_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"

    def start(self):
        if not self.running:
            self.running = True
            self.thread = threading.Thread(target=self._run, daemon=True)
            self.thread.start()

    def stop(self):
        self.running = False
        if self.thread:
            self.thread.join(timeout=2)
            if self.thread.is_alive():
                messagebox.showwarning("Timeout", "Stats thread did not exit in time. Proceeding with cleanup.")
        self._generate_graph()
        self._write_log()

    def _run(self):
        while self.running:
            info = self.receiver.get_frame_info()
            frame_rate = 0
            codec = "unknown"
            try:
                if "@" in info and "[" in info and "]" in info:
                    before_at, after_at = info.split("@")
                    fps_part, codec_part = after_at.split("[")
                    codec = codec_part.strip("] ")
                    if "fps" in fps_part:
                        fps_part = fps_part.replace("fps", "").strip()
                    if "/" in fps_part:
                        num, den = map(int, fps_part.split("/"))
                        frame_rate = round(num / den, 2) if den != 0 else 0
                    else:
                        frame_rate = float(fps_part)
            except Exception as e:
                print(f"[Parse Error] {e}")

            timestamp = datetime.now().strftime("%H:%M:%S")
            self.timestamps.append(timestamp)
            self.frame_rates.append(frame_rate)
            self.codecs.append(codec)

            print(f"[Report] {timestamp}: Frame Rate = {frame_rate} fps, Codec = {codec}")
            time.sleep(10)

    def _generate_graph(self):
        if len(self.timestamps) < 2:
            return

        last_codec = self.codecs[-1] if self.codecs else "unknown"

        plt.figure(figsize=(8, 4))
        plt.plot(self.timestamps, self.frame_rates, marker='o')
        plt.title(f"NDI Frame Rate Stability\nCodec: {last_codec}")
        plt.xlabel("Time")
        plt.ylabel("FPS")
        plt.xticks(rotation=45)
        plt.tight_layout()
        plt.grid(True)
        plt.savefig("ndi_framerate_report.png")
        plt.close()

    def _write_log(self):
        with open(self.log_file, "w") as f:
            f.write("NDI Frame Rate Report\n")
            for ts, fr, cc in zip(self.timestamps, self.frame_rates, self.codecs):
                f.write(f"{ts}: {fr} fps, Codec: {cc}\n")
