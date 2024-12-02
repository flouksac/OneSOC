import ctypes
import os
import platform
import shutil


# /!\ standardiser par rapport au yaml dans platform

def get_os_type():
    os_type = platform.system().lower()
    if os_type == "windows":
        return "Windows"
    elif os_type == "linux":
        return "Linux"
    elif os_type == "darwin":  # 'darwin' est utilisé pour macOS
        return "macOS"
    else:
        return "Unknown OS"

def get_os_version():
    os_version = platform.release()
    return os_version

def get_os():
    os_name, os_version = platform.system(), platform.release()

    if os_name == "Linux":
        try:
            with open("/etc/os-release") as f:
                os_info = {"NAME": None, "VERSION_ID": None}
                for line in f:
                    if os_info["NAME"] is not None and os_info["VERSION_ID"] is not None:
                        break
                    key, value = line.rstrip().split("=")
                    os_info[key] = value.strip('"')

            current_os = f"{os_info.get('NAME', 'Unknown')} {os_info.get('VERSION_ID', 'Unknown')}"
        except Exception as e:
            current_os = f"Linux {os_version}"
    else:
        current_os = f"{os_name} {os_version}"

    return current_os

def retrieve_is_admin():
    os_type = get_os_type().lower()
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

    return is_admin



def retrieve_package() -> None|list:
    os_type = get_os_type().lower()
    match os_type:
        case 'windows':
            return None
        
        case 'linux':
            package_managers = ["apt", "dnf", "yum"]
            found_managers = [
                manager for manager in package_managers if shutil.which(manager)
            ]
            if not found_managers:
                raise ValueError("No known package manager detected on this os.")
            return found_managers  # Retourne tous les gestionnaires trouvés
                    # vérifier la présence de apt, dnf , yum
        case _ :
            raise ValueError("OS not supported for admin rights privileges.")


def get_cpu_architecture():
    
    os_type = get_os_type().lower()
    match os_type:
        case 'windows':
            return platform.architecture()[0] 
        case _ :
            return platform.machine() 
   