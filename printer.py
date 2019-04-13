import hardware
import image_data
import skimage.io
import skimage as ski


class Paperang_Printer:
    def __init__(self):
        self.printer_hardware = hardware.Paperang()

    def print_image_file(self, path):
        if self.printer_hardware.connected:
            self.printer_hardware.sendImageToBt(image_data.binimage2bitstream(
                image_data.im2binimage(ski.io.imread("/home/broncotc/Downloads/20247675.jpg"))))
