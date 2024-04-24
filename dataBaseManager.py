#There will be 2 databases, one for the users and one for the groups the users are in.
#The users database will have the following fields: oauthID, email, groupIDs
#The groups database will have the following fields: groupID, groupName, groupMembers

import mysql.connector
import random
mydb = mysql.connector.connect(
        host="localhost",
        user= "mcall",
        password="Abcdef12345@",
    )

mycursor = mydb.cursor(buffered=True)

def resetDB():
    mycursor.execute("DROP DATABASE IF EXISTS FletTutorAppUsers")
    mydb.commit()

def initDB():
    mycursor.execute("CREATE DATABASE IF NOT EXISTS FletTutorAppUsers")
    mycursor.execute("USE FletTutorAppUsers")
    mycursor.execute("CREATE TABLE IF NOT EXISTS Users (oauthID VARCHAR(255) PRIMARY KEY, email VARCHAR(255), firstName VARCHAR(255), lastName VARCHAR(255))")
    mycursor.execute("CREATE TABLE IF NOT EXISTS Groupss (groupID VARCHAR(255) PRIMARY KEY, groupName VARCHAR(255), groupOwner VARCHAR(255))")
    mycursor.execute("CREATE TABLE IF NOT EXISTS GroupMembers ( rowID INT AUTO_INCREMENT PRIMARY KEY, groupID INT, groupMemberOAUTH VARCHAR(255), UNIQUE KEY (groupID, groupMemberOAUTH))")
    mycursor.execute("CREATE TABLE IF NOT EXISTS Applications (applicationID VARCHAR(255) PRIMARY KEY, groupID VARCHAR(255),  applicantOAUTH VARCHAR(255), additionalInfo TEXT, status VARCHAR(255), timeSubmitted TIMESTAMP DEFAULT CURRENT_TIMESTAMP)")
    mycursor.execute("CREATE TABLE IF NOT EXISTS timeSlots (timeSlotID VARCHAR(255) PRIMARY KEY, groupID VARCHAR(255),  timeSlot VARCHAR(255), userOAUTH VARCHAR(255))")
    mycursor.execute("CREATE TABLE IF NOT EXISTS groupPreferedTimeSlots (timeSlotID VARCHAR(255) PRIMARY KEY, groupID VARCHAR(255),  timeSlot VARCHAR(2000))")
    mycursor.execute("CREATE TABLE IF NOT EXISTS userTimeSlotsApplyingFor (timeSlotID VARCHAR(255) PRIMARY KEY, groupID VARCHAR(255),  timeSlot VARCHAR(2000), userOAUTH VARCHAR(255))")
    mycursor.execute("CREATE TABLE IF NOT EXISTS userTimeSlotsHas (timeSlotID VARCHAR(255) PRIMARY KEY, groupID VARCHAR(255),  timeSlot VARCHAR(2000), userOAUTH VARCHAR(255))")
    mydb.commit()

def makeGroup(groupName, groupOwner):
    if not doesUserExist(groupOwner):
        return ('OWNER DOES NOT EXIST (Incorrect OAUTHID)')
    groupID = random.randint(1000, 9999)
    #make sure groupID is unique
    mycursor.execute("USE FletTutorAppUsers")
    mycursor.execute("SELECT * FROM Groupss WHERE groupID = %s", (groupID,))
    while mycursor.fetchone() != None:
        groupID = random.randint(1000, 9999)
        mycursor.execute("SELECT * FROM Groupss WHERE groupID = %s", (groupID,))
    
    mycursor.execute("INSERT INTO Groupss (groupID, groupName, groupOwner) VALUES (%s, %s, %s)", (groupID, groupName, groupOwner))
    mydb.commit()
    return True
def getGroups(oauthID= None):
    mycursor.execute("USE FletTutorAppUsers")
    if (oauthID == None):
        mycursor.execute("SELECT * FROM Groupss")
    else:
        mycursor.execute("SELECT * FROM Groupss WHERE groupOwner = %s", (oauthID,))
    groupIDs = mycursor.fetchall()

    return groupIDs
