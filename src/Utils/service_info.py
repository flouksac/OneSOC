import shutil
import subprocess
from Utils.os_info import get_os_type


def find_service(service:str):
        
    os_type = get_os_type().lower()

    match os_type:
        case "windows":    
        
            try:    
                command = [
                    "powershell",
                    "-Command",
                    "Get-Service | Where-Object {$_.Name -like \"*"+service+"*\"}"
                ]
                output = subprocess.check_output(command, stderr=subprocess.STDOUT, text=True).strip()
                if "running" in output.lower():
                    return True

            except subprocess.CalledProcessError as e:
                if "cannot find" in e.output.lower():
                    return False
                print(f"Erreur lors de l'exécution de find_service sur windows : {e}")
            return False
        case "linux":
            try:
                 if shutil.which("systemctl"):
                    result = subprocess.run(["systemctl", "status", service], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
                    if result.returncode == 0:
                        return True
                
                 if shutil.which("service"):
                    result = subprocess.run(["service", service, "status"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
                    if "is running" in result.stdout.lower() or result.returncode == 0:
                        return True

                 if shutil.which("rc-service"):
                    result = subprocess.run(["rc-service", service, "status"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
                    if "started" in result.stdout.lower():
                        return True

                 if shutil.which("sv"):
                    result = subprocess.run(["sv", "status", service], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
                    if "run" in result.stdout.lower():
                        return True
            except subprocess.CalledProcessError as e:
                print(f"Erreur lors de l'exécution de find_service sur linux : {e}")
            return False
        case "darwin":
            try:
                output = subprocess.check_output(["launchctl", "list"], text=True)
                if service in output:
                    return True
            except subprocess.CalledProcessError as e:
                print(f"Erreur lors de l'exécution de find_service sur linux : {e}")
            return False