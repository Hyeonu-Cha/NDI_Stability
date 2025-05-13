import ctypes
import time

class NDIReceiver:
    def __init__(self):
        self.ndi = ctypes.CDLL("/Library/NDI SDK for Apple/lib/macOS/libndi.dylib")
        self.source = None
        self.receiver = None

        self._init_ndi()

    def _init_ndi(self):
        self.ndi.NDIlib_initialize.restype = ctypes.c_bool
        if not self.ndi.NDIlib_initialize():
            raise RuntimeError("NDI initialization failed")

        class NDIlib_find_create_t(ctypes.Structure):
            _fields_ = [("show_local_sources", ctypes.c_bool),
                        ("p_groups", ctypes.c_char_p),
                        ("p_extra_ips", ctypes.c_char_p)]

        self.finder_desc = NDIlib_find_create_t(True, None, None)
        self.ndi.NDIlib_find_create_v2.restype = ctypes.c_void_p
        self.finder = self.ndi.NDIlib_find_create_v2(ctypes.byref(self.finder_desc))

        self.ndi.NDIlib_find_wait_for_sources.argtypes = [ctypes.c_void_p, ctypes.c_uint32]
        self.ndi.NDIlib_find_wait_for_sources.restype = ctypes.c_bool

        self.ndi.NDIlib_find_get_current_sources.restype = ctypes.POINTER(self._source_struct())
        self.ndi.NDIlib_find_get_current_sources.argtypes = [ctypes.c_void_p, ctypes.POINTER(ctypes.c_uint32)]

    def _source_struct(self):
        class NDIlib_source_t(ctypes.Structure):
            _fields_ = [("p_ndi_name", ctypes.c_char_p),
                        ("p_url_address", ctypes.c_char_p)]
        return NDIlib_source_t

    def list_sources(self):
        self.ndi.NDIlib_find_wait_for_sources(self.finder, 2000)
        count = ctypes.c_uint32()
        ptr = self.ndi.NDIlib_find_get_current_sources(self.finder, ctypes.byref(count))
        sources = []
        for i in range(count.value):
            s = ptr[i]
            sources.append({
                'name': s.p_ndi_name.decode() if s.p_ndi_name else '<unnamed>',
                'url': s.p_url_address.decode() if s.p_url_address else '<no url>',
                'struct': s
            })
        return sources

    def connect(self, source_dict):
        source_struct = self._source_struct()
        raw = source_dict['struct']
        self.source = source_struct()
        self.source.p_ndi_name = raw.p_ndi_name
        self.source.p_url_address = raw.p_url_address

        self.ndi.NDIlib_recv_create_v2.restype = ctypes.c_void_p
        self.receiver = self.ndi.NDIlib_recv_create_v2()

        connect_fn = self.ndi.NDIlib_recv_connect
        connect_fn.argtypes = [ctypes.c_void_p, ctypes.POINTER(source_struct)]
        connect_fn(self.receiver, ctypes.byref(self.source))

        # Declare frame capture
        class NDIlib_video_frame_v2_t(ctypes.Structure):
            _fields_ = [("xres", ctypes.c_int),
                        ("yres", ctypes.c_int),
                        ("FourCC", ctypes.c_int),
                        ("frame_rate_N", ctypes.c_int),
                        ("frame_rate_D", ctypes.c_int),
                        ("picture_aspect_ratio", ctypes.c_float),
                        ("timecode", ctypes.c_longlong),
                        ("p_data", ctypes.c_void_p),
                        ("line_stride_in_bytes", ctypes.c_int),
                        ("p_metadata", ctypes.c_char_p),
                        ("timestamp", ctypes.c_longlong)]
        self.NDIlib_video_frame_v2_t = NDIlib_video_frame_v2_t

        self.ndi.NDIlib_recv_capture_v2.argtypes = [ctypes.c_void_p,
                                                    ctypes.POINTER(NDIlib_video_frame_v2_t),
                                                    ctypes.c_void_p, ctypes.c_void_p,
                                                    ctypes.c_uint32]
        self.ndi.NDIlib_recv_capture_v2.restype = ctypes.c_int

        self.ndi.NDIlib_recv_free_video_v2.argtypes = [ctypes.c_void_p, ctypes.POINTER(NDIlib_video_frame_v2_t)]

    def get_frame_info(self):
        if not self.receiver:
            return "Not connected"

        frame = self.NDIlib_video_frame_v2_t()
        result = self.ndi.NDIlib_recv_capture_v2(self.receiver, ctypes.byref(frame), None, None, 500)
        if result == 1:
            info = f"{frame.xres}x{frame.yres} @ {frame.frame_rate_N}/{frame.frame_rate_D}"
            self.ndi.NDIlib_recv_free_video_v2(self.receiver, ctypes.byref(frame))
            return info
        else:
            return "Waiting for video..."

    def is_connected(self):
        return self.receiver is not None