def getGroupsUserIsIn(oauthID):
    mycursor.execute("USE FletTutorAppUsers")
    mycursor.execute("SELECT * FROM GroupMembers WHERE groupMemberOAUTH = %s", (oauthID,))
    groupIDs = mycursor.fetchall()
    return groupIDs
def getGroupFromGroupID(groupID):
    mycursor.execute("USE FletTutorAppUsers")
    mycursor.execute("SELECT * FROM Groupss WHERE groupID = %s", (groupID,))
    group = mycursor.fetchone()
    return group
def deleteGroup(groupID):
    mycursor.execute("USE FletTutorAppUsers")
    mycursor.execute("DELETE FROM Groupss WHERE groupID = %s", (groupID,))
    #Delete all group members
    mycursor.execute("DELETE FROM GroupMembers WHERE groupID = %s", (groupID,))
    #Delete all applications
    mycursor.execute("DELETE FROM Applications WHERE groupID = %s", (groupID,))
    mydb.commit()
def changeGroupName(groupID, newName):
    mycursor.execute("USE FletTutorAppUsers")
    mycursor.execute("UPDATE Groupss SET groupName = %s WHERE groupID = %s", (newName, groupID))
    mydb.commit()
def addUser(oauthID, email, firstName, lastName):
    mycursor.execute("USE FletTutorAppUsers")
    mycursor.execute("SELECT * FROM Users WHERE email = %s", (email,))
    if mycursor.fetchone() == None:
        mycursor.execute("INSERT INTO Users (oauthID, email, firstName, lastName) VALUES(%s, %s, %s, %s)", (oauthID, email, firstName, lastName))
        mydb.commit()
        return (True)
    else:
        return ('USER ALREADY EXSISTS')    
def listUsers():
    mycursor.execute("USE FletTutorAppUsers")
    mycursor.execute("SELECT * FROM Users")
    users = mycursor.fetchall()
    return users
def deleteUser(oauthID):
    mycursor.execute("USE FletTutorAppUsers")
    mycursor.execute("DELETE FROM Users WHERE oauthID = %s", (oauthID,))
    mydb.commit()
def addUserToGroup(email, groupID):
    user = getUserFromEmail(email)
    if user != None:
        #Check for valid groupID
        if doesGroupExist(groupID):
            mycursor.execute("SELECT * FROM GroupMembers WHERE groupID = %s AND groupMemberOAUTH = %s", (groupID, user[0]))
            if mycursor.fetchone() == None:
                mycursor.execute("SELECT * FROM GroupMembers")
                mycursor.execute("INSERT INTO GroupMembers (groupID, groupMemberOAUTH) VALUES (%s, %s)", (groupID, user[0]))
                mydb.commit()  # Committing the INSERT query
                return True
            else:
                return ('USER ALREADY IN GROUP')
        else:
            return ('GROUP NOT FOUND')
        
    else:
        return ('USER NOT FOUND')
def getGroupMembers(groupID):
    mycursor.execute("USE FletTutorAppUsers")
    mycursor.execute("SELECT * FROM GroupMembers WHERE groupID = %s", (groupID,))
    members = mycursor.fetchall()
    return members
def doesUserExist(oauthID):
    mycursor.execute("USE FletTutorAppUsers")
    mycursor.execute("SELECT * FROM Users WHERE oauthID = %s", (oauthID,))
    user = mycursor.fetchone()
    if user == None:
        return False
    else:
        return True
def doesGroupExist(groupID):
    mycursor.execute("USE FletTutorAppUsers")
    mycursor.execute("SELECT * FROM Groupss WHERE groupID = %s", (groupID,))
    group = mycursor.fetchone()
    if group == None:
        return False
    else:
        return True
