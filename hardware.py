#!/usr/bin/python3
# -*-coding:utf-8-*-

import struct, zlib, logging
from bluetooth import BluetoothSocket, find_service, RFCOMM, discover_devices
from const import BtCommandByte
from platform import system #so we can tell which OS we're using
import codecs


class Paperang:
    standardKey = 0x35769521
    padding_line = 300
    max_send_msg_length = 1536
    max_recv_msg_length = 1024
    service_uuid = "00001101-0000-1000-8000-00805F9B34FB"

    def __init__(self, address=None):
        self.address = address
        self.crckeyset = False
        self.connected = True if self.connect() else False

    def connect(self):
        if self.address is None and not self.scandevices():
            return False
        if not self.scanservices():
            return False
        logging.info("Service found. Connecting to \"%s\" on %s..." % (self.service["name"], self.service["host"]))
        self.sock = BluetoothSocket(RFCOMM)
        if system() == "Darwin":
            self.sock.connect((self.service["host"].decode('UTF-8'), self.service["port"]))
        else:
            self.sock.connect((self.service["host"], self.service["port"]))
        self.sock.settimeout(60)
        logging.info("Connected.")
        self.registerCrcKeyToBt()
        return True

    def disconnect(self):
        try:
            self.sock.close()
        except:
            pass
        logging.info("Disconnected.")

    def scandevices(self):
        logging.warning("Searching for devices...\n"
                        "This will take some time; consider specifing a mac address to avoid a scan.")
        valid_names = ['MiaoMiaoJi', 'Paperang', 'Paperang_P2S']
        nearby_devices = discover_devices(lookup_names=True)
        valid_devices = list(filter(lambda d: len(d) == 2 and d[1] in valid_names, nearby_devices))
        if len(valid_devices) == 0:
            logging.error("Cannot find device with name %s." % " or ".join(valid_names))
            return False
        elif len(valid_devices) > 1:
            logging.warning("Found multiple valid machines, the first one will be used.\n")
            logging.warning("\n".join(valid_devices))
        else:
            if system() == "Darwin":
                logging.warning(
                    "Found a valid machine with MAC %s and name %s" % (valid_devices[0][0].decode('UTF-8'), valid_devices[0][1])
                )
                self.address = valid_devices[0][0].decode('UTF-8')
            else:
                logging.warning(
                    "Found a valid machine with MAC %s and name %s" % (valid_devices[0][0], valid_devices[0][1])
                )
                self.address = valid_devices[0][0]
        return True

    def scanservices(self):
        logging.info("Searching for services...")
        if system() == "Darwin":
            return self.scanservices_osx()

        # Example find_service() output on raspbian buster:
        # {'service-classes': ['1101'], 'profiles': [], 'name': 'Port', 'description': None,
        #  'provider': None, 'service-id': None, 'protocol': 'RFCOMM', 'port': 1, 
        #  'host': 'A1:B2:C3:D4:E5:F6'}
        service_matches = find_service(uuid=self.service_uuid, address=self.address)
        valid_service = list(filter(
            lambda s: 'protocol' in s and 'name' in s and s['protocol'] == 'RFCOMM' and (s['name'] == 'SerialPort' or s['name'] == 'Port'),
            service_matches
        ))
        print(valid_service[0])
        if len(valid_service) == 0:
            logging.error("Cannot find valid services on device with MAC %s." % self.address)
            return False
        logging.info("Found a valid service")
        self.service = valid_service[0]
        return True

    def scanservices_osx(self):
        # Example find_service() output on OSX 10.15.2:
        # [{'host': b'A1:B2:C3:D4:E5:F6', 'port': 1, 'name': 'Port', 'description': None,
        #  'provider': None, 'protocol': None, 'service-classes': [], 'profiles': [], 'service-id': None}]
        service_matches = find_service(address=self.address)
        # print("printing service matches...")
        # print(service_matches)
        # print("...done.")
        valid_services = list(filter(
            lambda s: 'name' in s and s['name'] == 'SerialPort',
            service_matches
        ))
        if len(valid_services) == 0:
            logging.error("Cannot find valid services on device with MAC %s." % self.address)
            return False
        self.service = valid_services[0]
        return True        

    def sendMsgAllPackage(self, msg):
        # Write data directly to device
        sent_len = self.sock.send(msg)
        logging.info("Sending msg with length = %d..." % sent_len)

    def crc32(self, content):
        return zlib.crc32(content, self.crcKey if self.crckeyset else self.standardKey) & 0xffffffff

    def packPerBytes(self, bytes, control_command, i):
        result = struct.pack('<BBB', 2, control_command, i)
        result += struct.pack('<H', len(bytes))
        result += bytes
        result += struct.pack('<I', self.crc32(bytes))
        result += struct.pack('<B', 3)
        return result

    def addBytesToList(self, bytes):
        length = self.max_send_msg_length
        result = [bytes[i:i + length] for i in range(0, len(bytes), length)]
        return result

    def sendToBt(self, data_bytes, control_command, need_reply=True):
        bytes_list = self.addBytesToList(data_bytes)
        for i, bytes in enumerate(bytes_list):
            tmp = self.packPerBytes(bytes, control_command, i)
            self.sendMsgAllPackage(tmp)
        if need_reply:
            return self.recv()

    def recv(self):
        # Here we assume that there is only one received packet.
        raw_msg = self.sock.recv(self.max_recv_msg_length)
        parsed = self.resultParser(raw_msg)
        logging.info("Recv: " + codecs.encode(raw_msg, "hex_codec").decode())
        logging.info("Received %d packets: " % len(parsed) + "".join([str(p) for p in parsed]))
        return raw_msg, parsed

    def resultParser(self, data):
        base = 0
        res = []
        while base < len(data) and data[base] == '\x02':
            class Info(object):
                def __str__(self):
                    return "\nControl command: %s(%s)\nPayload length: %d\nPayload(hex): %s" % (
                        self.command, BtCommandByte.findCommand(self.command)
                        , self.payload_length, codecs.encode(self.payload, "hex_codec")
                    )

            info = Info()
            _, info.command, _, info.payload_length = struct.unpack('<BBBH', data[base:base + 5])
            info.payload = data[base + 5: base + 5 + info.payload_length]
            info.crc32 = data[base + 5 + info.payload_length: base + 9 + info.payload_length]
            base += 10 + info.payload_length
            res.append(info)
        return res

    def registerCrcKeyToBt(self, key=0x6968634 ^ 0x2e696d):
        logging.info("Setting CRC32 key...")
        msg = struct.pack('<I', int(key ^ self.standardKey))
        self.sendToBt(msg, BtCommandByte.PRT_SET_CRC_KEY)
        self.crcKey = key
        self.crckeyset = True
        logging.info("CRC32 key set.")

    def sendPaperTypeToBt(self, paperType=0):
        # My guess:
        # paperType=0: normal paper
        # paperType=1: official paper
        msg = struct.pack('<B', paperType)
        self.sendToBt(msg, BtCommandByte.PRT_SET_PAPER_TYPE)

    def sendPowerOffTimeToBt(self, poweroff_time=0):
        msg = struct.pack('<H', poweroff_time)
        self.sendToBt(msg, BtCommandByte.PRT_SET_POWER_DOWN_TIME)

    def sendImageToBt(self, binary_img):
        self.sendPaperTypeToBt()
        # msg = struct.pack("<%dc" % len(binary_img), *map(bytes, binary_img))
        msg = b"".join(map(lambda x: struct.pack("<c",x.to_bytes(1,byteorder="little")),binary_img))
        # print(msg)
        self.sendToBt(msg, BtCommandByte.PRT_PRINT_DATA, need_reply=False)
        self.sendFeedLineToBt(self.padding_line)

    def sendSelfTestToBt(self):
        msg = struct.pack('<B', 0)
        self.sendToBt(msg, BtCommandByte.PRT_PRINT_TEST_PAGE)

    def sendDensityToBt(self, density):
        msg = struct.pack('<B', density)
        self.sendToBt(msg, BtCommandByte.PRT_SET_HEAT_DENSITY)

    def sendFeedLineToBt(self, length):
        msg = struct.pack('<H', length)
        self.sendToBt(msg, BtCommandByte.PRT_FEED_LINE)

    def queryBatteryStatus(self):
        msg = struct.pack('<B', 1)
        self.sendToBt(msg, BtCommandByte.PRT_GET_BAT_STATUS)

    def queryDensity(self):
        msg = struct.pack('<B', 1)
        self.sendToBt(msg, BtCommandByte.PRT_GET_HEAT_DENSITY)

    def sendFeedToHeadLineToBt(self, length):
        msg = struct.pack('<H', length)
        self.sendToBt(msg, BtCommandByte.PRT_FEED_TO_HEAD_LINE)

    def queryPowerOffTime(self):
        msg = struct.pack('<B', 1)
        self.sendToBt(msg, BtCommandByte.PRT_GET_POWER_DOWN_TIME)

    def querySNFromBt(self):
        msg = struct.pack('<B', 1)
        self.sendToBt(msg, BtCommandByte.PRT_GET_SN)

    def queryHardwareInfo(self):
        msg = struct.pack('<B', 1)
        self.sendToBt(msg, BtCommandByte.PRT_GET_HW_INFO)
