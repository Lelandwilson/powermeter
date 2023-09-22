
from flask import Flask, render_template, jsonify, request, flash, redirect, url_for, session
import json
import os
from libs.SQLDB import SQL_liteDB
from datetime import datetime, timedelta



app = Flask(__name__,
            static_folder='../static',
            template_folder='../templates')

# app.debug = True  # !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

app.config['SECRET_KEY'] = '7cce7410e80ce3f326f2b00e7edffee8'

# List of your user credentials, for example
user_list = []

# A dictionary of your data
seconds_data_dict = {}

# A reference to your database
main_db = None

# A dictionary to store the labels for the units
unit_labels = {}

# Unit labels file
unit_labels_file = 'unit_labels.json'

# If the unit labels file exists, load the labels from it
if os.path.exists(unit_labels_file):
    with open(unit_labels_file, 'r') as f:
        unit_labels = json.load(f)
else:
    unit_labels = {}

@app.route('/')
def home():
    if not session.get('logged_in'):
        try:
            unit_ids = list(seconds_data_dict.keys())
            print("Found Units:" + str(unit_ids))
        except:
            unit_ids = []
            print("Failed to Find Units:")
        return render_template('login.html', unit_ids=unit_ids)
    else:
        Msg = ''
        return render_template('index.html', sys_MSG=Msg, unit_ids=list(seconds_data_dict.keys()), unit_labels=unit_labels)


@app.route('/login', methods=['POST'])
def do_admin_login():
    for credentials in user_list:
        if request.form['username'] + ":" + request.form['password'] == credentials:
            session['logged_in'] = True
    else:
        flash('wrong password!')
    return home()


@app.route("/logout")
def logout():
    session['logged_in'] = False
    return home()


# @app.route('/unit/<int:unit_id>')
# def unit_page(unit_id):
#     # Check if the unit_id is in SECONDS_DATA_DICT
#     if unit_id not in seconds_data_dict:
#         return "Unit not found", 404  # Return a 404 error if it's not
#
#     # Otherwise, render the unit page
#     return render_template('unit_page.html', unit_id=unit_id, unit_ids=list(seconds_data_dict.keys()), unit_labels=unit_labels)


@app.route('/unit/<int:unit_id>')
def unit_page(unit_id):
    # Fetch the past day readings for the specific unit_id
    end_time = datetime.now()
    start_time = end_time - timedelta(days=1)
    past_day_readings = main_db.query_readings(unit_id, start_time, end_time)

    return render_template('unit_page.html', unit_id=unit_id, past_day_readings=past_day_readings, unit_labels=unit_labels)




@app.route('/basicDataStream')
def basicDataStream():
    # Initialize an empty list to store all lines of text
    text_lines = []

    # Loop over each unit_id and its data
    for unit_id, data in seconds_data_dict.items():
        # Only get the last entry from the data list
        last_entry = data[-1] if data else None
        # Format the unit_id and last_entry into a string, and add it to the list
        text_lines.append(f"Unit ID: {unit_id}{last_entry}")

    # Join all lines of text into a single string with newline characters in between
    series_text = "\n".join(text_lines)
    series_text += '\n'
    # Send the data as basic text
    return series_text


@app.route('/live_data')
def live_data():
    # Convert the seconds_data_dict to a format that Chartist.js can use
    labels = list(range(100))  # Assuming each reading is one second apart
    series = [list(seconds_data_dict[unit_id]) for unit_id in seconds_data_dict]

    # Send the data as JSON
    return jsonify(labels=labels, series=series)


@app.route('/settings', methods=['GET', 'POST'])
def settings():
    global unit_labels  # Make sure we're modifying the global unit_labels variable

    if request.method == 'POST':
        if 'reset' in request.form:
            # Reset all unit labels
            unit_labels.clear()
        else:
            # Update unit labels
            for unit_id in seconds_data_dict.keys():
                unit_labels[unit_id] = request.form.get(f"label_{unit_id}", f"Unit {unit_id}")

        # After updating the labels, save them to the file
        with open(unit_labels_file, 'w') as f:
            json.dump(unit_labels, f)

        # Return a JSON response
        return jsonify(success=True)

    return render_template('settings.html', unit_ids=list(seconds_data_dict.keys()), unit_labels=unit_labels)

@app.route('/api/unit-labels', methods=['GET'])
def get_unit_labels():
    return jsonify(unit_labels)

@app.route('/pastreadings/<period>')
def pastreadings(period):
    readings = main_db.get_all_readings(period)
    return render_template('pastreadings.html', readings=readings, period=period)


@app.route('/clear/<period>', methods=['POST'])
def clear_data(period):
    db = SQL_liteDB()
    db.clear_data(period)
    return redirect(url_for('pastreadings', period=period))


def run_webserver(UserList, IPaddress, Port, seconds_data_dict_param, mainDB_param):
    global user_list, seconds_data_dict, main_db
    user_list = UserList
    seconds_data_dict = seconds_data_dict_param
    main_db = mainDB_param
    app.run(debug=False, host=IPaddress, port=Port)
