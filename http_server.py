#!/usr/bin/env python3
import config
import hardware
import image_data
import asyncio
import tornado
import tempfile
import os
# import thread libs
from threading import Thread
from uuid import uuid4
import time
class PaperangPrinter:
    def __init__(self):
        self.printer_hardware = hardware.Paperang(config.macaddress)
    def print_image(self, path: str):
        if self.printer_hardware.connected:
            self.printer_hardware.sendImageToBt(image_data.load_and_convert_image(path))
class ImageStackThread(Thread):
    def __init__(self):
        super().__init__()
        self.printer_hardware = PaperangPrinter()
        self.images_stack = []
    def append_image(self, image_path: str):
        self.images_stack.append(image_path)
    def run(self):
        while True:
            if len(self.images_stack) > 0:
                image = self.images_stack.pop(0)
                print("printing image %s" % image)
                self.printer_hardware.print_image(path=image)
                time.sleep(1)

class PaperangPrinterHandler(tornado.web.RequestHandler):
    
    def post(self):
        try:
            # Get the Content-Type of the request
            content_type = self.request.headers.get("Content-Type")

            # Get the raw body of the request
            image_data = self.request.body

            # Check if we actually received any data
            if not image_data:
                raise ValueError("No image data received")

            self.write(f"Image uploaded to print successfully. Size: {len(image_data)} bytes")
            # Process the image (e.g., save it)
            salt = str(uuid4())
            filename = "uploaded_image_%s.%s" %(salt, content_type.split("/")[0])
            filename = f"/tmp/{filename}"
            with open(filename, "wb") as f:
                f.write(image_data)
                f.close()
            ImageStack.append_image(filename)
        except Exception as e:
            # print traceback if something goes wrong
            import traceback
            traceback.print_exc()
            self.printer_hardware.disconnect()
            self.set_status(400)
            self.write(f"Error processing image: {str(e)}")

global ImageStack
ImageStack = ImageStackThread()


def make_app():
    return tornado.web.Application([
        (r"/", PaperangPrinterHandler),
    ])

async def main():
    app = make_app()
    app.listen(8888)
    print("Listening on port 8888")
    ImageStack.start()
    await asyncio.Event().wait()

if __name__ == "__main__":
    asyncio.run(main())