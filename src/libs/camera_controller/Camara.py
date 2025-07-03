import cv2
import subprocess
import numpy as np

class Camera:
    def __init__(self, ffmpeg_path = r".\src\libs\camera_controller\ffmpeg\ffmpeg.exe", rtsp_url = f"rtsp://192.168.1.1:7070/webcam"):


        # Comando ffmpeg para capturar y enviar frames en formato raw (BGR)
        cmd = [
            ffmpeg_path,
            "-fflags", "nobuffer",            # Menor latencia
            "-flags", "low_delay",
            "-strict", "experimental",
            "-an",                            # Sin audio
            "-i", rtsp_url,
            "-f", "rawvideo",
            "-pix_fmt", "bgr24",
            "-"
        ]

        # Ejecutar FFmpeg y leer su salida binaria
        self.process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, bufsize=10**8)

        # Tamaño de cada frame (ajústalo al tamaño real del stream)
        self.width, self.height = 640, 360  # puedes probar con 1280x720 si el stream lo permite

        self.frame_size = self.width * self.height * 3  # porque bgr24 = 3 bytes por píxel

    def captura(self, name = "Frame"):
        cv2.imwrite(f"output/{name}.png", self.frame)

    def StartCamera(self):
        while True:
            raw_frame = self.process.stdout.read(self.frame_size)
            if len(raw_frame) != self.frame_size:
                break
            
            self.frame = np.flipud(np.frombuffer(raw_frame, dtype=np.uint8).reshape((self.height, self.width, 3)))

            cv2.imshow("Stream RTSP vía FFmpeg", self.frame)

            if cv2.waitKey(1) == 27:  # ESC para salir
                break
            
        self.process.terminate()
        cv2.destroyAllWindows()