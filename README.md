# URO V1 firmware 0.2.0

This is the first **hardware bring-up firmware**, written in C++ for the ESP32-S3 module using the Arduino framework and PlatformIO. It is not yet the complete URO assistant firmware.

## Implemented

- BLE GATT UART-style service named `URO-V1`.
- `PING`, `STATUS`, `VERSION`, `HELP`, and `REBOOT` commands.
- USB CDC serial command input at 115200 baud.
- Reports chip revision, free heap, PSRAM detection and subsystem readiness.

## BLE UUIDs

- Service: `6E400001-B5A3-F393-E0A9-E50E24DCCA9E`
- Write / RX: `6E400002-B5A3-F393-E0A9-E50E24DCCA9E`
- Notify / TX: `6E400003-B5A3-F393-E0A9-E50E24DCCA9E`

Send one UTF-8 command per write. Subscribe to TX notifications to receive the response.

## Build

```sh
pio run -d firmware
```

The target is an ESP32-S3 with 16 MB flash and 8 MB octal PSRAM (`ESP32-S3-WROOM-1-N16R8`). A project-local PlatformIO board definition sets the 16 MB flash and QIO/OPI memory configuration. Confirm the actual module marking before flashing.

## Build verification

PlatformIO compiled firmware version 0.2.0 successfully for the custom 16 MB flash / 8 MB OPI PSRAM board profile. The output was validated with esptool image-info. This is a compile check only; no physical PCB has been flashed or tested.

## Android flashing

The PCB routes USB-C D+/D− directly to the ESP32-S3 native USB pins. J6 is a 2×3 header: pad 1=GND, 2=3V3, 3=UART_TX, 4=UART_RX, 5=ESP_EN, 6=GPIO0/BOOT. It exposes the signals needed to enter ROM download mode; the board does not have dedicated BOOT/RESET pushbuttons. An Android USB-OTG flasher that supports ESP32-S3 can be used, but the build-generated flash files and offsets must be followed exactly. Do not guess offsets. The combined image in `release/URO-V1-phone-flash-r3.bin` is intended to be written at `0x0`; its component layout is in `release/flash-manifest.json`.

## Not implemented yet

- Camera capture: exact camera sensor/module and flex orientation are not selected.
- Display: exact panel/controller, resolution and backlight current are not selected.
- Microphone capture and speaker playback: I2S pins are reserved, but audio driver and stream protocol are not yet integrated.
- Battery percentage: there is no fuel-gauge IC or battery ADC measurement circuit on this PCB.
- Gemini/API calls: those belong in the Android app/backend, not in this firmware.
- Secure BLE pairing, OTA update and production power management.

Do not treat this firmware as a finished wearable product. Test on a current-limited bench supply first and have an experienced adult supervise the first hardware power-up, especially when a LiPo battery is involved.
