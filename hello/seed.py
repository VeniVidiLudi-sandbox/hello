"""`seed`: dev only, sample data."""
from .db import connect

with connect() as c:
    c.execute("INSERT INTO visits (id, n) VALUES (1, 100) ON CONFLICT (id) DO NOTHING")
print("seeded")
