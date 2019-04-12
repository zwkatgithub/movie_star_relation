from .entity import Entity

class Movie(Entity):

    def __init__(self, source_id, name, image, year, score, introduction):
        super().__init__()
        self.source_id = source_id
        self.name = name
        self.image = image
        self.year = year
        self.score = score
        self.introduction = introduction

        

