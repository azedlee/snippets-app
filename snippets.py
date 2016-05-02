import logging
import argparse
import psycopg2
import psycopg2.extras

logging.debug("Connecting to PostgreSQL")
connection = psycopg2.connect(database="snippets")
logging.debug("Database connection established.")

# Set the log output file, and the log level
logging.basicConfig(filename="snippets.log", level = logging.DEBUG)

def put(name, snippet, hide=False):
    """
    Store a snippet with an associated name.
    """
    logging.info("Storing snippet {!r}: {!r}".format(name, snippet))
    with connection, connection.cursor() as cursor:
        try:
            cursor.execute("INSERT INTO snippets values (%s, %s, %s)", (name, snippet, hide))
        except psycopg2.IntegrityError as e:
            connection.rollback()
            cursor.execute("UPDATE snippets SET message=%s WHERE keyword=%s", (snippet, name))
    connection.commit()
    logging.debug("Snippet stored successfully.")
    return name, snippet


def get(name):
    """
    Retrieve the snippet with a given name.
    """
    logging.info("Fetching snippet {!r}".format(name))
    with connection, connection.cursor() as cursor:
        cursor.execute("SELECT message FROM snippets WHERE \hidden=False AND keyword=%s", (name, ))
        row = cursor.fetchone()
    logging.debug("Snippet successfully fetched.")
    if not row:
        #no snippet was found with that name
        return "404: Snippet Not Found"
    return row[0]


def catalog():
    """
    Catalog to look up keywords
    """
    logging.info("Query Snippet")
    with connection, connection.cursor(cursor_factory=psycopg2.extras.DictCursor) as cursor:
        cursor.execute("SELECT keyword FROM snippets")
        rows = cursor.fetchall()
        for row in rows:
            print(row["keyword"])



def search(word):
    """
    Search for a string within snippet messages
    """
    logging.info("Search Function")
    with connection, connection.cursor(cursor_factory=psycopg2.extras.DictCursor) as cursor:
        cursor.execute("SELECT * FROM snippets WHERE message like '%%'||%s||'%%'", (word, ))
        rows = cursor.fetchall()
        for row in rows:
            print(row['message'])


def main():
    """Main function"""
    logging.info("Constructing parser")
    parser = argparse.ArgumentParser(description="Store and retrieve snippets of text")

    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # Subparser for the put command
    logging.debug("Constructing put subparser")
    put_parser = subparsers.add_parser("put", help="Store a snippet")
    put_parser.add_argument("name", help="Name of the snippet")
    put_parser.add_argument("snippet", help="Snippet text")
    put_parser.add_argument("--hide", help="Sets the column to hidden, not searchable with Search or Catalog commands")

    # Subparser for the get command
    logging.debug("Constructing get subparser")
    get_parser = subparsers.add_parser("get", help="Retrieve a snippet")
    get_parser.add_argument("name", help="The name of the snippet")
    
    # Subparser for the catalog command
    logging.debug("Constructing catalog subparser")
    get_parser = subparsers.add_parser("catalog", help="Return Keywords Catalog in snippet")

    # Subparser for the search command
    logging.debug("Constructing search subparser")
    get_parser = subparsers.add_parser("search", help="Search a given string anywhere in their messages")
    get_parser.add_argument("word", help="The string used to search")

    arguments = parser.parse_args()
    # Convert parsed arguments from Namespace to dictionary
    arguments = vars(arguments)
    command = arguments.pop("command")

    if command == "put":
        name, snippet = put(**arguments)
        print("Stored {!r} as {!r}".format(snippet, name))
    elif command == "get":
        snippet = get(**arguments)
        print("Retrieved snippet: {!r}".format(snippet))
    elif command == "catalog":
        catalog()
        print("Retrieved Keywords")
    elif command == "search":
        word = search(**arguments)
        print("Retrieved String: {!r}".format(word))

if __name__ == "__main__":
    main()