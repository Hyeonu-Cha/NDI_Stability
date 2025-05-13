from ndi_interface import ffi, lib, decode_fourcc
import time

class NDIReceiverCFFI:
    def __init__(self):
        if not lib.NDIlib_initialize():
            raise RuntimeError("NDI initialization failed")

        # Setup source finder
        find_settings = ffi.new("NDIlib_find_create_t*", [True, ffi.NULL, ffi.NULL])
        self.finder = lib.NDIlib_find_create_v2(find_settings)
        self.sources = []
        self.receiver = ffi.NULL

    def list_sources(self):
        lib.NDIlib_find_wait_for_sources(self.finder, 2000)
        count_ptr = ffi.new("uint32_t*")
        src_ptr = lib.NDIlib_find_get_current_sources(self.finder, count_ptr)
        self.sources = []
        for i in range(count_ptr[0]):
            s = src_ptr[i]
            name = ffi.string(s.p_ndi_name).decode() if s.p_ndi_name else '<unnamed>'
            url = ffi.string(s.p_url_address).decode() if s.p_url_address else '<no url>'
            self.sources.append({
                'name': name,
                'url': url,
                'struct': s
            })
        return self.sources

    def connect(self, source_dict):
        s = source_dict['struct']
        source = ffi.new("NDIlib_source_t*")
        source.p_ndi_name = s.p_ndi_name
        source.p_url_address = s.p_url_address

        self.receiver = lib.NDIlib_recv_create_v2()
        lib.NDIlib_recv_connect(self.receiver, source)

        self.frame = ffi.new("NDIlib_video_frame_v2_t*")

    def get_frame_info(self):
        if not self.receiver:
            return "Not connected"

        result = lib.NDIlib_recv_capture_v2(self.receiver, self.frame, ffi.NULL, ffi.NULL, 1000)
        if result == 1:
            xres = self.frame.xres
            yres = self.frame.yres
            num = self.frame.frame_rate_N
            den = self.frame.frame_rate_D or 1
            fourcc = decode_fourcc(self.frame.FourCC)
            fps = round(num / den, 2)

            lib.NDIlib_recv_free_video_v2(self.receiver, self.frame)
            return f"{xres}x{yres} @ {fps}fps [{fourcc}]"
        return "Waiting for video..."

    def is_connected(self):
        return self.receiver != ffi.NULL
