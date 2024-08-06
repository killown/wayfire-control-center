from flask import Flask, render_template, request, jsonify
import configparser
import os
import logging
import xml.etree.ElementTree as ET

app = Flask(__name__)

CONFIG_FILE = os.path.expanduser('~/.config/wayfire.ini')
METADATA_PATH = '/usr/share/wayfire/metadata'

# Configure logging
logging.basicConfig(level=logging.DEBUG)

def load_config():
    """Load the configuration from the wayfire.ini file."""
    config = configparser.ConfigParser(interpolation=None)  # Disable interpolation
    config.read(CONFIG_FILE)
    return config

def parse_xml_to_html(file_path):
    """Parse XML file and convert to HTML."""
    tree = ET.parse(file_path)
    root = tree.getroot()
    return convert_element_to_html(root)

def convert_element_to_html(element):
    """Convert XML element to HTML."""
    html = "<!DOCTYPE html>\n<html lang='en'>\n<head>\n"
    html += "<meta charset='UTF-8'>\n"
    html += "<meta name='viewport' content='width=device-width, initial-scale=1.0'>\n"
    html += "<title>Plugin Documentation</title>\n"
    html += "<style>\n"
    html += "body { font-family: Arial, sans-serif; margin: 20px; }\n"
    html += "h1, h2 { color: #333; }\n"
    html += "p { margin: 10px 0; }\n"
    html += "strong { font-weight: bold; }\n"
    html += "</style>\n</head>\n<body>\n"
    
    # Extract the plugin name and description
    plugin = element.find('plugin')
    if plugin is not None:
        plugin_name = plugin.get('name')
        plugin_short_desc = plugin.find('_short').text if plugin.find('_short') is not None else "No short description provided."
        plugin_long_desc = plugin.find('_long').text if plugin.find('_long') is not None else "No long description provided."

        html += f"<h1>{plugin_name}</h1>\n"
        html += f"<p><strong>Short Description:</strong> {plugin_short_desc}</p>\n"
        html += f"<p><strong>Long Description:</strong> {plugin_long_desc}</p>\n"

        # Iterate through all options to extract relevant information
        for option in plugin.findall('option'):
            name = option.get('name')
            long_desc = option.find('_long').text if option.find('_long') is not None else "No description provided."
            default_value = option.find('default').text if option.find('default') is not None else "No default value provided."
            
            html += f"<h2>{name}</h2>\n"
            html += f"<p><strong>Description:</strong> {long_desc}</p>\n"
            html += f"<p><strong>Default Value:</strong> {default_value}</p>\n"

    html += "</body>\n</html>"
    
    return html

@app.route('/')
def index():
    """Render the index page with the configuration."""
    config = load_config()
    return render_template('index.html', config=config)

@app.route('/add_option', methods=['POST'])
def add_option():
    """Add a new option to the configuration file."""
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
        logging.error(f'Error saving configuration: {e}')
        return jsonify(status='error', message=str(e))

@app.route('/delete_option', methods=['POST'])
def delete_option():
    """Delete an option from the configuration file."""
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
                logging.error(f'Error saving configuration: {e}')
                return jsonify(status='error', message=str(e))
    return jsonify(status='error', message='Section or option not found')

@app.route('/update_option', methods=['POST'])
def update_option():
    section = request.form.get('section')
    option = request.form.get('option')
    value = request.form.get('value')

    if not section or not option or value is None:
        return jsonify({'status': 'error', 'message': 'Invalid data'}), 400

    config = load_config()

    if section not in config.sections():
        config.add_section(section)
    
    config.set(section, option, value)

    try:
        with open(CONFIG_FILE, 'w') as configfile:
            config.write(configfile)
        return jsonify({'status': 'success'})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)})

@app.route('/create_section', methods=['POST'])
def create_section():
    """Create a new section in the configuration file."""
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
        logging.error(f'Error saving configuration: {e}')
        return jsonify(status='error', message=str(e))

@app.route('/help/<section>')
def help_section(section):
    """Serve the help content for a section."""
    file_path = os.path.join(METADATA_PATH, f'{section}.xml')
    if os.path.isfile(file_path):
        html_content = parse_xml_to_html(file_path)
        return html_content
    return "Help content not found.", 404

if __name__ == '__main__':
    app.run(debug=True)

