import flet as ft
from flet import ElevatedButton, Page
import dataBaseManager


class Group:
    GroupViewRail = ft.NavigationRail(expand=True)
    groupsToDisplay = None

    def __init__(e):

        Trailing=ft.FloatingActionButton(icon=ft.icons.CREATE, text="Add New Group")
        GroupViewRail.trailing=Trailing

        groupsToDisplay = dataBaseManager.getGroups()
        for group in groupsToDisplay:
            GroupViewRail.destinations.append(ft.NavigationRailDestination(label=group[1], icon=ft.icons.GROUP))

        Group.GroupViewRail.on_change = Group.pullUpData

    pageRow   = ft.Row(
                [
                    GroupViewRail,
                    ft.VerticalDivider(width=1),
                    ft.Column([ ft.Text("Body!")], alignment=ft.MainAxisAlignment.START, expand=True),
                ],
                expand=True,
            )


    facultyView = ft.View(
                        "/faculty",
                        [

                            pageRow,
                            
                        ],
                    )
    
    def pullUpData(e):
        index = e.control.selected_index
        print (Group.groupsToDisplay)
        groupData = dataBaseManager.getGroupFromGroupID(Group.groupsToDisplay[index][0])
        print (groupData)

        

