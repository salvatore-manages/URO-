"""URO V1 wearable AI assistant: single source of truth for schematic and PCB nets."""
import os, sys
sys.path.insert(0, os.path.dirname(__file__))
from schematic import Schematic

HERE = os.path.dirname(os.path.abspath(__file__))
PROJECT = os.path.dirname(HERE)

def design() -> Schematic:
    s = Schematic("board", title="URO V1 — Wearable AI Assistant", rev="A", project_dir=PROJECT)

    # ESP32-S3-WROOM-1-N16R8. Pin numbers are the module's 41-pin table,
    # Espressif datasheet v1.8, pp. 10–12. GPIO35–37 are reserved for octal PSRAM.
    u1 = {
        "1":"GND", "2":"+3V3", "3":"ESP_EN",
        "4":"CAM_D0", "5":"CAM_D1", "6":"CAM_D2", "7":"CAM_D3",
        "8":"CAM_D4", "9":"CAM_SIOD", "10":"CAM_SIOC", "11":"CAM_PWDN",
        "12":"CAM_D6", "13":"USB_DM", "14":"USB_DP", "15":"CAM_D5",
        "17":"CAM_D7", "18":"CAM_PCLK", "19":"CAM_HREF", "20":"CAM_VSYNC",
        "21":"CAM_XCLK", "22":"CAM_RESET", "23":"DISP_DC",
        "24":"DISP_DC_UNUSED", "25":"DISP_RST", "27":"BOOT0",
        "31":"I2S_BCLK", "32":"I2S_LRCLK", "33":"I2S_MIC_DOUT",
        "34":"I2S_SPK_DIN", "35":"DISP_SCLK", "36":"UART_RX",
        "37":"UART_TX", "38":"DISP_CS", "39":"DISP_MOSI",
        "40":"GND", "41":"GND"
    }
    # GPIO47 is not needed; pin 24 IO47 is intentionally left NC.
    u1.pop("24")
    s.part("U1", "RF_Module:ESP32-S3-WROOM-1", "ESP32-S3-WROOM-1-N16R8",
           block="Processor", footprint="RF_Module:ESP32-S3-WROOM-1",
           fields={"MPN":"ESP32-S3-WROOM-1-N16R8","LCSC":"C2913202",
                   "Datasheet":"https://www.espressif.com/sites/default/files/documentation/esp32-s3-wroom-1_wroom-1u_datasheet_en.pdf"},
           pins=u1)

    # USB-C sink connector: USB 2.0 data plus 5 V input. CC resistors are 5.1 kΩ.
    s.part("J1", "Connector:USB_C_Receptacle_USB2.0_16P", "USB-C 16P",
           block="USB-C and ESD", footprint="Connector_USB:USB_C_Receptacle_HRO_TYPE-C-31-M-12",
           fields={"MPN":"TYPE-C-31-M-12","Datasheet":"https://www.usb.org/sites/default/files/documents/usb_type-c.zip"},
           pins={"A1":"GND","A4":"USB_5V","A5":"CC1","A6":"USB_DP_PORT","A7":"USB_DM_PORT",
                 "A8":None,"A9":"USB_5V","A12":"GND","B1":"GND","B4":"USB_5V","B5":"CC2",
                 "B6":"USB_DP_PORT","B7":"USB_DM_PORT","B8":None,"B9":"USB_5V","B12":"GND","SH":"GND"})
    s.part("U6", "parts:USBLC6-2SC6", "USBLC6-2SC6",
           block="USB-C and ESD", footprint="parts:SOT-23-6",
           fields={"MPN":"USBLC6-2SC6","LCSC":"C2687116","Datasheet":"https://www.st.com/resource/en/datasheet/usblc6-2.pdf"},
           pins={"1":"USB_DP_PORT","2":"GND","3":"USB_DM_PORT","4":"USB_DM","5":"USB_5V","6":"USB_DP"})
    s.part("R1","Device:R","5.1k 1% CC1",block="USB-C and ESD",
           footprint="Resistor_SMD:R_0603_1608Metric",fields={"MPN":"0603 5.1k 1%","LCSC":"C23186"},
           pins={"1":"CC1","2":"GND"})
    s.part("R2","Device:R","5.1k 1% CC2",block="USB-C and ESD",
           footprint="Resistor_SMD:R_0603_1608Metric",fields={"MPN":"0603 5.1k 1%","LCSC":"C23186"},
           pins={"1":"CC2","2":"GND"})

    # Battery charger/power path. BQ24074 pin table: TI SLUS810N, pp. 7–9.
    # 3-wire pack connector carries a 10k NTC lead to TS; use a protected 1-cell LiPo pack.
    s.part("J2","Connector_Generic:Conn_01x03","1S LiPo + / NTC",
           block="Battery charger and power path",
           footprint="parts:JST_PH_B3B-PH-K_1x03_P2.00mm_Vertical",
           fields={"MPN":"JST PH 3-pin battery connector"},
           pins={"1":"VBAT","2":"GND","3":"BAT_NTC"})
    s.part("U4","parts:BQ24074RGT","BQ24074 power-path charger",
           block="Battery charger and power path",
           footprint="parts:VQFN-16-1EP_3x3mm_P0.5mm_EP1.6x1.6mm",
           fields={"MPN":"BQ24074RGTT","LCSC":"C2861252","Datasheet":"https://www.ti.com/lit/ds/symlink/bq24074.pdf"},
           pins={"1":"BAT_NTC","2":"VBAT","3":"VBAT","4":"GND","5":"GND","6":"USB_5V",
                 "7":None,"8":"GND","9":None,"10":"SYS_V","11":"SYS_V","12":"ILIM_SET",
                 "13":"USB_5V","14":None,"15":None,"16":"ISET_SET","17":"GND"})
    s.part("R6","Device:R","8.2k ISET",block="Battery charger and power path",
           footprint="Resistor_SMD:R_0603_1608Metric",pins={"1":"ISET_SET","2":"GND"})
    s.part("R7","Device:R","8.2k ILIM",block="Battery charger and power path",
           footprint="Resistor_SMD:R_0603_1608Metric",pins={"1":"ILIM_SET","2":"GND"})
    s.part("C1","Device:C","10uF USB input",block="Battery charger and power path",
           footprint="Capacitor_SMD:C_0805_2012Metric",pins={"1":"USB_5V","2":"GND"})
    s.part("C2","Device:C","10uF battery",block="Battery charger and power path",
           footprint="Capacitor_SMD:C_0805_2012Metric",pins={"1":"VBAT","2":"GND"})
    s.part("C3","Device:C","10uF system",block="Battery charger and power path",
           footprint="Capacitor_SMD:C_0805_2012Metric",pins={"1":"SYS_V","2":"GND"})

    # 3.3 V buck-boost. Values follow TI TPS63020 datasheet SLVS916I, pp. 3–4, 14–16.
    s.part("U5","parts:TI TPS63020","TPS63020 3V3 buck-boost",
           block="3.3 V power supply",
           footprint="parts:VSON-14_L4.0-W3.0-P0.50-BL-EP_TI_DSJ",
           fields={"MPN":"TPS63020DSJR","LCSC":"C15483","Datasheet":"https://www.ti.com/lit/ds/symlink/tps63020.pdf"},
           pins={"1":"SYS_V","2":"GND","3":"FB_3V3","4":"+3V3","5":"+3V3",
                 "6":"SW_B","7":"SW_B","8":"SW_A","9":"SW_A","10":"SYS_V","11":"SYS_V",
                 "12":"SYS_V","13":"SYS_V","14":None,"15":"GND"})
    s.part("L1","Device:L","1.5uH 4A shielded",block="3.3 V power supply",
           footprint="Inductor_SMD:L_1210_3225Metric",
           fields={"MPN":"FPB322520D-1R5MT0","LCSC":"C29780742"},
           pins={"1":"SW_A","2":"SW_B"})
    s.part("R4","Device:R","1M FB upper",block="3.3 V power supply",
           footprint="Resistor_SMD:R_0603_1608Metric",pins={"1":"+3V3","2":"FB_3V3"})
    s.part("R5","Device:R","180k FB lower",block="3.3 V power supply",
           footprint="Resistor_SMD:R_0603_1608Metric",pins={"1":"FB_3V3","2":"GND"})
    s.part("C4","Device:C","10uF VIN",block="3.3 V power supply",
           footprint="Capacitor_SMD:C_0805_2012Metric",pins={"1":"SYS_V","2":"GND"})
    s.part("C5","Device:C","10uF VIN",block="3.3 V power supply",
           footprint="Capacitor_SMD:C_0805_2012Metric",pins={"1":"SYS_V","2":"GND"})
    s.part("C6","Device:C","22uF VOUT",block="3.3 V power supply",
           footprint="Capacitor_SMD:C_0805_2012Metric",pins={"1":"+3V3","2":"GND"})
    s.part("C7","Device:C","22uF VOUT",block="3.3 V power supply",
           footprint="Capacitor_SMD:C_0805_2012Metric",pins={"1":"+3V3","2":"GND"})
    s.part("C8","Device:C","22uF VOUT",block="3.3 V power supply",
           footprint="Capacitor_SMD:C_0805_2012Metric",pins={"1":"+3V3","2":"GND"})
    s.part("C9","Device:C","100nF VINA",block="3.3 V power supply",
           footprint="Capacitor_SMD:C_0603_1608Metric",pins={"1":"SYS_V","2":"GND"})

    # ESP32 enable/reset bias and local bypass.
    s.part("R3","Device:R","10k EN pull-up",block="Processor",
           footprint="Resistor_SMD:R_0603_1608Metric",pins={"1":"+3V3","2":"ESP_EN"})
    s.part("C10","Device:C","1uF EN reset",block="Processor",
           footprint="Capacitor_SMD:C_0603_1608Metric",pins={"1":"ESP_EN","2":"GND"})
    s.part("C11","Device:C","100nF ESP32 bypass",block="Processor",
           footprint="Capacitor_SMD:C_0603_1608Metric",pins={"1":"+3V3","2":"GND"})

    # Digital I2S microphone. LR=GND selects left channel.
    s.part("U2","parts:ICS-43434","ICS-43434 I2S MEMS microphone",
           block="Audio input",
           footprint="parts:MIC-SMD_6P-L3.5-W2.7-P0.90-BL",
           fields={"MPN":"ICS-43434","LCSC":"C5656610","Datasheet":"https://invensense.tdk.com/"},
           pins={"1":"I2S_LRCLK","2":"GND","3":"GND","4":"I2S_BCLK","5":"+3V3","6":"I2S_MIC_DOUT"})
    s.part("C12","Device:C","100nF microphone bypass",block="Audio input",
           footprint="Capacitor_SMD:C_0603_1608Metric",pins={"1":"+3V3","2":"GND"})

    # I2S class-D speaker driver. GAIN_SLOT through 100k to GND selects 15 dB;
    # SD_MODE (pin 4) is tied to +3V3 for left-channel mode per the datasheet.
    s.part("U3","parts:MAX98357A","MAX98357A I2S speaker amplifier",
           block="Audio output",
           footprint="parts:TQFN-16-1EP_3x3mm_P0.5mm_EP1.23x1.23mm",
           fields={"MPN":"MAX98357AETE+T","LCSC":"C910544","Datasheet":"https://www.analog.com/media/en/technical-documentation/data-sheets/MAX98357A.pdf"},
           pins={"1":"I2S_SPK_DIN","2":"GAIN_SEL","3":"GND","4":"+3V3",
                 "7":"+3V3","8":"+3V3","9":"SPK_P","10":"SPK_N",
                 "11":"GND","14":"I2S_LRCLK","15":"GND","16":"I2S_BCLK","17":"GND"})
    s.part("R8","Device:R","100k gain select",block="Audio output",
           footprint="Resistor_SMD:R_0603_1608Metric",pins={"1":"GAIN_SEL","2":"GND"})
    s.part("C13","Device:C","10uF amplifier bypass",block="Audio output",
           footprint="Capacitor_SMD:C_0805_2012Metric",pins={"1":"+3V3","2":"GND"})
    s.part("C14","Device:C","100nF amplifier bypass",block="Audio output",
           footprint="Capacitor_SMD:C_0603_1608Metric",pins={"1":"+3V3","2":"GND"})
    s.part("J3","Connector_Generic:Conn_01x02","8 ohm speaker",
           block="Audio output",footprint="parts:JST_PH_S2B-PH-K_1x02_P2.00mm_Horizontal",
           pins={"1":"SPK_P","2":"SPK_N"})

    # External camera daughterboard connector. Pinout is URO's defined DVP cable contract,
    # not a claim that every OV2640 breakout uses this pin order.
    cam = {"1":"GND","2":"+3V3","3":"CAM_SIOC","4":"CAM_SIOD","5":"CAM_VSYNC",
           "6":"CAM_HREF","7":"CAM_PCLK","8":"CAM_XCLK","9":"CAM_D7","10":"CAM_D6",
           "11":"CAM_D5","12":"CAM_D4","13":"CAM_D3","14":"CAM_D2","15":"CAM_D1",
           "16":"CAM_D0","17":"CAM_RESET","18":"CAM_PWDN","19":"+3V3","20":"GND"}
    s.part("J4","Connector_Generic:Conn_01x24","Camera DVP 24P FPC",
           block="Camera interface",footprint="Connector_FFC-FPC:Hirose_FH12-24S-0.5SH_1x24-1MP_P0.50mm_Horizontal",
           fields={"Description":"URO camera cable pinout; match daughterboard"},
           pins=cam)
    s.note("Camera interface","24-pin FPC for an external 3.3 V DVP camera module. Pinout is documented in DESIGN.md; camera module must match it.")

    # External SPI display connector. Backlight pin is powered from 3V3 by the display module itself.
    s.part("J5","Connector_Generic:Conn_01x08","SPI display 8P FPC",
           block="Display interface",footprint="Connector_FFC-FPC:Hirose_FH12-8S-0.5SH_1x08-1MP_P0.50mm_Horizontal",
           fields={"Description":"URO SPI display cable pinout"},
           pins={"1":"GND","2":"+3V3","3":"DISP_SCLK","4":"DISP_MOSI",
                 "5":"DISP_RST","6":"DISP_DC","7":"DISP_CS","8":"+3V3"})
    s.note("Display interface","8-pin SPI FPC for a 3.3 V display module. BLK is tied to 3V3; module must include suitable backlight current limiting.")

    # UART programming/debug header (3.3 V USB-UART adapter only).
    s.part("J6","Connector_Generic:Conn_02x03_Odd_Even","UART / BOOT / RESET 3V3",
           block="Programming and test",footprint="Connector_PinHeader_2.54mm:PinHeader_2x03_P2.54mm_Vertical",
           pins={"1":"GND","2":"+3V3","3":"UART_TX","4":"UART_RX","5":"ESP_EN","6":"BOOT0"})
    s.note("Programming and test","6-pin 3.3 V header: GND, 3V3, UART TX, UART RX, EN and GPIO0/BOOT. Use 3.3 V logic only; never connect 5 V UART signals.")

    s.note("USB-C and ESD","USB 2.0 device data to ESP32-S3 native USB; CC1/CC2 each have 5.1kΩ Rd; USBLC6 protects D+/D−.")
    s.note("Battery charger and power path","BQ24074 power-path charger for a protected 1-cell LiPo with an external 10k NTC lead. ISET 8.2kΩ gives approximately 110mA charge current; EN1=1, EN2=0 selects USB500 input limit.")
    s.note("3.3 V power supply","TPS63020 buck-boost set to approximately 3.28V using 1MΩ/180kΩ feedback, 1.5uH inductor, TI-recommended input/output capacitors.")
    s.note("Processor","ESP32-S3-WROOM-1-N16R8. GPIO35–37 reserved for octal PSRAM; GPIO19/20 reserved for native USB.")
    s.note("Audio input","ICS-43434 digital I2S microphone; LR tied low for left channel.")
    s.note("Audio output","MAX98357A I2S mono class-D amplifier. Speaker output is differential; connect an 8Ω speaker only across SPK_P/SPK_N.")

    # Explicit supply flags make the external and generated power rails visible to ERC.
    s.flag("USB_5V","+3V3","GND")
    return s

if __name__ == "__main__":
    s=design()
    s.write(os.path.join(PROJECT,"board.kicad_sch"))
    print("Parts:",len(s.parts))
    print("Nets:",len(s.nets()))
    for n,p in s.nets().items(): print(n,":",p)
