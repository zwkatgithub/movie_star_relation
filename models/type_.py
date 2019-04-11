from entity import Entity

class Type(Entity):
    def __init__(self, content):
        super().__init__()
        self.content = content

        