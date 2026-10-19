from datetime import datetime, timezone
import getpass
import socket

def learnDateTime():
    ts = datetime.now(timezone.utc)

    print(f"UtcNow: {ts}")
    print(type(ts))

    id = 18
    print(type(id))
    id2: str = str(id)
    print(type(id2))


def getusermeta():
    username = getpass.getuser()
    hostname = socket.gethostname()

    print(f"Username: {username}")
    print(f"Hostname: {hostname}")


if __name__ == "__main__":
    #learnDateTime()
    getusermeta()
