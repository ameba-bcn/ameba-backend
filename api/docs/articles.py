

class ArticlesDocs:
    common = """
# ARTICLES
Endpoint para los artículos de la botiga. El objeto Article, al igual que 
Event y Subscription hereda de Item, por lo que comparten numeración única 
de ids. Es decir, un Article un Event y una Subscription nunca pueden 
compartir un mismo id. Lo mismo ocurre con las Variants que tienen tanto 
Article como Event y Subscription. 
"""
