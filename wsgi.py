from app import app
import json

config = ""
with open('config.json') as config_file:
   config = json.load(config_file)

if __name__ == '__main__':
    app.run(port=config['port'], host=config['host'], debug=True)