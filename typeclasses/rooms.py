"""
Room

Rooms are simple containers that has no location of their own.

"""

from evennia import DefaultRoom


class Room(DefaultRoom):
    """
    Rooms are like any Object, except their location is None
    (which is default). They also use basetype_setup() to
    add locks so they cannot be puppeted or picked up.
    (to change that, use at_object_creation instead)

    See examples/object.py for a list of
    properties and methods available on all Objects.
    """

    @property
    def x(self):
        x = self.tags.get(category="coordx")
        return int(x) if isinstance(x, str) else None

    @x.setter
    def x(self, x):
        old = self.tags.get(category="coordx")
        if old is not None:
            self.tags.remove(old, category="coordx")
        if x is not None:
            self.tags.add(str(x), category="coordx")

    @property
    def y(self):
        y = self.tags.get(category="coordy")
        return int(y) if isinstance(y, str) else None

    @y.setter
    def y(self, y):
        old = self.tags.get(category="coordy")
        if old is not None:
            self.tags.remove(old, category="coordy")
        if y is not None:
            self.tags.add(str(y), category="coordy")

    @classmethod
    def room_at_coords(cls, x, y):
        rooms = cls.objects.filter(db_tags__db_key=str(x), db_tags__db_category="coordx").filter(db_tags__db_key=str(y), db_tags__db_category="coordy")
        if rooms:
            return rooms[0]
        return None

    @classmethod
    def nearby_rooms(cls, x, y, dist):
        rooms_map = []
        for i in range((dist * 2) + 1):
            rooms_map.append([' · '] * ((dist * 2) + 1))
        rooms_map[dist][dist] = ' # '

        x_r = list(reversed([str(x - i) for i in range(0, dist + 1)])) + [str(x + i) for i in range(1, dist + 1)]
        y_r = list(reversed([str(y - i) for i in range(0, dist + 1)])) + [str(y + i) for i in range(1, dist + 1)]

        full_search = cls.objects.filter(db_tags__db_key__in = x_r, db_tags__db_category="coordx").filter(db_tags__db_key__in = y_r, db_tags__db_category="coordy")

        for room in full_search:
            x_rel = dist + int(room.tags.get(category="coordx")) - x
            y_rel = dist + int(room.tags.get(category="coordy")) - y
            if x_rel != dist and y_rel != dist:
                rooms_map[y_rel][x_rel] = ' ■ '

        return rooms_map