"""
Matt Clarke 2021.
Example script to demonstrate usage of the Drone class.

Keyboard controls:
    ↑ / ↓: Throttle
    ← / →: Roll
    W / S: Pitch
    A / D: Yaw

Dependencies:
    - getkey

This program is free software: you can redistribute it and/or modify it under
the terms of the GNU General Public License as published by the Free Software
Foundation, either version 3 of the License, or (at your option) any later
version.

This program is distributed in the hope that it will be useful, but WITHOUT
ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.
You should have received a copy of the GNU General Public License along with
this program. If not, see <http://www.gnu.org/licenses/>.
"""

from enum import Enum
import threading
import time
from getkey import getkey, keys

from drone import Drone
from camera_controller.Camara import Camera

class State(Enum):
    SOCKET_CREATE     = 1
    SOCKET_CONNECTED  = 2
    TAKEOFF           = 3
    CONTROL_LOOP      = 4
    INTERRUPT         = 5

class Controller():
    def __init__(self):
        self.state = State.SOCKET_CREATE

        self.controlState = {
            'throttle': 0.5,
            'pitch': 0.5,
            'roll': 0.5,
            'yaw': 0.5
        }

        self.lastKeyChange = 0

        self.camera = Camera()
        self.video = threading.Thread(target=self.camera.StartCamera, daemon=True)

        self.drone = Drone()

        self.teclas = False

    # Thread used to monitor keyboard input for control state
    def keycodeThread(self):

        while self.state != State.INTERRUPT and self.teclas:

            key = getkey(blocking=True)

            # throttle
            if key == keys.UP:
                self.controlState['throttle'] = 0.85
            elif key == keys.DOWN:
                self.controlState['throttle'] = 0.0
            else:
                self.controlState['throttle'] = 0.5

            # roll
            if key == keys.LEFT:
                self.controlState['roll'] = 0.3
            elif key == keys.RIGHT:
                self.controlState['roll'] = 0.7
            else:
                self.controlState['roll'] = 0.5

            # pitch
            if key == 'w':
                self.controlState['pitch'] = 0.3
            elif key == 's':
                self.controlState['pitch'] = 0.7
            else:
                self.controlState['pitch'] = 0.5

            # yaw - note: its 100% or 0% for yaw, no scaling
            if key == 'a':
                self.controlState['yaw'] = 0.0
            elif key == 'd':
                self.controlState['yaw'] = 1.0
            else:
                self.controlState['yaw'] = 0.5

            self.lastKeyChange = int(round(time.time() * 1000))

    def keytimeoutThread(self):
        # workaround for some weird blocking stuff with
        # getting currently pressed keys

        while self.state != State.INTERRUPT and self.teclas:
            if self.lastKeyChange > 0:
                now = int(round(time.time() * 1000))

                if now - self.lastKeyChange > 200:
                    self.controlState = {
                        'throttle': 0.5,
                        'pitch': 0.5,
                        'roll': 0.5,
                        'yaw': 0.5
                    }
    def StopControlTeclas(self):
        self.teclas = False

    def InitControlTeclas(self):
        self.teclas = True

        # Setup keycode thread
        keycodes = threading.Thread(target=self.keycodeThread, daemon=True)
        keycodes.start()

        # Hack for some input blocking related stuff
        keycodesHack = threading.Thread(target=self.keytimeoutThread, daemon=True)
        keycodesHack.start()

    def IniciaCam(self):  
        if (not self.video.is_alive()):
            self.video.start()
        else:
            print("ERROR: videocam is already active")

    def Init(self):
        state_ant = 0
        # Create control loop
        try:
            while True:
                if (self.state != state_ant):
                    print (f"STATE -> {self.state}")

                if self.state == State.SOCKET_CREATE:

                    if self.drone.connect():
                        self.state = State.SOCKET_CONNECTED

                elif self.state == State.SOCKET_CONNECTED:
                    print('Socket connected')

                    try:
                        self.drone.setup()
                        print("Setup drone completed")
                        time.sleep(1)
                        #proceso = subprocess.Popen(['python', './src/libs/camera_controller/Camara.py'])
                        self.IniciaCam()
                        print("Camera connected")
                        self.state = State.TAKEOFF
                    except KeyboardInterrupt as e:
                        raise e
                    except Exception as e:
                        print("Error Socket connected -> " + str(e))
                        self.state = State.SOCKET_CREATE

                elif self.state == State.TAKEOFF:
                    if (self.controlState['throttle'] != 0.5 or
                        self.controlState['pitch'] != 0.5 or
                        self.controlState['roll'] != 0.5 or
                        self.controlState['yaw'] != 0.5):

                        startTime = time.time_ns() // 1_000_000

                        while (time.time_ns() // 1_000_000) - startTime < 500:
                            self.drone.takeoff()
                            time.sleep(0.01)

                        self.state = State.CONTROL_LOOP
                    else:
                        self.drone.idle()

                elif self.state == State.CONTROL_LOOP:
                    try:
                        self.drone.control(self.controlState['throttle'], self.controlState['pitch'], self.controlState['roll'], self.controlState['yaw'])
                    except KeyboardInterrupt as e:
                        raise e
                    except Exception as e:
                        self.state = State.SOCKET_CREATE

                state_ant = self.state

        except KeyboardInterrupt as e:
            self.state = State.INTERRUPT

if __name__ == '__main__':
    controlador = Controller()
    controlador.Init()