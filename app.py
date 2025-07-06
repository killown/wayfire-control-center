from flask import Flask, render_template, request, jsonify, send_from_directory
import toml
import os
import logging
import ast
import xml.etree.ElementTree as ET
import shutil
from datetime import datetime
from wayfire import WayfireSocket

# Define source and destination
src_dir = "/usr/share/wayfire/metadata"
dest_dir = os.path.join(os.path.dirname(__file__), "metadata")

# Remove existing metadata folder if needed (optional)
if os.path.exists(dest_dir):
    shutil.rmtree(dest_dir)

# Copy the entire directory tree
try:
    shutil.copytree(src_dir, dest_dir)
    print(f"✅ Successfully copied metadata to: {dest_dir}")
except Exception as e:
    print(f"❌ Error copying metadata: {e}")


sock = WayfireSocket()
app = Flask(__name__)
app.config["DEBUG"] = True

CONFIG_FILE = os.path.expanduser("~/.config/waypanel/wayfire/wayfire.toml")
METADATA_PATH = "/usr/share/wayfire/metadata"
metadata_plugins = None

# Configure logging
logging.basicConfig(level=logging.DEBUG)


def backup_wayfire_ini():
    backup_dir = "/tmp/wayfire_config_backup/"
    os.makedirs(backup_dir, exist_ok=True)
    timestamp = datetime.now().strftime("%H-%d-%Y")
    backup_filename = f"wayfire-config-{timestamp}.ini"
    backup_path = os.path.join(backup_dir, backup_filename)
    shutil.copy2(CONFIG_FILE, backup_path)
    return backup_path


def load_config():
    """Load the configuration from the wayfire.toml file."""
    try:
        with open(CONFIG_FILE, "r") as f:
            return toml.load(f)
    except Exception as e:
        logging.error(f"Error loading TOML config: {e}")
        return {}


def parse_xml_to_html(file_path):
    """Parse XML file and convert to HTML."""
    tree = ET.parse(file_path)
    root = tree.getroot()
    return convert_element_to_html(root)


def get_metadata_files():
    """Get the list of XML files from the METADATA_PATH directory."""
    try:
        files = [f for f in os.listdir(METADATA_PATH) if f.endswith(".xml")]
        return sorted([os.path.splitext(f)[0] for f in files])
    except FileNotFoundError:
        logging.error(f"METADATA_PATH {METADATA_PATH} not found.")
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
    plugin = element.find("plugin")
    if plugin is not None:
        plugin_long_desc = (
            plugin.find("_long").text.strip()
            if plugin.find("_long") is not None
            else "No long description provided."
        )
        plugin_name = plugin.get("name")

        # Add the long description at the top with h2 tag
        html += f'<a href="https://github.com/WayfireWM/wayfire/wiki/Configuration#{plugin_name}" class="more-help-link" target="_blank">More Help In Wayfire Wiki</a>\n<br></br>'
        html += f"<h2>{plugin_long_desc}</h2>\n"

        # Iterate through all options to extract relevant information
        for option in plugin.findall("option"):
            name = option.get("name")
            long_desc = (
                option.find("_long").text.strip()
                if option.find("_long") is not None
                else "No description provided."
            )
            default_value = (
                option.find("default").text.strip()
                if option.find("default") is not None
                else "No default value provided."
            )

            html += f"<h4>Option: {name}</h4>\n"
            html += f"<p>{long_desc}</p>\n"
            html += f"<p><strong>Default Value:</strong> {default_value}</p>\n"

    html += "</body>\n</html>"

    return html


def convert_literal(s):
    try:
        return ast.literal_eval(s)
    except (ValueError, SyntaxError):
        return s


