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
data = []
detected = False


def player(p, repeat=2):
    """Plays sounds with different frequencies and volume levels"""
    global signal
    global detected

    volumes = [0, 20, 40, 60, 80]
    frequencies = [125, 250, 500, 1000, 2000]

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
                audio_data = (np.sin(2 * np.pi * np.arange(44100 * 0.5) * freq / 44100)).astype(np.float32)
                audio_data *= vol / 100.0  # Scale the audio data to adjust volume
                stream.write(audio_data.tobytes())
                if detected:
                    break
            if detected:
                break
        sleep(2)

    stream.stop_stream()
    stream.close()


def listener():
    """Listens to user input"""
    global signal
    global data
    global detected

    while 1:
        r = input()
        if signal:
            d = signal + [datetime.now()]
            print(f'Recording event: {d}')
            data.append(d)
            detected = True


def greeting(p, opening=True):
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


def analyse_results(data):
    now = datetime.now()
    """Stores and visualizes results"""
    # load data to DataFrame
    df = pd.DataFrame(data, columns=['frequency', 'volume', 'played', 'heard'])
    df['reaction_time'] = (df['heard'] - df['played']).dt.microseconds // 1000

    # average multiple results
    df = df.groupby(['frequency']).mean().reset_index()

    # save data
    df.to_csv(f'./results_{now:%Y%m%d%H%M%S}_data.csv', index=None)

    # visualize results
    plt.figure()
    plt.plot(df['frequency'].astype(str), df['volume'], marker='x')
    plt.title(f"Hearing capacity")
    plt.ylim([0, 100])
    plt.xlabel('Hz')
    plt.ylabel('volume')
    plt.gca().invert_yaxis()
    plt.savefig(f'./results_{now:%Y%m%d%H%M%S}_capacity.png')

    plt.figure()
    plt.plot(df['frequency'].astype(str), df['reaction_time'], marker='x')
    plt.title(f"Reaction time")
    plt.xlabel('Hz')
    plt.ylabel('ms')
    plt.savefig(f'./results_{now:%Y%m%d%H%M%S}_reaction.png')

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
    print('*' * 67)

    p = pyaudio.PyAudio()
    # play greeting
    greeting(p, opening=True)

    print('Test will start in 5 seconds...')
    sleep(5)
    # start listener
    p2 = threading.Thread(target=listener, daemon=True)
    p2.start()
    # start player
    player(p, repeat=args.repeat)

    # play greeting
    greeting(p, opening=False)

    analyse_results(data)
    print('Test is finished. Please check visualizations.')
