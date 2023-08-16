import json
import requests
from flask import Flask, Response

app = Flask(__name__)

def convert_to_prometheus_metric(data):
    metrics = []

    for category, values in data.items():
        for metric_name, metric_value in values.items():
            metric_name = f"{category}_{metric_name}"
            metrics.append(f"{metric_name} {metric_value}")

    return "\n".join(metrics)

def fetch_data_from_oekofen():
    response = requests.get('http://IP:PORT/PASSWD/all')  # replace 'http://IP:PORT/PASSWD/all' with your Oekofen JSON endpoint URL
    data_text = response.text

    # fix Oekofen JSON data (missing ") in Oekofen JSON Interface V4.02a_P
    data_text_sanitized = data_text.replace('"L_statetext:', '"L_statetext":')

    return data_text_sanitized

@app.route('/metrics')
def prometheus_metrics():
    # Beispielhaftes JSON-Dateiformat

    data = json.loads(fetch_data_from_oekofen())
    prometheus_metrics = convert_to_prometheus_metric(data)

    return Response(prometheus_metrics, mimetype='text/plain')

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8080) # choose your Port