import os
import shutil
import psutil
from math import ceil
import platform

def get_free_disk_space_gb():
    total, used, free = shutil.disk_usage("/")
    free_gb = free / (1024 ** 3)
    return round(free_gb, 0)


def get_ram_in_gb():
    ram = psutil.virtual_memory()
    ram_gb = ram.total / (1024 ** 3)
    return ceil(ram_gb)


def get_cpu_core_count():
    return os.cpu_count()
