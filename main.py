import redis
from prettytable import PrettyTable, PLAIN_COLUMNS

__author__ = "Samuel Plumppu"
__version__ = "1.0"
__copyright__ = "Copyright 2015, Samuel Plumppu"
__license__ = "MIT"

def flush():
    """Delete all data in the current db"""
    if r.smembers("user_ids"):
        if input("Are you sure? ('y' / 'n')\n~ ").lower().lstrip().rstrip() == "y":
            if r.flushdb() == True:
                print("\nSuccessfully flushed the db")
        else:
            print("\nOperation canceled")
    else:
        print("Nothing to remove, db is already empty.")

def print_help():
    """Print info about available commands"""
    for cmd in commands:
        print("{0:<6} - {1}".format(cmd, commands[cmd].__doc__))


def list_contacts():
    """Show information about your contacts"""

    uids = r.smembers("user_ids")
    if uids:    #if there are actual contacts
        contacts_found = []
        #get info about each contact and add it to the table
        for uid in uids:
            contact = r.hgetall("contacts:" + str(uid))
            if contact:
                contacts_found.append(contact)

        print_contacts(contacts_found)
    else:
        print("No contacts to display. Add new contacts with the 'add'-command")


def find():
    """Find contacts by name or phone"""
    uids = r.smembers("user_ids")
    if uids:    #if there are actual contacts

        search_type = get_search_type()
        contacts_found = find_contacts(search_type)
        if contacts_found:
            print_contacts(contacts_found)

        else:
            print("\nNo contacts found with the given name or phone")
    else:
        print("No contacts to display. Add new contacts with the 'add'-command")


def add():
    """Add a contact to the db"""
    next_id = r.get("next_id")
    if next_id == None:    # if id doesn't exist yet, create it
        r.set("next_id", 0)
        next_id = r.get("next_id")

    # get user input with basic input-validation
    name = ""
    while len(name) < 1:
        name = input("Contact Name: ").lstrip().rstrip()

    phone = ""
    while len(phone) < 1:
        phone = input("Phone: ").lstrip().rstrip()

    success = r.hmset("contacts:" + str(next_id), {"name": name, "phone": phone}) #insert new contact
    if success == True:
        r.sadd("user_ids", next_id) #keep user_ids in a set to make it easier to manage active users
        r.incr("next_id", 1)    #When operations is completed, increment next_id


def remove():
    """Remove a contact from the db"""
    uids = r.smembers("user_ids")
    if uids:    #if there are actual contacts
        search_type = get_search_type(find2remove = True)
        contacts_found = find_contacts(search_type, return_uid = True)
        if contacts_found:
            print("\n{0} contact(s) found".format(len(contacts_found)))

            for uid in contacts_found:
                name = r.hgetall("contacts:" + uid)['name']
                if input("Are you sure you want to delete '{0}'? ('y' / 'n')\n~ ".format(name)).lower().lstrip().rstrip() == "y":
                    if r.delete("contacts:" + uid) == True and r.srem("user_ids", uid) == True:
                        print("\nSuccessfully removed '{0}' from the db".format(name))
                else:
                    print("\nOperation canceled\n")

        else:
            print("\nNo contacts found with the given name or phone")
    else:
        print("No contacts to remove.")


# ------------------------------- HELPERS --------------------------------------

def get_search_type(find2remove = False):
    """Helper that lets the user decide with search_type to use

    The flag find2remove is used to show if the funciton is called from the remove-function.
    This affect which message that appears in the prompt.
    """
    search_type = ""
    while True:
        try:
            if find2remove:
                msg = "How do you want to find the contact to remove?\n'1': By name\n'2': By phone\n~ "
            else:
                msg = "How do you want to find the contact?\n'1': By name\n'2': By phone\n~ "
            search_type = int(input(msg))

            if search_type == 1 or search_type == 2:
                return search_type
            else:
                print("\nPlease enter a number in range 1-2\n")
        except ValueError:
            print("\nPlease enter a number in range 1-2\n")


def print_contacts(contacts_found):
    """Helper that takes a list of contacts and prints it in a nice table"""
    if contacts_found:
        contacts = PrettyTable(["Name", "Phone"])
        contacts.align["Name"] = "l"
        contacts.set_style(PLAIN_COLUMNS)

        print("{0} contact(s) found".format(len(contacts_found)))

        for contact in contacts_found:
            contacts.add_row([contact['name'], contact['phone']])

        print("\n", contacts.get_string(sortby="Name"))


def find_contacts(search_type, return_uid = False):
    """Helper that finds a contact either by name or phone, depending on the 'search_type'-flag.

    The 'return_uid'-flag decide if the found contacts should be returned as contact-objs or user_ids
    """
    uids = r.smembers("user_ids")
    if uids:    #if there are actual users

        name = ""
        phone = ""

        if search_type == 1:
            while len(name) < 1:
                name = input("\nContact name: ").lstrip().rstrip()
        elif search_type == 2:
            while len(phone) < 1:
                phone = input("\nPhone: ").lstrip().rstrip()
        else:
            print("\nInvalid search_type")

        if search_type == 1 or search_type == 2:
            contacts_found = []
            #look through all active users if there's a match with the given name or phone
            for uid in uids:
                contact = r.hgetall("contacts:" + str(uid))
                if contact:
                    if search_type == 1:
                        if name.lower() in contact['name'].lower():
                            if return_uid:
                                contacts_found.append(uid)
                            else:
                                contacts_found.append(contact)
                    elif search_type == 2:
                        if phone in contact['phone']:
                            if return_uid:
                                contacts_found.append(uid)
                            else:
                                contacts_found.append(contact)

            return contacts_found


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
        print("\n-=- CLI Kontaktz {} -=-\nType 'help' to list commands".format(__version__))

        running = True
        while running:
            cmd = input("\n~ ").lstrip().rstrip()
            if cmd in commands: #if input is a valid cmd -->
                commands[cmd]()     #run its callback stored in the commands-dict
            else:
                print("Unknown command. Type 'help' to list commands")
    else:
        print("Unable to connect to Redis. Make sure that the Redis-task is running\n('net start redis' in admin-cmd to start)")
