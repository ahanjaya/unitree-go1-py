import platform
import threading
import warnings

import cv2


class Go1Camera:
    def __init__(self, host: str, port: int) -> None:
        self._host = host
        self._port = port
        self._gst_pipeline = self._build_gstreamer_cmd()

        self.latest_frame = None
        self._capturing = threading.Event()
        self._capturing_thread = threading.Thread(
            target=self._capturing_thread_func,
            args=(self._capturing,),
        )
        self._capturing_thread.start()

    def close(self) -> None:
        self._capturing.set()
        self._capturing_thread.join()
        self._cap.release()

    def _get_cpu_arch_decoder(self) -> str:
        if platform.machine() == "x86_64":
            return "avdec_h264"
        else:
            return "omxh264dec"

    def _build_gstreamer_cmd(self) -> str:
        str_address = f"udpsrc address={self._host} port={self._port} ! "
        str_application = "application/x-rtp,media=video,encoding-name=H264 ! "
        str_decoder = f"rtph264depay ! h264parse ! {self._get_cpu_arch_decoder()} ! videoconvert ! appsink"

        return str_address + str_application + str_decoder

    def _capturing_thread_func(self, event) -> None:
        print(f"Capturing Thread Port: {self._port} Started.")

        self._cap = cv2.VideoCapture(self._gst_pipeline)
        while not event.is_set():
            ret, frame = self._cap.read()
            if not ret:
                warnings.warn("Make sure to run gstreamer client on each Jetson Nano.")
                warnings.warn("Make sure to compile opencv from source not from pip install.")
                self.close()

            if frame is not None:
                self.latest_frame = frame.copy()

        print(f"Capturing Thread Port: {self._port} Stopped.")
