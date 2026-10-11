
from datetime import datetime, timezone

ts = datetime.now(timezone.utc)

print(f"UtcNow: {ts}")
print(type(ts))

id = 18
print(type(id))
id2: str = str(id)
print(type(id2))
