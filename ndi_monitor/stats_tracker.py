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
        self.bitrates = []
        self.thread = None
        #self.log_file = f"ndi_framerate_log_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        self.log_file = f"logs/ndi_framerate_log_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"

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
            total_bytes = 0
            timestamp = datetime.now().strftime("%H:%M:%S")
            frame_rate = 0
            codec = "unknown"

            for _ in range(10):
                info = self.receiver.get_frame_info()
                size = self.receiver.get_last_frame_size()  # New method you must implement
                total_bytes += size

                try:
                    if "@" in info and "[" in info and "]" in info:
                        parts = info.split("@", 1)
                        after_at = parts[1] if len(parts) > 1 else ""

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

                time.sleep(1)

            bitrate_mbps = round((total_bytes * 8) / 10_000_000, 2)  # bits/sec → Mbps

            self.timestamps.append(timestamp)
            self.frame_rates.append(frame_rate)
            self.codecs.append(codec)
            self.bitrates.append(bitrate_mbps)

            print(f"[Report] {timestamp}: Frame Rate = {frame_rate} fps, Codec = {codec}, Bitrate = {bitrate_mbps} Mbps")

    def _generate_graph(self):
        if len(self.timestamps) < 2:
            return

        last_codec = self.codecs[-1] if self.codecs else "unknown"

        plt.figure(figsize=(10, 5))
        plt.subplot(2, 1, 1)
        plt.plot(self.timestamps, self.frame_rates, marker='o')
        plt.title(f"NDI Frame Rate Stability\nCodec: {last_codec}")
        plt.ylabel("FPS")
        plt.xticks(rotation=45)
        plt.grid(True)

        plt.subplot(2, 1, 2)
        plt.plot(self.timestamps, self.bitrates, marker='s', color='orange')
        plt.ylabel("Bitrate (Mbps)")
        plt.xlabel("Time")
        plt.xticks(rotation=45)
        plt.grid(True)

        plt.tight_layout()
        plt.savefig("logs/ndi_framerate_report.png")
        plt.close()

    def _write_log(self):
        with open(self.log_file, "w") as f:
            f.write("NDI Frame Rate and Bitrate Report\n")
            for ts, fr, cc, br in zip(self.timestamps, self.frame_rates, self.codecs, self.bitrates):
                f.write(f"{ts}: {fr} fps, Codec: {cc}, Bitrate: {br} Mbps\n")
