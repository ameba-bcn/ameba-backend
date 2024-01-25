import api.models as models

members = models.Member.objects.all()

membership = members[0].get_newest_membership()


member = members[0]
if 'pro' in member.type.lower():
    if '2023' in member.expires:
        pass
    elif '2024' in member.expires:
        pass
    elif '2025' in member.expires:
        pass


elif 'sup' in member.type.lower():
    pass

elif 'soc' in member.type.lower():
    pass