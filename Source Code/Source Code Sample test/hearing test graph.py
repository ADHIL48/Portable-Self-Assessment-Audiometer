import pandas as pd
import matplotlib.pyplot as plt

# Sample data
data = {
    'frequency': [125, 250, 750, 1000],
    'volume': [0, 10, 20, 30],
    'reaction_time': [100, 90, 80, 70]
}

df = pd.DataFrame(data)

# Plotting hearing capacity
plt.figure(figsize=(10, 5))
plt.subplot(1, 2, 1)
plt.plot(df['frequency'], df['volume'], marker='x')
plt.title('Hearing Capacity')
plt.xlabel('Frequency (Hz)')
plt.ylabel('Volume (dB)')
plt.grid(True)

# Plotting reaction time
plt.subplot(1, 2, 2)
plt.plot(df['frequency'], df['reaction_time'], marker='x', color='orange')
plt.title('Reaction Time')
plt.xlabel('Frequency (Hz)')
plt.ylabel('Reaction Time (ms)')
plt.grid(True)

plt.tight_layout()
plt.show()
