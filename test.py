import ctypes
import time

# Load NDI
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

# Function declarations
ndi.NDIlib_initialize.restype = ctypes.c_bool
ndi.NDIlib_find_create_v2.restype = ctypes.c_void_p
ndi.NDIlib_find_get_current_sources.restype = ctypes.POINTER(NDIlib_source_t)
ndi.NDIlib_find_get_current_sources.argtypes = [ctypes.c_void_p, ctypes.POINTER(ctypes.c_uint32)]
ndi.NDIlib_find_wait_for_sources.argtypes = [ctypes.c_void_p, ctypes.c_uint32]
ndi.NDIlib_find_wait_for_sources.restype = ctypes.c_bool
ndi.NDIlib_find_destroy.argtypes = [ctypes.c_void_p]
ndi.NDIlib_destroy.argtypes = []

# Init
print("🔁 Loading NDI...")
if not ndi.NDIlib_initialize():
    print("❌ NDI init failed")
    exit(1)
print("✅ NDI initialized")

# Finder create
create_desc = NDIlib_find_create_t(True, None, None)
finder = ndi.NDIlib_find_create_v2(ctypes.byref(create_desc))
if not finder:
    print("❌ Finder failed")
    exit(1)
print("🔍 Finder created")

# Wait for sources to appear
print("⏳ Waiting for NDI sources (5s timeout)...")
found = ndi.NDIlib_find_wait_for_sources(finder, 5000)
if not found:
    print("❌ No sources found after timeout")
    ndi.NDIlib_find_destroy(finder)
    ndi.NDIlib_destroy()
    exit(1)

# Get current sources
count = ctypes.c_uint32()
sources = ndi.NDIlib_find_get_current_sources(finder, ctypes.byref(count))
print(f"📡 Found {count.value} source(s)")

# List sources
for i in range(count.value):
    src = sources[i]
    name = src.p_ndi_name.decode() if src.p_ndi_name else "<Unnamed>"
    url = src.p_url_address.decode() if src.p_url_address else "<No URL>"
    print(f" - {name} ({url})")

# Clean up
ndi.NDIlib_find_destroy(finder)
ndi.NDIlib_destroy()
print("🧹 Done.")
