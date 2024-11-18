class Action:
    def __init__(self,name,value:dict):
        self.name:str = name
        self.description:str = value["description"]
        self.command_description:str = value["command_description"]
        
    
    