# boat-tracker

Boat tracking through AIS. The host service downloads current vessel data, creates a map image, and uploads `kart.bin` and `versjon.txt` to Azure Blob Storage. An ESP32 client checks the version and downloads the map when it changes.

## Configuration

Set `CLIENT_ID`, `CLIENT_SECRET`, `MMSI`, `AZURE_CONNECTION_STRING`, and `AZURE_SAS_TOKEN` for the host service.

ESP32 deployments also need `WIFI_SSID`, `WIFI_PASSWORD`, `VERSION_LINK`, and `MAP_LINK` in the local `secrets` module.

## Hardware

The ESP32 client is intended for these parts:

- [ESP32-S3 Development Board DevKitC-1 N8R2/N16R8, 44-pin, Type-C USB](https://a.aliexpress.com/_EvXKfbu)
- [WeAct 4.2-inch e-paper/e-Ink display module, SPI, black and white](https://a.aliexpress.com/_ExqyaSE)

The display is 400 by 300 pixels; the firmware sends exactly 15,000 bytes to the display.

The repository defines these SPI and control connections:

| ESP32-S3 signal | GPIO | Display connection |
| --- | ---: | --- |
| SCK | 11 | SPI clock |
| MOSI | 12 | SPI data |
| CS | 5 | Chip select |
| DC | 17 | Data/command select |
| RST | 16 | Display reset |
| BUSY | 4 | Display busy status |

The firmware creates SPI on bus 1 at 4 MHz with clock polarity 0 and clock phase 0. The display implementation does not use an MISO connection. BUSY is configured as an input and is considered busy when it reads HIGH.

The client starts Wi-Fi, downloads `kart.bin` over HTTP from `MAP_LINK`, and writes the display. It reads `VERSION_LINK` and refreshes only when the version differs from the value stored in RTC memory. It then deep-sleeps for 300,000 ms (5 minutes).
