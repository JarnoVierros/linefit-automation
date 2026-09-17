
import matplotlib.pyplot as plt

raw_x = []
raw_mod = []
raw_phase = []
leveled_x = []
leveled_mod = []
leveled_phase = []

raw_filename = "ergs\\20210601_01_raw\\modulat.dat"
with open(raw_filename, "r") as file:
    lines = file.readlines()
for line in lines[1:]:
    values = line.strip().split(" ")
    while "" in values:
        values.remove("")
    raw_x.append(float(values[0]))
    raw_mod.append(float(values[1]))
    raw_phase.append(float(values[2]))

leveled_filename = "ergs\\20210601_01_leveled\\modulat.dat"
with open(leveled_filename, "r") as file:
    lines = file.readlines()
for line in lines[1:]:
    values = line.strip().split(" ")
    while "" in values:
        values.remove("")
    leveled_x.append(float(values[0]))
    leveled_mod.append(float(values[1]))
    leveled_phase.append(float(values[2]))

mod_diff = []
phase_diff = []
for i in range(len(raw_x)):
    mod_diff.append(raw_mod[i]-leveled_mod[i])
    phase_diff.append(raw_phase[i]-leveled_phase[i])


figure, (ax1, ax2) = plt.subplots(2, 1, figsize=(7, 2*4.8))
ax1.plot(leveled_x, mod_diff)
ax1.set_ylabel("leveled amplitude - raw amplitude")
ax1.set_xlabel("OPD (cm)")
ax1.axhline(y=0, c="black")
ax1.tick_params(right=True)
ax1.set_ylim(-0.05, 0.05)

ax2.plot(raw_x, phase_diff)
ax2.set_ylabel("leveled phase error - raw phase error")
ax2.set_xlabel("OPD (cm)")
ax2.axhline(y=0, c="black")
ax2.tick_params(right=True)
ax2.set_ylim(-0.01, 0.01)

plt.subplots_adjust(left=0.15, right=0.85)

plt.show()