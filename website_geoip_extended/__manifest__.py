{
    'name': "Bemade Custom Module",
    'version': "17.0.0.1.0",
    'summary': "Module personnalisé pour Bemade Inc",
    'sequence': 10,
    'description': """
    Ce module personnalisé est développé pour étendre les fonctionnalités de base d'Odoo.
    
    Fonctionnalités:
    - Ajout de champs supplémentaires pour collecter plus d'informations sur le visiteur
    - Logger les informations de la requête
    - Obtenez les données de GeoIP et d'autres sources
    - Mise à jour du visiteur avec les nouvelles données
    """,
    'category': 'Tools',
    'author': "Benoit",
    'website': "https://bemade.org",
    'license': 'AGPL-3',
    'depends': [
        'base',
        'website',  # Ajoutez d'autres dépendances si nécessaire
    ],
    'data': [
        # Liste des fichiers de données XML ou CSV, par exemple:
        # 'views/templates.xml',
        # 'security/ir.model.access.csv',
        'views/website_visitor_views.xml',
    ],
    'demo': [
        # Fichiers de données de démo, par exemple:
        # 'demo/demo_data.xml',
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
    'external_dependencies': {
        'python': [
            'geoip2'
        ],  # Ajoutez les dépendances Python ici, par exemple ['pandas']
    },
}
