"""The `tick` job: every 5 minutes in prod, on command in dev."""
from .db import connect

with connect() as c:
    c.execute("INSERT INTO ticks DEFAULT VALUES")
print("tick")
