# Listing 1
import sqlite3

db = sqlite3.connect(":memory:")
db.executescript("""
CREATE TABLE events (
    event_id TEXT PRIMARY KEY, key TEXT NOT NULL,
    version INTEGER NOT NULL, authority INTEGER NOT NULL,
    effective INTEGER NOT NULL, expires INTEGER NOT NULL,
    approved INTEGER NOT NULL
);
CREATE TABLE sources (
    event_id TEXT PRIMARY KEY, text TEXT NOT NULL
);
CREATE TABLE grants (
    principal TEXT NOT NULL, key TEXT NOT NULL,
    PRIMARY KEY (principal, key)
);
CREATE TABLE revocations (
    event_id TEXT PRIMARY KEY, effective INTEGER NOT NULL
);
""")

db.executemany(
    "INSERT INTO events VALUES (?, ?, ?, ?, ?, ?, ?)",
    [
        ("E100", "auth.admin.mfa", 1, 10, 1, 30, 1),
        ("E101", "auth.admin.mfa", 2, 10, 10, 20, 1),
    ],
)
db.executemany(
    "INSERT INTO sources VALUES (?, ?)",
    [
        ("E100", "Administrative accounts require MFA."),
        ("E101",
         "Administrative accounts require phishing-resistant MFA."),
    ],
)
db.execute("INSERT INTO grants VALUES (?, ?)",
           ("aster", "auth.admin.mfa"))

def retrieve_current(key, principal, day):
    # Resolve approved metadata inside the trusted service.
    row = db.execute("""
        SELECT event_id, expires FROM events
        WHERE key = ? AND approved = 1 AND effective <= ?
        ORDER BY authority DESC, version DESC, effective DESC
        LIMIT 1
    """, (key, day)).fetchone()
    if row is None:
        return None

    event_id, expires = row
    grant = db.execute("""
        SELECT 1 FROM grants WHERE principal = ? AND key = ?
    """, (principal, key)).fetchone()
    revoked = db.execute("""
        SELECT 1 FROM revocations
        WHERE event_id = ? AND effective <= ?
    """, (event_id, day)).fetchone()

    # Expiry is exclusive: a record expiring on day 20 is
    # not current at day 20. Do not fall back to an older version.
    if not grant or revoked or day >= expires:
        return None

    source = db.execute(
        "SELECT text FROM sources WHERE event_id = ?", (event_id,)
    ).fetchone()
    return None if source is None else (event_id, source[0])

assert retrieve_current("auth.admin.mfa", "aster", 12) == (
    "E101", "Administrative accounts require phishing-resistant MFA."
)
assert retrieve_current("auth.admin.mfa", "visitor", 12) is None
assert retrieve_current("auth.admin.mfa", "aster", 21) is None

db.execute("INSERT INTO revocations VALUES (?, ?)", ("E101", 14))
assert retrieve_current("auth.admin.mfa", "aster", 15) is None
assert retrieve_current("auth.admin.mfa", "aster", 12)[0] == "E101"
print("All retrieval checks passed.")