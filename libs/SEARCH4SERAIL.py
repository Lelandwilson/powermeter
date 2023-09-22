import glob

class serach4Serial():
    def scan(self, usb1, usb2):
        serialPort = "-1"
        # Locate Serial Port to use
        USBList = glob.glob('/dev/cu.*')
        print("USB Devices: " + str(USBList))
        # /dev/tty.wchusbserial1420

        for matching in [s for s in USBList if usb1 in s or usb2 in s]:
            serialPort = str(matching)
            serialPort = serialPort.strip("[]'")
            print("Selecting-------->" + serialPort)

        return serialPort
