from Model.option import Option
from Model.action import Action
from Model.platform import Platform

class Component:
    def __init__(self,name:str,values:dict,all_existing_actions:dict):
        self.name:str = name
        self.description = values["description"]
        self.role =  values["role"]
        
        self.options: list[Option] = self.load_options(values)
        self.actions: list[Action] = self.load_actions(values,all_existing_actions)
        self.supported_platform: list[Platform] = self.load_supported_platform(values)
 
    def load_options(self,values:dict):
        options = []
        for key, value in values["options"].items():
            options.append(Option(key,value))
        return options
    
    def load_actions(self,values:dict,all_existing_actions:dict):
        actions = []
        for key in values["actions"]:
            if key in all_existing_actions.keys():
                actions.append(Action(key,all_existing_actions[key]))  
        return actions
    
    def load_supported_platform(self, values: dict):
        
        platforms = []

        recommended_os = values["platform"].get("recommended_os", {})
        
        for os_type, distros in recommended_os.items():
            if distros in ("None", None):
                continue  
            
            for distro, distro_data in distros.items():
                package = distro_data.get("package")
                
                for version_info, arch_data in distro_data.items():
                    if "version" not in version_info:
                        continue  
                    
                    architectures = arch_data.get("architecture", [])
                    if architectures in ("None",None):  
                        architectures = ['None']
                    
                    for architecture in architectures:
                        platform_data = values["platform"] | { # | for concatenation of two dictionnaries
                            "os_type": os_type,
                            "recommended_os": distro,
                            "version": version_info,
                            "package": package,
                            "architecture": architecture,
                        }
                        platforms.append(Platform(platform_data, host=False))
        
        return platforms