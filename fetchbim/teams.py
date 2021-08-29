import pymsteams

from fetchbim.settings import TEAMS_WEBHOOK


def sync_complete_msg(new_families_count=0, updated_families_count=0, send=True):
    message = pymsteams.connectorcard(TEAMS_WEBHOOK)
    message.title("Notion Family Sync")
    message.text(
        "Notion Content Calendar has successfully been synced with the admin database"
    )
    message.addLinkButton(
        "Content Calendar",
        "https://www.notion.so/fetchbim/f56ac916a3f049dda2df0f864ca63c62",
    )
    message.color("#4cb6ab")

    message_section = pymsteams.cardsection()
    if updated_families_count > 0:
        message_section.title("Sync Results")
        message_section.addFact("Updated Families:", updated_families_count)
    if new_families_count > 0:
        message_section.addFact("New Families:", new_families_count)
    if updated_families_count + new_families_count > 0:
        message_section.addFact("Total:", updated_families_count + new_families_count)
    message.addSection(message_section)
    if send:
        message.send()
    else:
        message.printme()


# @dataclass
# class TeamsCard:
#     text: str = ''
#     title: str = None
#     button: tuple = None

#     def __post_init__(self):
#         self.message = pymsteams.connectorcard(TEAMS_WEBHOOK)
#         self.message.text = self.text
#         if self.title:
#             self.message.title = self.title
#         if self.button:
#             self.message.addLinkbutton = self.button

#     def send(self):
#         self.message.send()

#     def preview(self):
#         self.message.printme()
