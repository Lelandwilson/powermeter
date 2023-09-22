from apscheduler.schedulers.background import BackgroundScheduler
# from USBSERIAL import store_averages, store_daily_averages
from libs.SQLDB import SQL_liteDB  # Assuming your SQLite DB class is in db_file.py
from collections import defaultdict


def store_averages(mainDB, SUMS, COUNTS):
    # global sums
    # global counts

    print("--Storing Average readings for past hour--")
    averages = defaultdict(dict)
    for unit in SUMS:
        for i in SUMS[unit]:
            averages[unit][i] = SUMS[unit][i] / COUNTS[unit][i]

    # Save averages to DB
    parameters = {
        0: "Time",
        1: "Frequency",
        2: "Samples",
        3: "Vrms",
        4: "Irms",
        5: "CCF",
        6: "Theta",
        7: "App_P",
        8: "Real_P",
        9: "Reac_P",
        10: "PF"
        #THD to be added
    }

    for unit_id, unit_averages in averages.items():
        for index, value in unit_averages.items():
            parameter = parameters.get(index, "Unknown")
            mainDB.store_reading(unit_id, parameter, value)

    # Reset the sums and counts for the next hour
    SUMS.clear()
    COUNTS.clear()


def store_daily_averages(mainDB):
    print("--Storing Average readings for past day--")
    daily_averages = defaultdict(dict)

    # List of parameters
    parameters = {
        0: "Time",
        1: "Frequency",
        2: "Samples",
        3: "Vrms",
        4: "Irms",
        5: "CCF",
        6: "Theta",
        7: "App_P",
        8: "Real_P",
        9: "Reac_P",
        10: "PF"
        #THD to be added
    }

    # Get a list of unique unit IDs
    unit_ids = set()
    for parameter in parameters.values():
        readings = mainDB.get_all_readings()
        for reading in readings:
            unit_ids.add(reading[0])

    # For each unit and each parameter, calculate the average
    for unit_id in unit_ids:
        for parameter_id, parameter in parameters.items():
            readings = mainDB.get_readings_last_24_hours(unit_id, parameter)
            if readings:
                values = [reading[0] for reading in readings]
                daily_averages[unit_id][parameter_id] = sum(values) / len(values)
            else:
                daily_averages[unit_id][parameter_id] = 0

    # Save daily averages to DB
    for unit_id, unit_averages in daily_averages.items():
        for parameter_id, value in unit_averages.items():
            mainDB.store_reading(unit_id, parameters[parameter_id], value)


def schedule_tasks(mainDB,SUMS, COUNTS):
    # Create an instance of your database class
    # mainDB = SQL_liteDB()

    # Create a scheduler
    scheduler = BackgroundScheduler()

    # Add the hourly average task, running every hour
    scheduler.add_job(store_averages, 'interval', hours=1, args=[mainDB,SUMS, COUNTS])

    # Add the daily average task, running every day at 23:59 (just before midnight)
    scheduler.add_job(store_daily_averages, 'cron', hour=23, minute=59, args=[mainDB])

    # Start the scheduler
    scheduler.start()

#
# # Run the scheduler
# schedule_tasks()
