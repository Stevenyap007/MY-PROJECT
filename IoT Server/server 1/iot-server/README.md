# Local IoT server

| Service | Address | Login |
|---|---|---|
| Node-RED (hub) | http://localhost:1880 | none |
| InfluxDB (logs, 30-day retention) | http://localhost:8086 | admin / iotsim12345 |
| Grafana (dashboard) | http://localhost:3000 | admin / admin12345 |
| Mosquitto (MQTT) | localhost:1883 | none |

Before first start: edit `mosquitto/config/mosquitto.conf` and replace both `yourname`.

Start:   `docker compose up -d --build`
Status:  `docker compose ps`
Logs:    `docker compose logs -f mosquitto`
Stop:    `docker compose down`   (data is kept)
Reset:   `docker compose down -v` (deletes ALL data, InfluxDB will be re-created)

Test the bridge (replace yourname):
  docker exec -it mosquitto mosquitto_sub -v -t "yourname-iotsim/#"
  docker exec -it mosquitto mosquitto_pub -t "yourname-iotsim/home/livingroom/light/set" -m ON
