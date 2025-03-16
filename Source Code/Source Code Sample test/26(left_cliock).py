import argparse
from datetime import datetime
from time import sleep
import numpy as np
import pyaudio
import threading
import pandas as pd
import matplotlib.pyplot as plt
from pynput.mouse import Listener, Button

# Use interactive backend for displaying plots in a separate window
plt.switch_backend('TkAgg')  # You may need to install TkAgg backend if not already installed

class HearingTest:
    def __init__(self):
        self.signal = None
        self.right_data = []
        self.detected = False

    def player(self, p, repeat=1, ear='right'):
        """Plays sounds with different frequencies and volume levels"""
        volumes = [0, 10, 20, 30, 40, 50, 60, 70, 80, 90]  # Adjusted volume levels in dB
        frequencies = [125, 250, 500, 1000, 2000, 4000, 8000]  # Adjusted frequencies in Hz

        # Repeat each frequency based on the provided argument
        frequencies = np.repeat(frequencies, repeat)

        stream = p.open(format=pyaudio.paFloat32,
                        channels=1,
                        rate=44100,
                        output=True)

        sleep(0.1)
        for freq in frequencies:
            self.detected = False
            for vol in volumes:
                print(f"Playing frequency: {freq} Hz at volume: {vol} dB for {ear} ear")
                self.signal = [freq, vol, datetime.now()]
                audio_data = (np.sin(2 * np.pi * np.arange(44100 * 0.5) * freq / 44100)).astype(np.float32)
                audio_data = audio_data * 10**(vol / 20)
                stream.write(audio_data.tobytes())
                sleep(2)  # Adding 2-second pause after playing each volume level
                if self.detected:
                    break
            sleep(2)  # Adding 2-second pause after playing each frequency

        stream.stop_stream()
        stream.close()

    def on_click(self, x, y, button, pressed):
        """Callback function for mouse clicks"""
        if button == Button.left and pressed:
            if self.signal:
                d = self.signal + [datetime.now()]
                print(f'Recording event: {d}')
                self.right_data.append(d)
                self.detected = True

    def listener(self):
        """Listens to mouse clicks"""
        with Listener(on_click=self.on_click) as listener:
            listener.join()

    def analyse_results(self, data, ear):
        """Stores and visualizes results"""
        now = datetime.now()

        # Load data to DataFrame
        df = pd.DataFrame(data, columns=['frequency', 'volume', 'played', 'heard'])
        df['reaction_time'] = (df['heard'] - df['played']).dt.microseconds // 1000

        # Create audiogram chart
        audiogram_fig, ax1 = plt.subplots(1)
        ax1.plot(df['frequency'], df['volume'], marker='x', linestyle='-', color='black')
        ax1.set(title=f"Audiogram for {ear} ear", xlim=[100, 9000], ylim=[-10, 90], xticks=[125, 250, 500, 1000, 2000, 4000, 8000], yticks=[-10, 0, 10, 20, 30, 40, 50, 60, 70, 80, 90], xlabel='Pitch (frequency in Hz)', ylabel='Hearing Level in decibels (volume in dB)')
        ax1.grid(True)

        # Add colored rows for different hearing loss stages
        ax1.axhspan(-10, 15, facecolor='green', alpha=0.3, label='Normal Hearing (0-15 dB)')
        ax1.axhspan(16, 25, facecolor='yellow', alpha=0.3, label='Slight Hearing Loss (16-25 dB)')
        ax1.axhspan(26, 40, facecolor='orange', alpha=0.3, label='Mild Hearing Loss (26-40 dB)')
        ax1.axhspan(41, 55, facecolor='red', alpha=0.3, label='Moderate Hearing Loss (41-55 dB)')
        ax1.axhspan(56, 70, facecolor='purple', alpha=0.3, label='Moderately Severe Hearing Loss (56-70 dB)')
        ax1.axhspan(71, 90, facecolor='brown', alpha=0.3, label='Severe Hearing Loss (71-90 dB)')
        ax1.axhspan(91, 120, facecolor='black', alpha=0.3, label='Profound Hearing Loss (91 dB or greater)')

        ax1.legend()
        ax1.set_xlabel('Pitch (frequency in Hz)', weight='bold')
        ax1.set_ylabel('Hearing Level in decibels (volume in dB)', weight='bold')
        plt.tight_layout()

        # Save and show audiogram chart
        audiogram_fig.savefig(f'./results_{ear}_{now:%Y%m%d%H%M%S}_audiogram.png')
        plt.show()
        plt.clf()
        plt.close()

        return df

    def create_excel_sheet(self, data):
        """Create an Excel sheet with the specified table format"""
        now = datetime.now()
        df = pd.DataFrame(data, columns=['Sl. No', 'Pitch (Frequency Hz)', 'Hearing Level (Volume dB)', 'Hearing Loss Range'])
        df.to_excel(f'./results_{now:%Y%m%d%H%M%S}.xlsx', index=None)
        print("Excel sheet created successfully.")

    def run_test(self):
        parser = argparse.ArgumentParser()
        parser.add_argument('-r', '--repeat', help='Number of times each frequency is repeated', type=int, default=1)  # Change default value to 1
        args = parser.parse_args()

        print('*' * 67)
        print('* Welcome to Hearing Test                                         *')
        print('*                                                                 *')
        print('* Please put on your headphones.                                  *')
        print('* Click the left mouse button when you start hearing pulsing sound.*')
        print('*' * 67)

        p = pyaudio.PyAudio()
        # Start listener
        p2 = threading.Thread(target=self.listener, daemon=True)
        p2.start()

        # Run test for the right ear
        print('Testing right ear...')
        self.player(p, repeat=args.repeat, ear='right')

        # Analyse and visualize results for the right ear
        right_df = self.analyse_results(self.right_data, 'right')
        self.right_data = []

        # Create Excel sheet
        data = [[i+1, freq, vol, self.get_hearing_loss_range(vol)] for i, (freq, vol) in enumerate(zip(right_df['frequency'], right_df['volume']))]
        self.create_excel_sheet(data)

        print('Test is finished. Please check visualizations and Excel sheet.')

    def get_hearing_loss_range(self, volume):
        """Return the hearing loss range based on the volume"""
        if volume >= 0 and volume <= 15:
            return 'Normal Hearing (0-15 dB)'
        elif volume <= 25:
            return 'Slight Hearing Loss (16-25 dB)'
        elif volume <= 40:
            return 'Mild Hearing Loss (26-40 dB)'
        elif volume <= 55:
            return 'Moderate Hearing Loss (41-55 dB)'
        elif volume <= 70:
            return 'Moderately Severe Hearing Loss (56-70 dB)'
        elif volume <= 90:
            return 'Severe Hearing Loss (71-90 dB)'
        else:
            return 'Profound Hearing Loss (91 dB or greater)'

def display_excel_table_as_image(excel_file_path):
    df = pd.read_excel(excel_file_path)

    fig, ax = plt.subplots(figsize=(8, 6))
    ax.axis('tight')
    ax.axis('off')
    ax.table(cellText=df.values, colLabels=df.columns, loc='center')
    plt.savefig('excel_table.png')
    plt.show()

if __name__ == '__main__':
    test = HearingTest()
    test.run_test()

    # Display Excel table as image
    excel_file_path = f'./results_{datetime.now():%Y%m%d%H%M%S}.xlsx'
    display_excel_table_as_image(excel_file_path)
