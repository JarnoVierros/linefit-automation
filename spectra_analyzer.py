
import matplotlib.pyplot as plt
import datetime

from brukeropus import read_opus

filename_start = "C:\\Users\\vierros\\Programs\\lft148dsk-distr\\lft148\\data\\spectra\\so\\hcl-nr10\\"
filename_end = "so20210601_NIR_InGaAs_AC_Nr10_10mm.0"
filename = filename_start + filename_end

opus_time_origin = datetime.datetime(year=1970, month=1, day=1)

opus_file = read_opus(filename)

print(opus_file.data_keys)

raw_x = opus_file.sm.x
raw_y = opus_file.sm.y

x = []
y = []
normalization_reference = None

for i in range(len(raw_x)):
    if 5670 <= raw_x[i] <= 5805:
        if normalization_reference == None:
            normalization_reference = raw_y[i]
        x.append(raw_x[i])
        y.append(raw_y[i]/normalization_reference)

start_time = opus_time_origin + datetime.timedelta(seconds=opus_file.SRT)
stop_time = start_time + datetime.timedelta(seconds=opus_file.DUR)

out_filename = filename_start+f"so{start_time.year}{str(start_time.month).zfill(2)}{str(start_time.day).zfill(2)}_01_start_{str(start_time.minute).zfill(2)}_{str(start_time.second).zfill(2)}_stop_{str(stop_time.minute).zfill(2)}_{str(stop_time.second).zfill(2)}.dpt"
with open(out_filename, "w") as file:
    for i in range(len(x)):
        file.write(f"{x[i]} {y[i]}\n")

plt.plot(x, y)
plt.show()