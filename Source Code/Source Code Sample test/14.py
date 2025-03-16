import argparse
from datetime import datetime
from time import sleep
import numpy as np
import pyaudio
import threading
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import tkinter as tk
from pyfiglet import Figlet

class HearingTest:
    def __init__(self, root):
        self.root = root
        self.signal = None
        self.left_data = []
        self.right_data = []
        self.detected = False
        self.previous_results = None
        self.paused = False

    def player(self, p, repeat=1, ear='both'):
        """Plays sounds with different frequencies and volume levels"""
        volumes = [0, 10, 20, 30, 40, 50, 60, 70, 80, 90]  # Adjusted volume levels in dB
        frequencies = [125, 250, 500, 1000, 2000]  # Adjusted frequencies in Hz

        # Repeat each frequency based on the provided argument
        frequencies = np.repeat(frequencies, repeat)

        stream = p.open(format=pyaudio.paFloat32,
                        channels=1,
                        rate=44100,
                        output=True)

        sleep(0.1)
        for freq in frequencies:
            if self.paused:
                while self.paused:
                    sleep(1)
            self.detected = False
            for vol in volumes:
                print(f"Playing frequency: {freq} Hz at volume: {vol} dB for {ear} ear")
                self.signal = [freq, vol, datetime.now()]
                audio_data = (np.sin(2 * np.pi * np.arange(44100 * 0.5) * freq / 44100)).astype(np.float32)
                if ear == 'both' or ear == 'left':
                    audio_data_left = audio_data * 10**(vol / 20)
                if ear == 'both' or ear == 'right':
                    audio_data_right = audio_data * 10**(vol / 20)
                if ear == 'both':
                    stream.write(audio_data_left.tobytes())
                    stream.write(audio_data_right.tobytes())
                elif ear == 'left':
                    stream.write(audio_data_left.tobytes())
                elif ear == 'right':
                    stream.write(audio_data_right.tobytes())
                if self.detected:
                    break
            sleep(2)

        stream.stop_stream()
        stream.close()

    def listener(self):
        """Listens to user input"""
        while True:
            r = input()
            if self.signal:
                d = self.signal + [datetime.now()]
                print(f'Recording event: {d}')
                if d[0] == 125:  # Assuming 125 Hz is played first
                    self.left_data.append(d)
                else:
                    self.right_data.append(d)
                self.detected = True

    def greeting(self, p, opening=True):
        """Plays simple greeting to check sound"""
        frequencies = [261, 329, 391]
        durations = [0.2, 0.2, 0.5]
        stream = p.open(format=pyaudio.paFloat32,
                        channels=1,
                        rate=44100,
                        output=True)
        sleep(0.1)
        if opening:
            for freq, duration in zip(frequencies, durations):
                audio_data = (np.sin(2 * np.pi * np.arange(int(44100 * duration)) * freq / 44100)).astype(np.float32)
                stream.write((audio_data * 0.5).tobytes())
        else:
            for freq, duration in zip(frequencies[::-1], durations):
                audio_data = (np.sin(2 * np.pi * np.arange(int(44100 * duration)) * freq / 44100)).astype(np.float32)
                stream.write((audio_data * 0.5).tobytes())

        stream.stop_stream()
        stream.close()

    def analyse_results(self, data, ear):
        """Stores and visualizes results"""
        now = datetime.now()

        # Load data to DataFrame
        df = pd.DataFrame(data, columns=['frequency', 'volume', 'played', 'heard'])
        df['reaction_time'] = (df['heard'] - df['played']).dt.microseconds // 1000

        # Calculate average reaction time
        avg_reaction_time = df['reaction_time'].mean()

        # Calculate frequency-specific hearing thresholds
        hearing_thresholds = []
        for freq in [125, 250, 500, 1000, 2000, 4000, 8000]:
            thresholds = df[df['frequency'] == freq]['volume'].tolist()
            if len(thresholds) > 0:
                mean_thr = np.mean([thr for thr in thresholds if thr is not None])  # Ignore None values
                hearing_thresholds.append((freq, mean_thr))
            else:
                hearing_thresholds.append((freq, None))

        # Calculate overall hearing capacity
        overall_hearing_capacity = sum([1 for freq, thr in hearing_thresholds if thr is not None and thr >= 20]) / len(hearing_thresholds) * 100

        # Save data
        df.to_csv(f'./results_{ear}_{now:%Y%m%d%H%M%S}_data.csv', index=None)

        # Create audiogram
        audiogram_colors = {
            'normal': '#FFFFFF',
            'slight': '#FF0000',
            'mild': '#FF8000',
            'moderate': '#FFFF00',
            'moderately_severe': '#80FF00',
            'severe': '#00FF80',
            'profound': '#0080FF'
        }
        audiogram_labels = {
            'normal': 'Normal',
            'slight': 'Slight',
            'mild': 'Mild',
            'moderate': 'Moderate',
            'moderately_severe': 'Moderately Severe',
            'severe': 'Severe',
            'profound': 'Profound'
        }

        fig, ax = plt.subplots(1)
        for freq, thr in hearing_thresholds:
            if thr is None:
                continue
            if thr >= 0 and thr < 20:
                color = audiogram_colors['normal']
                label = audiogram_labels['normal']
            elif thr >= 20 and thr < 40:
                color = audiogram_colors['slight']
                label = audiogram_labels['slight']
            elif thr >= 40 and thr < 55:
                color = audiogram_colors['mild']
                label = audiogram_labels['mild']
            elif thr >= 55 and thr < 70:
                color = audiogram_colors['moderate']
                label = audiogram_labels['moderate']
            elif thr >= 70 and thr < 90:
                color = audiogram_colors['moderately_severe']
                label = audiogram_labels['moderately_severe']
            elif thr >= 90 and thr < 120:
                color = audiogram_colors['severe']
                label = audiogram_labels['severe']
            else:
                color = audiogram_colors['profound']
                label = audiogram_labels['profound']

            ax.plot(freq, thr, marker='o', color=color, label=label)

        ax.set(title=f"Audiogram for {ear} ear", xlim=[100, 10000], ylim=[-10, 100], xscale='log', xlabel='Frequency (Hz)', ylabel='Volume (dB)')
        ax.grid()
        ax.legend()
        plt.savefig(f'./results_{ear}_{now:%Y%m%d%H%M%S}_audiogram.png')
        plt.show()
        plt.clf()
        plt.close()

        # Print results
        print(f"Average Reaction Time: {avg_reaction_time:.2f} ms")
        print(f"Overall Hearing Capacity: {overall_hearing_capacity:.2f}%")

        return df

    def run_test(self):
        parser = argparse.ArgumentParser()
        parser.add_argument('-r', '--repeat', help='Number of times each frequency is repeated', type=int, default=1)  # Change default value to 1
        args = parser.parse_args()

        f = Figlet(font='slant')
        print(f.renderText('HEARING TEST'))

        print('*' * 67)
        print('* Welcome to Hearing Test                                         *')
        print('*                                                                 *')
        print('* Please put on your headphones.                                  *')
        print('* Hit [ENTER] when you start hearing pulsing sound.               *')
        print('*' * 67)

        p = pyaudio.PyAudio()
        # Play greeting
        self.greeting(p, opening=True)

        print('Test will start in 5 seconds...')
        sleep(5)
        # Start listener
        p2 = threading.Thread(target=self.listener, daemon=True)
        p2.start()

        # Run test for the left ear
        print('Testing left ear...')
        self.player(p, repeat=args.repeat, ear='left')

        # Analyse and visualize results for the left ear
        left_df = self.analyse_results(self.left_data, 'left')

        # Reset data for the next test
        self.left_data = []

        # Play greeting
        self.greeting(p, opening=False)

        # Run test for the right ear
        print('Testing right ear...')
        self.player(p, repeat=args.repeat, ear='right')

        # Analyse and visualize results for the right ear
        right_df = self.analyse_results(self.right_data, 'right')
        self.right_data = []

        print('Test is finished. Please check visualizations.')

    def pause_test(self):
        self.paused = True

    def resume_test(self):
        self.paused = False

def main():
    root = tk.Tk()
    root.title("Hearing Test")

    app = HearingTest(root)
    run_button = tk.Button(root, text="Start Test", command=app.run_test)
    run_button.pack()

    pause_button = tk.Button(root, text="Pause Test", command=app.pause_test)
    pause_button.pack()

    resume_button = tk.Button(root, text="Resume Test", command=app.resume_test)
    resume_button.pack()

    root.mainloop()

if __name__ == "__main__":
    main()
