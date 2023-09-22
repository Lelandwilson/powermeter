Power Monitoring System
Overview
The Power Monitoring System is a web-based application designed to run on servers, such as a Raspberry Pi. The system interfaces with custom power monitoring devices to gather and present real-time and historical data regarding power usage metrics.

Key Features
Data Collection: Retrieves live data at a rate of 1800 times per second on the following parameters:

Voltage
Current
Frequency
Real, Reactive & Apparent Power
Current Crest Factor
Power Factor
Web-based UI: Offers both real-time and historical data visualizations. Real-time data is displayed through charts and graphs, while historical data can be viewed as charts, spreadsheets, or exported as CSV files.

Master/Slave System Hierarchy: A master unit manages and communicates with up to 100 slave devices. This architecture streamlines the data flow and optimizes system performance.

Efficient Communication: The I2C protocol ensures seamless communication using just four wires (VCC, Ground, SDA, and SCL), simplifying the connection requirements. The design can support up to 100 devices, staying within the 128-device limit set by the I2C protocol.

Slave Device Overview
Each slave device is responsible for monitoring one circuit. The Atmega328P microcontroller acts as the CPU, chosen for its versatility, pin count, inbuilt I2C protocol, and extensive open-source knowledge base.

Zero Crossing Detection: Ensures measurements align with AC signal cycles for accurate data collection.
Voltage Measurement: Utilizes a current transformer to adapt to the MCU's measurement capabilities.
Current Measurement: Incorporates the ACS758 hall-effect IC for bidirectional current measurements.
Master Device Overview
The Raspberry Pi serves as the master unit, handling communications with slave devices and hosting the web server for the UI.

I2C Communication: Uses a level shifter IC to manage communication between 3.3V and 5V devices.
Hardware: Comprises the Raspberry Pi and necessary pull-up resistors for I2C communication.
Future Considerations
The system has been designed with future scalability and enhancements in mind:

Potential for onboard power supply in slave devices or additional external power supplies.
Inclusion of a seven-channel dipswitch for manual address setting in future devices.
Expansion of the zero-crossing detection circuit to measure phase shift between voltage and current.
Consideration for alternative SBC systems like 'Onion OMEGA 2'.

Running the Program
To get your power monitoring system up and running, follow these steps:

Install Python Libraries:
First and foremost, you'll need to install the required Python libraries. To do this, navigate to the directory where your requirements.txt file is located and run the following command:

bash
Copy code
pip install -r requirements.txt
Hardware Connection:
Ensure that the custom PCB slave device network is correctly set up. There are two methods for this:

Direct Connection to Raspberry Pi: Connect the slave devices directly to the Raspberry Pi via I2C.
Via Serial Device: If you're using a different host computer, ensure a serial device is connected to facilitate communication over the I2C network.
Run the Main Script:
With the libraries installed and the hardware set up, you can now run the main script to activate the device, servers, and databases. Execute the following command:

bash
Copy code
python3 Pmon1.py
After following the above steps, your power monitoring system should be operational. Monitor the terminal for any logs or messages and access the web-based UI to interact with the data.




References
[1] I2C Protocol Documentation
[2] I2C Device Limitations Study
