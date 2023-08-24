import sqlite3
import wikipedia
from wikipedia import DisambiguationError, PageError

conn = sqlite3.connect('./databases/famous_people.db')
cursor = conn.cursor()

cursor.execute('''
    CREATE TABLE IF NOT EXISTS famous_people (
        id INTEGER PRIMARY KEY,
        name VARCHAR(100) NOT NULL UNIQUE CHECK ( name <> '' ),
        summary TEXT NOT NULL CHECK ( summary <> '' )
    )
''')


def find_and_add_person_summary(full_name):
    try:
        row_in_db = cursor.execute('SELECT * FROM famous_people WHERE lower(name)=lower(?)', (full_name,)).fetchall()
        if len(row_in_db) > 0:
            print("This name already exists in the DB")
            return

        search = wikipedia.search(full_name, 1, True) #e.g. (["Donald"], 'donald')
        array_person_found = search[0] #e.g. ["Donald"]
        suggestion = search[1] #e.g. 'donald'
        person_found = None
        if len(array_person_found) != 0:
            person_found = array_person_found[0]

        #if person exists
        if person_found is not None and array_person_found[0].lower() == full_name.lower():
            summary = wikipedia.summary(full_name)
            cursor.execute('INSERT INTO famous_people (name, summary) VALUES (?, ?)', (array_person_found[0], summary))
            conn.commit()
            print(f"Added '{array_person_found[0]}' to the database.")
        #if there is a suggestion
        elif suggestion:
            print(f"Did you mean {suggestion}?")
        #we do not find any person
        elif suggestion is None:
            print("I don’t not know this person")
    except DisambiguationError as e:
        print(f"The fullname '{full_name}' is ambiguous. Here is what Wikipedia suggests: {', '.join(e.options)}")
    except PageError as e: # e.g. 'stephen lang' raises an exception
        print(f"The fullname '{full_name}' does not match any pages. Try another!")


def main():
    while True:
        user_input = input("Enter the full name of someone famous (or 'q' to finish): ")

        if not user_input.strip():
            print("You have to enter a name")
            continue

        if user_input.lower() == 'q':
            print("Program finished")
            conn.close()
            break

        find_and_add_person_summary(user_input)


if __name__ == '__main__':
    main()

