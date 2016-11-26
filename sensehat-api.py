from os import popen
from sense_hat import SenseHat
from flask import Flask, jsonify, request

app = Flask(__name__)
sensehat = SenseHat()

#-#
#-# LED Matrix
#-#

@app.route('/sensehat/ledmatrix/pixel/<int:x>/<int:y>', methods=['GET'])
def ledmatrix_pixel(x, y):
    '''
    Gets an individual LED matrix pixel at the specified X-Y coordinate.
    '''
    return jsonify(sensehat.get_pixel(x, y))

@app.route('/sensehat/ledmatrix/pixel/<int:x>/<int:y>', methods=['POST'])
def ledmatrix_pixel_set(x, y):
    '''
    Sets an individual LED matrix pixel at the specified X-Y coordinate
    to the specified colour.
    '''
    payload = request.json
    if payload.get('pixel'):
        sensehat.set_pixel(x, y, payload.get('pixel'))
    else:
        sensehat.set_pixel(
            x, y,
            payload.get('red'),
            payload.get('green'),
            payload.get('blue')
        )
    return 'OK'

@app.route('/sensehat/ledmatrix/pixels', methods=['GET'])
def ledmatrix_pixels():
    '''
    Gets a list containing 64 smaller lists of [R,G,B] pixels
    representing what is currently displayed on the LED matrix.
    '''
    return jsonify(sensehat.get_pixels())

@app.route('/sensehat/ledmatrix/pixels', methods=['POST'])
def ledmatrix_pixels_set():
    '''
    Updates the entire LED matrix based on a 64 length list of pixel values.
    '''
    sensehat.set_pixels(request.json)
    return 'OK'

@app.route('/sensehat/ledmatrix/letter', methods=['POST'])
def ledmatrix_letter():
    '''
    Scrolls a string of text across the LED matrix using the specified
    speed and colours.
    '''
    sensehat.show_letter(
        str(request.json.get('letter')),
        request.json.get('text_colour', [255, 255, 255]),
        request.json.get('background_colour', [0, 0, 0])
    )
    return 'OK'

@app.route('/sensehat/ledmatrix/message', methods=['POST'])
def ledmatrix_message():
    '''
    Scrolls a string of text across the LED matrix using the specified
    speed and colours.
    '''
    sensehat.show_message(
        request.json.get('message'),
        request.json.get('scroll_speed', .1),
        request.json.get('text_colour', [255, 255, 255]),
        request.json.get('background_colour', [0, 0, 0])

    )
    return 'OK'

@app.route('/sensehat/ledmatrix/rotation', methods=['GET'])
def ledmatrix_rotation():
    '''
    Gets the LED matrix rotation.
    '''
    return jsonify(sensehat.rotation)

@app.route('/sensehat/ledmatrix/rotation', methods=['POST'])
def ledmatrix_rotation_set():
    '''
    Sets the LED matrix rotation for viewing, adjust if the Pi is upside
    down or sideways. 0 is with the Pi HDMI port facing downwards.
    '''
    sensehat.set_rotation(
        request.json.get('rotation'),
        request.json.get('redraw', True),
    )
    return 'OK'

@app.route('/sensehat/ledmatrix/flip', methods=['POST'])
def ledmatrix_flip():
    '''
    Flips the image on the LED matrix horizontally or vertically.
    '''
    orientation = request.json.get('orientation')
    redraw = request.json.get('redraw', True)
    if orientation == 'horizontal':
        return jsonify(sensehat.flip_h(redraw))
    elif orientation == 'vertical':
        return jsonify(sensehat.flip_v(redraw))

@app.route('/sensehat/ledmatrix/clear', methods=['POST'])
def ledmatrix_clear():
    '''
    Sets the entire LED matrix to a single colour, defaults to blank/off.
    '''
    payload = request.json or {}
    sensehat.clear(
        payload.get('red', 0),
        payload.get('green', 0),
        payload.get('blue', 0)
    )
    return 'OK'

@app.route('/sensehat/ledmatrix/lowlight', methods=['GET'])
def ledmatrix_lowlight():
    '''
    Returns whether the LED matrix is in low light mode or not.
    '''
    return ('OFF', 'ON')[sensehat.low_light]

@app.route('/sensehat/ledmatrix/lowlight/<string:status>', methods=['POST'])
def ledmatrix_lowlight_set(status):
    '''
    Sets the LED matrix low light mode on/off.
    Useful if the Sense HAT is being used in a dark environment.
    '''
    sensehat.low_light = status.lower() == 'on'
    return 'OK'

@app.route('/sensehat/ledmatrix/gamma', methods=['GET'])
def ledmatrix_gamma():
    '''
    Gets the gamma lookup table.
    '''
    return jsonify(sensehat.gamma)

