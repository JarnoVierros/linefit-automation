
import pathlib
import datetime
import subprocess
import os
import matplotlib.pyplot as plt
import numpy as np

from brukeropus import read_opus

measurement_times_file = "data\\measurement_times.txt"
work_directory = "work"
T_directory ="data\\T"

wire_resistance = 0.83 #0.60
r0 = 100
alpha = 0.00385

auto_duration = 3167.22 #seconds?

H35Cl_concentration = 1.3902e22
H37Cl_concentration = 1.3852e22

H35Cl_pressure = 4.999
H37Cl_pressure = 5.019

reference_T = 296

max_inclination = 1.196e-3

opus_time_origin = datetime.datetime(year=1970, month=1, day=1)

def plot_modulation(data):
    figure, (ax1, ax2) = plt.subplots(2, 1, figsize=(7, 2*4.8))
    ax1.plot(data["OPD"], data["Modulation"])
    ax1.set_ylabel("Modulation amplitude")
    ax1.set_xlabel("OPD (cm)")
    ax1.axhline(y=1, c="black")
    ax1.tick_params(right=True)
    ax1.set_ylim(0.95, 1.05)

    ax2.plot(data["OPD"], data["Phase"])
    ax2.set_ylabel("Phase error (rad)")
    ax2.set_xlabel("OPD (cm)")
    ax2.axhline(y=0, c="black")
    ax2.tick_params(right=True)
    ax2.set_ylim(-0.01, 0.01)

    plt.subplots_adjust(left=0.15, right=0.85)

def read_csv_data(filename, divider_symbol=","):
    data = {}
    with open(filename, "r") as file:
        lines = file.readlines()
        variables = lines[0].strip().split(divider_symbol)
        while "" in variables:
            variables.remove("")
        variables = [variable.strip() for variable in variables]
        for variable in variables:
            data[variable] = []
        for line in lines[1:]:
            values = line.strip().split(divider_symbol)
            while "" in values:
                values.remove("")
            for i in range(len(variables)):
                data[variables[i]].append(float(values[i]))
    return data

def get_T_times(filename, year, month, day, measurement_number=1):
    with open(filename, "r") as file:
        lines = file.readlines()

    for line in lines:
        if line[0] == "#" or len(line) < 1: continue
        T_date, T_time = line.split(",")
        T_date = T_date.strip()
        T_year = int(line[0:4])
        T_month = int(line[4:6])
        T_day = int(line[6:8])
        T_measurement_number = int(line[9:11])

        if T_year != year or T_month != month or T_day != day or T_measurement_number != measurement_number:
            continue

        T_time = T_time.strip()
        start, stop = T_time.split("-")
        start_hour, start_minute = start.split(":")
        start_datetime = datetime.datetime(year=T_year, month=T_month, day=T_day, hour=int(start_hour), minute=int(start_minute))
        
        if stop == "auto":
            stop_datetime = start_datetime + datetime.timedelta(seconds=auto_duration)
        else:
            stop_hour, stop_minute = stop.split(":")
            stop_datetime = datetime.datetime(year=T_year, month=T_month, day=T_day, hour=int(stop_hour), minute=int(stop_minute))

        return start_datetime, stop_datetime
    
    return None
        
def read_T_data(filename):
    data = {}
    data["time"] = []
    data["average"] = []
    data["resistance"] = []
    with open(filename, "r") as file:
        lines = file.readlines()
    for line in lines:
        try:
            line = line.strip()
            items = line.split(" ")
            while "" in items:
                items.remove("")
            year, month, day = items[0].split("-")
            hour, minute, second = items[1].split(":")
            data["time"].append(datetime.datetime(year=int(year), month=int(month), day=int(day), hour=int(hour), minute=int(minute), second=int(second)))
            data["average"].append(float(items[2]))
            data["resistance"].append(float(items[4]))
        except Exception as e:
            print("skipped invalid temperature file line, error:", e)
    return data

