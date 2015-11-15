import redis
from prettytable import PrettyTable, PLAIN_COLUMNS

def flush():
    """Delete all data in the current db"""
    if input("Are you sure? ('y' / 'n')\n~ ").lower() == "y":
        if r.flushdb() == True:
            print("\nSuccessfully flushed the db")
    else:
        print("\nOperation canceled")

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
        print("You've not added any contacts yet. Add new contacts with the 'add'-command")


def find():
    """Find contacts by name or phone"""
    uids = r.smembers("user_ids")
    if uids:    #if there are actual contacts
        search_type = ""
        running = True
        while running:
            try:
                search_type = int(input("How do you want to find the contact?\n'1': By name\n'2': By phone\n~ "))
                if search_type == 1 or search_type == 2:
                    running = False
                else:
                    print("\nPlease enter a number in range 1-2\n")
            except ValueError:
                print("\nPlease enter a number")

        if search_type == 1:
            name = ""
            while len(name) < 1:
                name = input("\nContact name: ")
        else:
            phone = ""
            while len(phone) < 1:
                phone = input("\nPhone: ")

        contacts_found = []
        #look through all active users if there's a match with the given name or phone
        for uid in uids:
            contact = r.hgetall("contacts:" + str(uid))
            if contact:
                if search_type == 1:
                    if contact['name'] == name:
                        contacts_found.append(contact)
                elif search_type == 2:
                    if contact['phone'] == phone:
                        contacts_found.append(contact)

        if contacts_found:
            print("\n{0} contact(s) found".format(len(contacts_found)))
            for contact in contacts_found:
                print("{0} - {1}".format(contact['name'], contact['phone']))
        else:
            print("\nNo contacts found with the given name or phone\n")
    else:
        print("You've not added any contacts yet. Add new contacts with the 'add'-command")


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
    "find": find,
    "flush": flush
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
