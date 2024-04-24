import unittest
import mysql.connector
from dataBaseManager import *

class TestDatabaseManager(unittest.TestCase):

    def setUp(self):
        # Connect to the database
        self.mydb = mysql.connector.connect(
            host="localhost",
            user="mcall",
            password="Abcdef12345@",
            database="FletTutorAppUsers"
        )
        # Create a cursor
        self.mycursor = self.mydb.cursor(buffered=True)

    def tearDown(self):
        # Close the database connection
        self.mydb.close()

    def test_resetDB(self):
        # Reset the database
        resetDB()
        # Check if the database is empty
        self.mycursor.execute("SHOW TABLES")
        tables = self.mycursor.fetchall()
        self.assertEqual(len(tables), 0)

    def test_initDB(self):
        # Initialize the database
        initDB()
        # Check if the tables are created
        self.mycursor.execute("SHOW TABLES")
        tables = self.mycursor.fetchall()
        self.assertEqual(len(tables), 7)

    def test_makeGroup(self):
        # Initialize the database
        initDB()
        # Create a group
        makeGroup("Group 1", "user1")
        # Check if the group is created
        self.mycursor.execute("SELECT * FROM Groupss")
        groups = self.mycursor.fetchall()
        self.assertEqual(len(groups), 1)

    def test_getGroups(self):
        # Initialize the database
        initDB()
        # Create some groups
        makeGroup("Group 1", "user1")
        makeGroup("Group 2", "user2")
        makeGroup("Group 3", "user1")
        # Get all groups
        all_groups = getGroups()
        self.assertEqual(len(all_groups), 3)
        # Get groups owned by user1
        user1_groups = getGroups("user1")
        self.assertEqual(len(user1_groups), 2)

    # Add more test cases for other functions...

if __name__ == '__main__':
    unittest.main()