import tkinter as tk
from tkinter import ttk
#from ndi_receiver import NDIReceiver
#from ndi_receiver_cffi import NDIReceiverCFFI 
from .ndi_receiver_cffi import NDIReceiverCFFI as NDIReceiver

from .stats_tracker import StatsTracker

class NDIMonitorApp:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("NDI Source Monitor")
        self.receiver = NDIReceiver()
        self.tracker = StatsTracker(self.receiver)

        self.sources = []
        self.source_var = tk.StringVar()

        self.setup_ui()
        self.update_sources()

    def setup_ui(self):
        ttk.Label(self.root, text="Select NDI Source:").pack(pady=5)
        self.source_combo = ttk.Combobox(self.root, textvariable=self.source_var, state="readonly")
        self.source_combo.pack(pady=5)

        btn_frame = ttk.Frame(self.root)
        btn_frame.pack(pady=5)

        connect_btn = ttk.Button(btn_frame, text="Connect", command=self.connect_source)
        connect_btn.pack(side="left", padx=5)

        stop_btn = ttk.Button(btn_frame, text="Export Reports", command=self.stop_monitoring)
        stop_btn.pack(side="left", padx=5)

        exit_btn = ttk.Button(btn_frame, text="Exit", command=self.exit_app)
        exit_btn.pack(side="left", padx=5)

        self.info_label = ttk.Label(self.root, text="Frame Info:")
        self.info_label.pack(pady=10)

    def update_sources(self):
        self.sources = self.receiver.list_sources()
        names = [s['name'] for s in self.sources]
        self.source_combo['values'] = names
        if names:
            self.source_combo.current(0)

    def connect_source(self):
        index = self.source_combo.current()
        if index >= 0:
            self.receiver.connect(self.sources[index])
            self.start_updating_info()
            self.tracker.start()

    def start_updating_info(self):
        def update():
            frame_info = self.receiver.get_frame_info()
            self.info_label.config(text=frame_info)
            if self.receiver.is_connected():
                self.root.after(1000, update)
        update()

    def stop_monitoring(self):
        self.tracker.stop()
        self.info_label.config(text="Monitoring stopped. Graph saved.")

    def exit_app(self):
        self.stop_monitoring()
        self.root.quit()

    def run(self):
        self.root.mainloop()
