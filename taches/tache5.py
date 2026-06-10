from gpiozero import DistanceSensor
from time import sleep

# Initialisation de la classe Distance pour le capteur à ultrasons
class Distance:

    def __init__(self):
        self.Tr = 23
        self.Ec = 24
        # Create a DistanceSensor object with a 2 meter maximum detection range.
        self.sensor = DistanceSensor(echo=self.Ec, trigger=self.Tr, max_distance=2)

    def checkdist(self):
        return self.sensor.distance * 1000  # Convert meters to millimeters.


if __name__ == "__main__":
    distance_sensor = Distance()
    while True:
        distance = distance_sensor.checkdist()
        print("%.2f mm" % distance)
        sleep(0.05)


