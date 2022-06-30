import pymsteams

from fetchbim import settings


def sync_complete_msg(
    title="Sync Complete",
    message="Database has successfully been synced",
    button=(None, None),
    send=True,
    table_dict=None,
):
    teams_message = pymsteams.connectorcard(settings.teams_webhook)
    teams_message.title(title)
    teams_message.text(message)
    teams_message.addLinkButton(button[0], button[1])
    teams_message.color("#4cb6ab")
    teams_message_section = pymsteams.cardsection()

    if table_dict:
        for k, v in table_dict.items():
            teams_message_section.addFact(k, v)
        teams_message.addSection(teams_message_section)
    if send:
        teams_message.send()
    else:
        teams_message.printme()
