from Model.ModelObjects.platform import Platform
from Utils.os_info import get_os, get_os_type, get_os_version, retrieve_is_admin, retrieve_package ,get_cpu_architecture
from Utils.hardware_info import get_ram_in_gb, get_free_disk_space_gb, get_cpu_core_count


class HostController:
    def __init__(self):
        self.host:Platform|None = None
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
            "recommended_os": get_os(), 
            "package": package,
            "version": get_os_version(),  
            "architecture": get_cpu_architecture(),  

            "admin_rights_needed": retrieve_is_admin()
        }
        self.host = Platform(host_data)

    def get_host(self)-> Platform :
        return self.host
    

    def is_minimum_compatible(self,platform:Platform) -> bool:
        
        if self.host is None:
            raise Exception("not able to determine what host config you have :'c")
 
        if not self.host.admin_rights_needed :
            if platform.admin_rights_needed : 
                raise Exception("You need to run this script with admin rights")
        
        
        if platform.minimum_ram is not None and platform.minimum_ram > self.host.minimum_ram:
            raise Exception("YOU NEED MORE RAM, GO TO SHOP")
            
        if platform.minimum_cpu_core is not None and platform.minimum_cpu_core > self.host.minimum_cpu_core:
            raise Exception("YOU NEED MORE CPU, GO TO SHOP")


        if platform.minimum_free_space is not None and platform.minimum_free_space > self.host.minimum_free_space:
            raise Exception("YOU NEED MORE SPACE, BUY A NAS")
        
        if platform.architecture !="None" and self.host.architecture.lower() not in platform.architecture.lower():
            raise Exception("The architecture of the CPU is not compatible")
        
        if self.host.os_type.lower() not in platform.os_type.lower():
            raise Exception("Your os type is not supported")


        if platform.package is not None and self.host.package is not None:
            if not ((self.host.package == ["dnf","yum"] and platform.package == "rpm")
                    or (self.host.package == ["apt"] and platform.package == "deb")) :
                raise Exception("A package manager is missing on your platform")

        return True
        
    def is_fully_compatible(self,platform:Platform) -> bool:

        try : 
            if self.is_minimum_compatible(platform):
                pass
        except Exception as e :
            raise e

        if platform.recommended_ram is not None and platform.recommended_ram > self.host.minimum_ram:
            return False
        
        if platform.recommended_cpu_core is not None and platform.recommended_cpu_core > self.host.minimum_cpu_core:
            return False

        if platform.recommended_free_space is not None and platform.recommended_free_space > self.host.minimum_free_space:
            return False

        if  platform.recommended_os.lower() not in self.host.recommended_os.lower() :
            return False
            
        platform_version = platform.version.split(" ")
        if not (len(platform_version)>=2 and platform_version[1].lower() != "x"):
            platform_sub_version = platform_version[1].split(".")
            host_sub_version = self.host.version.split(".")
            try: 
                
                platform_major = int(platform_sub_version[0])
                host_major = int(host_sub_version[0])
                platform_minor = None
                platform_patch = None
                if len(platform_sub_version)>1 and len(host_sub_version)>1:
                    platform_minor = int(platform_sub_version[1])
                    host_minor = int(host_sub_version[1])
                if len(platform_sub_version)>2 and len(host_sub_version)>2:
                    platform_patch = int(platform_sub_version[2])
                    host_patch = int(host_sub_version[2])

                if platform_major > host_major :
                    return False
                elif platform_minor is not None and host_minor is not None and platform_minor > host_minor :
                    return False
                elif platform_patch is not None and host_patch is not None and platform_patch > host_patch :
                    return False
                
            except:
                raise Exception("can't parse version properly") 

        return True
        
    