#!/usr/bin/env python3
import time
import hardware
import image_data
import tempfile
import os
from watchgod import watch
import config
from pathlib import Path

class Paperang_Printer:
    def __init__(self):
        if hasattr(config, "macaddress"):
            self.printer_hardware = hardware.Paperang(config.macaddress)
        else:
            self.printer_hardware = hardware.Paperang()
    
    def print_image(self, path):
        if self.printer_hardware.connected:
            self.printer_hardware.sendImageToBt(image_data.load_and_convert_image(path))

if __name__ == '__main__':
    mmj=Paperang_Printer()
    # `sirius-client` will write to this folder
    tmpdir = os.path.join(tempfile.gettempdir(), 'sirius-client')
    Path(tmpdir).mkdir(parents=True, exist_ok=True)
    
    for changes in watch(tmpdir):
        file = changes.pop()[1] 
        print("Printing " + file)
        mmj.print_image(file)
