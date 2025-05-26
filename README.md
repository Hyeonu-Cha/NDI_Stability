# NDI Stability Monitor

This project is a simple GUI tool to monitor and track NDI video stream stability.

## Features
- Lists all available NDI sources on the local network
- Connect to a source and display live resolution, frame rate, and codec
- Track stream statistics (frame rate, bitrate) over time
- Export results as `.txt` logs and `.png` graphs

## Installation

1. **Install the NDI SDK for macOS**  
   Download from: https://www.ndi.tv/sdk/  
   Make sure it installs to `/Library/NDI SDK for Apple/`.

2. **Clone this repository**:
   ```bash
   git clone https://github.com/HyeonuCha/NDI_Stability.git
   cd NDI_Stability

3. **Create and activate a virtual environment:**:
python3 -m venv .venv
source .venv/bin/activate
4. **Install required Python packages:**:

pip install -r requirements.txt

Running the App
python main.py


Output
PNG graph: logs/ndi_framerate_report.png

Text log: logs/ndi_framerate_log_<timestamp>.txt

Notes
This tool is built for macOS and expects the NDI SDK in /Library/NDI SDK for Apple/

GUI includes a dropdown to choose an NDI source and an Export button to stop tracking and save reports

Audio tracking is currently disabled for better stability