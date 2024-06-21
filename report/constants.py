def sprint_status_color(status: str):
    if status == "active":
        return ("bg-green-300", "text-green-800")
    elif status == "closed":
        return ("bg-red-300", "text-red-800")
    else:
        return ("bg-gray-300", "text-gray-800")


def issue_status_color(status: str):
    if status == "Backlog" or status == "Prepared":
        return ("bg-gray-300", "text-gray-800")
    elif status == "In Progress" or status == "Coding Done" or status == "In Testing":
        return ("bg-blue-300", "text-blue-800")
    elif status == "Done":
        return ("bg-green-300", "text-green-800")
    else:
        return ("bg-gray-300", "text-gray-800")


def issue_status_label(status: str):
    if status == "Backlog" or status == "Prepared":
        return "To Do"
    elif status == "In Progress" or status == "Coding Done" or status == "In Testing":
        return "In Progress"
    elif status == "Done":
        return "Done"
    else:
        return "Unknown"


def epic_color_map(jira_epic_color: str):
    if jira_epic_color == "green":
        return "bg-green-300"
    elif jira_epic_color == "blue":
        return "bg-blue-300"
    elif jira_epic_color == "yellow":
        return "bg-yellow-300"
    elif jira_epic_color == "purple":
        return "bg-purple-300"
    elif jira_epic_color == "teal":
        return "bg-cyan-300"
    elif jira_epic_color == "orange":
        return "bg-red-300"
    elif jira_epic_color == "gray":
        return "bg-gray-300"
    elif jira_epic_color == "dark_green":
        return "bg-green-500"
    elif jira_epic_color == "dark_blue":
        return "bg-blue-500"
    elif jira_epic_color == "dark_yellow":
        return "bg-yellow-500"
    elif jira_epic_color == "dark_purple":
        return "bg-purple-500"
    elif jira_epic_color == "dark_teal":
        return "bg-cyan-500"
    elif jira_epic_color == "dark_orange":
        return "bg-red-500"
    elif jira_epic_color == "dark_gray":
        return "bg-gray-500"
    else:
        return "bg-gray-300"
