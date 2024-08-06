from flask import Flask, render_template, request, jsonify
import configparser
import os
import logging
import xml.etree.ElementTree as ET
import json

app = Flask(__name__)

CONFIG_FILE = os.path.expanduser('~/.config/wayfire.ini')
METADATA_PATH = '/usr/share/wayfire/metadata'
metadata_plugins = None 

# Configure logging
logging.basicConfig(level=logging.DEBUG)

def sort_wayfire_ini_sections(config_file):
    config = configparser.ConfigParser(interpolation=None)
    config.read(config_file)
    sections = sorted(config.sections())
    sorted_config = configparser.ConfigParser(interpolation=None)
    for section in sections:
        sorted_config.add_section(section)
        for key, value in config.items(section):
            sorted_config.set(section, key, value)
    
    with open(config_file, 'w') as configfile:
        sorted_config.write(configfile)

def load_config():
    """Load the configuration from the wayfire.ini file."""
    sort_wayfire_ini_sections(CONFIG_FILE)
    config = configparser.ConfigParser(interpolation=None)  # Disable interpolation
    config.read(CONFIG_FILE)
    return config

def parse_xml_to_html(file_path):
    """Parse XML file and convert to HTML."""
    tree = ET.parse(file_path)
    root = tree.getroot()
    return convert_element_to_html(root)

def get_metadata_files():
    """Get the list of XML files from the METADATA_PATH directory."""
    try:
        files = [f for f in os.listdir(METADATA_PATH) if f.endswith('.xml')]
        return sorted([os.path.splitext(f)[0] for f in files])
    except FileNotFoundError:
        logging.error(f'METADATA_PATH {METADATA_PATH} not found.')
        return []

metadata_plugins = get_metadata_files()

def convert_element_to_html(element):
    """Convert XML element to HTML."""
    html = "<!DOCTYPE html>\n<html lang='en'>\n<head>\n"
    html += "<meta charset='UTF-8'>\n"
    html += "<meta name='viewport' content='width=device-width, initial-scale=1.0'>\n"
    html += "<title>Plugin Documentation</title>\n"
    html += "<style>\n"
    html += "body { font-family: Arial, sans-serif; margin: 20px; }\n"
    html += "h1 { color: #333; }\n"
    html += "h2 { color: #333; }\n"
    html += "h3 { color: #333; }\n"
    html += "h4 { color: #333; }\n"
    html += "p { margin: 10px 0; }\n"
    html += "strong { font-weight: bold; }\n"
    html += "pre { white-space: pre-wrap; } /* Preserve whitespace */\n"
    html += "</style>\n</head>\n<body>\n"
    
    # Extract the plugin element
    plugin = element.find('plugin')
    if plugin is not None:
        plugin_long_desc = plugin.find('_long').text.strip() if plugin.find('_long') is not None else "No long description provided."

        # Add the long description at the top with h2 tag
        html += f"<h2>{plugin_long_desc}</h2>\n"

        # Iterate through all options to extract relevant information
        for option in plugin.findall('option'):
            name = option.get('name')
            long_desc = option.find('_long').text.strip() if option.find('_long') is not None else "No description provided."
            default_value = option.find('default').text.strip() if option.find('default') is not None else "No default value provided."
            
            html += f"<h4>Option: {name}</h4>\n"
            html += f"<p>{long_desc}</p>\n"
            html += f"<p><strong>Default Value:</strong> {default_value}</p>\n"

    html += "</body>\n</html>"
    
    return html



def get_metadata():
    """Load metadata from XML files and return a list of plugins."""
    plugins = []
    for file_name in get_metadata_files():
        file_path = os.path.join(METADATA_PATH, f'{file_name}.xml')
        if os.path.isfile(file_path):
            tree = ET.parse(file_path)
            root = tree.getroot()
            plugin = root.find('plugin')
            if plugin is not None:
                plugin_name = plugin.get('name')
                plugins.append({'name': plugin_name, 'file': file_path})
    return plugins

def is_plugin_section(section, metadata_path=METADATA_PATH):
    """
    Check if a section is a plugin based on the presence of its metadata file.
    
    Args:
        section (str): The name of the section/plugin.
        metadata_path (str): The directory path where metadata XML files are stored.

    Returns:
        bool: True if the section is a plugin, False otherwise.
    """
    if not isinstance(metadata_path, str):
        raise TypeError("metadata_path should be a string")

    metadata_file = os.path.join(metadata_path, f'{section}.xml')
    return os.path.isfile(metadata_file)

