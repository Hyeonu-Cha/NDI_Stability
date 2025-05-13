import ctypes
import time
import struct

# Load NDI shared library
ndi = ctypes.CDLL("/Library/NDI SDK for Apple/lib/macOS/libndi.dylib")

# Structs
class NDIlib_source_t(ctypes.Structure):
    _fields_ = [
        ("p_ndi_name", ctypes.c_char_p),
        ("p_url_address", ctypes.c_char_p),
    ]

class NDIlib_find_create_t(ctypes.Structure):
    _fields_ = [
        ("show_local_sources", ctypes.c_bool),
        ("p_groups", ctypes.c_char_p),
        ("p_extra_ips", ctypes.c_char_p),
    ]

class NDIlib_video_frame_v2_t(ctypes.Structure):
    _fields_ = [
        ("xres", ctypes.c_int),
        ("yres", ctypes.c_int),
        ("FourCC", ctypes.c_int),
        ("frame_rate_N", ctypes.c_int),
        ("frame_rate_D", ctypes.c_int),
        ("picture_aspect_ratio", ctypes.c_float),
        ("timecode", ctypes.c_longlong),
        ("p_data", ctypes.c_void_p),
        ("line_stride_in_bytes", ctypes.c_int),
        ("p_metadata", ctypes.c_char_p),
        ("timestamp", ctypes.c_longlong),
    ]

# Function declarations
ndi.NDIlib_initialize.restype = ctypes.c_bool
ndi.NDIlib_find_create_v2.argtypes = [ctypes.POINTER(NDIlib_find_create_t)]
ndi.NDIlib_find_create_v2.restype = ctypes.c_void_p
ndi.NDIlib_find_get_current_sources.argtypes = [ctypes.c_void_p, ctypes.POINTER(ctypes.c_uint32)]
ndi.NDIlib_find_get_current_sources.restype = ctypes.POINTER(NDIlib_source_t)
ndi.NDIlib_recv_create_v2.restype = ctypes.c_void_p
ndi.NDIlib_recv_connect.argtypes = [ctypes.c_void_p, ctypes.POINTER(NDIlib_source_t)]
ndi.NDIlib_recv_capture_v2.argtypes = [ctypes.c_void_p, ctypes.POINTER(NDIlib_video_frame_v2_t), ctypes.c_void_p, ctypes.c_void_p, ctypes.c_uint32]
ndi.NDIlib_recv_capture_v2.restype = ctypes.c_int
ndi.NDIlib_recv_free_video_v2.argtypes = [ctypes.c_void_p, ctypes.POINTER(NDIlib_video_frame_v2_t)]
ndi.NDIlib_recv_destroy.argtypes = [ctypes.c_void_p]
ndi.NDIlib_find_destroy.argtypes = [ctypes.c_void_p]
ndi.NDIlib_destroy.argtypes = []

# Helper to decode FourCC
def decode_fourcc(code):
    return struct.pack("I", code).decode("utf-8", errors="ignore")

# Initialize NDI
if not ndi.NDIlib_initialize():
    print("NDI initialization failed.")
    exit(1)

# Create finder
create_desc = NDIlib_find_create_t(True, None, None)
finder = ndi.NDIlib_find_create_v2(ctypes.byref(create_desc))

if not finder:
    print("NDI finder creation failed.")
    ndi.NDIlib_destroy()
    exit(1)

time.sleep(2)  # Allow discovery time

# Get sources
num_sources = ctypes.c_uint32()
sources_ptr = ndi.NDIlib_find_get_current_sources(finder, ctypes.byref(num_sources))

print(f"\nFound {num_sources.value} NDI source(s):")

for i in range(num_sources.value):
    source = sources_ptr[i]
    name = source.p_ndi_name.decode("utf-8") if source.p_ndi_name else "<no name>"
    url = source.p_url_address.decode("utf-8") if source.p_url_address else "<no URL>"

    # Connect to receiver
    receiver = ndi.NDIlib_recv_create_v2()
    xres = yres = fps = 0
    codec = "n/a"

    if receiver:
        ndi.NDIlib_recv_connect(receiver, ctypes.byref(source))
        frame = NDIlib_video_frame_v2_t()

        # Try up to 5 times
        for attempt in range(5):
            result = ndi.NDIlib_recv_capture_v2(receiver, ctypes.byref(frame), None, None, 1000)
            if result == 1 and frame.xres > 0:
                xres = frame.xres
                yres = frame.yres
                fps = round(frame.frame_rate_N / frame.frame_rate_D, 2) if frame.frame_rate_D else 0
                codec = decode_fourcc(frame.FourCC)
                ndi.NDIlib_recv_free_video_v2(receiver, ctypes.byref(frame))
                break
            time.sleep(0.2)

        ndi.NDIlib_recv_destroy(receiver)

    print(f" - Name: {name}\n   URL: {url}\n   Res: {xres}x{yres} @ {fps}fps [{codec}]")

# Cleanup
ndi.NDIlib_find_destroy(finder)
ndi.NDIlib_destroy()
