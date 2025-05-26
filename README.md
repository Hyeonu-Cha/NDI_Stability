# NDI Stability Monitor

This tool allows you to detect, connect to, and monitor NDI video sources (TCP or Multicast) in real time. It displays and reports frame rate, codec, bitrate, and connection mode. Reports are generated every 10 seconds in both `.txt` and `.png` formats.

## Features
- Live GUI to select NDI source
- TCP and Multicast detection with fallback
- Displays real-time resolution, FPS, codec, and bitrate
- Auto-generates performance logs and bandwidth charts

## Folder Structure
```
TestNDI/
├── main.py               # Entry point
├── logs/                 # Contains auto-generated .txt and .png logs
├── ndi_monitor/
│   ├── __init__.py
│   ├── gui.py            # GUI logic (Tkinter)
│   ├── ndi_receiver_cffi.py  # NDI connection and frame handling
│   └── stats_tracker.py  # Tracks and graphs stream stats
├── ndi_interface.py      # CFFI bindings to NDI SDK
├── requirements.txt      # Python dependencies
└── README.md             # You are here
```

## Installation
### Requirements
- Python 3.9–3.13
- NDI SDK installed and added to system path (macOS: `/Library/NDI SDK for Apple`)

### Setup
```bash
# Clone and enter project
cd TestNDI

# Create virtual environment
python3 -m venv .venv
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

## Running
```bash
python main.py
```
Select an NDI source from the list. The app will begin monitoring and auto-export logs every 10 seconds.

## Notes
- If multicast is not supported, the app will automatically fall back to TCP.
- Ensure your firewall/network allows NDI traffic.

## License
MIT
