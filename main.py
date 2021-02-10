import mysql.connector
from mysql.connector import Error
import os

def convertToBinaryData(filename):
    with open(filename, 'rb') as file:
        binaryData = file.read()
    return binaryData

def insertBLOB(photo):
    print("Inserting " + photo + " into database...")
    try:
        connection = mysql.connector.connect(host='192.168.1.2',
                                             database='catpalooza',
                                             user='catpalooza',
                                             password='catpalooza')

        cursor = connection.cursor()
        sql_insert_blob_query = """ INSERT INTO photos (name, photo, size) VALUES (%s, %s, %s)"""

        catPic = convertToBinaryData(photo)

        # Convert data into tuple format
        insert_blob_tuple = (os.path.basename(photo), catPic, os.path.getsize(photo))
        result = cursor.execute(sql_insert_blob_query, insert_blob_tuple)
        connection.commit()
        print("Image successfully entered into the database", result)

    except Error as error:
        print("Failed inserting BLOB into MySQL table {}".format(error))

    finally:
        if (connection.is_connected()):
            cursor.close()
            connection.close()
            print("MySQL connection is closed")

def uploadDirectoryToDatabase(directory):
    for file in os.listdir('reddit_sub_cat'):
        if os.path.isdir(file):
            uploadDirectoryToDatabase(os.path.join(directory, file))
        elif file.endswith('.jpg') or file.endswith('.jpeg') or file.endswith('.png') or file.endswith('.webp'):
            insertBLOB(os.path.join(directory, file))

uploadDirectoryToDatabase('reddit_sub_cat')
