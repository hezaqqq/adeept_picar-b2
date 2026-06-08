import time
from robotLight import RobotWS2812 

class LEDController:
    def __init__(self):
        self.led_driver = RobotWS2812()
        self.led_driver.LED_COUNT = 14
        self.colors_map = {
            'R': (255, 0, 0),
            'G': (0, 255, 0),
            'B': (0, 0, 255),
            'N': (0, 0, 0)
        }

    def control_led(self, led_no, color, intensity=255):
        if not (0 <= led_no < 14):
            print(f"Erreur : Le numéro de LED {led_no} est invalide (doit être entre 0 et 13).")
            return

        color = color.upper()
        if color not in self.colors_map:
            print(f"Erreur : Couleur '{color}' non reconnue. Utilisez R, G, B ou N.")
            return
        intensity = max(0, min(255, int(intensity)))
        base_r, base_g, base_b = self.colors_map[color]

        r = int((base_r * intensity) / 255)
        g = int((base_g * intensity) / 255)
        b = int((base_b * intensity) / 255)

        self.led_driver.strip.setPixelColor(led_no, (r << 16) | (g << 8) | b)
        self.led_driver.strip.show()

    def turn_off_all(self):
        """Éteint toutes les LED d'un coup."""
        for i in range(14):
            self.led_driver.strip.setPixelColor(i, 0)
        self.led_driver.strip.show()


if __name__ == "__main__":
    controller = LEDController()
    controller.turn_off_all()
    
    print("<n°LED> <Couleur> [Intensité]")
    print("-" * 30)

    while True:
        try:
            commande = input("\nEntrez votre commande : ").strip()
            
            if commande.upper() in ["Q", "0"]:
                controller.turn_off_all()
                break
                
            elements = commande.split()
            if len(elements) < 2:
                print("Format invalide. Rappel : <n°LED> <Couleur> [Intensité]")
                continue
                
            if not elements[0].isdigit():
                print("Le numéro de LED doit être un entier.")
                continue
            led_no = int(elements[0])
            color = elements[1]

            intensity = 255
            if len(elements) >= 3:
                if elements[2].isdigit():
                    intensity = int(elements[2])
                else:
                    print("L'intensité doit être un entier entre 0 et 255")

            controller.control_led(led_no, color, intensity)
            print(f"LED {led_no} -> Couleur {color.upper()} (Intensité: {min(max(0, intensity), 255)})")

        except KeyboardInterrupt:
            controller.turn_off_all()
            print("\nProgramme interrompu.")
            break
        except Exception as e:
            print(f"Une erreur est survenue : {e}")