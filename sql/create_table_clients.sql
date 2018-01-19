CREATE TABLE IF NOT EXISTS clients (
    id INTEGER PRIMARY KEY,
    slug TEXT UNIQUE,
    pretty_name TEXT,
    hash TEXT UNIQUE
)
