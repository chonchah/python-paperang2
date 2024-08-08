#!/usr/bin/env python3
import config
import hardware
import image_data
import asyncio
import tornado
import tempfile
import os
class PaperangPrinterHandler(tornado.web.RequestHandler):
    def __init__(self, application, request, **kwargs):
        print("attempting test print to MAC address \"% s\""% config.macaddress)
        self.printer_hardware = hardware.Paperang(config.macaddress)
        super().__init__(application, request, **kwargs)
    def print_image(self, path):
        if self.printer_hardware.connected:
            self.printer_hardware.sendImageToBt(image_data.load_and_convert_image(path))

    def post(self):
        try:
            # Get the Content-Type of the request
            content_type = self.request.headers.get("Content-Type")

            # Get the raw body of the request
            image_data = self.request.body

            # Check if we actually received any data
            if not image_data:
                raise ValueError("No image data received")

            # Process the image (e.g., save it)
            filename = "uploaded_image.%s" % content_type.split("/")[1]
            filename = f"/tmp/{filename}"
            with open(filename, "wb") as f:
                f.write(image_data)
                f.close()
            self.print_image(filename)
            self.printer_hardware.disconnect()
            self.write(f"Image uploaded successfully. Size: {len(image_data)} bytes")
        except Exception as e:
            self.set_status(400)
            self.write(f"Error processing image: {str(e)}")
def make_app():
    return tornado.web.Application([
        (r"/", PaperangPrinterHandler),
    ])

async def main():
    app = make_app()
    app.listen(8888)
    print("Listening on port 8888")
    await asyncio.Event().wait()

if __name__ == "__main__":
    asyncio.run(main())