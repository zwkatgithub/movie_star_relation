from .entity import Entity

class Star(Entity):

    def __init__(self, source_id, name, birthday, 
        image, country, height, weight, constellation):
        super().__init__()
        self.source_id = source_id
        self.name = name
        self.birthday = birthday
        self.image = image
        self.country = country
        self.height = height
        self.weight = weight
        self.constellation = constellation