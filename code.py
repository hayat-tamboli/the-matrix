import board
import displayio
import framebufferio
import rgbmatrix
import adafruit_display_text.label
import terminalio
from adafruit_bitmap_font import bitmap_font
import time
from math import sin
import rtc
import os
# import ipaddress
# import wifi
# import socketpool

bit_depth_value = 6
unit_width = 64
unit_height = 32
# used for chaining multiple screens
chain_width = 1
chain_height = 1
serpentine_value = True

width_value = unit_width*chain_width
height_value = unit_height*chain_height

displayio.release_displays()

matrix = rgbmatrix.RGBMatrix(
    width = width_value, height=height_value, bit_depth=bit_depth_value,
    rgb_pins = [board.GP0, board.GP1, board.GP2, board.GP3, board.GP4, board.GP5],
    addr_pins = [board.GP6, board.GP7, board.GP8, board.GP9],
    clock_pin = board.GP16, latch_pin=board.GP12, output_enable_pin=board.GP13,
    tile = chain_height, serpentine=serpentine_value,
    doublebuffer = True)

DISPLAY = framebufferio.FramebufferDisplay(matrix, auto_refresh=True,rotation=0)
DISPLAY.brightness = 0.1

now = t0 =time.monotonic_ns()
append_flag = 0

currentTime = "0"

def refreshTime() -> None:
    # resets time on refresh
    r = rtc.RTC()
    refreshTimeToConfig = time.struct_time((2024, 05, 15, 02, 32, 00, 2, -1,-1))
    if(time.time()>(time.mktime(refreshTimeToConfig))):
        r.datetime = time.localtime()
    else:
        r.datetime = refreshTimeToConfig

def calculate_current_time() -> String:
    global currentTime
    currentTime = str(time.localtime().tm_hour) + ":" + str(time.localtime().tm_min)
    return currentTime

