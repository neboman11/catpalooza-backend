import mysql.connector
from mysql.connector import Error
import os
import argparse

def convertToBinaryData(filename):
    with open(filename, 'rb') as file:
        binaryData = file.read()
    return binaryData

def insertBLOB(photo, table):
    print("Inserting " + photo + " into database...")
    try:
        connection = mysql.connector.connect(host='192.168.1.2',
                                             database='catpalooza',
                                             user='catpalooza',
                                             password='catpalooza')

        cursor = connection.cursor()
        sql_insert_blob_query = "INSERT INTO %s (name, photo, size) VALUES (%s, %s, %s)"

        catPic = convertToBinaryData(photo)

        # Convert data into tuple format
        insert_blob_tuple = (table, os.path.basename(photo), catPic, os.path.getsize(photo))
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

def uploadDirectoryToDatabase(directory, table):
    for file in os.listdir('reddit_sub_cat'):
        if os.path.isdir(file):
            uploadDirectoryToDatabase(os.path.join(directory, file))
        elif file.endswith('.jpg') or file.endswith('.jpeg') or file.endswith('.png') or file.endswith('.webp'):
            insertBLOB(os.path.join(directory, file), table)

# if __name__ == '__main__':
#     parser = argparse.ArgumentParser()
#     parser.add_argument('--dir', type=str, help='The directory containing images to upload.')
#     args = parser.parse_args()
#     uploadDirectoryToDatabase(args.dir, 'photos')

#     # TODO: Remove
#     uploadDirectoryToDatabase(os.path.join(args.dir, 'angry cat'), 'angry_ct')