@app.route('/sensehat/ledmatrix/gamma', methods=['POST'])
def ledmatrix_gamma_set():
    '''
    Sets the gamma lookup table.
    The lookup table is a list of 32 numbers that must be between 0 and 31.
    '''
    sensehat.gamma = request.json
    return 'OK'

@app.route('/sensehat/ledmatrix/gamma/reset', methods=['POST'])
def ledmatrix_gamma_reset():
    '''
    Sets the gamma lookup table to default, ideal if you've been
    messing with it and want to get it back to a default state.
    '''
    sensehat.gamma_reset()
    return 'OK'


#-#
#-# Environmental sensors
#-#

def temperature_from_cpu():
    '''
    Gets the Raspberry Pi's CPU temperature in Celsius.
    '''
    cpu_temp = popen('/opt/vc/bin/vcgencmd measure_temp').read()
    cpu_temp = cpu_temp.replace('temp=','')
    cpu_temp = cpu_temp.replace('\'C\n','')
    return float(cpu_temp)

@app.route('/sensehat/temperature', methods=['GET'])
def temperature():
    '''
    Gets the temperature in Celsius calibrated with respect for the
    parasitic heat generated by the Raspberry Pi's CPU.
    '''
    raw_temp = sensehat.temperature
    cpu_temp = temperature_from_cpu()
    cal_temp = raw_temp - ((cpu_temp - raw_temp) / 2)
    return jsonify(cal_temp)

@app.route('/sensehat/temperature/raw', methods=['GET'])
def temperature_raw():
    '''
    Gets the temperature in Celsius.
    '''
    return jsonify(sensehat.temperature)

@app.route('/sensehat/temperature/from/humidity', methods=['GET'])
def temperature_from_humidity():
    '''
    Gets the temperature in Celsius from the humidity sensor.
    '''
    return jsonify(sensehat.temperature_from_humidity)

@app.route('/sensehat/temperature/from/pressure', methods=['GET'])
def temperature_from_pressure():
    '''
    Gets the temperature in Celsius from the pressure sensor.
    '''
    return jsonify(sensehat.temperature_from_pressure)

@app.route('/sensehat/humidity', methods=['GET'])
def humidity():
    '''
    Gets the percentage of relative humidity.
    '''
    return jsonify(sensehat.humidity)

@app.route('/sensehat/pressure', methods=['GET'])
def pressure():
    '''
    Gets the pressure in Millibars.
    '''
    return jsonify(sensehat.pressure)


#-#
#-# IMU Sensor
#-#

@app.route('/sensehat/imu/config', methods=['GET'])
def imu_config():
    '''
    Gets the status for the accelerometer, gyroscope and magnetometer sensors.
    '''
    result = {
        'accelerometer_enabled': sensehat._accel_enabled,
        'compass_enabled': sensehat._compass_enabled,
        'gyroscope_enabled': sensehat._gyro_enabled
    }
    return jsonify(result)

@app.route('/sensehat/imu/config', methods=['PUT'])
def imu_config_update():
    '''
    Enables and disables the accelerometer, gyroscope and/or magnetometer.
    '''
    sensehat.set_imu_config(
        request.json.get('compass_enabled', sensehat._compass_enabled),
        request.json.get('gyroscope_enabled', sensehat._gyro_enabled),
        request.json.get('accelerometer_enabled', sensehat._accel_enabled)
    )
    return 'OK'

@app.route('/sensehat/accelerometer', methods=['GET'])
def accelerometer():
    '''
    Calls IMU config to disable the magnetometer and gyroscope then
    gets the current orientation from the accelerometer only.
    '''
    return jsonify(sensehat.accelerometer)

@app.route('/sensehat/accelerometer/raw', methods=['GET'])
def accelerometer_raw():
    '''
    Gets the raw x, y and z axis accelerometer data.
    '''
    return jsonify(sensehat.accelerometer_raw)

@app.route('/sensehat/gyroscope', methods=['GET'])
def gyroscope():
    '''
    Calls IMU config to disable the magnetometer and accelerometer then
    gets the current orientation from the gyroscope only.
    '''
    return jsonify(sensehat.gyroscope)

@app.route('/sensehat/gyroscope/raw', methods=['GET'])
def gyroscope_raw():
    '''
    Gets the raw x, y and z axis gyroscope data.
    '''
    return jsonify(sensehat.gyroscope_raw)


@app.route('/sensehat/compass', methods=['GET'])
def compass():
    '''
    Calls IMU config to disable the gyroscope and accelerometer then
    gets the direction of North from the magnetometer in degrees.
    '''
    return jsonify(sensehat.compass)


@app.route('/sensehat/compass/raw', methods=['GET'])
def compass_raw():
    '''
    Gets the raw x, y and z axis magnetometer data.
    '''
    return jsonify(sensehat.compass_raw)


#-#
#-# MAIN
#-#

if __name__ == '__main__':
    app.run(host='0.0.0.0')
