# URO V1 r3 — Android phone flashing

## Firmware image

- Target: ESP32-S3-WROOM-1-N16R8 (16 MB flash, 8 MB OPI PSRAM)
- Combined image: `URO-V1-phone-flash-r3.bin`
- Flash address for the combined image: `0x0`
- Build: PlatformIO / Arduino, firmware version 0.2.0
- Build result: successful compile; no physical board test has been performed.

The combined image contains the bootloader, partition table, Arduino boot_app0 data and application image. Its component offsets are listed in `firmware/release/flash-manifest.json`.

## J6 programming header

J6 is a 2×3 header. The schematic pad numbers map as follows:

| J6 pad | Signal |
|---:|---|
| 1 | GND |
| 2 | +3V3 |
| 3 | UART_TX |
| 4 | UART_RX |
| 5 | ESP_EN |
| 6 | BOOT0 / GPIO0 |

Use 3.3 V logic only. Do not apply 5 V to UART or GPIO pins.

## Phone workflow

1. Use a compatible USB-OTG connection from the Android phone to the board's USB-C port. Do not connect the LiPo battery for the first firmware test.
2. The ESP32-S3 must be in ROM download mode for the first flash. J6 exposes BOOT0 and EN for that purpose; use the board's documented programming procedure and have an experienced adult supervise the first hardware session.
3. Use an ESP32-S3-compatible Android USB flasher. The Play Store listing for ESP32_Flasher states support for ESP32-S3 and USB OTG; it is a third-party app, not an Espressif app.
4. Select the combined file `URO-V1-phone-flash-r3.bin` and set its flash offset to `0x0`. If the app only accepts separate images, use the exact component offsets in `flash-manifest.json`.
5. Do not change flash mode, frequency or size from the manifest: DIO, 80 MHz, 16 MB.

## What this firmware currently does

After boot, URO advertises a BLE UART-style service named `URO-V1`. It responds to `PING`, `STATUS`, `VERSION`, `HELP` and `REBOOT`. Camera, display and audio streaming are not yet implemented. The firmware has not been tested on a physical PCB.
