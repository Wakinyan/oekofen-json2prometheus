import json
import requests
from flask import Flask, Response

app = Flask(__name__)

def convert_to_prometheus_metric(data):
    metrics = []

    # Block system
    block_name = "system"
    system = data.get(block_name, {})
    #metrics.append(f"oekofen_metric_name_1st_level[{{label=\"value\"[, label=\"value\"]}}] {system.get(metric_name_2nd_level[, default_value])}
    metrics.append(f"oekofen_ambient_temperature{{unit=\"°C\", factor=\"0.1\"}} {system.get('L_ambient')}\n")
    metrics.append(f"oekofen_system_errors {system.get('L_errors')}\n")
    metrics.append(f"oekofen_system_usb_stick {system.get('L_usb_stick')}\n")
    metrics.append(f"oekofen_system_existing_boiler{{unit=\"°C\", factor=\"0.1\"}} {system.get('L_existing_boiler')}\n")
    # ... continue adding other weather metrics

    # Block weather
    block_name = "weather"
    weather = data.get(block_name, {})
    metrics.append(f"oekofen_weather_info{{source=\"{weather.get('L_source')}\", location=\"{weather.get('L_location')}\"}} 1\n")
    metrics.append(f"oekofen_weather_temperature{{unit=\"°C\", factor=\"0.1\"}} {weather.get('L_temp',0)}\n")
    metrics.append(f"oekofen_weather_clouds{{unit=\"%\", factor=\"1\"}} {weather.get('L_clouds',-1)}\n")
    metrics.append(f"oekofen_weather_forecast_temperature_average{{unit=\"°C\", factor=\"0.1\"}} {weather.get('L_forecast_temp',0)}\n")
    metrics.append(f"oekofen_weather_forecast_clouds_average{{unit=\"%\", factor=\"1\"}} {weather.get('L_forecast_clouds',-1)}\n")
    metrics.append(f"oekofen_weather_forecast_day {weather.get('L_forecast_today',-1)}\n")
    metrics.append(f"oekofen_weather_starttime {weather.get('L_starttime',-1)}\n")
    metrics.append(f"oekofen_weather_endtime {weather.get('L_endtime',-1)}\n")
    metrics.append(f"oekofen_weather_cloud_limit{{unit=\"%\", factor=\"1\"}} {weather.get('cloud_limit',-1)}\n")
    metrics.append(f"oekofen_weather_hysteresys{{unit=\"K\", factor=\"0.1\"}} {weather.get('hysteresys',0)}\n")
    metrics.append(f"oekofen_weather_offtemp{{unit=\"°C\", factor=\"0.1\"}} {weather.get('offtemp',0)}\n")
    metrics.append(f"oekofen_weather_lead{{unit=\"minutes\", factor=\"1\"}} {weather.get('lead',0)}\n")
    metrics.append(f"oekofen_weather_refresh {weather.get('refresh',0)}\n")
    metrics.append(f"oekofen_weather_oekomode {weather.get('oekomode',-1)}\n")
    # ... continue adding other weather metrics

    # Block forecast
    block_name = "forecast"
    # "forecast_info":"date|temp|cloud|speed|image|code|unit[|sunrise|sunset] code see https://openweathermap.org/weather-conditions"
    forecast = data.get(block_name, {})
    for key, value in forecast.items():
        parts = value.split("|")
        if len(parts) >= 6:
            # Get number from key (after "L_w_")
            forecast_number = int(key[4:])

            # temperature
            metrics.append(f"oekofen_weather_forecast_{forecast_number*3}h_temperature{{unit=\"°C\", factor=\"1\"}} {parts[1]}\n")

            # cloud
            metrics.append(f"oekofen_weather_forecast_{forecast_number*3}h_clouds{{unit=\"%\", factor=\"1\"}} {parts[2]}\n")

            # windspeed
            metrics.append(f"oekofen_weather_forecast_{forecast_number*3}h_windspeed{{unit=\"km/h\", factor=\"1\"}} {(parts[3])[:-4]}\n")

            # openweathermap code see https://openweathermap.org/weather-conditions"
            metrics.append(f"oekofen_weather_forecast_{forecast_number*3}h_code{{ow_image_code=\"{parts[4]}\"}} {parts[5]}\n")

    # Block hk1
    block_name = "hk1"
    block_data = data.get(block_name, {})
    # set name manuel within this script
    #block_data['name'] = "Heizkreis"
    metrics.append(f"oekofen_heating_circuit_roomtemp_actual{{unit=\"°C\", factor=\"0.1\", part_name=\"{block_data.get('name')}\", oekofen_part_id=\"{block_name}\"}} {block_data.get('roomtemp_act',0)}\n")
    metrics.append(f"oekofen_heating_circuit_roomtemp_setpoint{{unit=\"°C\", factor=\"0.1\", part_name=\"{block_data.get('name')}\", oekofen_part_id=\"{block_name}\"}} {block_data.get('roomtemp_set',0)}\n")
    metrics.append(f"oekofen_heating_circuit_flowtemp_act{{unit=\"°C\", factor=\"0.1\", part_name=\"{block_data.get('name')}\", oekofen_part_id=\"{block_name}\"}} {block_data.get('flowtemp_act',0)}\n")
    metrics.append(f"oekofen_heating_circuit_flowtemp_set{{unit=\"°C\", factor=\"0.1\", part_name=\"{block_data.get('name')}\", oekofen_part_id=\"{block_name}\"}} {block_data.get('flowtemp_set',0)}\n")
    metrics.append(f"oekofen_heating_circuit_comfort{{unit=\"K\", factor=\"0.1\", part_name=\"{block_data.get('name')}\", oekofen_part_id=\"{block_name}\"}} {block_data.get('L_comfort',0)}\n")
    metrics.append(f"oekofen_heating_circuit_state{{statetext=\"{block_data.get('L_statetext')}\", part_name=\"{block_data.get('name')}\", oekofen_part_id=\"{block_name}\"}} {block_data.get('L_state',-1)}\n")
    metrics.append(f"oekofen_heating_circuit_pump{{part_name=\"{block_data.get('name')}\", oekofen_part_id=\"{block_name}\"}} {block_data.get('L_pump',-1)}\n")
    metrics.append(f"oekofen_heating_circuit_remote_override{{unit=\"K\", factor=\"0.1\", part_name=\"{block_data.get('name')}\", oekofen_part_id=\"{block_name}\"}} {block_data.get('remote_override',0)}\n")
    metrics.append(f"oekofen_heating_circuit_mode_auto{{part_name=\"{block_data.get('name')}\", oekofen_part_id=\"{block_name}\"}} {block_data.get('mode_auto',-1)}\n")
    metrics.append(f"oekofen_heating_circuit_time_programme{{part_name=\"{block_data.get('name')}\", oekofen_part_id=\"{block_name}\"}} {block_data.get('time_prg',-1)}\n")
    metrics.append(f"oekofen_heating_circuit_temperature_setback{{unit=\"°C\", factor=\"0.1\", part_name=\"{block_data.get('name')}\", oekofen_part_id=\"{block_name}\"}} {block_data.get('temp_setback',0)}\n")
    metrics.append(f"oekofen_heating_circuit_temperature_heat{{unit=\"°C\", factor=\"0.1\", part_name=\"{block_data.get('name')}\", oekofen_part_id=\"{block_name}\"}} {block_data.get('temp_heat',0)}\n")
    metrics.append(f"oekofen_heating_circuit_temperatuer_vacation{{unit=\"°C\", factor=\"0.1\", part_name=\"{block_data.get('name')}\", oekofen_part_id=\"{block_name}\"}} {block_data.get('temp_vacation',0)}\n")
    metrics.append(f"oekofen_heating_circuit_oekomode{{part_name=\"{block_data.get('name')}\", oekofen_part_id=\"{block_name}\"}} {block_data.get('oekomode',-1)}\n")
    # ... continue adding other hk1 metrics

    block_name = "pu1"
    block_data = data.get(block_name, {})
    # set name manuel within this script
    #block_data['name'] = "Pufferspeicher"
    metrics.append(f"oekofen_buffer_temperature_top_actual{{unit=\"°C\", factor=\"0.1\", part_name=\"{block_data.get('name')}\", oekofen_part_id=\"{block_name}\"}} {block_data.get('L_tpo_act', 0)}\n")
    metrics.append(f"oekofen_buffer_temperature_middle_actual{{unit=\"°C\", factor=\"0.1\", part_name=\"{block_data.get('name')}\", oekofen_part_id=\"{block_name}\"}} {block_data.get('L_tpm_act', 0)}\n")
    metrics.append(f"oekofen_buffer_temperature_top_setpoint{{unit=\"°C\", factor=\"0.1\", part_name=\"{block_data.get('name')}\", oekofen_part_id=\"{block_name}\"}} {block_data.get('L_tpo_set', 0)}\n")
    metrics.append(f"oekofen_buffer_temperature_middle_setpoint{{unit=\"°C\", factor=\"0.1\", part_name=\"{block_data.get('name')}\", oekofen_part_id=\"{block_name}\"}} {block_data.get('L_tpm_set', 0)}\n")
    metrics.append(f"oekofen_buffer_pump_release_temperature{{unit=\"°C\", factor=\"0.1\", part_name=\"{block_data.get('name')}\", oekofen_part_id=\"{block_name}\"}} {block_data.get('L_pump_release', 0)}\n")
    metrics.append(f"oekofen_buffer_pump{{unit=\"%\", factor=\"1\", part_name=\"{block_data.get('name')}\", oekofen_part_id=\"{block_name}\"}} {block_data.get('L_pump', -1)}\n")
    metrics.append(f"oekofen_buffer_state{{nstatetext=\"{block_data.get('L_statetext')}\", part_name=\"{block_data.get('name')}\", oekofen_part_id=\"{block_name}\"}} {block_data.get('L_state', -1)}\n")
    metrics.append(f"oekofen_buffer_mintemp_off{{unit=\"°C\", factor=\"0.1\", part_name=\"{block_data.get('name')}\", oekofen_part_id=\"{block_name}\"}} {block_data.get('mintemp_off', 0)}\n")
    metrics.append(f"oekofen_buffer_mintemp_on{{unit=\"°C\", factor=\"0.1\", part_name=\"{block_data.get('name')}\", oekofen_part_id=\"{block_name}\"}} {block_data.get('mintemp_on', 0)}\n")
    metrics.append(f"oekofen_buffer_ext_mintemp_off{{unit=\"°C\", factor=\"0.1\", part_name=\"{block_data.get('name')}\", oekofen_part_id=\"{block_name}\"}} {block_data.get('ext_mintemp_off', 0)}\n")
    metrics.append(f"oekofen_buffer_ext_mintemp_on{{unit=\"°C\", factor=\"0.1\", part_name=\"{block_data.get('name')}\", oekofen_part_id=\"{block_name}\"}} {block_data.get('ext_mintemp_on', 0)}\n")

    block_name = "ww1"
    block_data = data.get(block_name, {})
    # set name manuel within this script
    #block_data['name'] = "Warmwasser"
    metrics.append(f"oekofen_hot_water_temperature_setpoint{{unit=\"°C\", factor=\"0.1\", part_name=\"{block_data.get('name')}\", oekofen_part_id=\"{block_name}\"}} {block_data.get('L_temp_set', 0)}\n")
    metrics.append(f"oekofen_hot_water_ontemp_actual{{unit=\"°C\", factor=\"0.1\", part_name=\"{block_data.get('name')}\", oekofen_part_id=\"{block_name}\"}} {block_data.get('L_ontemp_act', 0)}\n")
    metrics.append(f"oekofen_hot_water_offtemp_actual{{unit=\"°C\", factor=\"0.1\", part_name=\"{block_data.get('name')}\", oekofen_part_id=\"{block_name}\"}} {block_data.get('L_offtemp_act', 0)}\n")
    metrics.append(f"oekofen_hot_water_pump{{part_name=\"{block_data.get('name')}\", oekofen_part_id=\"{block_name}\"}} {block_data.get('L_pump', -1)}\n")
    metrics.append(f"oekofen_hot_water_state{{statetext=\"{block_data.get('L_statetext')}\", part_name=\"{block_data.get('name')}\", oekofen_part_id=\"{block_name}\"}} {block_data.get('L_state', -1)}\n")
    metrics.append(f"oekofen_hot_water_time_programme{{part_name=\"{block_data.get('name')}\", oekofen_part_id=\"{block_name}\"}} {block_data.get('time_prg', -1)}\n")
    metrics.append(f"oekofen_hot_water_sensor_on{{part_name=\"{block_data.get('name')}\", oekofen_part_id=\"{block_name}\"}} {block_data.get('sensor_on', -1)}\n")
    metrics.append(f"oekofen_hot_water_sensor_off{{part_name=\"{block_data.get('name')}\", oekofen_part_id=\"{block_name}\"}} {block_data.get('sensor_off', -1)}\n")
    metrics.append(f"oekofen_hot_water_mode_auto{{part_name=\"{block_data.get('name')}\", oekofen_part_id=\"{block_name}\"}} {block_data.get('mode_auto', -1)}\n")
    metrics.append(f"oekofen_hot_water_mode_dhw{{part_name=\"{block_data.get('name')}\", oekofen_part_id=\"{block_name}\"}} {block_data.get('mode_dhw', -1)}\n")
    metrics.append(f"oekofen_hot_water_heat_once{{part_name=\"{block_data.get('name')}\", oekofen_part_id=\"{block_name}\"}} {block_data.get('heat_once', -1)}\n")
    metrics.append(f"oekofen_hot_water_temp_min_set{{unit=\"°C\", factor=\"0.1\", part_name=\"{block_data.get('name')}\", oekofen_part_id=\"{block_name}\"}} {block_data.get('temp_min_set', 0)}\n")
    metrics.append(f"oekofen_hot_water_temp_max_set{{unit=\"°C\", factor=\"0.1\", part_name=\"{block_data.get('name')}\", oekofen_part_id=\"{block_name}\"}} {block_data.get('temp_max_set', 0)}\n")
    metrics.append(f"oekofen_hot_water_smartstart{{part_name=\"{block_data.get('name')}\", oekofen_part_id=\"{block_name}\"}} {block_data.get('smartstart', -1)}\n")
    metrics.append(f"oekofen_hot_water_use_boiler_heat{{part_name=\"{block_data.get('name')}\", oekofen_part_id=\"{block_name}\"}} {block_data.get('use_boiler_heat', -1)}\n")
    metrics.append(f"oekofen_hot_water_oekomode{{part_name=\"{block_data.get('name')}\", oekofen_part_id=\"{block_name}\"}} {block_data.get('oekomode', -1)}\n")

    block_name = "sk1"
    block_data = data.get(block_name, {})
    # set name manuel within this script
    #block_data['name'] = "Solarkreis"
    metrics.append(f"oekofen_solar_circuit_collector_temperature_actual{{unit=\"°C\", factor=\"0.1\", part_name=\"{block_data.get('name')}\", oekofen_part_id=\"{block_name}\"}} {block_data.get('L_koll_temp', 0)}\n")
    metrics.append(f"oekofen_solar_circuit_buffer_temperature_bottom{{unit=\"%\", factor=\"1\", part_name=\"{block_data.get('name')}\", oekofen_part_id=\"{block_name}\"}} {block_data.get('L_spu', 0)}\n")
    metrics.append(f"oekofen_solar_circuit_pump{{part_name=\"{block_data.get('name')}\", oekofen_part_id=\"{block_name}\"}} {block_data.get('L_pump', -1)}\n")
    metrics.append(f"oekofen_solar_circuit_state{{statetext=\"{block_data.get('L_statetext')}\", part_name=\"{block_data.get('name')}\", oekofen_part_id=\"{block_name}\"}} {block_data.get('L_state', -1)}\n")
    metrics.append(f"oekofen_solar_circuit_mode{{part_name=\"{block_data.get('name')}\", oekofen_part_id=\"{block_name}\"}} {block_data.get('mode', -1)}\n")
    metrics.append(f"oekofen_solar_circuit_cooling{{part_name=\"{block_data.get('name')}\", oekofen_part_id=\"{block_name}\"}} {block_data.get('cooling', -1)}\n")
    metrics.append(f"oekofen_solar_circuit_buffer_temperature_bottom_max{{part_name=\"{block_data.get('name')}\", oekofen_part_id=\"{block_name}\"}} {block_data.get('spu_max', 0)}\n")

    block_name = "pe1"
    block_data = data.get(block_name, {})
    # set name manuel within this script
    #block_data['name'] = "Pelletkessel"
    metrics.append(f"oekofen_pellematic_info{{pellematic_type=\"{block_data.get('L_type')}\", part_name=\"{block_data.get('name')}\", oekofen_part_id=\"{block_name}\"}} 1\n")
    metrics.append(f"oekofen_pellematic_temp_actual{{unit=\"°C\", factor=\"0.1\", part_name=\"{block_data.get('name')}\", oekofen_part_id=\"{block_name}\"}} {block_data.get('L_temp_act', 0)}\n")
    metrics.append(f"oekofen_pellematic_temp_setpoint{{unit=\"°C\", factor=\"0.1\", part_name=\"{block_data.get('name')}\", oekofen_part_id=\"{block_name}\"}} {block_data.get('L_temp_set', 0)}\n")
    metrics.append(f"oekofen_pellematic_exhaust_gas_temperature{{unit=\"°C\", factor=\"0.1\", part_name=\"{block_data.get('name')}\", oekofen_part_id=\"{block_name}\"}} {block_data.get('L_ext_temp', 0)}\n")
    metrics.append(f"oekofen_pellematic_combustion_chamber_temperature_actual{{unit=\"°C\", factor=\"0.1\", part_name=\"{block_data.get('name')}\", oekofen_part_id=\"{block_name}\"}} {block_data.get('L_frt_temp_act', 0)}\n")
    metrics.append(f"oekofen_pellematic_combustion_chamber_temperature_setpoint{{unit=\"°C\", factor=\"0.1\", part_name=\"{block_data.get('name')}\", oekofen_part_id=\"{block_name}\"}} {block_data.get('L_frt_temp_set', 0)}\n")
    metrics.append(f"oekofen_pellematic_combustion_chamber_end_temperature{{unit=\"°C\", factor=\"0.1\", part_name=\"{block_data.get('name')}\", oekofen_part_id=\"{block_name}\"}} {block_data.get('L_frt_temp_end', 0)}\n")
    metrics.append(f"oekofen_pellematic_burner_contact{{part_name=\"{block_data.get('name')}\", oekofen_part_id=\"{block_name}\"}} {block_data.get('L_br', -1)}\n")
    metrics.append(f"oekofen_pellematic_ak{{part_name=\"{block_data.get('name')}\", oekofen_part_id=\"{block_name}\"}} {block_data.get('L_ak', -1)}\n")
    metrics.append(f"oekofen_pellematic_emergency_stop{{part_name=\"{block_data.get('name')}\", oekofen_part_id=\"{block_name}\"}} {block_data.get('L_not', -1)}\n")
    metrics.append(f"oekofen_pellematic_safety_thermostat{{part_name=\"{block_data.get('name')}\", oekofen_part_id=\"{block_name}\"}} {block_data.get('L_stb', -1)}\n")
    metrics.append(f"oekofen_pellematic_modulation{{unit=\"%\", factor=\"1\", part_name=\"{block_data.get('name')}\", oekofen_part_id=\"{block_name}\"}} {block_data.get('L_modulation', -1)}\n")
    metrics.append(f"oekofen_pellematic_burner_runtime{{unit=\"zs\", factor=\"0.01\", part_name=\"{block_data.get('name')}\", oekofen_part_id=\"{block_name}\"}} {block_data.get('L_runtimeburner', -1)}\n")
    metrics.append(f"oekofen_pellematic_burner_resttime{{unit=\"zs\", factor=\"0.01\", part_name=\"{block_data.get('name')}\", oekofen_part_id=\"{block_name}\"}} {block_data.get('L_resttimeburner', -1)}\n")
    metrics.append(f"oekofen_pellematic_airflow{{unit=\"%\", factor=\"1\", part_name=\"{block_data.get('name')}\", oekofen_part_id=\"{block_name}\"}} {block_data.get('L_currentairflow', -1)}\n")
    metrics.append(f"oekofen_pellematic_lowpressure_actual{{unit=\"EH\", factor=\"0.1\", part_name=\"{block_data.get('name')}\", oekofen_part_id=\"{block_name}\"}} {block_data.get('L_lowpressure', -1)}\n")
    metrics.append(f"oekofen_pellematic_lowpressure_setpoint{{unit=\"EH\", factor=\"0.1\", part_name=\"{block_data.get('name')}\", oekofen_part_id=\"{block_name}\"}} {block_data.get('L_lowpressure_set', -1)}\n")
    metrics.append(f"oekofen_pellematic_vacuum_fan{{unit=\"%\", factor=\"1\", part_name=\"{block_data.get('name')}\", oekofen_part_id=\"{block_name}\"}} {block_data.get('L_fluegas', -1)}\n")
    metrics.append(f"oekofen_pellematic_uw_speed1{{unit=\"%\", factor=\"1\", part_name=\"{block_data.get('name')}\", oekofen_part_id=\"{block_name}\"}} {block_data.get('L_uw_speed', -1)}\n")
    metrics.append(f"oekofen_pellematic_state{{statetext=\"{block_data.get('L_statetext')}\", part_name=\"{block_data.get('name')}\", oekofen_part_id=\"{block_name}\"}} {block_data.get('L_state', -1)}\n")
    metrics.append(f"oekofen_pellematic_burner_starts{{part_name=\"{block_data.get('name')}\", oekofen_part_id=\"{block_name}\"}} {block_data.get('L_starts', -1)}\n")
    metrics.append(f"oekofen_pellematic_burner_runtime{{unit=\"h\", factor=\"1\", part_name=\"{block_data.get('name')}\", oekofen_part_id=\"{block_name}\"}} {block_data.get('L_runtime', -1)}\n")
    metrics.append(f"oekofen_pellematic_avg_runtime{{unit=\"min\", factor=\"1\", part_name=\"{block_data.get('name')}\", oekofen_part_id=\"{block_name}\"}} {block_data.get('L_avg_runtime', -1)}\n")
    metrics.append(f"oekofen_pellematic_uw_release_temperature{{unit=\"°C\", factor=\"0.1\", part_name=\"{block_data.get('name')}\", oekofen_part_id=\"{block_name}\"}} {block_data.get('L_uw_release', 0)}\n")
    metrics.append(f"oekofen_pellematic_uw_speed2{{unit=\"%\", factor=\"1\", part_name=\"{block_data.get('name')}\", oekofen_part_id=\"{block_name}\"}} {block_data.get('L_uw', -1)}\n")
    metrics.append(f"oekofen_pellematic_storage_fill_level{{unit=\"kg\", factor=\"1\", part_name=\"{block_data.get('name')}\", oekofen_part_id=\"{block_name}\"}} {block_data.get('L_storage_fill', -1)}\n")
    metrics.append(f"oekofen_pellematic_storage_min{{unit=\"kg\", factor=\"1\", part_name=\"{block_data.get('name')}\", oekofen_part_id=\"{block_name}\"}} {block_data.get('L_storage_min', -1)}\n")
    metrics.append(f"oekofen_pellematic_storage_max{{unit=\"kg\", factor=\"1\", part_name=\"{block_data.get('name')}\", oekofen_part_id=\"{block_name}\"}} {block_data.get('L_storage_max', -1)}\n")
    metrics.append(f"oekofen_pellematic_storage_popper{{unit=\"kg\", factor=\"1\", part_name=\"{block_data.get('name')}\", oekofen_part_id=\"{block_name}\"}} {block_data.get('L_storage_popper', -1)}\n")
    metrics.append(f"oekofen_pellematic_pellet_usage_today{{unit=\"kg\", factor=\"1\", part_name=\"{block_data.get('name')}\", oekofen_part_id=\"{block_name}\"}} {block_data.get('storage_fill_today', -1)}\n")
    metrics.append(f"oekofen_pellematic_pellet_usage_yesterday{{unit=\"kg\", factor=\"1\", part_name=\"{block_data.get('name')}\", oekofen_part_id=\"{block_name}\"}} {block_data.get('storage_fill_yesterday', -1)}\n")
    metrics.append(f"oekofen_pellematic_mode{{part_name=\"{block_data.get('name')}\", oekofen_part_id=\"{block_name}\"}} {block_data.get('mode', -1)}\n")

    # Add more blocks and metrics as needed...

    return metrics

def fetch_data_from_oekofen():
    response = requests.get('http://IP:PORT/PASSWD/all')  # replace 'http://IP:PORT/PASSWD/all' with your Oekofen JSON endpoint URL
    data_text = response.text

    # fix Oekofen JSON data (missing ") in Oekofen JSON Interface V4.02a_P
    data_text_sanitized = data_text.replace('"L_statetext:', '"L_statetext":')

    return data_text_sanitized

@app.route('/metrics')
def prometheus_metrics():

    data = json.loads(fetch_data_from_oekofen())

    prometheus_metrics = convert_to_prometheus_metric(data)

    return Response(prometheus_metrics, mimetype='text/plain')

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8080)