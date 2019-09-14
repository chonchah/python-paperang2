import hardware
import image_data
import skimage.io
import skimage as ski
import instakit as ik

class Paperang_Printer:
    def __init__(self):
        # pass
        # self.printer_hardware = hardware.Paperang('00:15:83:C2:67:20')
        self.printer_hardware = hardware.Paperang('00:15:83:C2:67:20')

    def print_image_file(self, path):
        if self.printer_hardware.connected:
            # self.printer_hardware.sendSelfTestToBt()
            self.printer_hardware.sendImageToBt(image_data.binimage2bitstream(
                image_data.im2binimage(ski.io.imread(path),conversion="threshold")))
    
    def print_dithered_image(self, path):
        if self.printer_hardware.connected:
            self.printer_hardware.sendImageToBt(image_data.im2binimage2(path))

if __name__=="__main__":
    mmj=Paperang_Printer()
    # mmj.print_dithered_image("/Users/ktamas/Downloads/frame.png")
    mmj.print_dithered_image("/Users/ktamas/Pictures/hard-job-being-a-baby.jpeg")
    mmj.print_dithered_image("/Users/ktamas/Desktop/-km49qIJ_400x400.png")
    mmj.print_dithered_image("/Users/ktamas/Downloads/10827905_10152921795874452_6300515507948976079_o.jpg")
    # mmj.print_dithered_image("/Users/ktamas/Downloads/10827905_10152921795874452_6300515507948976079_o.jpg")
