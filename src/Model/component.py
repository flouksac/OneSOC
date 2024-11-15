from Model.option import Option
from Model.action import Action
from Model.platform import Platform

class Component:
    def __init__(self,name:str,value:dict,all_existing_actions:dict):
        self.name:str = name
        self.description = value["description"]
        
        self.options: list[Option] = self.load_options(value)
        self.actions: list[Action] = self.load_actions(value,all_existing_actions)
        self.supported_platform: list[Platform] = self.load_supported_platform(value)
 
    def load_options(self,value:dict):
        options = []
        for key, value in value["options"].items():
            options.append(Option(key,value))
        return options
    
    
    def load_actions(self,value:dict,all_existing_actions:dict):
        actions = []
        for key in value["actions"]:
            if key in all_existing_actions.keys():
                actions.append(Action(key,all_existing_actions[key]))  
        return actions
    
    def load_supported_platform(self,value:dict):
        pass