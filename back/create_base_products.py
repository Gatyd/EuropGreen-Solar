import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'EuropGreenSolar.settings')
django.setup()

from billing.models import Product

def create_base_products():
    base_products = [
        {
            "name": "Panneaux solaires",
            "description": "Panneaux DMEG (ou équivalent)\nDimension : 1950mm x 1134mm x 30mm\nCellule N type\nGarantie 25 ans pièces et rendement",
            "unit_price": 90,
            "type": "panel",
        },
        {
            "name": "Onduleur centralisé Huawei SUN2000-10K-LC0",
            "description": "Garantie 10 ans\nMise à la terre de l'installation photovoltaïque comprise",
            "unit_price": 1550,
            "type": "inverter",
        },
        {
            "name": "Matériel de pose sur toiture en surimposition",
            "description": "Fixations K2 systems\n- Rails aluminium + crochets renforcés\n- Fixation directe sur chevrons\n- Résistance validée aux charges météo\n- Système discret & esthétique",
            "unit_price": 800,
            "type": "structure",
        },
        {
            "name": "Main d'oeuvre",
            "description": "Forfait main d'oeuvre\n- Pose des panneaux et raccordement électrique\n- Mise en service de l'installation\n- Mise en service des applications associées",
            "unit_price": 2500,
            "type": "service",
        },
        {
            "name": "Fourniture d'équipe solaire",
            "description": "kit solaire :\n- Compteur de production\n- Boitier AC/DC\n- Accessoires électriques, câblage",
            "unit_price": 1500,
            "type": "other",
        }
    ]

    for product_data in base_products:
        product, created = Product.objects.get_or_create(
            name=product_data["name"],
            type=product_data["type"],
            unit_price=product_data["unit_price"],
            description=product_data["description"],
        )
        if created:
            print(f"Produit créé: {product.name}")
        else:
            print(f"Produit existant: {product.name}")

if __name__ == "__main__":
    create_base_products()