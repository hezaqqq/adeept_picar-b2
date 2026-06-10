import time
import argparse
from gpiozero import InputDevice

# Initialisation de la classe LineFollower pour les capteurs de suivi de ligne
class LineFollower:
    def __init__(self):
        self.line_pin_left = 22
        self.line_pin_middle = 27
        self.line_pin_right = 17

        self.left = InputDevice(pin=self.line_pin_right)
        self.middle = InputDevice(pin=self.line_pin_middle)
        self.right = InputDevice(pin=self.line_pin_left)

    def run(self):
        status_right = self.right.value
        status_middle = self.middle.value
        status_left = self.left.value
        print('left: %d   middle: %d   right: %d' %(status_right,status_middle,status_left))


if __name__ == '__main__':
    try:
      line_follower = LineFollower()
      while 1:
        line_follower.run()
        time.sleep(0.3)
    except KeyboardInterrupt:
        pass


