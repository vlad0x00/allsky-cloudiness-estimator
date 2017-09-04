from threading import Lock

name_counter = 0
name_lock = Lock()
def generate_name():
    global name_counter
    global name_lock

    name_lock.acquire()
    try:
        name_counter += 1
        return str(name_counter)
    finally:
        name_lock.release()
