from background_task import background


@background(schedule=0)
def schedule_reminders(membership):
    pass
