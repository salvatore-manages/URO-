#pragma once

// URO V1 Rev 3 pin contract from DESIGN.md. Verify against the assembled PCB.
namespace uro {
// Programming strap; exposed as J6 pad 6, not driven by application firmware.
constexpr int BOOT0 = 0;
// I2S microphone + speaker share clocks.
constexpr int I2S_BCLK = 38;
constexpr int I2S_WS = 39;
constexpr int I2S_MIC_DATA = 40;
constexpr int I2S_SPK_DIN = 41;

// SPI display connector J5.
constexpr int DISP_SCLK = 42;
constexpr int DISP_MOSI = 1;
constexpr int DISP_CS = 2;
constexpr int DISP_DC = 21;
constexpr int DISP_RESET = 48;

// DVP camera connector J4.
constexpr int CAM_D0 = 4;
constexpr int CAM_D1 = 5;
constexpr int CAM_D2 = 6;
constexpr int CAM_D3 = 7;
constexpr int CAM_D4 = 15;
constexpr int CAM_D5 = 3;
constexpr int CAM_D6 = 8;
constexpr int CAM_D7 = 9;
constexpr int CAM_PCLK = 10;
constexpr int CAM_HREF = 11;
constexpr int CAM_VSYNC = 12;
constexpr int CAM_XCLK = 13;
constexpr int CAM_RESET = 14;
constexpr int CAM_PWDN = 18;
constexpr int CAM_SCCB_SCL = 17;
constexpr int CAM_SCCB_SDA = 16;
}
