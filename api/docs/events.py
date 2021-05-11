

class EventsDocs:
    common = """
# EVENTS
Endpoint para los eventos de la agenda. El objeto Event, al igual que 
Article y Subscription hereda de Item, por lo que comparten numeración única 
de ids. Es decir, un Article un Event y una Subscription nunca pueden 
compartir un mismo id. Lo mismo ocurre con las Variants que tienen tanto 
Article como Event y Subscription. 
"""
