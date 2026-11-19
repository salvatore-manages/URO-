#include <Arduino.h>
#include <BLEDevice.h>
#include <BLEServer.h>
#include <BLEUtils.h>
#include <esp_system.h>
#include <esp_heap_caps.h>
#include "uro_pins.h"

// URO V1 firmware: ESP32-S3 BLE bring-up and diagnostic command interface.
// Camera, display and audio drivers are intentionally not enabled until the
// exact camera/display modules and their electrical pin contracts are selected.
static constexpr char FW_VERSION[] = "0.2.0";
static constexpr char DEVICE_NAME[] = "URO-V1";
static constexpr char SERVICE_UUID[] = "6E400001-B5A3-F393-E0A9-E50E24DCCA9E";
static constexpr char RX_UUID[]      = "6E400002-B5A3-F393-E0A9-E50E24DCCA9E";
static constexpr char TX_UUID[]      = "6E400003-B5A3-F393-E0A9-E50E24DCCA9E";

static BLECharacteristic* txCharacteristic = nullptr;
static BLEServer* bleServer = nullptr;
static volatile bool bleConnected = false;
static uint32_t bootMillis = 0;
static String serialBuffer;

static void sendLine(const String& message) {
  Serial.println(message);
  if (bleConnected && txCharacteristic != nullptr) {
    txCharacteristic->setValue(message.c_str());
    txCharacteristic->notify();
  }
}

static String statusText() {
  const uint32_t uptime = (millis() - bootMillis) / 1000UL;
  const bool psramReady = psramFound();
  const uint32_t psramBytes = psramReady ? ESP.getPsramSize() : 0;
  String out = "URO_STATUS,fw=" + String(FW_VERSION);
  out += ",chip=" + String(ESP.getChipModel());
  out += ",rev=" + String(ESP.getChipRevision());
  out += ",uptime_s=" + String(uptime);
  out += ",heap_free=" + String(ESP.getFreeHeap());
  out += ",psram=" + String(psramReady ? "yes" : "no");
  out += ",psram_bytes=" + String(psramBytes);
  out += ",ble=" + String(bleConnected ? "connected" : "advertising");
  out += ",camera=not_configured,display=not_configured,audio=not_configured";
  out += ",battery_gauge=not_fitted";
  return out;
}

static void processCommand(String command) {
  command.trim();
  command.toUpperCase();
  if (command.isEmpty()) return;

  if (command == "PING") {
    sendLine("PONG");
  } else if (command == "STATUS") {
    sendLine(statusText());
  } else if (command == "VERSION") {
    sendLine(String("URO_VERSION,") + FW_VERSION);
  } else if (command == "HELP") {
    sendLine("COMMANDS: PING | STATUS | VERSION | HELP | REBOOT | CAMERA | DISPLAY | AUDIO");
  } else if (command == "CAMERA" || command == "DISPLAY" || command == "AUDIO") {
    sendLine("NOT_READY,select_and_verify_the_exact_external_module_before_enabling_this_driver");
  } else if (command == "REBOOT") {
    sendLine("REBOOTING");
    delay(150);
    ESP.restart();
  } else {
    sendLine("ERR,unknown_command;send=HELP");
  }
}

class ServerCallbacks final : public BLEServerCallbacks {
  void onConnect(BLEServer*) override {
    bleConnected = true;
    sendLine("URO_BLE_CONNECTED");
  }
  void onDisconnect(BLEServer* server) override {
    bleConnected = false;
    delay(80);
    server->startAdvertising();
    Serial.println("URO_BLE_DISCONNECTED; advertising restarted");
  }
};

class RxCallbacks final : public BLECharacteristicCallbacks {
  void onWrite(BLECharacteristic* characteristic) override {
    const String value = characteristic->getValue();
    if (value.length() > 0) processCommand(value);
  }
};

static void startBle() {
  BLEDevice::init(DEVICE_NAME);
  BLEDevice::setMTU(185);
  bleServer = BLEDevice::createServer();
  bleServer->setCallbacks(new ServerCallbacks());
  BLEService* service = bleServer->createService(SERVICE_UUID);

  txCharacteristic = service->createCharacteristic(
      TX_UUID, BLECharacteristic::PROPERTY_READ | BLECharacteristic::PROPERTY_NOTIFY);
  txCharacteristic->setValue("URO_READY");

  BLECharacteristic* rx = service->createCharacteristic(
      RX_UUID, BLECharacteristic::PROPERTY_WRITE | BLECharacteristic::PROPERTY_WRITE_NR);
  rx->setCallbacks(new RxCallbacks());

  service->start();
  BLEAdvertising* advertising = BLEDevice::getAdvertising();
  advertising->addServiceUUID(SERVICE_UUID);
  advertising->setScanResponse(true);
  advertising->start();
}

void setup() {
  bootMillis = millis();
  Serial.begin(115200);
  delay(250);
  Serial.println();
  Serial.printf("URO V1 firmware %s starting\n", FW_VERSION);
  Serial.printf("Chip: %s, revision %u, flash %lu MB, PSRAM %s\n",
                ESP.getChipModel(), ESP.getChipRevision(),
                ESP.getFlashChipSize() / (1024U * 1024U),
                psramFound() ? "present" : "not detected");
  startBle();
  sendLine("URO_READY;BLE=advertising;send=HELP");
}

void loop() {
  while (Serial.available() > 0) {
    const char ch = static_cast<char>(Serial.read());
    if (ch == '\n' || ch == '\r') {
      if (!serialBuffer.isEmpty()) {
        processCommand(serialBuffer);
        serialBuffer = "";
      }
    } else if (serialBuffer.length() < 120) {
      serialBuffer += ch;
    } else {
      serialBuffer = "";
      sendLine("ERR,serial_command_too_long");
    }
  }
  delay(5);
}