def getUserFromEmail(email):
    mycursor.execute("USE FletTutorAppUsers")
    mycursor.execute("SELECT * FROM Users WHERE email = %s", (email,))
    user = mycursor.fetchone()
    return user
def getUserFromOAUTH(oauthID):
    mycursor.execute("USE FletTutorAppUsers")
    mycursor.execute("SELECT * FROM Users WHERE oauthID = %s", (oauthID,))
    user = mycursor.fetchone()
    return user
def removeUserFromGroup(email, groupID):
    user = getUserFromEmail(email)
    if user != None:
        mycursor.execute("USE FletTutorAppUsers")
        mycursor.execute("DELETE FROM GroupMembers WHERE groupID = %s AND groupMemberOAUTH = %s", (groupID, user[0]))
        mydb.commit()
        return True
    else:
        return ('USER NOT FOUND')
def createApplication(groupID, applicantOAUTH, additionalInfo):
    mycursor.execute("USE FletTutorAppUsers")
    if not doesGroupExist(groupID):
        return ('GROUP DOES NOT EXIST')
    if not doesUserExist(applicantOAUTH):
        return ('USER DOES NOT EXIST')
    if getGroupFromGroupID(groupID)[2] == applicantOAUTH:
        return ('CANNOT APPLY TO OWN GROUP')
    #Check if user is already in group
    mycursor.execute("SELECT * FROM GroupMembers WHERE groupID = %s AND groupMemberOAUTH = %s", (groupID, applicantOAUTH))
    if mycursor.fetchone() != None:
        return ('USER ALREADY IN GROUP')
    #check if user has already applied
    mycursor.execute("SELECT * FROM Applications WHERE groupID = %s AND applicantOAUTH = %s", (groupID, applicantOAUTH))
    if mycursor.fetchone() != None:
        return ('USER ALREADY APPLIED')
    mycursor.execute("SELECT * FROM Applications")
    rowNumber = len(mycursor.fetchall())
    mycursor.execute("INSERT INTO Applications (applicationID, groupID, applicantOAUTH, additionalInfo, status) VALUES (%s, %s, %s, %s, %s)", (rowNumber, groupID, applicantOAUTH, additionalInfo, 'PENDING'))
    mydb.commit()
def getApplications(groupID=None):
    mycursor.execute("USE FletTutorAppUsers")
    if groupID == None:
        mycursor.execute("SELECT * FROM Applications")
        applications = mycursor.fetchall()
        mydb.commit()
        return applications
    else:
        mycursor.execute("SELECT * FROM Applications WHERE groupID = %s", (groupID,))
        applications = mycursor.fetchall()
        mydb.commit()
        return applications  
def deleteApplication(userID, groupID):
    mycursor.execute("USE FletTutorAppUsers")
    mycursor.execute("DELETE FROM Applications WHERE groupID = %s AND applicantOAUTH = %s", (groupID, userID))
    mydb.commit()
def denyApplication(userID, groupID):
    mycursor.execute("USE FletTutorAppUsers")
    #Check if user is in group
    mycursor.execute("SELECT * FROM GroupMembers WHERE groupID = %s AND groupMemberOAUTH = %s", (groupID, userID))
    if mycursor.fetchone() != None:
        deleteApplication(userID, groupID)
        return ('USER ALREADY IN GROUP')
    #Check if user has applied
    mycursor.execute("SELECT * FROM Applications WHERE groupID = %s AND applicantOAUTH = %s", (groupID, userID))
    application = mycursor.fetchone()
    if application == None:
        return ('USER HAS NOT APPLIED TO THIS GROUP')
    #Change status of application to denied
    mycursor.execute("UPDATE Applications SET status = %s WHERE groupID = %s AND applicantOAUTH = %s", ('DENIED', groupID, userID))
    mydb.commit()
