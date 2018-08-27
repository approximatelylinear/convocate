
import datetime

def get_timestamp():
    return datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')

PEOPLE = {
    "Ashley": {
        'fname': "Ashley",
        'lname': "Bobashly"
    },
    "Anna": {
        'fname': "Anna",
        'lname': "Bobana"
    }
}

def read():
    return [PEOPLE[key] for key in sorted(PEOPLE.keys())]
