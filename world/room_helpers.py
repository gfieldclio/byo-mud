from django.conf import settings
from evennia.utils import create, utils, search, logger

def create_room(caller, room_name, description=None):
    new_room = create.create_object(
        settings.BASE_ROOM_TYPECLASS,
        room_name,
        report_to=caller
    )
    if description:
        new_room.db.desc = description

    return new_room

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