##########################################
#### Our SQLite3 management functions ####
##########################################

import sqlite3

'''
Les 4 opérations fondamentales sur une base de données
INSERT (CREATE)
SELECT (READ)
UPDATE (UPDATE)
DELETE (DELETE)

Etapes à effectuer dans sqlite3
connect_to_db()
create_cursor()
read_from_cursor()
write_to_cursor() >>> commit_to_db()
disconnect_from_db()
'''


def connect_to_db(db_path): #/home/tux/meals.db  meals.db
  
  try:
    db_link = sqlite3.connect(db_path)
    
  except sqlite3.Error as error:
    print("Error while connecting to database : ", error)
    
  return db_link


def create_cursor(db_link):
      
  try:
    db_cursor = db_link.cursor()
    
  except sqlite3.Error as error:
    print("Error while creating database cursor : ", error)
    
  return db_cursor #TODO what if returning None?


def read_from_cursor(db_cursor,sql_query,sql_values=tuple()):
      
  try:
    db_cursor.execute(sql_query,sql_values)
    query_result = db_cursor.fetchall()
    
  except sqlite3.Error as error:
    print("Error while reading from cursor : ", error)
    
  return query_result


def write_to_cursor(db_cursor,sql_query,sql_values=tuple()):
      
  try:
    db_cursor.execute(sql_query, sql_values)
    
  except sqlite3.Error as error:
    print("Error while writing to cursor : ", error)


def commit_to_db(db_link):
      
  try:
    db_link.commit()
  except sqlite3.Error as error:
    
    print("Error while commiting cursor to database : ", error)


def disconnect_from_db(db_link):
      
  try:
    db_link.close()
  except sqlite3.Error as error:
    
    print("Error while disconnecting from database : ", error)


###################
#### Test code ####
###################

db_link = connect_to_db('meals.db')
db_cursor = create_cursor(db_link)
sql_query = 'SELECT * FROM employee'
# sql_values = () # ou tuple()
# [(1, 'John', 'SMITH', None), (2, 'John', 'SMITH', None), (3, 'Olivia', 'JONES', None), (4, 'Jack', 'DAVIS', None)]
query_result = read_from_cursor(db_cursor,sql_query)
disconnect_from_db(db_link)
print(query_result)
