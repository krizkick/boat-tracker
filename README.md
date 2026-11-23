# boat-tracker

Boat tracking through AIS. The host service downloads current vessel data, creates a map image, and uploads `kart.bin` and `versjon.txt` to Azure Blob Storage. An ESP32 client checks the version and downloads the map when it changes.

## Configuration

Set `CLIENT_ID`, `CLIENT_SECRET`, `MMSI`, `AZURE_CONNECTION_STRING`, and `AZURE_SAS_TOKEN` for the host service.

ESP32 deployments also need `WIFI_SSID`, `WIFI_PASSWORD`, `VERSION_LINK`, and `MAP_LINK` in the local `secrets` module.
