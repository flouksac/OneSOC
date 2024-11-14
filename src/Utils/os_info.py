import platform

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

