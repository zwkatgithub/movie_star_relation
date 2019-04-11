from .entity import Entity

class MovieType(Entity):
    def __init__(self, movie_id, type_id):
        self.movie_id = movie_id
        self.type_id = type_id