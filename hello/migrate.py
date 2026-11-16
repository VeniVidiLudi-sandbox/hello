"""`migrate`: run by the platform before traffic switches to a release."""
from .db import connect

with connect() as c:
    c.execute("CREATE TABLE IF NOT EXISTS visits (id int PRIMARY KEY, n bigint NOT NULL)")
    c.execute("CREATE TABLE IF NOT EXISTS ticks (id bigserial PRIMARY KEY, at timestamptz NOT NULL DEFAULT now())")
print("migrated")
