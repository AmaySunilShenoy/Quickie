from flask import current_app as app
import os
def route_list():
    routes = []
    for rule in app.url_map.iter_rules():
        route = {
            'endpoint': rule.endpoint,
            'methods': ','.join(rule.methods),
            'path': str(rule),
        }
        routes.append(route)
    return routes

def get_performance_content():
    script_dir = os.path.dirname(__file__)  # Get the directory of the script
    log_file_path = os.path.join(script_dir, '../performance.log')
    try:
        with open(log_file_path, 'r') as file:
            content = file.readlines()
            return content
    except FileNotFoundError:
        return f"File  not found."
    except Exception as e:
        return f"An error occurred: {str(e)}"