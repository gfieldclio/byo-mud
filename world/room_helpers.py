from django.conf import settings
from evennia.utils import create, utils, search, logger

def dig(caller, room):
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

    caller.msg(room_string)

def link(caller, source, target):
    sourceroom, sourceexit = source
    targetroom, targetexit = target

    if type(sourceexit) is str:
        create.create_object(
            settings.BASE_EXIT_TYPECLASS,
            sourceexit,
            sourceroom,
            destination=targetroom,
            report_to=caller,
        )
    else:
        sourceexit.destination = targetroom

    if type(targetexit) is str:
        create.create_object(
            settings.BASE_EXIT_TYPECLASS,
            targetexit,
            targetroom,
            destination=sourceroom,
            report_to=caller,
        )
    else:
        targetexit.destination = sourceroom

    link_string = "Created link from %s(%s) to %s(%s)." % (
        sourceroom,
        sourceexit,
        targetroom,
        targetexit
    )
    caller.msg(link_string)