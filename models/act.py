from .entity import Entity

class Act(Entity):
    def __init__(self, star_id, movie_id):
        super().__init__()
        self.star_id = star_id
        self.movie_id = movie_id

