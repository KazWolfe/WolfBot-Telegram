import AwooUtils

COMMANDS = AwooUtils.CommandManager()

def register(name, helptext, helpargs, permset):
    def wrap(fn):
        # perform registration here
        # fn points to the function itself
        # fn.__name__ is the name of the function
        COMMANDS.register(fn, name, helptext, helpargs, permset)
        print "Registered command /" + name
    return wrap