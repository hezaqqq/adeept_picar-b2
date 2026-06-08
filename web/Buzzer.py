#!/usr/bin/env python3
# File name   : Buzzer.py
# Website     : www.Adeept.com
# Author      : Adeept / Gemini
# Date        : 2026/06/08
from gpiozero import TonalBuzzer
import time 
import threading

# Initialize TonalBuzzer on GPIO 18
tb = TonalBuzzer(18)

class Player(threading.Thread):
    def __init__(self, *args, **kwargs):
        # Note, Duration (seconds) at ~130 BPM march speed
        # "rest" turns off the buzzer temporarily.
        # "G2" is utilized at high volume/low pitch to replicate the 3 heavy march steps.
        
        self.VER_POST_MELODY = [
            # Measure 1: "Auf der Hei-de" (Pickup & entry)
            ["G4", 0.15], ["A4", 0.15], ["G4", 0.15], ["G4", 0.15],
            # Measure 2: "blüht ein klei-nes"
            ["C5", 0.30], ["C5", 0.15], ["C5", 0.15],
            # Measure 3: "Blü-me-lein"
            ["E5", 0.30], ["D5", 0.15], ["C5", 0.15],
            # Measure 4: (Instrumental/Vocal hold)
            ["G4", 0.30], ["A4", 0.15], ["G4", 0.15],
            
            # Measure 5: "und das heißt"
            ["B4", 0.15], ["C5", 0.15], ["D5", 0.30],
            # Measure 6: (Pause)
            ["rest", 0.15],
            
            # Measures 7-8: "E-RI-KA!" + The Three Massive March Stomps
            ["C5", 0.35], ["D5", 0.15], ["C5", 0.30], # "E-ri-ka!"
            ["rest", 0.10],
            ["G2", 0.12], ["rest", 0.08],             # STOMP 1
            ["G2", 0.12], ["rest", 0.08],             # STOMP 2
            ["G2", 0.12], ["rest", 0.30],             # STOMP 3
        ]

        self.CHORUS_MELODY = [
            # Measure 1: "Denn ihr Herz ist"
            ["G4", 0.15], ["C5", 0.30], ["B4", 0.15], ["B4", 0.15],
            # Measure 2: "vol-ler Sü-ßig-"
            ["B4", 0.15], ["B4", 0.15], ["A4", 0.15], ["B4", 0.15],
            # Measure 3: "-keit"
            ["C5", 0.30], ["G4", 0.15], ["A4", 0.15], ["G4", 0.15],
            
            # Measure 4: "Es ge-hört nur"
            ["B4", 0.30], ["C5", 0.15], ["D5", 0.15], ["D5", 0.15],
            # Measure 5: "mir al-lein"
            ["D5", 0.15], ["D5", 0.15], ["G5", 0.15], ["F5", 0.15], ["E5", 0.15],
            # Measure 6: (Fill)
            ["C5", 0.30], ["G4", 0.15], ["A4", 0.15], ["G4", 0.15],
        ]

        # Compile the entire structural song layout based directly on your request
        self.song_SONG = (
            self.VER_POST_MELODY + self.VER_POST_MELODY +  # Verse 1 (x2)
            self.CHORUS_MELODY +                           # Chorus 1
            self.VER_POST_MELODY +                         # Post-Chorus 1
            self.VER_POST_MELODY + self.VER_POST_MELODY +  # Verse 2 (x2)
            self.CHORUS_MELODY +                           # Chorus 2
            self.VER_POST_MELODY                           # Post-Chorus 2
        )

        self.__flag = threading.Event()
        self.__flag.clear()
        self.MusicMode = 0

        super(Player, self).__init__(*args, **kwargs)

    def play(self, tune):
        for note, duration in tune:
            if self.MusicMode == 0:
                break
            
            if note == "rest":
                tb.stop()
            else:
                tb.play(note)
                
            time.sleep(float(duration)) 
        tb.stop() 

    def start_playing(self):
        self.MusicMode = 1
        self.resume()

    def pause(self):
        self.__flag.clear()
        tb.stop()
        self.MusicMode = 0

    def resume(self):
        self.__flag.set()

    def run(self):
        while True:
            self.__flag.wait()
            try:
                self.play(self.song_SONG)
                # End of song execution auto-pause
                self.pause()
            except Exception as e:
                print(f"Playback error: {e}")
                self.pause()

if __name__ == "__main__":
    player = Player()
    player.start()
    
    print("Playing 'song' by Herms Niel (C-Major Tab Edition)...")
    player.start_playing()
    
    # Let the entire compilation play out or hit Ctrl+C to terminate early
    try:
        while player.MusicMode == 1:
            time.sleep(0.5)
    except KeyboardInterrupt:
        player.pause()
        print("\nPerformance halted by user.")