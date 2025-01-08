class Option:
    def __init__(self,key,value) -> None:
        self.key = key
        self.value = value

    def __str__(self) -> str:
        return f"{self.key} : {self.value}"

    def __repr__(self) -> str:
        return f"{self.key} : {self.value}"