def acceptApplication(userID, groupID):
    mycursor.execute("USE FletTutorAppUsers")
    #Check if user is in group
    mycursor.execute("SELECT * FROM GroupMembers WHERE groupID = %s AND groupMemberOAUTH = %s", (groupID, userID))
    if mycursor.fetchone() != None:
        deleteApplication(userID, groupID)
        return ('USER ALREADY IN GROUP')
    #Check if user has applied
    mycursor.execute("SELECT * FROM Applications WHERE groupID = %s AND applicantOAUTH = %s", (groupID, userID))
    application = mycursor.fetchone()
    if application == None:
        return ('USER HAS NOT APPLIED TO THIS GROUP')
    mycursor.execute("INSERT INTO GroupMembers (rowID, groupID, groupMemberOAUTH) VALUES (%s, %s, %s)", (len(getGroupMembers(groupID)), groupID, userID))
    mycursor.execute("DELETE FROM Applications WHERE groupID = %s AND applicantOAUTH = %s", (groupID, userID))

    mydb.commit()
def getApplicationsFromUser(userID):
    mycursor.execute("USE FletTutorAppUsers")
    mycursor.execute("SELECT * FROM Applications WHERE applicantOAUTH = %s", (userID,))
    applications = mycursor.fetchall()
    return applications
def getApplicationsNotDenied(groupID):
    mycursor.execute("USE FletTutorAppUsers")
    if groupID == None:
        mycursor.execute("SELECT * FROM Applications WHERE status != 'DENIED'")
        applications = mycursor.fetchall()
        mydb.commit()
        return applications
    else:
        mycursor.execute("SELECT * FROM Applications WHERE groupID = %s AND status != 'DENIED'", (groupID,))
        applications = mycursor.fetchall()
        mydb.commit()
        return applications
def getApplicationsDenied(groupID):
    mycursor.execute("USE FletTutorAppUsers")
    if groupID == None:
        mycursor.execute("SELECT * FROM Applications WHERE status = 'DENIED'")
        applications = mycursor.fetchall()
        mydb.commit()
        return applications
    else:
        mycursor.execute("SELECT * FROM Applications WHERE groupID = %s AND status = 'DENIED'", (groupID,))
        applications = mycursor.fetchall()
        mydb.commit()
        return applications
def pergeOldDenies(groupID):
    mycursor.execute("USE FletTutorAppUsers")
    mycursor.execute("DELETE FROM Applications WHERE groupID = %s AND status = 'DENIED'", (groupID,))
    mydb.commit()
def addTimeSlot(groupID, timeSlot, userOAUTH):
    mycursor.execute("USE FletTutorAppUsers")
    mycursor.execute("SELECT * FROM timeSlots")
    rowNumber = len(mycursor.fetchall())
    mycursor.execute("INSERT INTO timeSlots (timeSlotID, groupID, timeSlot, userOAUTH) VALUES (%s, %s, %s, %s)", (rowNumber, groupID, timeSlot, userOAUTH))
    mydb.commit()
def getTimeSlots(groupID):
    mycursor.execute("USE FletTutorAppUsers")
    mycursor.execute("SELECT * FROM timeSlots WHERE groupID = %s", (groupID,))
    timeSlots = mycursor.fetchall()
    return timeSlots
def removeTimeSlot(timeSlotID):
    mycursor.execute("USE FletTutorAppUsers")
    mycursor.execute("DELETE FROM timeSlots WHERE timeSlotID = %s", (timeSlotID,))
    mydb.commit()
def addGroupPreferedTimeSlot(groupID, timeSlot):
    mycursor.execute("USE FletTutorAppUsers")
    mycursor.execute("SELECT * FROM groupPreferedTimeSlots")
    #overwrite timeSlot if it already exists
    mycursor.execute("SELECT * FROM groupPreferedTimeSlots WHERE groupID = %s", (groupID,))
    if mycursor.fetchone() != None:
        mycursor.execute("DELETE FROM groupPreferedTimeSlots WHERE groupID = %s", (groupID,))
    mycursor.execute("SELECT * FROM groupPreferedTimeSlots")
    rowNumber = len(mycursor.fetchall())
    mycursor.execute("INSERT INTO groupPreferedTimeSlots (timeSlotID, groupID, timeSlot) VALUES (%s, %s, %s)", (rowNumber, groupID, timeSlot))
    mydb.commit()
