import time

def time_convert(sec):
    mins = sec // 60
    sec = sec % 60
    hours = mins // 60
    mins = mins % 60
    return f"{mins}:{sec}"


def scanners_timing(start_time):
    end_time = time.time()
    time_lapsed = end_time - start_time
    return time_lapsed
