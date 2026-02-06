import os
from config import TICKET_COUNTER_FILE

def get_next_ticket_id():
    if not os.path.exists(TICKET_COUNTER_FILE):
        with open(TICKET_COUNTER_FILE, "w") as f:
            f.write("1")
        return 1

    with open(TICKET_COUNTER_FILE, "r+") as f:
        ticket_id = int(f.read())
        f.seek(0)
        f.write(str(ticket_id + 1))
        f.truncate()
        return ticket_id
