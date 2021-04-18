

class CoversDocs:
    common = """
# COVERS

Endpoint para obtener los visuales de la portada. Se devuelven ordenados según
los index configurados en el admin panel, de menor index a mayor. Si hay dos 
index iguales se ordena por fecha, de más reciente a más antiguo.

Sólo se devuelven las portadas marcadas como ```is_active=True``` en el 
admin panel. 
"""
