
import matplotlib.pyplot as plt

raw_x = []
raw_mod = []
raw_phase = []

#raw_filename = "C:\\Users\\vierros\\Programs\\lft148dsk-distr\\lft148\\examples-win\\TCCON\\lamp\\HCl\\prescribed\\evac\\ergs\\specre01.dat"

raw_filename = "C:\\Users\\vierros\\Programs\\lft148dsk-distr\\lft148\\ergs\\20210601_01_raw\\specre05.dat"
with open(raw_filename, "r") as file:
    lines = file.readlines()
for line in lines[1:]:
    values = line.strip().split(" ")
    while "" in values:
        values.remove("")
    raw_x.append(float(values[0]))
    raw_mod.append(float(values[1]))
    raw_phase.append(float(values[2]))



plt.plot(raw_x, raw_mod)
plt.show()