def get_T(directory, start_time, stop_time):
    if start_time.year != stop_time.year or start_time.month != stop_time.month or start_time.day != stop_time.day:
        raise Exception("Start and stop of measurement are on different days. Automatically dealing with this has not been implemented.")
    path = pathlib.Path(directory)
    file_iterator = path.iterdir()
    total_resistance = 0
    resistance_measurements = 0
    for file in file_iterator:
        file_year = int(file.name[0:4])
        file_month = int(file.name[4:6])
        file_day = int(file.name[6:8])
        if file_year != start_time.year or file_month != start_time.month or file_day != start_time.day:
            continue
        if  file.name[-4:] == ".dat":
            T_data = read_T_data(file)
            for i in range(len(T_data["time"])):
                if start_time <= T_data["time"][i] <= stop_time:
                    total_resistance += T_data["resistance"][i]
                    resistance_measurements += 1
        else:
            subfile_iterator = file.iterdir()
            for subfile in subfile_iterator:
                if  subfile.name[-4:] != ".dat": continue
                T_data = read_T_data(subfile)
                for i in range(len(T_data["time"])):
                    if start_time <= T_data["time"][i] <= stop_time:
                        total_resistance += T_data["resistance"][i]
                        resistance_measurements += 1
    
    if resistance_measurements < 1:
        return None

    mean_resistance = total_resistance/resistance_measurements
    mean_T = 273.15 + ((mean_resistance-wire_resistance)-r0)/(alpha*r0)
    return mean_T

def analyze_raw_spectrum(filename):

    opus_file = read_opus(filename)
    raw_x = opus_file.sm.x
    raw_y = opus_file.sm.y
    x = []
    y = []
    normalization_reference = None
    for i in range(len(raw_x)):
        if 5670 <= raw_x[i] <= 5805:
            if normalization_reference == None:
                normalization_reference = np.mean(raw_y[i:i+10])
            x.append(raw_x[i])
            y.append(raw_y[i]/normalization_reference)

    start_time = opus_time_origin + datetime.timedelta(seconds=opus_file.SRT)
    stop_time = start_time + datetime.timedelta(seconds=opus_file.DUR)

    path = pathlib.Path(filename)

    try:
        measurement_number = int(path.name[11:13])
    except:
        measurement_number = 1

    out_filename = str(path.parent)+f"\\so{start_time.year}{str(start_time.month).zfill(2)}{str(start_time.day).zfill(2)}_{str(measurement_number).zfill(2)}_start_{str(start_time.hour).zfill(2)}_{str(start_time.minute).zfill(2)}_stop_{str(stop_time.hour).zfill(2)}_{str(stop_time.minute).zfill(2)}.dpt"
    with open(out_filename, "w") as file:
        for i in range(len(x)):
            file.write(f"{x[i]} {y[i]}\n")
    
    return (out_filename, (start_time, stop_time))


