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



def test_lists():
    #perms = ["admin", "user", "read", "planner"]
    perms = []

    if not "admin" in perms and not "user" in perms:
        print("you do not have access")

if __name__ == "__main__":
    test_lists()
