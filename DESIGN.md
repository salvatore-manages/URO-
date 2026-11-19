# URO V1 — Wearable AI Assistant PCB

## Goal

A 60 mm × 60 mm, four-layer learning prototype PCB for a pendant/wearable URO device. The ESP32-S3 handles BLE/Wi-Fi, camera capture, display control and I2S audio. An Android phone supplies the internet connection and Gemini/backend access. This is a prototype design for engineering review, not a production-ready or electrically validated consumer device.

## Selected architecture

USB-C 5 V input and a protected 1-cell LiPo battery feed a TI BQ24074 power-path charger. Its SYS output feeds a TI TPS63020 buck-boost set to approximately 3.28 V. The 3.3 V rail powers the ESP32-S3 module, digital microphone, I2S class-D amplifier, camera and display interfaces.

## Parts and evidence

| Ref | Selected part | Purpose / evidence |
|---|---|---|
| U1 | Espressif ESP32-S3-WROOM-1-N16R8, LCSC C2913202 | 16 MB flash, 8 MB octal PSRAM; module datasheet v1.8 pin table pp. 10–12, supply pp. 16–17 |
| U4 | TI BQ24074RGTT, LCSC C2861252 | 1-cell charger with power path; TI SLUS810N pin table pp. 7–9, typical application pp. 13–15 |
| U5 | TI TPS63020DSJR, LCSC C15483 | Buck-boost regulator; TI SLVS916I pin table p. 4, typical application/layout pp. 14–16 |
| L1 | FPB322520D-1R5MT0, 1.5 µH, 4 A, 6.5 A saturation, LCSC C29780742 | TPS63020 inductor |
| U2 | TDK InvenSense ICS-43434, LCSC C5656610 | I2S MEMS microphone, 1.65–3.63 V; datasheet supply/pin details pp. 4, 8 |
| U3 | MAX98357AETE+T, LCSC C910544 | I2S mono class-D speaker amplifier; datasheet pp. 4–5 |
| U6 | USBLC6-2SC6, LCSC C2687116 | USB D+/D− ESD protection |
| J1 | TYPE-C-31-M-12 USB-C receptacle | USB 2.0 device data and 5 V input; CC1/CC2 each use 5.1 kΩ Rd |
| J2 | JST PH 3-pin | Protected 1S LiPo +, pack ground and external 10 kΩ NTC lead |
| J3 | JST PH 2-pin | Differential speaker output connector; 8 Ω speaker assumed |
| J4 | Hirose FH12 24-pin, 0.5 mm FPC | URO-defined 3.3 V DVP camera cable pinout; camera daughterboard must match this contract |
| J5 | Hirose FH12 8-pin, 0.5 mm FPC | 3.3 V SPI display cable pinout; module must include suitable backlight current limiting |
| J6 | 2×3 2.54 mm header | GND, 3V3, UART TX, UART RX, ESP_EN and GPIO0/BOOT access for programming/debug |

## Power decisions

