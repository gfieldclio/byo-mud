"""
Commands

Commands describe the input the account can do to the game.

"""

from django.conf import settings
from evennia.commands.command import Command as BaseCommand
from evennia.utils import create, utils, search, logger
from world.room_helpers import create_room
from typeclasses.items import Item

from evennia import default_cmds
from evennia.commands.default.building import CmdDig

class Command(BaseCommand):
    """
    Inherit from this if you want to create your own command styles
    from scratch.  Note that Evennia's default commands inherits from
    MuxCommand instead.

    Note that the class's `__doc__` string (this text) is
    used by Evennia to create the automatic help entry for
    the command, so make sure to document consistently here.

    Each Command implements the following methods, called
    in this order (only func() is actually required):
        - at_pre_cmd(): If this returns anything truthy, execution is aborted.
        - parse(): Should perform any extra parsing needed on self.args
            and store the result on self.
        - func(): Performs the actual work.
        - at_post_cmd(): Extra actions, often things done after
            every command, like prompts.

    """

    pass

class CmdGet(default_cmds.MuxCommand):
    """
    Usage:
      get <obj>

    Picks up an object from your location and puts it in
    your inventory. Creates the object if it didn't already
    exist.
    """

    key = "get"
    aliases = "grab"
    locks = "cmd:all()"
    arg_regex = r"\s|$"

    def func(self):
        caller = self.caller

        if not self.args:
            caller.msg("I don't get it")
            return
        obj = caller.search(self.args, location=caller.location, quiet=True)
        if not obj:
            answer = yield("There is no %s... Yet! Do you want to create it?" % self.args)
            if answer.strip().lower() in ("yes", "y"):
                obj = create.create_object(
                    Item,
                    self.args,
                    caller.location,
                    report_to=caller
                )
                obj.db.desc = ""
            else:
                return
        if type(obj) == list:
            obj = obj[0]
        if caller == obj:
            caller.msg("You can't get yourself.")
            return
        if not obj.access(caller, "get"):
            if obj.db.get_err_msg:
                caller.msg(obj.db.get_err_msg)
            else:
                caller.msg("You can't get that.")
            return

        # calling at_before_get hook method
        if not obj.at_before_get(caller):
            return

        success = obj.move_to(caller, quiet=True)
        if not success:
            caller.msg("This can't be picked up.")
        else:
            caller.msg("You pick up %s." % obj.name)
            caller.location.msg_contents(
                "%s picks up %s." % (caller.name, obj.name), exclude=caller
            )
            # calling at_get hook method
            obj.at_get(caller)

class CmdSetHome(default_cmds.MuxCommand):
    """
    Usage:
      sethome

    Sets a given location as your new home.
    """

    key = "sethome"

    def func(self):
        """Implement the command"""
        caller = self.caller
        if caller.home == caller.location:
            caller.msg("You are already home!")
        else:
            caller.home = caller.location
            caller.msg("%s is your new home." % caller.location)

class CmdDescribe(default_cmds.MuxCommand):
    """
    Usage:
      describe
      describe <obj>

    Updates the description for a location or object. You
    are only allowed to set a description if there isn't
    one yet.
    """

    key = "describe"
    locks = "cmd:all()"
    arg_regex = r"\s|$"

    def func(self):
        caller = self.caller

        if not self.args:
            obj = caller.location
        else:
            obj = caller.search(self.args, location=caller.location, quiet=True)
            if not obj:
                obj = caller.search(self.args, location=caller, quiet=True)

        if type(obj) == list:
            obj = obj[0]

        if not obj.access(caller, "describe"):
            if obj.db.get_err_msg:
                caller.msg(obj.db.get_err_msg)
            else:
                caller.msg("%s has already been described." % obj)
            return

        if obj.id == 2 and not obj.access(caller, "edit"):
            caller.msg("Limbo is beyond description to you.")

        description = yield("How would you describe %s? Add some flavour to your description. Once the description is set, it's permanent." % (obj))
        if description:
            obj.db.desc = description

class CmdTaste(default_cmds.MuxCommand):
    """
    Taste

    Usage:
        taste <obj>

    Interact with an object to see what it tastes like.
    """
    key = "taste"
    locks = "cmd:all()"
    arg_regex = r"\s|$"

    def func(self):
        caller = self.caller

        if not self.args:
            caller.msg("If you don't taste something, how can you taste anything?")
            return
        else:
            obj = caller.search(self.args, location=caller.location, quiet=True)
            if not obj:
                obj = caller.search(self.args, location=caller, quiet=True)

        if type(obj) == list:
            obj = obj[0]

        current_description = obj.attributes.get('taste')

        if current_description:
            caller.msg(current_description)
            return

        if not obj.access(caller, "taste"):
            if obj.db.get_err_msg:
                caller.msg(obj.db.get_err_msg)
            else:
                caller.msg("%s can't be tasted. Shame on you for trying." % obj)
            return

        description = yield("What happens when you try to taste %s? You can describe how it tastes, or what happens as a result of you trying to taste it. Once the description is set, it's permanent." % obj)
        if description:
            obj.db.taste = description


