from mcp990x import Sensor
from time import sleep
import random
import time
import numpy as np
import rich
from rich.live import Live
from rich.table import Table


def read_sensor(channel):
    return s.read(channel)

def generate_table() -> Table:
    """Make a new table."""
    table = Table(title="Temperatures (C)", box=rich.box.MINIMAL_DOUBLE_HEAD)
    for channel in range(4):
        table.add_column("   %d   "%channel)

    row = []
    for channel in range(4):
        reading = read_sensor(channel)
        row.append(reading)
    table.add_row(*np.array(row, dtype=str))
    return table


s = Sensor(1, i2c_addr=0x3c, debug=False)
s.set_config((1<<2)) # enable extended range mode
with Live(generate_table(), refresh_per_second=4) as live:
    while True:
        time.sleep(2)
        live.update(generate_table())