- USB-C sink: 5.1 kΩ Rd on CC1 and CC2; USBLC6-2SC6 protects the USB data pair.
- BQ24074 CE is held low to enable charging. EN1=USB_5V and EN2=GND select the 500 mA USB input-current mode. ISET=8.2 kΩ gives approximately 110 mA charge current (nominal estimate from TI's programming relationship). ILIM=8.2 kΩ is fitted but is inactive in the selected EN1/EN2 mode.
- TS is connected to the third battery connector pin. The battery pack must provide a compatible 10 kΩ NTC thermistor between that pin and pack ground; do not use a two-wire pack without revising the circuit.
- TPS63020 uses a 1.5 µH inductor, two 10 µF input capacitors, three 22 µF output capacitors and a 100 nF VINA bypass. The 1 MΩ / 180 kΩ feedback divider targets approximately 3.28 V from the 0.5 V feedback reference.
- The selected module requires a 3.0–3.6 V supply and Espressif specifies at least 0.5 A supply capability. The TPS63020 has headroom for the expected peak load, but the full simultaneous camera/Wi-Fi/audio load still needs bench verification.

## ESP32-S3 pin allocation

The module's pins 28–30 (GPIO35–37) are left unused because they are connected to the octal PSRAM on this module. GPIO19/20 are reserved for native USB D−/D+. GPIO0 (module pad 27) is brought to J6 pad 6 as BOOT0; J6 pad 5 is ESP_EN.

- Camera DVP: D0=GPIO4, D1=GPIO5, D2=GPIO6, D3=GPIO7, D4=GPIO15, D5=GPIO3, D6=GPIO8, D7=GPIO9; PCLK=GPIO10, HREF=GPIO11, VSYNC=GPIO12, XCLK=GPIO13; RESET=GPIO14, PWDN=GPIO18; SCCB SCL=GPIO17, SDA=GPIO16.
- I2S microphone: BCLK=GPIO38, WS=GPIO39, microphone data out=GPIO40. ICS-43434 LR is tied low for left channel.
- I2S speaker: DIN=GPIO41, BCLK=GPIO38, LRCLK=GPIO39. MAX98357A GAIN_SLOT is pulled low for 15 dB; SD_MODE is held high to enable the amplifier.
- SPI display: SCLK=GPIO42, MOSI=GPIO1, CS=GPIO2, DC=GPIO21, RESET=GPIO48. Display connector provides GND, 3V3, SCLK, MOSI, RESET, DC, CS and 3V3 for module backlight supply.
- UART0 programming: module RXD0/TXD0 go to J6 pad 4/pad 3 respectively. J6 pads are 1=GND, 2=3V3, 3=UART_TX, 4=UART_RX, 5=ESP_EN, 6=BOOT0. Use 3.3 V logic only.
- EN has a 10 kΩ pull-up and 1 µF reset capacitor.

## Camera and display connector contracts

J4 pinout: 1 GND, 2 3V3, 3 CAM_SIOC, 4 CAM_SIOD, 5 VSYNC, 6 HREF, 7 PCLK, 8 XCLK, 9 D7, 10 D6, 11 D5, 12 D4, 13 D3, 14 D2, 15 D1, 16 D0, 17 RESET, 18 PWDN, 19 3V3, 20 GND. Pins 21–24 are NC. This is a project-defined DVP connector contract, not a universal OV2640 pinout. Select or design the camera daughterboard to match it before connecting hardware.

J5 pinout: 1 GND, 2 3V3, 3 SCLK, 4 MOSI, 5 RESET, 6 DC, 7 CS, 8 3V3/backlight supply. Select a compatible 3.3 V SPI display module and verify its backlight current limiting before assembly.

## Routing and layout

- Board outline is 60 × 60 mm, four copper layers. F.Cu and B.Cu retain the existing routed signals; In1.Cu and In2.Cu are continuous GND reference planes. Existing B.Cu GND zone is retained. The inner planes are intended to remain unrouted.
- ESP32 module antenna is at the top edge. Keep the antenna keep-out clear of copper, battery, metal and enclosure material as specified by Espressif.
- Inner-layer ground planes provide reference/return paths for the outer signal layers. Zone fill was regenerated after the stackup change; verify the final Gerbers and factory stackup before ordering.
- Autorouter routed all 154 of 154 connections in the latest full route (752 tracks / 83 vias).

## Verification status

- Revision update: four copper layers with GND reference planes on In1.Cu and In2.Cu; added BOOT0 and ESP_EN to a 2×3 programming header J6; rerouted all 139 connections.
- The four-layer stackup is assumed by analysis (35 µm outer copper, 18 µm inner copper; 0.210/1.075/0.210 mm dielectric, εr 4.4); this stackup must be confirmed with the chosen fabricator.

- KiCad file syntax: passed.
- Schematic ERC: 0 errors, 1 warning. The warning is the MAX98357A exposed pad connected to GND; the imported symbol marks that exposed pad as unspecified.
- PCB DRC after the J6 revision and full reroute: 0 unconnected, 0 errors, 2 warnings. Both warnings are the ESP32 module antenna-edge graphic touching the board outline; confirm this is intentional against the module layout guide. Review the silkscreen and keep-out treatment before fabrication.
- Board and schematic pad connectivity: matched.
- DC estimate at the current assumed loads: +3V3 drop 117 mV (3.5%) at U1, above the 99 mV target, with a local current-density neck (223 A/mm²). Widen the 3V3 path and rerun the analysis before fabrication.
- Thermal estimate using stated average power assumptions (U1 0.32 W, U5 0.25 W, U4 0.15 W, U3 0.08 W): hottest board spot 59 °C under U5 at 25 °C ambient. This is a model, not a measured temperature.
- PDN estimate after the J6 reroute: +3V3 at U1 peaks at 1.14 Ω versus a 410 mΩ target; move/add local decoupling and re-check before production.
- Signal/EMC estimate: USB differential impedance is 130 Ω versus a 90 Ω target; several fast nets still cross reference-plane gaps. Real RF/EMC compliance has not been signed off.

## Not verified / must be checked before ordering or powering

- Camera module model, exact flex contact orientation and daughterboard pin compatibility.
- Display module model, FPC contact orientation, logic levels and backlight current.
- Battery pack dimensions, chemistry, protection, NTC curve and connector polarity. Use a protected 1-cell LiPo pack with a matching 10 kΩ NTC.
- Speaker impedance, rated power and acoustic enclosure. 8 Ω is a design assumption.
- Power integrity under simultaneous Wi-Fi TX, camera capture and speaker output; regulator/charger thermal rise; battery runtime.
- USB differential impedance, return path/EMC, RF antenna performance and enclosure keep-out.
- Silkscreen cleanup and isolated copper zone investigation.
- First-article electrical tests and manufacturer review. Do not order or connect a battery until these checks are complete.
