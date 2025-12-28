#! /usr/bin/env python

from dotenv import load_dotenv

from alexkaufmanlive import create_app

load_dotenv(".env")

application = create_app()

if __name__ == "__main__":
    application.run(host="0.0.0.0", port=3000, debug=True, threaded=False)
