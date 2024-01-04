import yaml

def load_config(file_path):
    with open(file_path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)
    
def print_yaml_content(file_path):
    """Prints the content of a YAML file in a human-readable format."""

    try:
        with open(file_path, "r") as file:
            yaml_data = yaml.safe_load(file)

        # Print the parsed YAML data in a user-friendly way
        print(f"Content from {file_path}: \n")
        print(yaml.dump(yaml_data, default_flow_style=False))

    except FileNotFoundError:
        print(f"Error: File '{file_path}' not found.")
    except yaml.YAMLError as exc:
        print(f"Error parsing YAML file: {exc}")