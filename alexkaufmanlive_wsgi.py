import sys

path = "/home/dustiestgolf/alexkaufmanlive"
if path not in sys.path:
    sys.path.insert(0, path)

from alexkaufmanlive import create_app

application = create_app()
