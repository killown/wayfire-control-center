from flask import Flask, render_template, request, jsonify, redirect, url_for
import configparser
import os

app = Flask(__name__)

CONFIG_FILE = os.path.expanduser('~/.config/wayfire.ini')

def load_config():
    config = configparser.ConfigParser(interpolation=None)  # Disable interpolation
    config.read(CONFIG_FILE)
    return config

@app.route('/')
def index():
    config = load_config()
    return render_template('index.html', config=config)

@app.route('/add_option', methods=['POST'])
def add_option():
    section = request.form['section']
    option = request.form['option']
    value = request.form['value']
    
    config = load_config()

    if section not in config.sections():
        config.add_section(section)

    config.set(section, option, value)

    try:
        with open(CONFIG_FILE, 'w') as configfile:
            config.write(configfile)
        return jsonify(status='success')
    except Exception as e:
        return jsonify(status='error', message=str(e))

@app.route('/delete_option', methods=['POST'])
def delete_option():
    section = request.form['section']
    option = request.form['option']
    
    config = load_config()
    
    if section in config:
        if option in config[section]:
            del config[section][option]
            # Save changes
            try:
                with open(CONFIG_FILE, 'w') as configfile:
                    config.write(configfile)
                return jsonify(status='success')
            except Exception as e:
                return jsonify(status='error', message=str(e))
    return jsonify(status='error', message='Section or option not found')


@app.route('/update_option', methods=['POST'])
def update_option():
    section = request.form['section']
    option = request.form['option']
    value = request.form['value']
    
    config = load_config()
    
    if section not in config:
        config.add_section(section)
    
    config[section][option] = value
    
    try:
        with open(CONFIG_FILE, 'w') as configfile:
            config.write(configfile)
        return jsonify(status='success')
    except Exception as e:
        return jsonify(status='error', message=str(e))

@app.route('/create_section', methods=['POST'])
def create_section():
    section_name = request.form.get('section_name')
    option_name = request.form.get('option_name')
    option_value = request.form.get('option_value')

    config = load_config()

    if section_name not in config.sections():
        config.add_section(section_name)
    
    config.set(section_name, option_name, option_value)

    try:
        with open(CONFIG_FILE, 'w') as configfile:
            config.write(configfile)
        return jsonify(status='success')
    except Exception as e:
        return jsonify(status='error', message=str(e))

if __name__ == '__main__':
    app.run(debug=True)

