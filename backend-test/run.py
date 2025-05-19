import os
from app import create_app

config_name = os.getenv('FLASK_ENV') if os.getenv('FLASK_ENV') else 'default'
if config_name not in ['development', 'testing', 'production']:
    config_name = 'default'

app = create_app(config_name)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)