# Oekofen JSON zu Prometheus Konverter

English description below!
Dieses Repository enthält Python-Skripte, um Daten von einem Oekofen JSON-Endpunkt zu holen und sie in ein Format zu konvertieren, das von Prometheus gelesen werden kann.

## Voraussetzungen

- Python 3
- Flask (zur Bereitstellung der URL/metrics für Prometheus)
- requests (zum Aufruf der Oekofen URL)
- json

## Installation

1. Klone dieses Repository oder lade die Skripte herunter.
2. Installiere die erforderlichen Python-Bibliotheken:

```bash
pip install Flask requests
```

3. Bearbeite die Skripte (`json2prometheus_v1.py` oder `json2prometheus_v2.py`) und setze die korrekte IP, den Port und das Passwort für deinen Oekofen JSON-Endpunkt.

4. Erstelle ein systemd-Service-File, um den Konverter als Service laufen zu lassen. Ein Beispiel für ein solches File ist unten angegeben.

## Systemd Service

Ein Beispiel für ein systemd-Service-File:

```ini
[Unit]
Description=oekofen JSON to Prometheus convert
After=network.target

[Service]
User='Username to run with'
WorkingDirectory=/path/to/json2prometheus/file/folder
ExecStart=/usr/bin/python3 json2prometheus.py

[Install]
WantedBy=multi-user.target
```

Ersetze `'Username to run with'` durch den gewünschten Benutzernamen und `/path/to/json2prometheus/file/folder` durch den tatsächlichen Pfad zu deinem Skript.

## Verwendung

Starte den Service mit:

```bash
sudo systemctl start oekofen-json-to-prometheus.service
```

Aktiviere den Service, um ihn beim Booten zu starten:

```bash
sudo systemctl enable oekofen-json-to-prometheus.service
```

## Hinweis

Es gibt zwei Versionen des Skripts: `json2prometheus_v1.py` und `json2prometheus_v2.py`. Die zweite Version (`v2`) bietet eine detailliertere und strukturiertere Ausgabe im Prometheus-Format.

## Beschreibung von 'json2prometheus_v2.py'

Das Skript dient dazu, Daten von einem ÖkoFen Heizsystem abzurufen und sie in ein für Prometheus verständliches Format zu konvertieren.

### Importierte Module:

- `json`: Zum Arbeiten mit JSON-Daten.
- `requests`: Zum Senden von HTTP-Anfragen.
- `flask`: Ein Mikro-Webframework in Python.

### Hauptfunktionen:

1. **`convert_to_prometheus_metric(data)`**:
    - Ziel: Konvertiert die von ÖkoFen erhaltenen Daten in ein für Prometheus verständliches Format.
    - Beispiel:
      ```python
      metrics.append(f"oekofen_ambient_temperature{{unit=\"°C\", factor=\"0.1\"}} {system.get('L_ambient')}\n")
      ```

2. **`fetch_data_from_oekofen()`**:
    - Ziel: Stellt eine HTTP-Anfrage an das ÖkoFen Heizsystem und holt die Daten.
    - Beispiel:
      ```python
      response = requests.get('http://IP:PORT/PASSWD/all')
      ```

### Flask-Endpunkt:

- **`/metrics`**:
    - Wenn dieser Endpunkt aufgerufen wird, werden die Daten von ÖkoFen abgerufen, konvertiert und als Textantwort im Prometheus-Format zurückgegeben.
    - Beispiel:
      ```python
      @app.route('/metrics')
      def prometheus_metrics():
          data = json.loads(fetch_data_from_oekofen())
          prometheus_metrics = convert_to_prometheus_metric(data)
          return Response(prometheus_metrics, mimetype='text/plain')
      ```

### Hauptausführung:

- Das Skript startet die Flask-App und hört auf Port 8080 auf dem Host 0.0.0.0.
  ```python
  if __name__ == "__main__":
      app.run(host='0.0.0.0', port=8080)


---

# Oekofen JSON to Prometheus Converter

This repository contains Python scripts to fetch data from an Oekofen JSON endpoint and convert it into a format readable by Prometheus.

## Prerequisites

- Python 3
- Flask (to provide the URL/metrics endpoint for prometheus)
- requests (to get Oekofen data from the Oekofen endpoint)
- json

## Installation

1. Clone this repository or download the scripts.
2. Install the required Python libraries:

```bash
pip install Flask requests
```

3. Edit the scripts (`json2prometheus_v1.py` or `json2prometheus_v2.py`) to set the correct IP, port, and password for your Oekofen JSON endpoint.

4. Create a systemd service file to run the converter as a service. An example of such a file is provided below.

## Systemd Service

An example systemd service file:

```ini
[Unit]
Description=oekofen JSON to Prometheus convert
After=network.target

[Service]
User='Username to run with'
WorkingDirectory=/path/to/json2prometheus/file/folder
ExecStart=/usr/bin/python3 json2prometheus.py

[Install]
WantedBy=multi-user.target
```

Replace `'Username to run with'` with the desired username and `/path/to/json2prometheus/file/folder` with the actual path to your script.

## Usage

Start the service with:

```bash
sudo systemctl start oekofen-json-to-prometheus.service
```

Enable the service to start on boot:

```bash
sudo systemctl enable oekofen-json-to-prometheus.service
```

## Note

There are two versions of the script: `json2prometheus_v1.py` and `json2prometheus_v2.py`. The second version (`v2`) provides a more detailed and structured output in Prometheus format.

## Description of 'json2prometheus_v2.py'

This script is designed to retrieve data from an ÖkoFen heating system and convert it into a format understandable by Prometheus.

### Imported Modules:

- `json`: For working with JSON data.
- `requests`: For sending HTTP requests.
- `flask`: A micro web framework in Python.

### Main Functions:

1. **`convert_to_prometheus_metric(data)`**:
    - Purpose: Converts the data received from ÖkoFen into a format understandable by Prometheus.
    - Example:
      ```python
      metrics.append(f"oekofen_ambient_temperature{{unit=\"°C\", factor=\"0.1\"}} {system.get('L_ambient')}\n")
      ```

2. **`fetch_data_from_oekofen()`**:
    - Purpose: Sends an HTTP request to the ÖkoFen heating system and retrieves the data.
    - Example:
      ```python
      response = requests.get('http://IP:PORT/PASSWD/all')
      ```

### Flask Endpoint:

- **`/metrics`**:
    - When this endpoint is accessed, it retrieves the data from ÖkoFen, converts it, and returns it as a text response in the Prometheus format.
    - Example:
      ```python
      @app.route('/metrics')
      def prometheus_metrics():
          data = json.loads(fetch_data_from_oekofen())
          prometheus_metrics = convert_to_prometheus_metric(data)
          return Response(prometheus_metrics, mimetype='text/plain')
      ```

### Main Execution:

- The script starts the Flask app and listens on port 8080 on host 0.0.0.0.
  ```python
  if __name__ == "__main__":
      app.run(host='0.0.0.0', port=8080)

