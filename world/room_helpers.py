from django.conf import settings
from evennia.utils import create, utils, search, logger

def autodig(caller, room):
    if not room["name"]:
        caller.msg("You must supply a new room name.")
        return

    # Create the new room
    typeclass = settings.BASE_ROOM_TYPECLASS

    # create room
    new_room = create.create_object(
        typeclass, room["name"], aliases=room["aliases"], report_to=caller
    )
    alias_string = ""
    if new_room.aliases.all():
        alias_string = " (%s)" % ", ".join(new_room.aliases.all())
    room_string = "Created room %s(%s)%s of type %s." % (
        new_room,
        new_room.dbref,
        alias_string,
        typeclass,
    )

    caller.msg("%s" % (room_string))

