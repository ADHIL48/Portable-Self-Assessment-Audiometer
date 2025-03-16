import argparse
from datetime import datetime
from time import sleep
from pysine import sine
import pyaudio
import threading
from pyfiglet import Figlet
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

signal = None
data_left_ear = []
data_right_ear = []
detected_left_ear = False
detected_right_ear = False

def player(p, repeat=2, ear='left'):
    """Plays sounds with different frequencies and volume levels for left or right ear"""
    global signal
    global detected_left_ear
    global detected_right_ear

    volumes = [0, 10, 20, 30, 40, 50, 60, 70, 80, 90, 100]  # Volume levels in dB
    frequencies = [125, 250, 500, 1000, 2000, 4000, 8000]  # Frequency levels in Hz

    # shuffle frequencies
    frequencies = np.repeat(frequencies, repeat)
    np.random.shuffle(frequencies)

    stream = p.open(format=pyaudio.paFloat32,
                    channels=1,
                    rate=44100,
                    output=True)

    sleep(0.1)
    for freq in frequencies:
        detected = False
        for vol in volumes:
            print(freq, vol)
            for n in range(3):
                signal = [freq, vol, datetime.now()]
                amplitude = 10 ** (vol / 20)  # Convert dB to linear amplitude
                audio_data = (amplitude * np.sin(2 * np.pi * np.arange(44100 * 0.5) * freq / 44100)).astype(np.float32)
                stream.write(audio_data.tobytes())
                if ear == 'left':
                    if detected_left_ear:
                        break
                else:
                    if detected_right_ear:
                        break
            if ear == 'left':
                if detected_left_ear:
                    break
            else:
                if detected_right_ear:
                    break
        sleep(2)

    stream.stop_stream()
    stream.close()


def listener():
    """Listens to user input"""
    global signal
    global data_left_ear
    global data_right_ear
    global detected_left_ear
    global detected_right_ear

    while 1:
        r = input()
        if signal:
            d = signal + [datetime.now()]
            print(f'Recording event: {d}')
            if r.lower() == 'l':
                data_left_ear.append(d)
                detected_left_ear = True
            elif r.lower() == 'r':
                data_right_ear.append(d)
                detected_right_ear = True


def greeting(p, opening=True):
    """Plays simple greeting to check sound"""
    frequencies = [261, 329, 391]  # Default frequencies for greeting
    durations = [0.2, 0.2, 0.5]  # Default durations for greeting
    stream = p.open(format=pyaudio.paFloat32,
                    channels=1,
                    rate=44100,
                    output=True)
    sleep(0.1)
    if opening:
        for freq, duration in zip(frequencies, durations):
            amplitude = 0.5  # Default amplitude for greeting
            audio_data = (amplitude * np.sin(2 * np.pi * np.arange(int(44100 * duration)) * freq / 44100)).astype(np.float32)
            stream.write(audio_data.tobytes())
    else:
        for freq, duration in zip(frequencies[::-1], durations):
            amplitude = 0.5  # Default amplitude for greeting
            audio_data = (amplitude * np.sin(2 * np.pi * np.arange(int(44100 * duration)) * freq / 44100)).astype(np.float32)
            stream.write(audio_data.tobytes())

    stream.stop_stream()
    stream.close()


def analyse_results(data, ear):
    now = datetime.now()
    """Stores and visualizes results"""
    # load data to DataFrame
    df = pd.DataFrame(data, columns=['frequency', 'volume', 'played', 'heard'])

    # save data
    df.to_csv(f'./results_{now:%Y%m%d%H%M%S}_{ear}_data.csv', index=None)

    # visualize results
    plt.figure()
    plt.plot(df['frequency'].astype(str), df['volume'], marker='x')
    plt.title(f"{ear.capitalize()} Ear Hearing Capacity")
    plt.ylim([0, 100])
    plt.xlabel('Frequency (Hz)')
    plt.ylabel('Volume (dB)')
    plt.gca().invert_yaxis()
    plt.savefig(f'./results_{now:%Y%m%d%H%M%S}_{ear}_capacity.png')
    plt.show()

    return df


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-r', '--repeat', help='Number of times each frequency is repeated', required=False, default=2)
    args = parser.parse_args()

    f = Figlet(font='slant')
    print(f.renderText('HEARING TEST'))

    print('*' * 67)
    print('* Welcome to Hearing Test                                         *')
    print('*                                                                 *')
    print('* Please put on your headphones.                                  *')
    print('* Hit [ENTER] when you start hearing pulsing sound.               *')
    print('* Press "L" when you hear the sound in the left ear.              *')
    print('* Press "R" when you hear the sound in the right ear.             *')
    print('*' * 67)

    p = pyaudio.PyAudio()
    # play greeting
    greeting(p, opening=True)

    print('Left Ear Test will start in 5 seconds...')
    sleep(5)
    # start listener for left ear
    p2_left_ear = threading.Thread(target=listener, daemon=True)
    p2_left_ear.start()
    # start player for left ear
    player(p, repeat=args.repeat, ear='left')

    print('Now, Right Ear Test will start in 5 seconds...')
    sleep(5)
    # start listener for right ear
    p2_right_ear = threading.Thread(target=listener, daemon=True)
    p2_right_ear.start()
    # start player for right ear
    player(p, repeat=args.repeat, ear='right')

    # play greeting
    greeting(p, opening=False)

    # Analyze and display results for left ear
    analyse_results(data_left_ear, ear='left')
    print('Left Ear Test is finished. Please check visualizations.')

    # Analyze and display results for right ear
    analyse_results(data_right_ear, ear='right')
    print('Right Ear Test is finished. Please check visualizations.')
