import os

import flet as ft
from flet import ElevatedButton, LoginEvent, Page, ButtonStyle, MaterialState
from flet.auth.providers import GitHubOAuthProvider, GoogleOAuthProvider
import json
import dataBaseManager
from io import BytesIO
import qrcode
import base64
from flet import TemplateRoute


ALLOWED_DOMAINS = ["fredonia.edu", "gmail.com"]



def main(page: ft.Page):

    #Used https://www.youtube.com/watch?v=1di08jEJRS8&t=9s
    def morning(s):
        qr = qrcode.make (s)
        buffered = BytesIO()
        # SAVE IMAGE QRCODE TO JPEG OR WHATEVER
        qr.save(buffered,format="JPEG")
        s1 = base64.b64encode(buffered.getvalue())
        resultOfQrCode = s1.decode("utf-8")
        return (resultOfQrCode)

    with open('google_oauth.json') as f:
        data = json.load(f)
        google_client_id = data['web']['client_id']
        google_client_secret = data['web']['client_secret']
    providerG = GoogleOAuthProvider(
        client_id=google_client_id,
        client_secret=google_client_secret,
        redirect_url="http://localhost:8550/oauth_callback",
    )
    provider = GitHubOAuthProvider(
        client_id=os.getenv("GITHUB_CLIENT_ID"),
        client_secret=os.getenv("GITHUB_CLIENT_SECRET"),
        redirect_url="http://13.58.90.158:8550/oauth_callback",
    )
    def Google_login_button_click(e):
        page.login(providerG)

    def logoutAndHideDialog(e):
        page.logout()
        page.dialog.open = False
        page.update()

    notFredonia = ft.AlertDialog(
        title=ft.Text("You must login with a Fredonia email"),
        actions=[
            ft.TextButton("Log Out", on_click=logoutAndHideDialog),
        ],
        )
    def show_notFredonia(e):
        page.dialog = notFredonia
        notFredonia.open = True
        page.update()

    def studentSelection(e):
        e.open = False
        page.go("/student")

    


    def facultySelection(e):
        e.open = False
        page.go("/facultygroups")
        page.update()

    def adminSelection(e):
        e.open = False
        page.go("/admin")

    def appSelection(e):
        e.open = False
        page.go("/app")


    

    accountTypeView = ft.View(
                "/",
                [ft.Row(
        [
        ft.Column([ElevatedButton("Student", on_click=studentSelection),
            ElevatedButton("Group Manager", on_click=facultySelection),
            ElevatedButton("Application Manager", on_click=appSelection),
            ElevatedButton("Admin", on_click=adminSelection),],alignment=ft.MainAxisAlignment.CENTER, 
        horizontal_alignment=ft.CrossAxisAlignment.CENTER)      
        ],
        expand=True,
        alignment=ft.MainAxisAlignment.CENTER,
        vertical_alignment=ft.CrossAxisAlignment.CENTER,
        )
        ]
            )

    
    def on_login(e: LoginEvent):
        if not e.error:
            route_change(page.route)
        if page.auth.user["email"].split("@")[1] not in ALLOWED_DOMAINS:
            page.logout()
            show_notFredonia(e)
            return
        if not dataBaseManager.doesUserExist(page.auth.user.id):
            dataBaseManager.addUser(page.auth.user.id, page.auth.user["email"], page.auth.user["name"].split(" ")[0], page.auth.user["name"].split(" ")[-1])
        
    def on_logout(e):
        route_change(page.route)
        page.update()

    google_icon = ft.Image(src="googleLogo.webp", width=32, height=32, tooltip="Image Tooltip")

    google_login_button = ElevatedButton("Login with Google", on_click=Google_login_button_click, content=ft.Row([google_icon ,ft.Text(value="Login with Google")]), width=200, height=50)
    centered_google_login_button_view = ft.View(
                "/",
                [ft.Row(
        [
        ft.Column([google_login_button],alignment=ft.MainAxisAlignment.CENTER, 
        horizontal_alignment=ft.CrossAxisAlignment.CENTER)      
        ],
        expand=True,
        alignment=ft.MainAxisAlignment.CENTER,
        vertical_alignment=ft.CrossAxisAlignment.CENTER,
        )
        ]
            )
    
    groupNameText = ft.Text()
    userExtraInfo = ft.TextField(multiline=True, label="Extra Info")
    
    
    


    def route_change(route):
        pageToAppend = None
        page.views.clear()
        troute = TemplateRoute(page.route)
        def spawnCreateScheduleView(groupID, mode = "groupOwner", userToView = None):
                #MODES: groupOwner, tutor
                #If userToView is not None, then the schedule will be for that user. In this mode the user will not be able to edit the schedule

                #create a popup that allows the user to create a schedule
                #There should be buttons to change between the monday-sunday schedule
                #you should be able to select empty slots and fill them with a tutor
                #you should be able to select a tutor and remove them from a slot
                #you should be able to save the schedule


                userOAUTH = page.auth.user.id
                if (userToView != None):
                    mode = "tutor"
                    userOAUTH = userToView

                tableOnPage = False

                possibleColors = [ft.colors.GREEN,  ft.colors.BLUE]
                selectionColors = [ft.colors.LIGHT_GREEN_ACCENT, ft.colors.LIGHT_BLUE_ACCENT]
                if userToView != None:
                    selectionColors = [ft.colors.LIGHT_GREEN_ACCENT, ft.colors.LIGHT_GREEN_ACCENT]

                def on_save(e):
                    #save the schedule
                    timeslotString = ""
                    for selectedTimeslot in selectedTimes:
                        timeslotString += str(selectedTimeslot) + ","
                    if (mode == "groupOwner"):
                        dataBaseManager.addGroupPreferedTimeSlot(groupID, timeslotString)
                    elif (mode == "tutor"):
                        dataBaseManager.addUserTimeSlotApplyingFor(groupID, timeslotString, userOAUTH)
                    page.dialog.open = False
                    page.update()
                    pass
                def on_cancel(e):
                    page.dialog.open = False
                    page.update()


                def refreshTimeTable(e):
                    dayTable.columns.clear()
                    dayTable.rows.clear()
                    dayTable.columns.append(ft.DataColumn(ft.Text("Times")))
                    for time in times:
                        dayTable.rows.append(ft.DataRow(cells=[ft.DataCell(ft.Text(time))],on_select_changed=addToSelectedCells, data=times.index(time) + ((days.index(currentDay.value) + 1) * len(times) )))
                    for cell in dayTable.rows:
                        print (selectedTimes)
                        if (str(cell.data) in selectedTimes):
                            cell.selected = True
                    for time in timeSlotsToHighlight:
                        for cell in dayTable.rows:
                            if (str(cell.data) == time[1]):
                                if cell.selected:
                                    cell.color = selectionColors[possibleColors.index(time[0])]
                                else:
                                    cell.color = time[0]
                    if (tableOnPage):
                        dayTable.update()
                def on_day_change(e):
                    currentDay.value = e.control.text
                    refreshTimeTable(None)
                    page.update()
                selectedTimes = []


                timeSlotsToHighlight = []
                #each entry will be a dupel, first color, second time slot

                

                mondayThroughSunday = ft.MenuBar(
                    controls=[
                        ft.TextButton(text="Monday", on_click=on_day_change),
                        ft.TextButton(text="Tuesday", on_click=on_day_change),
                        ft.TextButton(text="Wednesday", on_click=on_day_change),
                        ft.TextButton(text = "Thursday", on_click=on_day_change),
                        ft.TextButton(text = "Friday", on_click=on_day_change),
                        ft.TextButton(text = "Saturday", on_click=on_day_change),
                        ft.TextButton(text = "Sunday", on_click=on_day_change),
                    ],
                )


                

                
                dayTable = ft.DataTable()
                #dayTable settings
                #load previously selected times
                if (mode == "groupOwner"):
                    groupPreferedTimeSlots = dataBaseManager.getGroupPreferedTimeSlots(groupID)
                    if (groupPreferedTimeSlots != None and groupPreferedTimeSlots != [] and groupPreferedTimeSlots[0][2] != None):
                        selectedTimes = groupPreferedTimeSlots[0][2].split(",")
                elif (mode == "tutor"):
                    tutorSelectedTimeSlots = dataBaseManager.getUserTimeSlotsApplyingFor(groupID, userOAUTH)
                    print(tutorSelectedTimeSlots)
                    if (tutorSelectedTimeSlots != None and tutorSelectedTimeSlots != [] and tutorSelectedTimeSlots[0][2] != None):
                        selectedTimes = tutorSelectedTimeSlots[0][2].split(",")
                    groupPreferedTimeSlots = dataBaseManager.getGroupPreferedTimeSlots(groupID)
                    if (groupPreferedTimeSlots != [] and groupPreferedTimeSlots[0][2] != None):
                        for time in groupPreferedTimeSlots[0][2].split(","):
                            timeSlotsToHighlight.append([ft.colors.BLUE, time])



                def addToSelectedCells(e):
                    if userToView != None:
                        return
                    e.control.selected = not e.control.selected
                    if (e.control.selected == True):
                        if (e.control.color in possibleColors):
                            e.control.color = selectionColors[possibleColors.index(e.control.color)]
                        selectedTimes.append(str(e.control.data))
                    else:
                        if (e.control.color in selectionColors):
                            e.control.color = possibleColors[selectionColors.index(e.control.color)]
                        selectedTimes.remove(str(e.control.data))
                    e.control.update()

                

                usersInGroup = ["Times,"]
                days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
                times = ["8:00", "9:00", "10:00", "11:00", "12:00", "1:00", "2:00", "3:00", "4:00", "5:00", "6:00", "7:00", "8:00"]
                colorMeanings = ft.Row(controls=[ft.Text("Green: tutoring"), ft.Text("Red: Unavailable"), ft.Text("Blue: times avaliable for tutoring")])
                currentDay = ft.Text("Monday")

                

                page.dialog = ft.AlertDialog(
                    title=ft.Text("Schedule Creation"),
                    content=ft.Column(controls=[mondayThroughSunday, ft.Row(controls = [currentDay]),ft.Column(controls= [dayTable],expand=True, scroll="adaptive") ,ft.Row(controls=[ft.ElevatedButton("Save", on_click=on_save), ft.ElevatedButton("Cancel", on_click=on_cancel), colorMeanings]),]),
                                      )
                page.dialog.open = True
                refreshTimeTable(None)
                tableOnPage = True
                page.update()


        def applyForGroup(e):
            print(dataBaseManager.createApplication(troute.id,page.auth.user.id, userExtraInfo.value))

            page.go("/")



        if troute.match("/joingroup/:id"):
            if dataBaseManager.doesGroupExist(troute.id):
                groupNameText.value = dataBaseManager.getGroupFromGroupID(troute.id)[1]
                preferedTimesButton = ft.ElevatedButton("Manage Prefered Times", on_click=lambda _: spawnCreateScheduleView(troute.id, "tutor"))

                if (page.auth != None):
                    pageToAppend = ft.View(
                    "/",
                    [   ft.Column([
                        ft.Row([
                            ft.Text("You are signing up for:"), groupNameText,
                        ]),
                        ft.Row([
                            ft.Text("Name: "), ft.Text(page.auth.user["name"]),
                        ]),
                        ft.Row([
                            ft.Text("Email: "), ft.Text(page.auth.user["email"]),
                        ]),
                        ft.Row([
                            ft.Text("Relivent Info: "), userExtraInfo,
                        ]),
                        ft.Row([
                            preferedTimesButton,
                        ]),
                        ft.Row([
                            ft.Text("Please note that the group manager will be able to see this information"),
                        ]),
                        ft.Row([
                            ft.ElevatedButton("Apply for Group", on_click=applyForGroup),
                        ]),
                    ]),
                    ],
                )
            else:
                page.go("/")
        elif troute.match("/scheduleDesigner/:id"):
            if dataBaseManager.doesGroupExist(troute.id):
                #column 1" Times. Rows are the times
                #BUTTON TEMPLET
                preferedTimeSlots = dataBaseManager.getGroupPreferedTimeSlots(troute.id)
                rowOfTimes = ft.Column()
                
                scheduleDisplay = ft.Row(
                    controls=[
                        ft.Column(controls=[
                            rowOfTimes,

                        ],
                        ),

                    ],
                )
                days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
                times = ["8:00", "9:00", "10:00", "11:00", "12:00", "1:00", "2:00", "3:00", "4:00", "5:00", "6:00", "7:00", "8:00"]
                for time in times:
                    rowOfTimes.controls.append(ft.Row(controls = [ft.Text(time)]))
                usersInGroup = dataBaseManager.getGroupMembers(troute.id)
                def spawnScheduleButton(studentID, timeSlot):
                    textTypes = [" ", "Available", "Assigned"]
                    textColors = [ft.colors.WHITE, ft.colors.BLUE, ft.colors.GREEN]
                    text = timeSlot
                    return ft.ElevatedButton(text, on_click=lambda _: print("Clicked"), data = studentID)
                def makeRowOfUserButtons(studentID):
                    preferedUserTimes = dataBaseManager.getUserTimeSlotsApplyingFor(troute.id, studentID)
                    row = []
                    for times in scheduleDisplay.controls[0].controls:
                        for time in times.controls:
                            time.controls.append(spawnScheduleButton(studentID, ""))
                    return row
                def refreshSchedule(e):
                    if (e == None):
                        dayToSwitchTo = "Monday"
                    else: dayToSwitchTo = e.control.text
                    firstDay = 13
                    for day in days:
                        if (day == dayToSwitchTo):
                            firstDay = days.index(day) * len(times)
                    page.update()
                    
                for user in usersInGroup:
                    makeRowOfUserButtons(user[2])
                

                

                groupNameText.value = dataBaseManager.getGroupFromGroupID(troute.id)[1]
                pageToAppend = ft.View(
                    "/",
                    [   ft.Column([
                        ft.Row([
                            ft.Text("You are managing the schedule for:"), groupNameText,
                        ]),
                        scheduleDisplay,
                    ]),
                    ],
                )
                refreshSchedule(None)
            else:
                page.go("/")
            

        def hideDialog(e):
            page.dialog.open = False
            page.update()
        def downloadQRCode(e):
            #Do in the future
            pass
        def generateGroupJoinLink(e):
            link = "http://localhost:8550/joingroup/" + getCurrentGroup()
            #generate QR code
            page.dialog = ft.AlertDialog(
                title=ft.Text("Group Join Link"),
                content= ft.Column([ft.Text(link, selectable=True), ft.Image(src_base64=morning(link))]),
                actions=[
                    ft.ElevatedButton(
                        text="Ok",
                        on_click=hideDialog,
                    ),
                ],
            )
            page.dialog.open = True
            page.update()


        if (page.auth == None):
            pageToAppend = centered_google_login_button_view
        else: 
            if (pageToAppend == None):
                pageToAppend = accountTypeView
        page.views.append(
            pageToAppend
        )
        if page.route == "/facultygroups":  
            if (page.auth == None):
                page.go("/")
            def getCurrentGroup():
                groupsToDisplay = dataBaseManager.getGroups(page.auth.user.id)
                index = GroupViewRail.selected_index
                if (index == -1):
                    return None
                return groupsToDisplay[index][0]
            def spawnGroupUserAdd(e):
                email = ft.TextField()
                def handle_clickReopen(event):
                    page.dialog.open = False
                    spawnGroupUserAdd(event)
                def on_click(e):
                    groupsToDisplay = dataBaseManager.getGroups(page.auth.user.id)
                    index = GroupViewRail.selected_index
                    if (index == -1):
                        page.dialog.open = False
                        page.update()
                        return
                    groupID = groupsToDisplay[index][0]
                    results = dataBaseManager.addUserToGroup(email.value, groupID)
                    refreshGroupMembersTable(None)

                    if (results != True):
                        page.dialog = ft.AlertDialog(
                            title=ft.Text(results),
                            actions=[
                                ft.ElevatedButton(
                                    text="Ok",
                                    on_click = handle_clickReopen,
                                ),
                            ],
                        )
                        page.dialog.open = True
                        page.update()
                        groupMembersTable.update()

                        return

                    page.dialog.open = False
                    populateGroupView(None)
                    page.update()

                def on_click2(e):
                    page.dialog.open = False
                    page.update()

                page.dialog = ft.AlertDialog(
                    title=ft.Text("Enter User Email"),
                    content=email,
                    actions=[
                        ft.ElevatedButton(
                            text="Add User",
                            on_click=on_click,
                        ),
                        ft.ElevatedButton(text="Cancel", on_click=on_click2),
                    ],
                )
                page.dialog.open = True
                page.update()


            def changeGroupName(e):
                groupsToDisplay = dataBaseManager.getGroups(page.auth.user.id)
                index = GroupViewRail.selected_index
                dataBaseManager.changeGroupName(groupsToDisplay[index][0], textFieldGroupName.value)
                populateGroupView(None)
                refreshGroupMembersTable(None)



            def initiateUserDeletion(e):
                groupMembersTable.show_checkbox_column = True
                groupMembersTable.update()
                e.control.text = "Confirm Deletion"
                e.control.on_click = finilaizeUserDeletion
                e.control.update()

            def finilaizeUserDeletion(e):
                for row in groupMembersTable.rows:
                    if (row.selected == True):
                        print(dataBaseManager.removeUserFromGroup(row.cells[0].content.value, getCurrentGroup()))
                groupMembersTable.show_checkbox_column = False
                for row in groupMembersTable.rows:
                    row.selected = False
                groupMembersTable.update()
                e.control.text = "Remove User from Group"
                e.control.on_click = initiateUserDeletion
                e.control.update()
                refreshGroupMembersTable(None)
            def selectAllInTable(e):
                amountNotSelected = 0
                for row in groupMembersTable.rows:
                    if (row.selected == False):
                        amountNotSelected += 1
                if (amountNotSelected == 0):
                    for row in groupMembersTable.rows:
                        row.selected = False
                else:
                    for row in groupMembersTable.rows:
                        row.selected = True

                groupMembersTable.update()
            
            groupMembersTable = ft.DataTable(
                columns=[
                    ft.DataColumn(ft.Text("Email")),
                    ft.DataColumn(ft.Text("First Name")),
                    ft.DataColumn(ft.Text("Last Name")),
                ],
                on_select_all=selectAllInTable,
                
                
            )

            
            textFieldGroupName = ft.TextField()
            buttonSaveName = ft.ElevatedButton("Save Name", on_click=changeGroupName) 
            groupModificationRow = ft.Column(
                controls=
                [
                    ft.Row([ft.Text("Group Name"), textFieldGroupName, buttonSaveName]),
                    ft.Row([groupMembersTable]),
                    ft.Row([ft.ElevatedButton("Add User to Group", on_click=spawnGroupUserAdd), ft.ElevatedButton("Remove User from Group" , on_click=initiateUserDeletion)]),
                    ft.Row([ft.ElevatedButton("Generate Invites", on_click=generateGroupJoinLink), ft.ElevatedButton("Delete Group")]),
                ]
            )
            def itemSelectionChanged(e):
                e.control.selected = not e.control.selected
                e.control.update()

            def refreshGroupMembersTable(e):
                groupMembersTable.rows.clear()
                groupMembers = dataBaseManager.getGroupMembers(getCurrentGroup())
                if (groupMembers != None):
                    for member in groupMembers:
                        memberInfo = dataBaseManager.getUserFromOAUTH(member[2])
                        groupMembersTable.rows.append(ft.DataRow(cells=[ft.DataCell(ft.Text(memberInfo[1],), ), ft.DataCell(ft.Text(memberInfo[2])), ft.DataCell(ft.Text(memberInfo[3]))], on_select_changed=itemSelectionChanged))
                groupMembersTable.update()
                page.update()

            def pullUpData(e):
                if (e == None):
                    groupModificationRow.visible = False
                    return
                if (e.control.selected_index == None):
                    groupModificationRow.visible = False
                    return
                else: 
                    if (e.control.selected_index == -1):
                        groupModificationRow.visible = False
                        return
                    
                groupModificationRow.visible = True
                groupsToDisplay = dataBaseManager.getGroups(page.auth.user.id)
                index = e.control.selected_index
                groupData = dataBaseManager.getGroupFromGroupID(groupsToDisplay[index][0])
                groupMembers = dataBaseManager.getGroupMembers(groupsToDisplay[index][0])
                textFieldGroupName.value = groupData[1]
                groupMembersTable.rows.clear()



                
                            
                
                if (groupMembers != None):
                    for member in groupMembers:
                        memberInfo = dataBaseManager.getUserFromOAUTH(member[2])
                        groupMembersTable.rows.append(ft.DataRow(cells=[ft.DataCell(ft.Text(memberInfo[1],), ), ft.DataCell(ft.Text(memberInfo[2])), ft.DataCell(ft.Text(memberInfo[3]))], on_select_changed=itemSelectionChanged))
                groupMembersTable.update()
                page.update()
 
                
            
            def spawnGroupNaming(e):
                name = ft.TextField()
                def on_click(e):
                    dataBaseManager.makeGroup(name.value, page.auth.user.id)
                    page.dialog.open = False
                    populateGroupView(None)
                    page.update()

                def on_click2(e):
                    page.dialog.open = False
                    page.update()

                page.dialog = ft.AlertDialog(
                    title=ft.Text("Enter Group Name"),
                    content=name,
                    actions=[
                        ft.ElevatedButton(
                            text="Create Group",
                            on_click=on_click,
                        ),
                        ft.ElevatedButton(text="Cancel", on_click=on_click2),
                    ],
                )
                page.dialog.open = True
                page.update()
            
            def populateGroupView(e):
                groupsToDisplay = dataBaseManager.getGroups(page.auth.user.id)
                
                GroupViewRail.destinations.clear()


                if (len(groupsToDisplay) == 0):
                    page.update()
                    return
                for group in groupsToDisplay:
                    GroupViewRail.destinations.append(ft.NavigationRailDestination(label=group[1], icon=ft.icons.GROUP))
                page.update()
            
            GroupViewRail = ft.NavigationRail(expand=True)
            Trailing=ft.FloatingActionButton(icon=ft.icons.CREATE, text="Add New Group", on_click=spawnGroupNaming)
            GroupViewRail.trailing=Trailing

            def deleteGroup(e):
                groupsToDisplay = dataBaseManager.getGroups(page.auth.user.id)
                index = GroupViewRail.selected_index
                dataBaseManager.deleteGroup(groupsToDisplay[index][0])
                pullUpData(None)
                populateGroupView(e)

            pullUpData(None)
            GroupViewRail.on_change = pullUpData
            
            deleteGroupButton = ft.ElevatedButton("Delete Group", on_click=deleteGroup)

            def manageScheduleOnClick(e):
                spawnCreateScheduleView(getCurrentGroup())

            manageSchedule = ft.ElevatedButton("Create/Change Group Prefered Schedule", on_click=manageScheduleOnClick)
            manageTutorSchedule = ft.ElevatedButton("Launch Tutor Schedule Maker", on_click=lambda _: page.go("/scheduleDesigner/" + getCurrentGroup()))

            pageRow=ft.Row(
                [
                    GroupViewRail,
                    ft.VerticalDivider(width=1),
                    deleteGroupButton,
                    ft.Column([groupModificationRow], alignment=ft.MainAxisAlignment.START, expand=True),
                    manageSchedule,
                    manageTutorSchedule,
                    
                ],
            expand=True,
                )
            facultyView = ft.View(
                                    "/facultygroups",
                                    [

                                        pageRow,
                                    ],
                                )
            

            groupModificationRow.visible = False
            populateGroupView(None)
            page.views.append(facultyView)
        if page.route == "/app":
            groupsToDisplay = dataBaseManager.getGroups(page.auth.user.id)
            if (len(groupsToDisplay) == 0):
                page.views.append(ft.View(
                    "/app",
                    [
                        ft.Column([ft.Text("There are no applications to review")]),
                        ft.ElevatedButton("Go Back", on_click=lambda _: page.go("/")),
                    ],
                ))
                page.update()
                return
            else:
                expansionTilesToSpawn = []
                for group in groupsToDisplay:
                    expansionTilesToSpawn.append(ft.ExpansionTile(
                    title=ft.Text("Group: " + group[1]),
                    subtitle=ft.Text("Applications to review: " + str(len(dataBaseManager.getApplicationsNotDenied(group[0])))),
                    affinity=ft.TileAffinity.LEADING,
                    initially_expanded=True,
                    collapsed_text_color=ft.colors.BLUE,
                    text_color=ft.colors.BLUE,
                    controls=[
                    ],
                ),)
                def acceptApplication(userID, groupID, group):

                    dataBaseManager.acceptApplication(userID, groupID)
                    expansionTilesToSpawn.remove(group)
                    page.update()
                    
                for group in expansionTilesToSpawn:
                    for application in dataBaseManager.getApplicationsNotDenied(groupsToDisplay[expansionTilesToSpawn.index(group)][0]):
                        userData = dataBaseManager.getUserFromOAUTH(application[2])
                        if (userData == None):
                            print("User not found")
                        else:
                            group.controls.append(ft.Column([ft.Text("Name: " + userData[2] + " " + userData[3]), ft.Text("Email: " + userData[1]), ft.Text("Application: " + application[3])]))
                            group.controls.append(ft.Row([ft.ElevatedButton("View Schedule", on_click=lambda _: spawnCreateScheduleView(groupsToDisplay[expansionTilesToSpawn.index(group)][0], "groupOwner", userData[0]))]))
                            group.controls.append(ft.Row([ft.ElevatedButton("Accept", on_click=lambda _: acceptApplication(userData[0],application[1], group)), ft.ElevatedButton("Deny", on_click=lambda _: dataBaseManager.denyApplication(userData[0], application[1]))]))
                    amountDenied = len(dataBaseManager.getApplicationsDenied(groupsToDisplay[expansionTilesToSpawn.index(group)][0]))
                    if (amountDenied > 0):
                        def pergeOldDenys(e):
                            dataBaseManager.pergeOldDenies(e.control.data)
                            e.control.visible = False
                            e.control.update()
                        group.controls.append(ft.ElevatedButton("Perge Old Denies ("+ str(amountDenied) + ")",data=groupsToDisplay[expansionTilesToSpawn.index(group)][0], on_click=pergeOldDenys))
                page.views.append(ft.View(
                    "/app",
                    [
                        ft.Column(expansionTilesToSpawn),
                        ft.ElevatedButton("Go Back", on_click=lambda _: page.go("/")),
                    ],
                ))
        if page.route == "/student":
            expansionTilesToSpawn = []
            #We will grab all the groups the user is in, and then we will grab all the applications for other groups
            groupsToDisplay = dataBaseManager.getGroupsUserIsIn(page.auth.user.id)
            for group in groupsToDisplay:
                expansionTilesToSpawn.append(ft.ExpansionTile(
                    title=ft.Text("Group: " + dataBaseManager.getGroupFromGroupID(group[1])[1]),
                    subtitle=ft.Text(""),
                    affinity=ft.TileAffinity.LEADING,
                    initially_expanded=True,
                    collapsed_text_color=ft.colors.BLUE,
                    text_color=ft.colors.BLUE,
                    controls=[
                    ],
                ),)
            applicationsFromUser = dataBaseManager.getApplicationsFromUser(page.auth.user.id)
            #Seperate into applications that are accepted and denied
            pendingApplications = []
            deniedApplications = []
            for application in applicationsFromUser:
                if (application[3] == "DENIED"):
                    deniedApplications.append(application)
                else:
                    pendingApplications.append(application)
            for pendingApp in pendingApplications:
                expansionTilesToSpawn.append(ft.ExpansionTile(
                    title=ft.Text("Application to: " + dataBaseManager.getGroupFromGroupID(pendingApp[1])[1]),
                    subtitle=ft.Text("Status: " + pendingApp[3]),
                    affinity=ft.TileAffinity.LEADING,
                    initially_expanded=True,
                    collapsed_text_color=ft.colors.BLUE,
                    text_color=ft.colors.BLUE,
                    controls=[
                    ],
                ),)
            for deniedApp in deniedApplications:
                expansionTilesToSpawn.append(ft.ExpansionTile(
                    title=ft.Text("Application to: " + dataBaseManager.getGroupFromGroupID(deniedApp[1])[1]),
                    subtitle=ft.Text("Status: " + deniedApp[3]),
                    affinity=ft.TileAffinity.LEADING,
                    initially_expanded=True,
                    collapsed_text_color=ft.colors.BLUE,
                    text_color=ft.colors.BLUE,
                    controls=[
                    ],
                ),)
            page.views.append(ft.View(
                    "/student",
                    [
                        ft.Column(expansionTilesToSpawn),
                        ft.ElevatedButton("Go Back", on_click=lambda _: page.go("/")),
                    ],
                ))

                

                
                

        page.update()

    def view_pop(view):
        page.views.pop()
        top_view = page.views[-1]
        page.go(top_view.route)

    page.on_login = on_login
    page.on_logout = on_logout
    page.on_route_change = route_change
    page.on_view_pop = view_pop
    page.go(page.route)


    
ft.app(target=main, port=8550, view=ft.WEB_BROWSER, assets_dir="assets")