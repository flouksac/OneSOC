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
        pass

    def get_all_components(self) -> list[Component]:
        return self.components
    
    def get_all_options(self) -> list[Option]:
        pass

    def get_host(self) -> Platform:
        pass

    def load_component(self,data:dict) -> list[Component]:
        components = []
        print(data["Action"])
        #print(data["Components"])
        for key, value in data["Components"].items():
            components.append(Component(key,value,data["Action"]))
            
        return components
            
    def init(self,config_path):
        data = YamlLoader(config_path).data
        self.components = self.load_component(data)
        