import ctypes
import os

from Utils.os_info import get_os, get_os_type, get_os_version
from Utils.hardware_info import get_ram_in_gb, get_free_disk_space_gb , get_cpu_core_count


class Platform:
    def __init__(self,values:dict,host=False):
        
        self.minimum_ram = None
        self.minimum_cpu_core = None
        self.minimum_free_space = None
        
        self.recommended_ram = None
        self.recommended_free_space = None
        self.recommended_cpu_core = None
        
        self.os_type = None
        self.recommended_os = None
        self.package = None
        self.version = None
        self.architecture = None
        
        self.admin_rights_needed = None
    
        self.host = host    
        self.load_platform(values)
    
    def load_platform(self,values:dict):
        for key, value in values.items():
            if hasattr(self, key):  # Vérifie si l'attribut existe
                setattr(self, key, value)
            else:
                print(f"Clé inconnue ignorée : {key}")
            
            

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
