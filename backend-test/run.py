import os
from app import create_app

# Determine config name from environment or default to 'development'
config_name = os.getenv('FLASK_ENV') if os.getenv('FLASK_ENV') else 'default'
# FLASK_ENV can be 'development', 'production', 'testing'
# Our config map uses 'development', 'testing', 'production'
# Adjust if FLASK_ENV uses different values.
if config_name not in ['development', 'testing', 'production']:
    config_name = 'default'


app = create_app(config_name)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000) # Port 5000 for backend