class CmdTouch(default_cmds.MuxCommand):
    """
    Touch

    Usage:
        touch <obj>

    Interact with an object to see what it feels like.
    """
    key = "touch"
    locks = "cmd:all()"
    aliases = "feel"
    arg_regex = r"\s|$"

    def func(self):
        caller = self.caller

        if not self.args:
            caller.msg("You feel nothing.")
            return
        else:
            obj = caller.search(self.args, location=caller.location, quiet=True)
            if not obj:
                obj = caller.search(self.args, location=caller, quiet=True)

        if type(obj) == list:
            obj = obj[0]

        current_description = obj.db.touch

        if current_description:
            caller.msg(current_description)
            return

        if not obj.access(caller, "touch"):
            if obj.db.get_err_msg:
                caller.msg(obj.db.get_err_msg)
            else:
                caller.msg("%s can't be touched. Shame on you for trying." % obj)
            return

        description = yield("What happens when you try to touch %s? You can describe what it feels like, how it reacts to your touch, or what happens as a result of you trying to touch it. Once the description is set, it's permanent." % obj)
        if description:
            obj.db.touch = description


class CmdSmell(default_cmds.MuxCommand):
    """
    Smell

    Usage:
        smell <obj>

    Interact with an object to see what it smells like.
    """
    key = "smell"
    locks = "cmd:all()"
    aliases = "sniff"
    arg_regex = r"\s|$"

    def func(self):
        caller = self.caller

        if not self.args:
            caller.msg("You smell.")
            return
        else:
            obj = caller.search(self.args, location=caller.location, quiet=True)
            if not obj:
                obj = caller.search(self.args, location=caller, quiet=True)

        if type(obj) == list:
            obj = obj[0]

        current_description = obj.db.smell

        if current_description:
            caller.msg(current_description)
            return

        if not obj.access(caller, "smell"):
            if obj.db.get_err_msg:
                caller.msg(obj.db.get_err_msg)
            else:
                caller.msg("%s isn't there for you to smell. Shame on you for trying." % obj)
            return

        description = yield("What happens when you try to smell %s? You can describe how it smells, or what happens as a result of you trying to smell it. Once the description is set, it's permanent." % obj)
        if description:
            obj.db.smell = description


class CmdExplore(default_cmds.MuxCommand):
    """
    Explore

    Usage:
        explore

    Special dig command for regular users
    """

    key = "explore"
    locks = "cmd:all()"
    help_category = "Navigation"
    directions = {
        "n": ("north", "s"),
        "ne": ("northeast", "sw"),
        "e": ("east", "w"),
        "se": ("southeast", "nw"),
        "s": ("south", "n"),
        "sw": ("southwest", "ne"),
        "w": ("west", "e"),
        "nw": ("northwest", "se"),
        "u": ("up", "d"),
        "d": ("down", "u"),
        "i": ("in", "o"),
        "o": ("out", "i"),
    }

    def func(self):
        if not self.lhs:
            self.caller.msg("Usage: explore <direction>")
            return

        explore_direction = self.lhslist[0]
        if explore_direction not in self.directions:
            string = "explore can only understand the following directions: %s." % ",".join(
                sorted(self.directions.keys())
            )
            self.caller.msg(string)
            return

        self.caller.msg("You move %s from %s into a new area." % (self.directions[explore_direction][0], self.caller.location))

        new_room_name = None
        while not new_room_name:
            new_room_name = yield("What is this place called?")
            if new_room_name:
                break
            self.caller.msg("A name must be provided.")

        new_room = create_room(self.caller, new_room_name)

        exit_to_abbrev = explore_direction
        exit_to_name = self.directions[explore_direction][0]
        back_from_abbrev = self.directions[explore_direction][1]
        back_from_name = self.directions[back_from_abbrev][0]

        # Create exit to
        exit_to = create.create_object(
            settings.BASE_EXIT_TYPECLASS,
            exit_to_name,
            self.caller.location,
            aliases = [exit_to_abbrev],
            destination = new_room,
            report_to = self.caller,
        )

        # Create exit back
        exit_back = create.create_object(
            settings.BASE_EXIT_TYPECLASS,
            back_from_name,
            new_room,
            aliases = [back_from_abbrev],
            destination = self.caller.location,
            report_to = self.caller,
        )

        self.caller.msg("%s added to map" % new_room)
        self.caller.move_to(new_room)

class CmdMap(default_cmds.MuxCommand):
    """
    View map

    Usage:
        map

    Special dig command for regular users
    """

    key = "map"
    locks = "cmd:all()"
    help_category = "Navigation"

    def func(self):
        caller = self.caller

        map_grid = caller.location.nearby_rooms(caller.location.x, caller.location.y, 3)

        for row in map_grid:
            caller.msg("".join(row))

