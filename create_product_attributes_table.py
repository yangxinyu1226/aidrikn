import database

db_file = 'nainai_tea.db'
connection = database.create_connection(db_file)
if connection:
    database.create_tables(connection)
    connection.close()
    print("Product attributes table creation attempt complete.")