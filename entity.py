class Entity(object):
    """
    Entities are just numbers!
    """
    num_entities = 0

    @staticmethod
    def create():
        Entity.num_entities += 1
        return Entity.num_entities - 1
