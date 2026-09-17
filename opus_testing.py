
#from brukeropus import find_opus_files, read_opus, OPUSFile, Opus, parse_file_and_print

from brukeropus import read_opus
from matplotlib import pyplot as plt

filename_start = "C:\\Users\\vierros\\Programs\\lft148dsk-distr\\lft148\\data\\spectra\\so\\hcl-nr10\\"
filename_end = "so20210601_NIR_InGaAs_AC_Nr10_10mm.0"
#filename_end = "so20220615_tr.01"
filename = filename_start + filename_end

#filename = "C:\\Users\\vierros\\test\\210507-lft148dsk-distr\\lft148dsk-distr\\lft148\\spectra\\hcl-tccon\\081009-bremen\\hcl081009-vac.0"
#filename = "C:\\Users\\vierros\\Programs\\lft148dsk-distr\\lft148\\examples-win\\TCCON\\lamp\\HCl\\prescribed\\evac\\ergs\\specre01.dat"

opus_file = read_opus(filename)  # Returns an OPUSFile class

#print(opus_file.SRT)

#opus_file.print_parameters()  # Pretty prints all metadata in the file to the console

print(opus_file.data_keys)

plt.plot(opus_file.sm.x, opus_file.sm.y)
#plt.plot(opus_file.t.x, opus_file.t.y)
plt.show()


if 'a' in opus_file.data_keys:  # If absorbance spectra was extracted from file
    plt.plot(opus_file.a.x, opus_file.a.y)  # Plot absorbance spectra
    plt.title(opus_file.sfm + ' - ' + opus_file.snm)  # Sets plot title to Sample Form - Sample Name
    plt.show()  # Display plot

