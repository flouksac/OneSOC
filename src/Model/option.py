class Option:
    def __init__(self,key,value) -> None:
        self.key = key
        self.value = value
        
    def __str__(self):
        return str(self.key)+":"+str(self.value)