@app.route("/add_options", methods=["POST"])
def add_options():
    data = request.get_json()
    section = data.get("section")
    options = data.get("options")
    if not section or not options:
        return jsonify(status="error", message="Missing parameters"), 400
    config = load_config()
    if section not in config:
        config[section] = {}
    for option in options:
        opt = option.get("option")
        val = option.get("value")
        if opt and val:
            config[section][opt] = val
    try:
        with open(CONFIG_FILE, "w") as f:
            toml.dump(config, f)
        return jsonify(status="success")
    except Exception as e:
        logging.error(f"Error saving configuration: {e}")
        return jsonify(status="error", message=str(e))


@app.route("/delete_option", methods=["POST"])
def delete_option():
    data = request.get_json()
    section = data.get("section")
    option = data.get("option")
    if not section or not option:
        return jsonify(status="error", message="Missing parameters"), 400
    config = load_config()
    if section not in config:
        return jsonify(status="error", message="Section not found"), 404
    if option not in config[section]:
        return jsonify(status="error", message="Option not found"), 404
    del config[section][option]
    try:
        with open(CONFIG_FILE, "w") as f:
            toml.dump(config, f)
        return jsonify(status="success")
    except Exception as e:
        logging.error(f"Error saving configuration: {e}")
        return jsonify(status="error", message=str(e))


def disable_plugin(plugin_name):
    """Disable a plugin by removing it from the core/plugins list in wayfire.toml"""
    try:
        with open(CONFIG_FILE, "r") as f:
            config = toml.load(f)

        plugins = config.get("core", {}).get("plugins", "").split()
        if not plugins:
            print("No plugins found in wayfire.toml")
            return

        # Remove plugin if present
        new_plugins = [p for p in plugins if p != plugin_name]
        if len(plugins) == len(new_plugins):
            print(f"Plugin '{plugin_name}' not found in plugin list.")
            return

        config["core"]["plugins"] = " ".join(new_plugins)

        with open(CONFIG_FILE, "w") as f:
            toml.dump(config, f)

        print(f"Plugin '{plugin_name}' disabled successfully in wayfire.toml")
    except Exception as e:
        print(f"Error disabling plugin: {e}")


def enable_plugin(plugin_name):
    """Enable a plugin by adding it to the core/plugins list in wayfire.toml"""
    try:
        with open(CONFIG_FILE, "r") as f:
            config = toml.load(f)

        if "core" not in config:
            config["core"] = {}

        plugins = config["core"].get("plugins", "").split()

        if plugin_name in plugins:
            print(f"Plugin '{plugin_name}' is already enabled.")
            return

        plugins.append(plugin_name)
        config["core"]["plugins"] = " ".join(plugins)

        with open(CONFIG_FILE, "w") as f:
            toml.dump(config, f)

        print(f"Plugin '{plugin_name}' enabled successfully in wayfire.toml")
    except Exception as e:
        print(f"Error enabling plugin: {e}")


@app.route("/toggle_plugin", methods=["POST"])
def toggle_plugin():
    """Toggle the status of a plugin."""
    try:
        data = request.get_json()  # Expecting JSON data
        plugin_name = data.get("plugin_name")
        status = data.get("status")
        if not plugin_name or status not in ["enabled", "disabled"]:
            return jsonify(status="error", message="Missing or invalid parameters"), 400

        config = load_config()
        plugins_list = config.get("core", {}).get("plugins", "").split()

        print(plugin_name)
        if status == "enabled":
            if plugin_name not in plugins_list:
                enable_plugin(plugin_name)
        if status == "disabled":
            if plugin_name in plugins_list:
                disable_plugin(plugin_name)

    except Exception as e:
        logging.error(f"Error saving configuration: {e}")
        return jsonify(status="error", message=str(e))

    return jsonify(status="success")


@app.before_request
def log_request_info():
    if request.path == "/update_option":
        print("Headers:", dict(request.headers))
        print("Data:", request.get_data(as_text=True))


