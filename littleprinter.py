import time
import hardware
import image_data
from watchgod import watch

class Paperang_Printer:
    def __init__(self):
        self.printer_hardware = hardware.Paperang()
    
    def print_sirius_image(self, path):
        if self.printer_hardware.connected:
            self.printer_hardware.sendImageToBt(image_data.sirius(path))
    
if __name__ == '__main__':
    mmj=Paperang_Printer()
    for changes in watch('/Users/monica/tmp'):
        file = changes.pop()[1] 
        print("Printing " + file)
        mmj.print_sirius_image(file)
