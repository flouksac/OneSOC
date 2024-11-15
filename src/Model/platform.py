import ctypes
import os

from Utils.os_info import get_os, get_os_type, get_os_version
from Utils.hardware_info import get_ram_in_gb, get_free_disk_space_gb , get_cpu_core_count


class Platform:
    def __init__(self,host=True,values:dict={}):
        self.data = {'os':os, 'is_admin':{}, 'hardware':{}} # services ? docker ? ou bien dans une autre classe
        if host:
            self.retrieve_os()
            self.retrieve_is_admin()
            self.retrieve_hardware()


    def retrieve_os(self):
        self.data['os']['os_name'] = get_os()
        self.data['os']['os_type'] = get_os_type()
        self.data['os']['os_version'] = get_os_version()

    def retrieve_is_admin(self):
        os_type = self.data['os']['os_type'].lower()
        is_admin = False
        if 'windows' in os_type:
            try:
                is_admin = (ctypes.windll.shell32.IsUserAnAdmin() != 0)
            except AttributeError:
                is_admin = False

        elif 'linux' in os_type or 'mac' in os_type:
            is_admin = os.geteuid() == 0

        else:
            raise ValueError("OS not supported for admin rights privileges.")

        self.data['is_admin']=is_admin

    def retrieve_hardware(self):
        self.data['hardware']['ram'] = get_ram_in_gb()
        self.data['hardware']['free_disk'] = get_free_disk_space_gb()
        self.data['hardware']['cpu_core'] = get_cpu_core_count()
