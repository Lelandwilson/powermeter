import threading
import time
import re
from collections import defaultdict
from collections import deque
import serial


# # Initialize the sum and count dictionaries
# sums = defaultdict(lambda: defaultdict(float))
# counts = defaultdict(lambda: defaultdict(int))


def parse_data(line):
    # Define a regular expression pattern to match the unit ID and data
    pattern = r'<(\d+)> \[([\d,]+)\]'
    # Use the pattern to search the line
    match = re.search(pattern, line)
    if match:
        # If a match was found, extract the unit ID and data
        unit_id = int(match.group(1))
        data = list(map(int, match.group(2).split(',')))

        # Define a dictionary of transformations to apply to the data
        transformations = {
            2: lambda x: x / 100,  # RMS V
            4: lambda x: x / 100,  # CCF
            5: lambda x: x / 100,  # Theta
            # 6: lambda x: x / 100,  # Apparent P
            # 7: lambda x: x / 100,  # Real P
            # 8: lambda x: x / 100,  # Reactive P
            9: lambda x: x / 100,  # PF
        }

        # Apply the transformations to the data
        for i, value in enumerate(data):
            if i in transformations:
                data[i] = transformations[i](value)
        return unit_id, data
    else:
        # If no match was found, return None
        return None


# JSON DATA This function should be called every time a new reading is received
def add_reading(unit, parameters, SUMS, COUNTS):

    # global sums
    # global counts

    for i, parameter in enumerate(parameters):
        SUMS[unit][i] += parameter
        COUNTS[unit][i] += 1


# store averages into DB
# def store_averages(mainDB):
#     print("--Storing Average readings for past hour--")
#     averages = defaultdict(dict)
#     for unit in sums:
#         for i in sums[unit]:
#             averages[unit][i] = sums[unit][i] / counts[unit][i]
#
#     # Save averages to DB
#     parameters = {
#         0: "Time",
#         1: "Frequency",
#         2: "Samples",
#         3: "Vrms",
#         4: "Irms",
#         5: "CCF",
#         6: "Theta",
#         7: "App_P",
#         8: "Real_P",
#         9: "Reac_P",
#         10: "PF"
#         #THD to be added
#     }
#
#     for unit_id, unit_averages in averages.items():
#         for index, value in unit_averages.items():
#             parameter = parameters.get(index, "Unknown")
#             mainDB.store_reading(unit_id, parameter, value)
#
#     # Reset the sums and counts for the next hour
#     sums.clear()
#     counts.clear()
#
# def store_daily_averages(mainDB):
#     print("--Storing Average readings for past day--")
#     daily_averages = defaultdict(dict)
#
#     # List of parameters
#     parameters = {
#         0: "Time",
#         1: "Frequency",
#         2: "Samples",
#         3: "Vrms",
#         4: "Irms",
#         5: "CCF",
#         6: "Theta",
#         7: "App_P",
#         8: "Real_P",
#         9: "Reac_P",
#         10: "PF"
#         #THD to be added
#     }
#
#     # Get a list of unique unit IDs
#     unit_ids = set()
#     for parameter in parameters.values():
#         readings = mainDB.get_all_readings()
#         for reading in readings:
#             unit_ids.add(reading[0])
#
#     # For each unit and each parameter, calculate the average
#     for unit_id in unit_ids:
#         for parameter_id, parameter in parameters.items():
#             readings = mainDB.get_readings_last_24_hours(unit_id, parameter)
#             if readings:
#                 values = [reading[0] for reading in readings]
#                 daily_averages[unit_id][parameter_id] = sum(values) / len(values)
#             else:
#                 daily_averages[unit_id][parameter_id] = 0
#
#     # Save daily averages to DB
#     for unit_id, unit_averages in daily_averages.items():
#         for parameter_id, value in unit_averages.items():
#             mainDB.store_reading(unit_id, parameters[parameter_id], value)
#

#Dictionary used for visualising the live data
def parseData_to_SecondsDict(unit_id, data, SECONDS_DATA_DICT):
    #global SECONDS_DATA_DICT

    # unit_id, data = parse_string(strings)
    # unit_id, data = parse_string(s)
    if unit_id in SECONDS_DATA_DICT:
        # If the unit ID is already in the dictionary, append the new data to the existing deque
        SECONDS_DATA_DICT[unit_id].append(data)
    else:
        # If the unit ID is not in the dictionary, add a new deque with the data
        SECONDS_DATA_DICT[unit_id] = deque([data], maxlen=100)

    # print(SECONDS_DATA_DICT.values())
    # print(SECONDS_DATA_DICT[2])



class readSerialStream(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)

    def stream(self, serialPort, baudRate, mainDB, SECONDS_DATA_DICT, SUMS, COUNTS):
        active_devices = set()
        last_checked_time = time.time()
        with serial.Serial(serialPort, baudRate, timeout=1) as ser:
            while True:
                try:
                    # Check for disconnected devices every second
                    if time.time() - last_checked_time > 1.0:
                        for device in SECONDS_DATA_DICT.keys():
                            if device not in active_devices:
                                SECONDS_DATA_DICT[device].append(-1)
                        active_devices.clear()
                        last_checked_time = time.time()

                    line = ser.readline().decode('utf-8').strip()
                    if line:
                        result = parse_data(line)
                        if result is not None:
                            unit_id, data = result
                            active_devices.add(unit_id)
                            try:
                                parseData_to_SecondsDict(unit_id, data, SECONDS_DATA_DICT)
                                add_reading(unit_id, data, SUMS, COUNTS)
                                #
                                # if time.localtime().tm_min == 0 and time.localtime().tm_sec == 0:
                                #     store_averages(mainDB)

                            except:
                                print("Failed to parse data: " + line)  # Corrupt data stream
                except:
                    # print("Data Error: Incorrect format")  #Likely a non AC connected slave device
                    time.sleep(1)

