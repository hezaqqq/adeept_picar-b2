import time
from robotLight import RobotWS2812 

class LEDController:
    def __init__(self, led_count=14):
        self.led_driver = RobotWS2812()
        self.led_count = led_count
        
        self.led_red_offset = 0
        self.led_green_offset = 1
        self.led_blue_offset = 2

        self.led_brightness_list = [255] * self.led_count
        self.led_original_color = [0] * (self.led_count * 3)
        self.led_color = [0] * (self.led_count * 3)
    
    def set_ledpixel(self, index, r, g, b, brightness=None):
        if index < 0 or index >= self.led_count:
            print(f"LED {index} invalide(0-{self.led_count-1}).")
            return 
            
        if brightness is not None:
            self.led_brightness_list[index] = brightness
            
        current_brightness = self.led_brightness_list[index]
        
        p = [0, 0, 0]
        p[self.led_red_offset] = round(r * current_brightness / 255)
        p[self.led_green_offset] = round(g * current_brightness / 255)
        p[self.led_blue_offset] = round(b * current_brightness / 255)
        
        self.led_original_color[index * 3 + self.led_red_offset] = r
        self.led_original_color[index * 3 + self.led_green_offset] = g
        self.led_original_color[index * 3 + self.led_blue_offset] = b
        
        for i in range(3):
            self.led_color[index * 3 + i] = p[i]

    def set_led_color_data(self, index, r, g, b, brightness=None):
        self.set_ledpixel(index, r, g, b, brightness) 

    def turn_off_all(self):
        for i in range(self.led_count):
            self.led_original_color[i*3 : i*3+3] = [0, 0, 0]
            self.led_color[i*3 : i*3+3] = [0, 0, 0]
            self.led_brightness_list[i] = 255


if __name__ == "__main__":
    controller = LEDController(led_count=14)
    controller.turn_off_all()
    
    print("Format : <n°LED> <R> <G> <B> [Intensité]")
    print("-" * 45)

    while True:
        try:
            commande = input("\nEntrez votre commande : ").strip()
            
            if commande.upper() in ["Q", "0"]:
                controller.turn_off_all()
                break
                
            elements = commande.split()
            if len(elements) < 4:
                print("Format invalide")
                continue
                
            index = int(elements[0])
            r = int(elements[1])
            g = int(elements[2])
            b = int(elements[3])
            
            if len(elements) >= 5:
                brightness = int(elements[4])
            else:
                brightness = 255

            controller.set_led_color_data(index, r, g, b, brightness)
            print(f"LED {index} -> ({r}, {g}, {b}) Intensité: {brightness}")

        except KeyboardInterrupt:
            controller.turn_off_all()
            break

        except Exception as e:
            print(f"Erreur : {e}")