from flask import Flask, send_file, jsonify
import time
import os

app = Flask(__name__)

# Directory where image files are stored
IMAGE_DIR = "images"

@app.route('/image/<filename>')
def get_image(filename):
    # Simulate slow response
    time.sleep(4)  # 1-second delay
    
    file_path = os.path.join(IMAGE_DIR, filename)
    if os.path.exists(file_path):
        return send_file(file_path, mimetype='image/jpeg')
    else:
        return "File not found", 404


@app.route('/')
def index():
    images = {
        "images": [
            {
                "name": "comet",
                "url": "/image/comet.png"
            },
            {
                "name": "cardiff",
                "url": "/image/cardiff.png"
            },
            {
                "name": "mutiny",
                "url": "/image/mutiny.png"
            },
            {
                "name": "macmillan",
                "url": "/image/macmillan.png"
            }
        ]
    }
    return jsonify(images)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80)
