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
    
    def load_supported_platform(self,values:dict):
        platforms = []
        for _ in values["platform"].keys():
            platforms.append(Platform(False,values["platform"]))
        return platforms