import redis
from prettytable import PrettyTable, PLAIN_COLUMNS

#TODO: add func that clear db

def print_help():
    """Print available commands"""
    for cmd in commands:
        print("{0:<6} - {1}".format(cmd, commands[cmd]))


def list_contacts():
    """Show information about your contacts"""

    uids = r.smembers("user_ids")
    if uids:    #if there are actual contacts
        contacts = PrettyTable(["Name", "Phone"])
        contacts.align["Name"] = "l"
        contacts.set_style(PLAIN_COLUMNS)

        #get info about each contact and add it to the table
        for uid in uids:
            user = r.hgetall("contacts:" + str(uid))
            contacts.add_row([user['name'], user['phone']])

        print(contacts.get_string(sortby="Name"))
    else:
        print("No contacts found. Add new contacts with the 'add'-command")


def find():
    """Find a contact by name or phone"""
    pass


def add():
    """Add a contact to the db"""
    next_id = r.get("next_id")
    if next_id == None:    # if id doesn't exist yet, create it
        r.set("next_id", 0)
        next_id = r.get("next_id")
    r.sadd("user_ids", next_id) #keep user_ids in a set to make it easier to manage active users

    # get user input with basic input-validation
    name = ""
    while len(name) < 1:
        name = input("Contact Name: ")

    phone = ""
    while len(phone) < 1:
        phone = input("Phone: ")

    r.hmset("contacts:" + str(next_id), {"name": name, "phone": phone}) #insert new contact
    r.incr("next_id", 1)    #When operations is completed, increment next_id


def remove():
    """Remove a contact from the db"""
    #Bad solution, find something better
    #name = input("Name to remove: ")
    #phone = input("Phone to remove: ")

    #Add check to make sure that correct values are supplied
    #TODO: change this to work with hashes
    """r.lrem("contacts.name", name)
    r.lrem("contacts.phone", phone)"""


commands = {
    "help": print_help.__doc__,
    "add": add.__doc__,
    "remove": remove.__doc__,
    "list": list_contacts.__doc__,
    "find": find.__doc__
}

if __name__ == '__main__':

    r = redis.Redis(
        host = 'localhost',
        port = 6379,
        decode_responses = True)

    #"Start Redis --> 1: run cmd as admin \n2: run 'net start redis'"
    #"Stop Redis --> 1: run cmd as admin \n2: run 'net stop redis'"

    if r:
        print("\nRedis connected")
        print("\n-=- CLI Kontaktz 0.1 -=-\nType 'help' to list commands")

        running = True
        while running:
            #TODO: rewrite this part to loop through the commands-dict,
            #      use the keys as commands and values as callback-functions
            #      also rename current commands-dict to command_descriptions
            cmd = input("\n~ ")
            if cmd == "help":
                print_help()
            elif cmd == "add":
                add()
            elif cmd == "remove":
                remove()
            elif cmd == "list":
                list_contacts()
            elif cmd == "find":
                find()
            else:
                print("Unknown command. Type 'help' to list commands")
    else:
        print("Unable to connect to Redis. Make sure that the Redis-task is running\n('net start redis' in admin-cmd to start)")