def process_spectra():
    path = pathlib.Path(work_directory)
    file_iterator = path.iterdir()
    for file in file_iterator:
        if file.name[0:2] == "so" and file.name[-4:] == ".dpt":
            file_type = "dpt"
            year = int(file.name[2:6])
            month = int(file.name[6:8])
            day = int(file.name[8:10])
            measurement_number = int(file.name[11:13])

            if (file.name[13:20] == "_start_"):
                try:
                    start = datetime.datetime(year=year, month=month, day=day, hour=int(file.name[20:22]), second=int(file.name[23:25]))
                    stop = datetime.datetime(year=year, month=month, day=day, hour=int(file.name[31:33]), second=int(file.name[34:36]))
                    T_times = (start, stop)
                except:
                    T_times = get_T_times(measurement_times_file, year, month, day, measurement_number)
                    if T_times == None:
                        print(f"file {file} skipped because measurement time information was not found in {measurement_times_file}.")
                        continue
            else:
                T_times = get_T_times(measurement_times_file, year, month, day, measurement_number)
                if T_times == None:
                    print(f"file {file} skipped because measurement time information was not found in {measurement_times_file}.")
                    continue

            T = get_T(T_directory, T_times[0], T_times[1])
            if T == None:
                print(f"file {file} skipped because no temperature measurements were found in {T_directory}.")
                continue

        elif file.name[0:2] == "so" and file.name[-5:-2] == "tr.":
            file_type = "opus"
            year = int(file.name[2:6])
            month = int(file.name[6:8])
            day = int(file.name[8:10])
            measurement_number = int(file.name[-2:])

            try:
                opus_file = read_opus(file)
                start_time = opus_time_origin + datetime.timedelta(seconds=opus_file.SRT)
                stop_time = start_time + datetime.timedelta(seconds=opus_file.DUR)
                T_times = (start_time, stop_time)
            except:
                print(f"Failed to read measurement time from {file}, reading from {measurement_times_file} instead.")
                T_times = get_T_times(measurement_times_file, year, month, day, measurement_number)
                if T_times == None:
                    print(f"Ffile {file} skipped because measurement time information was not found in {measurement_times_file}.")
                    continue

            T = get_T(T_directory, T_times[0], T_times[1])
            if T == None:
                print(f"File {file} skipped because no temperature measurements were found in {T_directory}.")
                continue

        elif file.name[0:2] == "so" and file.name[-25:]=="NIR_InGaAs_AC_Nr10_10mm.0":
            file_type = "dpt"
            year = int(file.name[2:6])
            month = int(file.name[6:8])
            day = int(file.name[8:10])

            try:
                measurement_number = int(file.name[11:13])
            except:
                measurement_number = 1

            (dpt_filename, T_times) = analyze_raw_spectrum(file)

            T = get_T(T_directory, T_times[0], T_times[1])
            if T == None:
                print(f"file {file} skipped because no temperature measurements were found in {T_directory}.")
                continue

            file = dpt_filename
        else:
            #print(f"skipping file {file} because it is of unknown type")
            continue

        with open("lft14_template.inp", "r") as template_file:
            template = template_file.read()

        def insert_value(text, marker, value):
            start = text.find(marker)
            if start == -1:
                exception_string = "Marker "+marker+" nor found in template."
                raise Exception(exception_string)
            stop = start + len(marker)
            new_text = text[:start]
            new_text += str(value)
            new_text += text[stop:]
            #print(f"text len={len(new_text)}")
            return new_text
        
        new_input_file = template

        output_dir = f"ergs\\{year}{str(month).zfill(2)}{str(day).zfill(2)}_{str(measurement_number).zfill(2)}"
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)

        new_input_file = insert_value(new_input_file, "%output_directory%", output_dir)

        if file_type == "dpt":
            new_input_file = insert_value(new_input_file, "%file_format%", "0")
        elif file_type == "bin":
            new_input_file = insert_value(new_input_file, "%file_format%", "1")
        elif file_type == "opus":
            new_input_file = insert_value(new_input_file, "%file_format%", "2")
        else:
            error_string = f"Unknown file type {file_type}"
            raise Exception(error_string)

        filename_string = 12*(str(file)+"\n") + str(file)
        new_input_file = insert_value(new_input_file, "%filenames%", filename_string)

        new_input_file = insert_value(new_input_file, "%T1%", T)

        new_input_file = insert_value(new_input_file, "%%gas1%", H35Cl_concentration)

        scaled_H35Cl_pressure = H35Cl_pressure*T/reference_T
        new_input_file = insert_value(new_input_file, "%ptot1%", scaled_H35Cl_pressure)
        new_input_file = insert_value(new_input_file, "%ppart1%", scaled_H35Cl_pressure)


        new_input_file = insert_value(new_input_file, "%T2%", T)

        new_input_file = insert_value(new_input_file, "%%gas2%", H37Cl_concentration)

        scaled_H37Cl_pressure = H37Cl_pressure*T/reference_T
        new_input_file = insert_value(new_input_file, "%ptot2%", scaled_H37Cl_pressure)
        new_input_file = insert_value(new_input_file, "%ppart2%", scaled_H37Cl_pressure)


        new_input_file = insert_value(new_input_file, "%max_inclination%", max_inclination)

        with open("lft14.inp", "w") as input_file:
            input_file.write(new_input_file)

        input_dir = f"input\\{year}{str(month).zfill(2)}{str(day).zfill(2)}_{str(measurement_number).zfill(2)}"
        if not os.path.exists(input_dir):
            os.makedirs(input_dir)
        with open(input_dir+"\\lft14.inp", "w") as input_file_copy:
            input_file_copy.write(new_input_file)

        subprocess.run(["lft148.exe"])

        modulation_filename = f"ergs\\{year}{str(month).zfill(2)}{str(day).zfill(2)}_{str(measurement_number).zfill(2)}\\modulat.dat"
        data = read_csv_data(modulation_filename, " ")

        plot_modulation(data)

        figure_name = f"figures\\{year}{str(month).zfill(2)}{str(day).zfill(2)}_{str(measurement_number).zfill(2)}.png"
        plt.savefig(figure_name)

if __name__ == "__main__":

    process_spectra()