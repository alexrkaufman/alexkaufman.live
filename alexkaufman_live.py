import os

from dotenv import load_dotenv

from alexkaufmanlive import create_app
from alexkaufmanlive.config import DevConfig, ProdConfig

load_dotenv(".env")

if os.getenv("FLASK_ENV") == "production":
    config = ProdConfig()
else:
    config = DevConfig()


application = create_app(config)

if __name__ == "__main__":
    application.run(host="0.0.0.0", port=3000, debug=True, threaded=False)