@app.route('/help/<section>')
def help_content(section):
    """Fetch and return help content for a specific section."""
    xml_file = os.path.join(METADATA_PATH, f'{section}.xml')
    
    if os.path.isfile(xml_file):
        html_content = parse_xml_to_html(xml_file)
        return jsonify({'status': 'success', 'content': html_content})
    else:
        return jsonify({'status': 'error', 'message': 'Help content not found'})

def update_wayfire_ini():
    """Update the Wayfire configuration file with new sections."""
    config = load_config()
    metadata_sections = get_metadata_files()
    existing_sections = config.sections()

    for section in metadata_sections:
        if section not in existing_sections:
            config.add_section(section)
            # Optionally, set default options here
            # config.set(section, 'default_option', 'default_value')

    try:
        with open(CONFIG_FILE, 'w') as configfile:
            config.write(configfile)
        logging.info('Wayfire configuration file updated with new sections.')
    except Exception as e:
        logging.error(f'Error saving configuration: {e}')


@app.context_processor
def inject_helpers():
    """Inject helper functions and variables into the template context."""
    try:
        update_wayfire_ini()
        config = load_config()
    except Exception as e:
        logging.error(f'Error updating or loading config: {e}')
        config = configparser.ConfigParser()  # Provide a fallback or empty config

    try:
        metadata = get_metadata()
    except Exception as e:
        logging.error(f'Error loading metadata: {e}')
        metadata = []

    metadata_plugins = [item['name'] for item in metadata]
    
    enabled_plugins = config.get('core', 'plugins', fallback='').split()
    
    enabled_plugins = [plugin for plugin in enabled_plugins if plugin in metadata_plugins]

    def is_plugin_section(section):
        """Check if a section is a plugin based on its metadata."""
        return section in metadata_plugins

    return {
        'is_plugin_section': is_plugin_section,
        'plugins_list': enabled_plugins,
        'metadata': metadata
    }


@app.route('/')
def index():
    config = load_config()
    metadata = get_metadata()
    metadata_plugins = get_metadata_files()
    enabled_plugins = config.get('core', 'plugins', fallback='').split()
    if enabled_plugins is None:
        enabled_plugins = []
    if metadata is None:
        metadata = {}
    
    return render_template('index.html', config=config, metadata=metadata, metadata_plugins=metadata_plugins, enabled_plugins=enabled_plugins)

@app.route('/toggle_plugin', methods=['POST'])
def toggle_plugin():
    """Toggle the plugin in the configuration file."""
    data = request.get_json()
    plugin = data.get('plugin')

    if not plugin:
        return jsonify(status='error', message='No plugin provided'), 400

    config = load_config()
    plugins_list = config.get('core', 'plugins', fallback='').split()

    # Get the list of valid plugins from metadata
    valid_plugins = [os.path.splitext(f)[0] for f in os.listdir(METADATA_PATH) if f.endswith('.xml')]

    if plugin not in valid_plugins:
        return jsonify(status='error', message='Plugin not found in metadata'), 400

    if plugin in plugins_list:
        plugins_list.remove(plugin)
    else:
        plugins_list.append(plugin)

    config.set('core', 'plugins', ' '.join(plugins_list))

    try:
        with open(CONFIG_FILE, 'w') as configfile:
            config.write(configfile)
        logging.info(f'Toggled plugin: {plugin}. New plugins list: {plugins_list}')
        return jsonify(status='success')
    except Exception as e:
        logging.error(f'Error saving configuration: {e}')
        return jsonify(status='error', message=str(e))

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

@app.route('/icons')
def icons():
    config = load_config()
    print(metadata_plugins)
    enabled_plugins = config.get('core', 'plugins', fallback='').split()
    return render_template('icons.html', config=config, metadata_plugins=metadata_plugins, enabled_plugins=enabled_plugins)

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
        else:
            return jsonify(status='error', message='Option not found'), 400
    else:
        return jsonify(status='error', message='Section not found'), 400

if __name__ == '__main__':
    app.run(debug=True)

