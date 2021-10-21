from background_task import background


@background(schedule=0)
def notify_member_about_to_expire():
    pass


@background(schedule=0)
def notify_member_expired():
    pass


@background(schedule=0)
def notify_event_reminder():
    pass