class RGB_Api():
    def __init__(self):
        global currentTime
        currentTime = calculate_current_time()
        # Set image
        self.image = 'CN.bmp'
        # Set text
        self.txt_str = currentTime
        self.txt_color = 0x00c9f225
        self.txt_x = 14
        self.txt_y = 14
        # self.txt_font = "LeagueSpartan-Bold-16.bdf"
        self.txt_font = "Satoshi Medium-16-r.bdf"
        self.txt_line_spacing = 1
        self.txt_scale = 1

        #Set scroll
        self.scroll_speed = 10

        #The following codes don't need to be set
        self.sroll_BITMAP = displayio.OnDiskBitmap(open(self.image, 'rb'))
        self.sroll_image1 = displayio.TileGrid(
                self.sroll_BITMAP,
                pixel_shader = getattr(self.sroll_BITMAP, 'pixel_shader', displayio.ColorConverter()),
                width = 1,
                height = 1,
                x = 0,
                y = 0,
                tile_width = self.sroll_BITMAP.width,
                tile_height = self.sroll_BITMAP.height)
        self.sroll_image2 = displayio.TileGrid(
                self.sroll_BITMAP,
                pixel_shader = getattr(self.sroll_BITMAP, 'pixel_shader', displayio.ColorConverter()),
                width = 1,
                height = 1,
                x = -self.sroll_BITMAP.width,
                y = -self.sroll_BITMAP.height,
                tile_width = self.sroll_BITMAP.width,
                tile_height = self.sroll_BITMAP.height)
        if self.txt_font == terminalio.FONT:
            self.txt_font = terminalio.FONT
        else:
            self.txt_font = bitmap_font.load_font(self.txt_font)
        self.sroll_text1 = adafruit_display_text.label.Label(
                self.txt_font,
                color = self.txt_color,
                line_spacing = self.txt_line_spacing,
                scale = self.txt_scale,
                text = currentTime)
        self.sroll_text1.x = 0
        self.sroll_text1.y = DISPLAY.height//2
        self.sroll_text2 = adafruit_display_text.label.Label(
                self.txt_font,
                color = self.txt_color,
                line_spacing = self.txt_line_spacing,
                scale = self.txt_scale,
                text = currentTime)
        self.sroll_text2.x = -self.sroll_text1.bounding_box[2]
        self.sroll_text2.y = DISPLAY.height//2

        self.rebound_flag = 0 #Rebound_flag
        self.sroll_object = 0

    #@brief:  Display an image in static mode
    #@param:  self
    #@retval: None
    def static_image(self):
        BITMAP = displayio.OnDiskBitmap(open(self.image, 'rb'))
        GROUP = displayio.Group()
        GROUP.append(displayio.TileGrid(
        BITMAP,
        pixel_shader = getattr(BITMAP, 'pixel_shader', displayio.ColorConverter()),
        width = 1,
        height = 1,
        tile_width = BITMAP.width,
        tile_height = BITMAP.height))

        DISPLAY.root_group = GROUP
        DISPLAY.refresh()
        while True:
            pass

    #@brief:  Display an image from left to right in horizontal mode
    #@param:  self
    #@retval: None
    def image_left_to_right_horizontal(self):
        global append_flag
        self.sroll_image2.y = 0
        x = self.sroll_image1.x + 1
        time.sleep(1/self.scroll_speed)
        if x > self.sroll_BITMAP.width:
            x = 0
        self.sroll_image1.x = x
        self.sroll_image2.x = -(self.sroll_BITMAP.width-self.sroll_image1.x)
        if append_flag == 0:
            append_flag =1
            GROUP.append(RGB.sroll_image1)
            GROUP.append(RGB.sroll_image2)
            DISPLAY.root_group = GROUP

    #@brief:  Display an image from right to left in horizontal mode
    #@param:  self
    #@retval: None
    def image_right_to_left_horizontal(self):
        global append_flag
        self.sroll_image2.y = 0
        x = self.sroll_image1.x - 1
        time.sleep(1/self.scroll_speed)
        if x < 0:
            x = self.sroll_BITMAP.width
        self.sroll_image1.x = x
        self.sroll_image2.x = -(self.sroll_BITMAP.width-self.sroll_image1.x)
        if append_flag == 0:
            append_flag =1
            GROUP.append(RGB.sroll_image1)
            GROUP.append(RGB.sroll_image2)
            DISPLAY.root_group = GROUP

    #@brief:  Display an image from up to down in vertical mode
    #@param:  self
    #@retval: None
    def image_up_to_down_vertical(self):
        global append_flag
        self.sroll_image2.x = 0
        y = self.sroll_image1.y + 1
        time.sleep(1/self.scroll_speed)
        if y > self.sroll_BITMAP.height:
            y = 0
        self.sroll_image1.y = y
        self.sroll_image2.y = -(self.sroll_BITMAP.height-self.sroll_image1.y)
        if append_flag == 0:
            append_flag =1
            GROUP.append(RGB.sroll_image1)
            GROUP.append(RGB.sroll_image2)
            DISPLAY.root_group = GROUP

    #@brief:  Display an image from down to up in vertical mode
    #@param:  self
    #@retval: None
    def image_down_to_up_vertical(self):
        global append_flag
        self.sroll_image2.x = 0
        y = self.sroll_image1.y - 1
        time.sleep(1/self.scroll_speed)
        if y < 0:
            y = self.sroll_BITMAP.height
        self.sroll_image1.y = y
        self.sroll_image2.y = -(self.sroll_BITMAP.height-self.sroll_image1.y)
        if append_flag == 0:
            append_flag =1
            GROUP.append(RGB.sroll_image1)
            GROUP.append(RGB.sroll_image2)
            DISPLAY.root_group = GROUP

    #@brief:  Display a text in static mode
    #@param:  self
    #@retval: None
    def static_text(self):
        TEXT = adafruit_display_text.label.Label(
            self.txt_font,
            color = self.txt_color,
            scale = self.txt_scale,
            text = self.txt_str,
            line_spacing = self.txt_line_spacing
            )
        TEXT.x = self.txt_x
        TEXT.y = self.txt_y
        GROUP = displayio.Group()
        GROUP.append(TEXT)
        DISPLAY.root_group = GROUP
        DISPLAY.refresh()
        while True:
            pass


    #@brief:  Display a text from left to right in sinusoidal scrolling mode
    #@param:  self
    #@retval: None
    def text_sin_left_to_right(self):
        global append_flag
        global now
        global t0
        T = 1/self.scroll_speed
        t_max = t0 + T
        n = 5/self.scroll_speed
        A = 7.5
        Y0 = DISPLAY.height//2
        dt = (now - t0) * 1e-9
        time.sleep(1/self.scroll_speed)
        x = self.sroll_text1.x + 1
        if x > DISPLAY.width:
            x = 0
        self.sroll_text1.x = x
        self.sroll_text2.x = -(DISPLAY.width-self.sroll_text1.x)
        y =  round(Y0 + sin(dt / n) * A)
        self.sroll_text2.y=self.sroll_text1.y = y
        while True:
            now = time.monotonic_ns()
            if now > t_max:
                break
            time.sleep((t_max - now) * 1e-9)
        t_max += T
        if append_flag == 0:
            append_flag =1
            GROUP.append(self.sroll_text1)
            GROUP.append(self.sroll_text2)
            DISPLAY.root_group = GROUP

    #@brief:  Display a text from right to left in sinusoidal scrolling mode
    #@param:  self
    #@retval: None
    def text_sin_right_to_left(self):
        global append_flag
        global now
        global t0
        T = 1/self.scroll_speed
        t_max = t0 + T
        n = 5/self.scroll_speed
        A = 7.5
        Y0 = DISPLAY.height//2
        dt = (now - t0) * 1e-9
        time.sleep(1/self.scroll_speed)
        x = self.sroll_text1.x - 1
        if x < 0:
            x = DISPLAY.width
        self.sroll_text1.x = x
        self.sroll_text2.x = -(DISPLAY.width-self.sroll_text1.x)
        y =  round(Y0 + sin(dt / n) * A)
        self.sroll_text2.y=self.sroll_text1.y = y
        while True:
            now = time.monotonic_ns()
            if now > t_max:
                break
            time.sleep((t_max - now) * 1e-9)
        t_max += T
        if append_flag == 0:
            append_flag =1
            GROUP.append(self.sroll_text1)
            GROUP.append(self.sroll_text2)
            DISPLAY.root_group = GROUP

    #@brief:  Display a text from up to down in sinusoidal scrolling mode
    #@param:  self
    #@retval: None
    def text_sin_up_to_down(self):
        global append_flag
        global now
        global t0
        T = 1/self.scroll_speed
        t_max = t0 + T
        n = 5/self.scroll_speed
        A = 5
        X0 = 6
        dt = (now - t0) * 1e-9
        time.sleep(1/self.scroll_speed)
        y = self.sroll_text1.y + 1
        if y > DISPLAY.height:
            y = 0
        self.sroll_text1.y = y
        self.sroll_text2.y = -(DISPLAY.height-self.sroll_text1.y)
        x =  round(X0 + sin(dt / n) * A)
        self.sroll_text2.x=self.sroll_text1.x = x
        while True:
            now = time.monotonic_ns()
            if now > t_max:
                break
            time.sleep((t_max - now) * 1e-9)
        t_max += T
        if append_flag == 0:
            append_flag =1
            GROUP.append(self.sroll_text1)
            GROUP.append(self.sroll_text2)
            DISPLAY.root_group = GROUP

    #@brief:  Display a text from down to up in sinusoidal scrolling mode
    #@param:  self
    #@retval: None
    def text_sin_down_to_up(self):
        global append_flag
        global now
        global t0
        T = 1/self.scroll_speed
        t_max = t0 + T
        n = 5/self.scroll_speed
        A = 5
        X0 = 6
        dt = (now - t0) * 1e-9
        time.sleep(1/self.scroll_speed)
        y = self.sroll_text1.y - 1
        if y < 0:
            y = DISPLAY.height
        self.sroll_text1.y = y
        self.sroll_text2.y = -(DISPLAY.height-self.sroll_text1.y)
        x =  round(X0 + sin(dt / n) * A)
        self.sroll_text2.x=self.sroll_text1.x = x
        while True:
            now = time.monotonic_ns()
            if now > t_max:
                break
            time.sleep((t_max - now) * 1e-9)
        t_max += T
        if append_flag == 0:
            append_flag =1
            GROUP.append(self.sroll_text1)
            GROUP.append(self.sroll_text2)
            DISPLAY.root_group = GROUP

    #@brief:  Display a text from left to right in horizontal mode
    #@param:  self
    #@retval: None
    def text_left_to_right_horizontal(self):
        global append_flag
        self.sroll_text1.y=DISPLAY.height//2
        self.sroll_text2.y=DISPLAY.height//2
        x = self.sroll_text1.x + 1
        time.sleep(1/self.scroll_speed)
        if x > DISPLAY.width:
            x = 0
        self.sroll_text1.x = x
        self.sroll_text2.x=-(DISPLAY.width-self.sroll_text1.x)
        if append_flag == 0:
            append_flag =1
            GROUP.append(self.sroll_text1)
            GROUP.append(self.sroll_text2)
            DISPLAY.root_group = GROUP

    #@brief:  Display a text from left to right in horizontal mode
    #@param:  self
    #@retval: None
    def text_right_to_left_horizontal(self):
        global append_flag
        self.sroll_text1.y=DISPLAY.height//2
        self.sroll_text2.y=DISPLAY.height//2
        x = self.sroll_text1.x - 1
        time.sleep(1/self.scroll_speed)
        if x < 0:
            x = DISPLAY.width
        self.sroll_text1.x = x
        self.sroll_text2.x=-(DISPLAY.width-self.sroll_text1.x)
        if append_flag == 0:
            append_flag =1
            GROUP.append(self.sroll_text1)
            GROUP.append(self.sroll_text2)
            DISPLAY.root_group = GROUP

    #@brief:  Display a text from up to down in vertical mode
    #@param:  self
    #@retval: None
    def text_up_to_down_vertical(self):
        global append_flag
        self.sroll_text1.x=0
        self.sroll_text2.x=0
        y = self.sroll_text1.y + 1
        time.sleep(1/self.scroll_speed)
        if y > DISPLAY.height:
            y = 0
        self.sroll_text1.y = y
        self.sroll_text2.y=-(DISPLAY.height-self.sroll_text1.y)
        if append_flag == 0:
            append_flag =1
            GROUP.append(self.sroll_text1)
            GROUP.append(self.sroll_text2)
            DISPLAY.root_group = GROUP

    #@brief:  Display a text from down to up in vertical mode
    #@param:  self
    #@retval: None
    def text_down_to_up_vertical(self):
        global append_flag
        self.sroll_text1.x=0
        self.sroll_text2.x=0
        y = self.sroll_text1.y - 1
        time.sleep(1/self.scroll_speed)
        if y < 0:
            y = DISPLAY.height
        self.sroll_text1.y = y
        self.sroll_text2.y=-(DISPLAY.height-self.sroll_text1.y)
        if append_flag == 0:
            append_flag =1
            GROUP.append(self.sroll_text1)
            GROUP.append(self.sroll_text2)
            DISPLAY.root_group = GROUP

    #@brief:  Display a text in left and right rebound mode
    #@param:  self
    #@retval: None
    def text_rebound_left_and_right(self):
        global append_flag
        self.sroll_text1.y=DISPLAY.height//2
        time.sleep(1/self.scroll_speed)
        if self.rebound_flag == 0:
            x = self.sroll_text1.x + 1
            if x > DISPLAY.width-self.sroll_text1.bounding_box[2]:
                self.rebound_flag = 1
        else :
            x = self.sroll_text1.x - 1
            if x < 0:
                self.rebound_flag = 0
        self.sroll_text1.x = x
        if append_flag == 0:
            append_flag =1
            GROUP.append(self.sroll_text1)
            DISPLAY.root_group = GROUP

    #@brief:  Display a text in up and down rebound mode
    #@param:  self
    #@retval: None
    def text_rebound_up_and_down(self):
        global append_flag
        time.sleep(1/self.scroll_speed)
        if self.rebound_flag == 0:
            y = self.sroll_text1.y + 1
            if y > DISPLAY.height-8:
                self.rebound_flag = 1
        else :
            y = self.sroll_text1.y - 1
            if y < 3:
                self.rebound_flag = 0
        self.sroll_text1.y = y
        if append_flag == 0:
            append_flag =1
            GROUP.append(self.sroll_text1)
            DISPLAY.root_group = GROUP

    #@brief:  Display a time in static mode
    #@param:  self
    #@retval: None
    def static_time(self):
        global currentTime
        TEXT = adafruit_display_text.label.Label(
            self.txt_font,
            color = self.txt_color,
            scale = self.txt_scale,
            text = currentTime,
            line_spacing = self.txt_line_spacing
            )
        TEXT.x = self.txt_x
        TEXT.y = self.txt_y
        GROUP = displayio.Group()
        GROUP.append(TEXT)
        DISPLAY.root_group = GROUP
        oldTime = currentTime
        currentTime =  calculate_current_time()
        if(currentTime != oldTime):
            DISPLAY.refresh()


def main() -> None:
    refreshTime()
    RGB = RGB_Api()
    GROUP = displayio.Group()
    # print("Connecting to WiFi")

    #  connect to your SSID
    # wifi.radio.connect(os.getenv('CIRCUITPY_WIFI_SSID'), os.getenv('CIRCUITPY_WIFI_PASSWORD'))

    # print("Connected to WiFi")

    # pool = socketpool.SocketPool(wifi.radio)

    #  prints MAC address to REPL
    # print("My MAC addr:", [hex(i) for i in wifi.radio.mac_address])

    #  prints IP address to REPL
    # print("My IP address is", wifi.radio.ipv4_address)

    #  pings Google
    ## ipv4 = ipaddress.ip_address("8.8.4.4")
    # print("Ping google.com: %f ms" % (wifi.radio.ping(ipv4)*1000))

    while True:
        RGB.static_time()

if __name__ == '__main__':
    main()
