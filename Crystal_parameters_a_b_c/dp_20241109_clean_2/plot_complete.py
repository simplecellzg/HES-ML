import pandas as pd
import matplotlib.pyplot as plt

# Read data, skipping the first 71 lines
data = pd.read_csv('log.lammps.thermo', skiprows=1, delim_whitespace=True, header=None, on_bad_lines='skip')

# Select data from the first row to the last 10 rows before the end
data = data.iloc[:-1]  # Remove the last 10 rows

# Plot 1: Time vs Temperature
x1 = data.iloc[:, 0] * 0.001  # First column, time in ps
y1 = data.iloc[:, 1]          # Second column, temperature in K

plt.figure(figsize=(10, 5))
plt.plot(x1, y1, color='red', marker='o', linestyle='-')  # Red point-line graph
plt.xlabel('Time (ps)')
plt.ylabel('Temperature (K)')
plt.title('Temperature vs Time')
plt.savefig('plot1_temperature_vs_time.png')
plt.show()

# Plot 2: Temperature vs Energy
x2 = data.iloc[:, 1]          # Second column, temperature in K
y2 = data.iloc[:, 2]          # Third column, energy in eV

plt.figure(figsize=(10, 5))
plt.scatter(x2, y2, color='blue')  # Blue point-line graph
plt.xlabel('Temperature (K)')
plt.ylabel('Energy (eV)')
plt.title('Energy vs Temperature')
plt.savefig('plot2_energy_vs_temperature.png')
plt.show()
