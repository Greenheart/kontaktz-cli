import redis

def help():
    """Print available commands"""
    print("\n")
    for cmd in commands:
        print("{0} - {1}".format(cmd, commands[cmd]))


def add():
    """Add a contact to the db"""

def remove():
    """Remove a contact from the db"""

commands = {
    "help": help.__doc__,
    "add": add.__doc__,
    "remove": remove.__doc__
}

if __name__ == '__main__':

    #TODO: detect if redis is working --> if not, show how user can start redis
    #"Start Redis --> 1: run cmd as admin \n2: run 'net start redis'"
    #"Stop Redis --> 1: run cmd as admin \n2: run 'net stop redis'"

    print("-=- CLI Contactz 0.1 -=-\n'help' to show commands")
    running = True
    while running:
        cmd = input("~ ")
        if cmd == "help":
            help()
        elif cmd == "add":
            add()
        elif cmd == "remove":
            remove()
