# Paperang(喵喵机) Python API

### Requirements & Dependencies

OS: Linux

Python: 3.5-3.7 (tested)

Python Modules; install with `pip3 install [modulename]`
1. `pybluez` Needed by operating on the system bluetooth stack
2. `numpy`
3. `scikit-image`
4. `Cython`
5. `instakit`
`pilkit`
`numba`
`watchgod` (to watch little printer queue)


### macOS instructions/usage

On the command line, in terminal or your favorite console app:
1. ensure you have python3 installed via `which python3`


Connect your paperang to your mac:
1. Settings > Bluetooth
2. Make sure bluetooth is on
3. Find device named "paperang" and click "connect"
   you'll get a dialog that tells you that you must configure the paperang in printer settings. the problem is that it doesn't show up in the printer list. 
   Your paperang might disconnect from bluetooth at this point. That's okay!
   Hit cancel.
4. run `system_profiler SPBluetoothDataType` on the command line and look for a block like this:
   ```          Paperang:
              Address: FC-58-FA-19-04-68
              Major Type: Miscellaneous
              Minor Type: Unknown
              Services: Port
              Paired: Yes
              Configured: Yes
              Connected: No
              Firmware Version: 0x0000
              Class of Device: 0x00 0x00 0x0000
              EDR Supported: No
              eSCO Supported: No
              SSP Supported: Yes
    ```
    The value after `Address:` is what you want. Copy that text!
5. add printer. choose "IP" type. paste in the text from the previous step into the "address" field. Set "printer type" to "Generic PostScript Printer." (IDK if this matters.) You should be connected!


Printer's not staying connected.
Things I've tried that haven't worked so far:
- running the script as quickly as I can right after bluetooth connect
- running a screen job with `screen /dev/tty.PaperangPort 9600` (c.f. https://superuser.com/questions/715703/is-there-anyway-to-use-bluetooth-serial-port-profile-spp-devices-on-mac-os-x-m)
- installing blueutil and using that to connect, then running the script. (c.f. https://trevorsullivan.net/2019/07/30/control-bluetooth-on-apple-macbook-pro-from-the-command-line/)
    - error: "ERROR:root:Cannot find valid services on device with MAC FC-58-FA-19-04-68."


### 建立连接 
### Establishing a connection

`BtManager()` Leave the parameters blank to search for nearby paperang devices

`BtManager("AA:BB:CC:DD:EE:FF")` Calling with a specific MAC address skips searching for devices, saving time

### 打印图像
### Printing images

从API看该机器只能输入二值图像进行打印，所以文本转图片是在客户端完成的。
The printer's API only accepts binary images for printing, so we need to convert text to images on the client side.

The format of the printed image is binary data, each bit represents black (1) or white (0), and 384 dots per line.

```python
mmj = BtManager()
mmj.sendImageToBt(img)
mmj.disconnect()
```

### 其他杂项

`registerCrcKeyToBt(key=123456)` 更改通信CRC32 KEY(不太懂这么做是为了啥,讲道理监听到这个包就能拿到key的)

`sendPaperTypeToBt(paperType=0)` 更改纸张类型(疯狂卖纸呢)

`sendPowerOffTimeToBt(poweroff_time=0)` 更改自动关机时间

`sendSelfTestToBt()` 打印自检页面

`sendDensityToBt(density)` 设置打印密度

`sendFeedLineToBt(length)` 控制打印完后的padding

`queryBatteryStatus()` 查询剩余电量

`queryDensity()` 查询打印密度

`sendFeedToHeadLineToBt(length)` 不太懂和 `sendFeedLineToBt` 有什么区别，但是看起来都是在打印后调用的。

`queryPowerOffTime()` 查询自动关机时间

`querySNFromBt()` 查询设备SN

其实还有挺多操作的，有兴趣的看着`const.py`猜一猜好了。

### 图像工具

`ImageConverter.image2bmp(path)` 任意图像到可供打印的二进制数据转换
 
`TextConverter.text2bmp(text)` 指定文字到可供打印的二进制数据转换

### 微信公众平台工具

两个小脚本，用来实现发送图片给微信公众号后自动打印。

`wechat.php` 用于VPS接收腾讯数据，默认只允许指定用户打印。

`printer_server.py` 放置于树莓派等有蓝牙的靠近喵喵机的机器上运行，可以使用`tinc`等建立VPN以供VPS直接访问。

### 吐槽

这玩意就不能增加一个多次打印的功能吗？以较低温度多次打印再走纸，应该可以实现打印灰度图的。

逆了好久的固件也没搞出来啥东西，真是菜。希望有大佬能告诉我一点人生的经验。

顺便丢两个芯片型号: `NUC123LD4BN0`, `STM32F071CBU6`，似乎是Cortex-M0。

PS: 本代码仅供非盈利用途，如用于商业用途请另请高明。

### Acknowledgement 致谢
Thanks for all the reverse engineering work done by the original author of this project.


