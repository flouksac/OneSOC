from Model.loaderYAML import YamlLoader
from Model.ModelObjects.component import Component
from Model.ModelObjects.platform import Platform
from Model.ModelObjects.option import Option
from Model.ModelObjects.action import Action
from DesignPattern.singleton import Singleton




class Model(metaclass = Singleton):
    
    def __init__(self):
        self.components:list[Component] = []

    def get_all_actions(self) -> list[Action]:
        actions = [] 
        for component in self.components:
            for current_action in component.actions:
                if not any(current_action.name== known_action.name for known_action in actions):
                    actions.append(current_action)
        return actions

    def get_all_components(self) -> list[Component]:
        return self.components
    
    def get_all_components_by_action(self,action:str) -> list[Component]:
        output = []
        for component in self.components:
            if component.is_action_supported(action):
                output.append(component)
        return output
                
    
    def get_all_options(self) -> dict[str:Option]: 
        options = {} 
        for component in self.components:
            options[component.name] = []
            for current_option in component.options:
                options[component.name].append(current_option)
        return options
    
    def get_options_of_components(self,components:list[str]) -> dict[str:Option]:
        options = {} 
        for component in self.components:
            if not component.name.lower() in components:
                continue
            options[component.name] = []
            for current_option in component.options:
                options[component.name].append(current_option)
        return options

    def load_component(self,data:dict) -> list[Component]:
        components = []
        for key, value in data["Components"].items():
            components.append(Component(key,value,data["Action"]))
            
        return components
            
    def init(self,config_path):
        data = YamlLoader(config_path).data
        self.components = self.load_component(data)
