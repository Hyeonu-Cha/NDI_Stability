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
        self.start_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
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
            frame_rate = 0
            codec = "unknown"
            timestamp_label = self.receiver.get_elapsed_time_label()

            for _ in range(10):
                info = self.receiver.get_frame_info()
                size = self.receiver.get_last_frame_size()
                total_bytes += size

                try:
                    if "@" in info and "[" in info and "]" in info:
                        before_at, after_at = info.split("@", 1)
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

            bitrate_mbps = round((total_bytes * 8) / 10_000_000, 2)

            self.timestamps.append(timestamp_label)
            self.frame_rates.append(frame_rate)
            self.codecs.append(codec)
            self.bitrates.append(bitrate_mbps)

            print(f"[Report] {timestamp_label}: Frame Rate = {frame_rate} fps, Codec = {codec}, Bitrate = {bitrate_mbps} Mbps")

    def _generate_graph(self):
        if len(self.timestamps) < 2:
            return

        last_codec = self.codecs[-1] if self.codecs else "unknown"

        plt.figure(figsize=(10, 5))
        plt.subplot(2, 1, 1)
        plt.plot(self.timestamps, self.frame_rates, marker='o')
        plt.title(f"NDI Frame Rate Stability\nCodec: {last_codec} | Start: {self.start_time}")
        plt.ylabel("FPS")
        plt.xticks(rotation=45)
        plt.grid(True)

        plt.subplot(2, 1, 2)
        plt.plot(self.timestamps, self.bitrates, marker='s', color='orange')
        plt.ylabel("Bitrate (Mbps)")
        plt.xlabel("Duration")
        plt.xticks(rotation=45)
        plt.grid(True)

        plt.tight_layout()
        plt.savefig("logs/ndi_framerate_report.png")
        plt.close()

    def _write_log(self):
        with open(self.log_file, "w") as f:
            f.write(f"NDI Frame Rate and Bitrate Report\nStart Time: {self.start_time}\n\n")
            for ts, fr, cc, br in zip(self.timestamps, self.frame_rates, self.codecs, self.bitrates):
                f.write(f"{ts}: {fr} fps, Codec: {cc}, Bitrate: {br} Mbps\n")
