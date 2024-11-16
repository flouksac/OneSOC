from Model.load_yaml import YamlLoader
from Model.component import Component
from Model.platform import Platform
from Model.option import Option
from Model.action import Action

class Model:
    def __init__(self):
        
        #self.host_platform = Platform()
        self.components = None 
        
    def get_all_actions(self) -> list[Action]:
        actions = [] 
        for component in self.components:
            for current_action in component.actions:
                if not any(current_action.name== known_action.name for known_action in actions):
                    actions.append(current_action)
        return actions

    def get_all_components(self) -> list[Component]:
        return self.components
    
    def get_all_options(self) -> dict[str:Option]: 
        options = {} 
        for component in self.components:
            options[component.name] = []
            for current_option in component.options:
                #if not any(current_option.key== known_option.key for known_option in options):
                
                options[component.name].append(current_option)
        return options
    
    def get_options_of_components(self,components:list[str]) -> dict[str:Option]:
        options = {} 
        for component in self.components:
            if not component.name.lower() in components:
                continue
            options[component.name] = []
            for current_option in component.options:
                #if not any(current_option.key== known_option.key for known_option in options):
                options[component.name].append(current_option)
        return options
    
    

    def get_host(self) -> Platform:
        if self.host_platform() is not None:
            return self.host_platform
        else:
            raise ValueError("Host need to be analyzed first") 
        

    def load_component(self,data:dict) -> list[Component]:
        components = []
        for key, value in data["Components"].items():
            components.append(Component(key,value,data["Action"]))
            
        return components
            
    def init(self,config_path):
        data = YamlLoader(config_path).data
        self.components = self.load_component(data)
