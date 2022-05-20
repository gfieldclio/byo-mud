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

        #if explore_direction not in directions
        #figure this out later

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

# -------------------------------------------------------------
#
# The default commands inherit from
#
#   evennia.commands.default.muxcommand.MuxCommand.
#
# If you want to make sweeping changes to default commands you can
# uncomment this copy of the MuxCommand parent and add
#
#   COMMAND_DEFAULT_CLASS = "commands.command.MuxCommand"
#
# to your settings file. Be warned that the default commands expect
# the functionality implemented in the parse() method, so be
# careful with what you change.
#
# -------------------------------------------------------------

# from evennia.utils import utils
#
#
# class MuxCommand(Command):
#     """
#     This sets up the basis for a MUX command. The idea
#     is that most other Mux-related commands should just
#     inherit from this and don't have to implement much
#     parsing of their own unless they do something particularly
#     advanced.
#
#     Note that the class's __doc__ string (this text) is
#     used by Evennia to create the automatic help entry for
#     the command, so make sure to document consistently here.
#     """
#     def has_perm(self, srcobj):
#         """
#         This is called by the cmdhandler to determine
#         if srcobj is allowed to execute this command.
#         We just show it here for completeness - we
#         are satisfied using the default check in Command.
#         """
#         return super().has_perm(srcobj)
#
#     def at_pre_cmd(self):
#         """
#         This hook is called before self.parse() on all commands
#         """
#         pass
#
#     def at_post_cmd(self):
#         """
#         This hook is called after the command has finished executing
#         (after self.func()).
#         """
#         pass
#
#     def parse(self):
#         """
#         This method is called by the cmdhandler once the command name
#         has been identified. It creates a new set of member variables
#         that can be later accessed from self.func() (see below)
#
#         The following variables are available for our use when entering this
#         method (from the command definition, and assigned on the fly by the
#         cmdhandler):
#            self.key - the name of this command ('look')
#            self.aliases - the aliases of this cmd ('l')
#            self.permissions - permission string for this command
#            self.help_category - overall category of command
#
#            self.caller - the object calling this command
#            self.cmdstring - the actual command name used to call this
#                             (this allows you to know which alias was used,
#                              for example)
#            self.args - the raw input; everything following self.cmdstring.
#            self.cmdset - the cmdset from which this command was picked. Not
#                          often used (useful for commands like 'help' or to
#                          list all available commands etc)
#            self.obj - the object on which this command was defined. It is often
#                          the same as self.caller.
#
#         A MUX command has the following possible syntax:
#
#           name[ with several words][/switch[/switch..]] arg1[,arg2,...] [[=|,] arg[,..]]
#
#         The 'name[ with several words]' part is already dealt with by the
#         cmdhandler at this point, and stored in self.cmdname (we don't use
#         it here). The rest of the command is stored in self.args, which can
#         start with the switch indicator /.
#
#         This parser breaks self.args into its constituents and stores them in the
#         following variables:
#           self.switches = [list of /switches (without the /)]
#           self.raw = This is the raw argument input, including switches
#           self.args = This is re-defined to be everything *except* the switches
#           self.lhs = Everything to the left of = (lhs:'left-hand side'). If
#                      no = is found, this is identical to self.args.
#           self.rhs: Everything to the right of = (rhs:'right-hand side').
#                     If no '=' is found, this is None.
#           self.lhslist - [self.lhs split into a list by comma]
#           self.rhslist - [list of self.rhs split into a list by comma]
#           self.arglist = [list of space-separated args (stripped, including '=' if it exists)]
#
#           All args and list members are stripped of excess whitespace around the
#           strings, but case is preserved.
#         """
#         raw = self.args
#         args = raw.strip()
#
#         # split out switches
#         switches = []
#         if args and len(args) > 1 and args[0] == "/":
#             # we have a switch, or a set of switches. These end with a space.
#             switches = args[1:].split(None, 1)
#             if len(switches) > 1:
#                 switches, args = switches
#                 switches = switches.split('/')
#             else:
#                 args = ""
#                 switches = switches[0].split('/')
#         arglist = [arg.strip() for arg in args.split()]
#
#         # check for arg1, arg2, ... = argA, argB, ... constructs
#         lhs, rhs = args, None
#         lhslist, rhslist = [arg.strip() for arg in args.split(',')], []
#         if args and '=' in args:
#             lhs, rhs = [arg.strip() for arg in args.split('=', 1)]
#             lhslist = [arg.strip() for arg in lhs.split(',')]
#             rhslist = [arg.strip() for arg in rhs.split(',')]
#
#         # save to object properties:
#         self.raw = raw
#         self.switches = switches
#         self.args = args.strip()
#         self.arglist = arglist
#         self.lhs = lhs
#         self.lhslist = lhslist
#         self.rhs = rhs
#         self.rhslist = rhslist
#
#         # if the class has the account_caller property set on itself, we make
#         # sure that self.caller is always the account if possible. We also create
#         # a special property "character" for the puppeted object, if any. This
#         # is convenient for commands defined on the Account only.
#         if hasattr(self, "account_caller") and self.account_caller:
#             if utils.inherits_from(self.caller, "evennia.objects.objects.DefaultObject"):
#                 # caller is an Object/Character
#                 self.character = self.caller
#                 self.caller = self.caller.account
#             elif utils.inherits_from(self.caller, "evennia.accounts.accounts.DefaultAccount"):
#                 # caller was already an Account
#                 self.character = self.caller.get_puppet(self.session)
#             else:
#                 self.character = None
