import smbus2
import threading
import time
import re
from collections import defaultdict
from collections import deque

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
def add_reading(unit, parameters, sums, counts):

    # global sums
    # global counts

    for i, parameter in enumerate(parameters):
        sums[unit][i] += parameter
        counts[unit][i] += 1


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



class linux_I2c(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)

    def i2coms(self, busNo, slaveAddresses, mainDB, SECONDS_DATA_DICT, SUMS, COUNTS):

        def check_and_swap(data1, data2):
            # Check if the first part of the message ends with a bracket and the second part starts with a bracket
            if data1[-1] == ']' and data2[0] == '[':
                # If they are, swap the two parts
                data1, data2 = data2, data1
            # Return the corrected message
            return data1, data2

        # Create an SMBus instance
        bus = smbus2.SMBus(busNo)

        # Define the period
        PERIOD = 1

        # Define the data to send
        dataToSend = 400
        # Convert the data to a list of integers
        dataBytes = [dataToSend >> 8, dataToSend & 0xFF]

        # Define the last transmission time
        lastTransmission = time.time()

        while True:
            currentMillis = time.time()
            if currentMillis - lastTransmission >= PERIOD:
                lastTransmission = currentMillis
                for address in slaveAddresses:
                    # print("<00{}> ".format(address))
                    try:
                        # Write the data to the slave
                        bus.write_i2c_block_data(address, 0, dataBytes)
                        # Read 29 bytes of data from the slave
                        data1 = bus.read_i2c_block_data(address, 0, 29)
                        data1 = ''.join(chr(i) for i in data1 if i != 255)

                        # Read another 25 bytes of data from the slave
                        data2 = bus.read_i2c_block_data(address, 0, 25)
                        data2 = ''.join(chr(i) for i in data2 if i != 255)

                        # Check if the brackets are in the correct position and swap the two parts of the message if they are not
                        data1, data2 = check_and_swap(data1, data2)

                        # Combine the data
                        data = data1 + data2

                        # Combine the data
                        unit_id = ("<00{}> ".format(address))

                        line = unit_id + data1 + data2
                        result = parse_data(line)
                        if result is not None:
                            unit_id, data = result
                            print(unit_id, data)
                            try:
                                parseData_to_SecondsDict(unit_id, data, SECONDS_DATA_DICT)  # Parse the data into the relevant unit dicts
                                add_reading(unit_id, data, SUMS, COUNTS)  # Running Averages

                                # # If the current time is on the hour, store the averages
                                # if time.localtime().tm_min == 0 and time.localtime().tm_sec == 0:
                                #     store_averages(mainDB)

                            except:
                                print("Failed to parse data: " + line)

                    except:
                        pass
                        # print("-")

                # print("")
