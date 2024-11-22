import ctypes
import os
import shutil

from Model.ModelObjects.platform import Platform
from Utils.os_info import get_os, get_os_type, get_os_version, retrieve_is_admin, retrieve_package
from Utils.hardware_info import get_ram_in_gb, get_free_disk_space_gb, get_cpu_core_count


class HostController:
    def __init__(self):
        self.host = None
        self.load_host()

    def load_host(self):

        try :
            package = retrieve_package()
        except :
            package = None

        host_data = {  # correspond a la ram courrante de l'ordinateur
            "minimum_ram": get_ram_in_gb(),
            "minimum_cpu_core": get_cpu_core_count(),
            "minimum_free_space": get_free_disk_space_gb(),

            "recommended_ram": get_ram_in_gb(),
            "recommended_free_space": get_cpu_core_count(),
            "recommended_cpu_core": get_free_disk_space_gb(),

            "os_type": get_os_type(),
            "recommended_os": get_os(),  # Nom
            "package": package,
            "version": get_os_version(),  # Version
            "architecture": None,  # TODO archi-proc

            "admin_rights_needed": retrieve_is_admin()
        }
        self.host = Platform(host_data, True)

    def get_host(self):
        return self.host


