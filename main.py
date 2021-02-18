#!/usr/bin/python3

import mysql.connector
from mysql.connector import Error
import os
import argparse

def convertToBinaryData(filename):
    with open(filename, 'rb') as file:
        binaryData = file.read()
    return binaryData

def insertBLOB(dbConnection, photo, table):
    print("Inserting " + photo + " into database...")
    try:
        databaseCursor = dbConnection.cursor()
        sql_insert_blob_query = "INSERT INTO {} (name, photo, size) VALUES (%s, %s, %s)".format(table)

        catPic = convertToBinaryData(photo)

        # Convert data into tuple format
        insert_blob_tuple = (os.path.basename(photo), catPic, os.path.getsize(photo))
        databaseCursor.execute(sql_insert_blob_query, insert_blob_tuple)
        dbConnection.commit()
        print("Image successfully entered into table {}".format(table))

    except Error as error:
        print("Failed inserting BLOB into MySQL table {}".format(error))

    finally:
        databaseCursor.close()

def uploadDirectoryToDatabase(dbConnection, directory, table):
    for file in os.listdir(directory):
        if os.path.isdir(os.path.join(directory, file)):
            uploadDirectoryToDatabase(dbConnection, os.path.join(directory, file), table)
        elif file.endswith('.jpg') or file.endswith('.jpeg') or file.endswith('.png') or file.endswith('.webp'):
            insertBLOB(dbConnection, os.path.join(directory, file), table)

def openDatabaseConnection():
    connection = mysql.connector.connect(host='192.168.1.2',
                                             database='catpalooza',
                                             user='catpalooza',
                                             password='catpalooza')

    return connection

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--dir', type=str, default='.', help='The directory containing images to upload.')
    args = parser.parse_args()

    dbConnection = openDatabaseConnection()
    print("Opened connection to mysql database")
    uploadDirectoryToDatabase(dbConnection, str(args.dir), 'photos')
    if (dbConnection.is_connected()):
        dbConnection.close()
        print("MySQL connection is closed")
