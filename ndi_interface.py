from cffi import FFI
import os

ffi = FFI()

# C declarations from the NDI SDK we need
ffi.cdef("""
    typedef struct {
        const char* p_ndi_name;
        const char* p_url_address;
    } NDIlib_source_t;

    typedef struct {
        bool show_local_sources;
        const char* p_groups;
        const char* p_extra_ips;
    } NDIlib_find_create_t;
    
    typedef struct {
        int xres, yres;
        int FourCC;
        int frame_rate_N;
        int frame_rate_D;
        float picture_aspect_ratio;
        long long timecode;
        void* p_data;
        int line_stride_in_bytes;
        const char* p_metadata;
        long long timestamp;
    } NDIlib_video_frame_v2_t;

    bool NDIlib_initialize(void);
    void* NDIlib_find_create_v2(const NDIlib_find_create_t* p_create_settings);
    bool NDIlib_find_wait_for_sources(void* p_instance, uint32_t timeout_in_ms);
    const NDIlib_source_t* NDIlib_find_get_current_sources(void* p_instance, uint32_t* p_no_sources);
    void* NDIlib_recv_create_v2(void);
    void NDIlib_recv_connect(void* p_instance, const NDIlib_source_t* p_src);
    int NDIlib_recv_capture_v2(void* p_instance,
                                NDIlib_video_frame_v2_t* p_video_data,
                                void* p_audio_data,
                                void* p_metadata,
                                uint32_t timeout_in_ms);
    void NDIlib_recv_free_video_v2(void* p_instance, NDIlib_video_frame_v2_t* p_video_data);
    void NDIlib_find_destroy(void* p_instance);
    void NDIlib_recv_destroy(void* p_instance);
    void NDIlib_destroy(void);
""")

# Load libndi.dylib
ndi_path = "/Library/NDI SDK for Apple/lib/macOS/libndi.dylib"
if not os.path.exists(ndi_path):
    raise RuntimeError("NDI library not found at expected location")

lib = ffi.dlopen(ndi_path)

# Convenience: convert FourCC to string
def decode_fourcc(fourcc):
    chars = bytes([
        fourcc & 0xFF,
        (fourcc >> 8) & 0xFF,        (fourcc >> 16) & 0xFF,
        (fourcc >> 24) & 0xFF,
        0  # Null-terminator
    ])
    return ffi.string(ffi.new("char[]", chars)).decode("utf-8", errors="ignore")


__all__ = ["ffi", "lib", "decode_fourcc"]
