import time
import hardware
import image_data

class Paperangg_Printer:
    def __init__(self):
        self.printer_hardware = hardware.Paperang()

        # having trouble connecting? uncomment the following line and input
        # your paperang's MAC address to connect directly
        # self.printer_hardware = hardware.Paperang("AA:BB:CC:DD:EE:FF")

    def print_self_test(self):
        if self.printer_hardware.connected:
            self.printer_hardware.sendSelfTestToBt()
            self.printer_hardware.disconnect()
        else:
            print("printer not connected.")

    def print_sirius_image(self, path):
        if self.printer_hardware.connected:
            self.printer_hardware.sendImageToBt(image_data.sirius(path))

if __name__ == '__main__':
    mmj=Paperangg_Printer()
    mmj.print_self_test()