@app.route("/update_option", methods=["POST"])
def update_option():
    try:
        data = request.get_json(force=True)
        section = data.get("section")
        option = data.get("option")
        value = data.get("value")
        value = convert_literal(value)

        if not all([section, option, value]):
            return jsonify(
                {
                    "status": "error",
                    "message": "Missing required fields: section, option, and value",
                }
            ), 400

        config = load_config()
        if section not in config:
            config[section] = {}

        config[section][option] = value

        with open(CONFIG_FILE, "w") as f:
            toml.dump(config, f)

        return jsonify({"status": "success"}), 200

    except Exception as e:
        logging.error(f"Error updating option: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500


def get_metadata():
    """Load metadata from XML files and return a list of plugins."""
    plugins = []
    for file_name in get_metadata_files():
        file_path = os.path.join(METADATA_PATH, f"{file_name}.xml")
        if os.path.isfile(file_path):
            tree = ET.parse(file_path)
            root = tree.getroot()
            plugin = root.find("plugin")
            if plugin is not None:
                plugin_name = plugin.get("name")
                plugins.append({"name": plugin_name, "file": file_path})
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

    metadata_file = os.path.join(metadata_path, f"{section}.xml")
    return os.path.isfile(metadata_file)


@app.route("/help/<section>")
def help_content(section):
    """Fetch and return help content for a specific section."""
    xml_file = os.path.join(METADATA_PATH, f"{section}.xml")

    if os.path.isfile(xml_file):
        html_content = parse_xml_to_html(xml_file)
        return jsonify({"status": "success", "content": html_content})
    else:
        return jsonify({"status": "error", "message": "Help content not found"})


def update_wayfire_ini():
    """Update the Wayfire configuration file with new sections."""
    config = load_config()
    metadata_sections = get_metadata_files()

    # Ensure all metadata sections exist in core.plugins or top-level
    for section in metadata_sections:
        if (
            section not in config.get("core", {}).get("plugins", "").split()
            and section not in config
        ):
            config[section] = {}

    try:
        with open(CONFIG_FILE, "w") as f:
            toml.dump(config, f)
        logging.info("Wayfire configuration file updated with new sections.")
    except Exception as e:
        logging.error(f"Error saving configuration: {e}")


@app.context_processor
def inject_helpers():
    """Inject helper functions and variables into the template context."""
    try:
        update_wayfire_ini()
        config = load_config()
    except Exception as e:
        logging.error(f"Error updating or loading config: {e}")
        config = {}  # Provide a fallback empty dict instead of ConfigParser

    try:
        metadata = get_metadata()
    except Exception as e:
        logging.error(f"Error loading metadata: {e}")
        metadata = []

    metadata_plugins = [item["name"] for item in metadata]

    # Access plugins safely from TOML-style dict
    enabled_plugins = config.get("core", {}).get("plugins", "").split()

    enabled_plugins = [
        plugin for plugin in enabled_plugins if plugin in metadata_plugins
    ]

    def is_plugin_section(section):
        """Check if a section is a plugin based on its metadata."""
        return section in metadata_plugins

    return {
        "is_plugin_section": is_plugin_section,
        "plugins_list": enabled_plugins,
        "metadata": metadata,
    }


@app.route("/metadata/<filename>")
def serve_metadata(filename):
    # Ensure we're serving from the correct local metadata directory
    local_metadata_dir = os.path.join(os.path.dirname(__file__), "metadata")
    return send_from_directory(local_metadata_dir, filename)


@app.route("/")
def index():
    # make it backup wayfire.ini during server startup
    backup_wayfire_ini()
    config = load_config()
    metadata = get_metadata()
    metadata_plugins = get_metadata_files()
    enabled_plugins = config.get("core", {}).get("plugins", "").split()
    if enabled_plugins is None:
        enabled_plugins = []
    if metadata_plugins is None:
        metadata_plugins = []

    return render_template(
        "index.html",
        config=config,
        config_sections=[s for s in config.keys() if isinstance(config[s], dict)],
        enabled_plugins=enabled_plugins,
        metadata_plugins=metadata_plugins,
    )


if __name__ == "__main__":
    app.run(debug=False, port=5001)
