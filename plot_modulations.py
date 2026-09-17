
import pathlib
import matplotlib.pyplot as plt

from autofitter import plot_modulation
from autofitter import read_csv_data

path = pathlib.Path("ergs")
file_iterator = path.iterdir()

measurements = []

for directory in file_iterator:
    year = directory.name[0:4]
    month = directory.name[4:6]
    day = directory.name[6:8]
    measurement_number = directory.name[9:11]

    filename = f"{str(directory)}\\modulat.dat"
    try:
        data = read_csv_data(filename, " ")
    except:
        print(f"data file not found in {directory}")
        continue

    measurements.append((data, f"{year}-{str(month).zfill(2)}-{str(day).zfill(2)} {str(measurement_number).zfill(2)}"))

    plot_modulation(data)

    figure_name = f"figures\\{year}{str(month).zfill(2)}{str(day).zfill(2)}_{str(measurement_number).zfill(2)}.png"
    plt.savefig(figure_name)


figure, (ax1, ax2) = plt.subplots(2, 1, figsize=(9, 2*4.8))

for measurement in measurements:

    data = measurement[0]
    measurement_name = measurement[1]

    ax1.plot(data["OPD"], data["Modulation"], label=measurement_name)

    ax2.plot(data["OPD"], data["Phase"], label=measurement_name)


ax1.set_ylabel("Modulation amplitude")
ax1.set_xlabel("OPD (cm)")
ax1.axhline(y=1, c="black")
ax1.tick_params(right=True)
ax1.set_xlim(0, 45)
ax1.set_ylim(0.95, 1.05)
#ax1.legend()
ax1.legend(bbox_to_anchor=(1.05, 1), loc="upper left", borderaxespad=0.)

ax2.set_ylabel("Phase error (rad)")
ax2.set_xlabel("OPD (cm)")
ax2.axhline(y=0, c="black")
ax2.tick_params(right=True)
ax2.set_xlim(0, 45)
ax2.set_ylim(-0.01, 0.01)
ax2.legend(bbox_to_anchor=(1.05, 1), loc="upper left", borderaxespad=0.)

plt.subplots_adjust(left=0.15, right=0.75)

figure_name = f"figures\\compilation.png"
plt.savefig(figure_name)

