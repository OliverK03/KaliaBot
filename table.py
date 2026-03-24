import sqlite3

connection = sqlite3.connect('user.db')
cursor = connection.cursor()

create_table_query = """
    CREATE TABLE IF NOT EXISTS users(
        id integer primary key,
        kaliacount integer
    );
"""

cursor.execute(create_table_query)
connection.commit()
connection.close()

sample_data_query = """
    INSERT INTO users (id, kaliacount)
    VALUES (?, ?)
"""

sample_data = [(111111, 1),
               (121111, 2),
               (112111, 22),
               ]

with sqlite3.connect('user.db') as connection:
    cursor = connection.cursor()
    cursor.executemany(sample_data_query, sample_data)