def getGroupPreferedTimeSlots(groupID):
    mycursor.execute("USE FletTutorAppUsers")
    mycursor.execute("SELECT * FROM groupPreferedTimeSlots WHERE groupID = %s", (groupID,))
    timeSlots = mycursor.fetchall()
    return timeSlots
def removeGroupPreferedTimeSlot(timeSlotID):
    mycursor.execute("USE FletTutorAppUsers")
    mycursor.execute("DELETE FROM groupPreferedTimeSlots WHERE timeSlotID = %s", (timeSlotID,))
    mydb.commit()
def addUserTimeSlotApplyingFor(groupID, timeSlot, userOAUTH):
    mycursor.execute("USE FletTutorAppUsers")
    mycursor.execute("SELECT * FROM userTimeSlotsApplyingFor")
    #overwrite timeSlot if it already exists
    mycursor.execute("SELECT * FROM userTimeSlotsApplyingFor WHERE groupID = %s", (groupID,))
    if mycursor.fetchone() != None:
        mycursor.execute("DELETE FROM userTimeSlotsApplyingFor WHERE groupID = %s", (groupID,))
    mycursor.execute("SELECT * FROM userTimeSlotsApplyingFor")
    rowNumber = len(mycursor.fetchall())
    mycursor.execute("INSERT INTO userTimeSlotsApplyingFor (timeSlotID, groupID, timeSlot, userOAUTH) VALUES (%s, %s, %s, %s)", (rowNumber, groupID, timeSlot, userOAUTH))
    mydb.commit()
def getUserTimeSlotsApplyingFor(groupID, userOAUTH):
    mycursor.execute("USE FletTutorAppUsers")
    mycursor.execute("SELECT * FROM userTimeSlotsApplyingFor WHERE groupID = %s AND userOAUTH = %s", (groupID, userOAUTH))
    timeSlots = mycursor.fetchall()
    return timeSlots
def isGroupOwner(groupID, userOAUTH):
    mycursor.execute("USE FletTutorAppUsers")
    mycursor.execute("SELECT * FROM Groupss WHERE groupID = %s AND groupOwner = %s", (groupID, userOAUTH))
    group = mycursor.fetchone()
    if group == None:
        return False
    else:
        return True
def addUserTimeSlotsAssigned(groupID, timeSlot, userOAUTH):
    mycursor.execute("USE FletTutorAppUsers")
    mycursor.execute("SELECT * FROM userTimeSlotsHas")
    #overwrite timeSlot if it already exists
    mycursor.execute("SELECT * FROM userTimeSlotsHas WHERE groupID = %s", (groupID,))
    if mycursor.fetchone() != None:
        mycursor.execute("DELETE FROM userTimeSlotsHas WHERE groupID = %s", (groupID,))
    mycursor.execute("SELECT * FROM userTimeSlotsHas")
    rowNumber = len(mycursor.fetchall())
    mycursor.execute("INSERT INTO userTimeSlotsHas (timeSlotID, groupID, timeSlot, userOAUTH) VALUES (%s, %s, %s, %s)", (rowNumber, groupID, timeSlot, userOAUTH))
    mydb.commit()
def getUserTimeSlotsAssigned(groupID, userOAUTH):
    mycursor.execute("USE FletTutorAppUsers")
    mycursor.execute("SELECT * FROM userTimeSlotsHas WHERE groupID = %s AND userOAUTH = %s", (groupID, userOAUTH))
    timeSlots = mycursor.fetchall()
    return timeSlots



