import redis
from prettytable import PrettyTable, PLAIN_COLUMNS

#TODO: add func that clear db

def print_help():
    """Print info about available commands"""
    for cmd in commands:
        print("{0:<6} - {1}".format(cmd, commands[cmd].__doc__))


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
            if user:
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

    # get user input with basic input-validation
    name = ""
    while len(name) < 1:
        name = input("Contact Name: ")

    phone = ""
    while len(phone) < 1:
        phone = input("Phone: ")

    success = r.hmset("contacts:" + str(next_id), {"name": name, "phone": phone}) #insert new contact
    if success == True:
        r.sadd("user_ids", next_id) #keep user_ids in a set to make it easier to manage active users
        r.incr("next_id", 1)    #When operations is completed, increment next_id


def remove():
    """Remove a contact from the db"""
    #Bad solution, find something better
    #name = input("Name to remove: ")
    #phone = input("Phone to remove: ")

    #Add check to make sure that correct values are supplied
    #TODO: change this to work with hashes
    # 1. find uid of contact with name x or phone y
    # 2. del contacts:uid to remove
    """r.lrem("contacts.name", name)
    r.lrem("contacts.phone", phone)"""


commands = {
    "help": print_help,
    "add": add,
    "remove": remove,
    "list": list_contacts,
    "find": find
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
            cmd = input("\n~ ")
            if cmd in commands: #if input is a valid cmd --> run it
                commands[cmd]()
            else:
                print("Unknown command. Type 'help' to list commands")
    else:
        print("Unable to connect to Redis. Make sure that the Redis-task is running\n('net start redis' in admin-cmd to start)")
