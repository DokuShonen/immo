"""Images des proprietes et formatage de l'affichage."""
import base64
import functools
import os
import re

from utils.database import DatabaseError, db_manager

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
UPLOAD_DIR = os.path.join(BASE_DIR, "uploads", "properties")

# Photographies stables (Unsplash CDN) par type de bien.
TYPE_IMAGES = {
    "Appartement": [
        ("photo-1523217582562-09d0def993a6", "appartement"),
        ("photo-1502672260266-1c1ef2d93688", "appartement"),
        ("photo-1600607687939-ce8a6c25118c", "interieur"),
    ],
    "Maison": [
        ("photo-1560518883-ce09059eeffa", "maison"),
        ("photo-1568605114967-8130f3a36994", "maison"),
        ("photo-1580587771525-78b9dba3b914", "maison"),
    ],
    "Bureau": [
        ("photo-1497366811353-6870744d04b2", "bureau"),
        ("photo-1497366216548-37526070297c", "bureau"),
    ],
    "Commercial": [
        ("photo-1441986300917-64674bd600d8", "commerce"),
        ("photo-1447958374760-1ce70cf11ee3", "commerce"),
    ],
    "Terrain": [
        ("photo-1500382017468-9049fed747ef", "terrain"),
        ("photo-1466692476868-aef1dfb1e735", "terrain"),
    ],
}

DEFAULT_IMAGES = ["photo-1564013799919-ab600027ffc6", "photo-1570129477492-45c003edd2be"]

EXTENSIONS_AUTORISEES = (".png", ".jpg", ".jpeg", ".webp", ".avif")


def _img_url(photo_id, w=900):
    return (
        f"https://images.unsplash.com/{photo_id}"
        f"?auto=format&fit=crop&w={w}&q=62&sat=-12"
    )


def _nom_sur(nom_original):
    """Nom de fichier sur : seuls les caracteres alphanumeriques sont
    conserves, ce qui supprime toute tentative de traversee de repertoire
    et les espaces qui casseraient l'URL."""
    base = os.path.basename(nom_original or "")
    extension = os.path.splitext(base)[1].lower()
    if extension not in EXTENSIONS_AUTORISEES:
        extension = ".jpg"
    rafraichir = re.sub(r"[^A-Za-z0-9_-]+", "-", os.path.splitext(base)[0]).strip("-")
    if not rafraichir:
        rafraichir = "photo"
    return rafraichir[:60] + extension


@functools.lru_cache(maxsize=256)
def _data_uri(chemin, modification):
    """Transforme un fichier image en URL de donnees, exploitable par le
    navigateur dans un attribut src."""
    try:
        with open(chemin, "rb") as f:
            contenu = f.read()
    except OSError:
        return None
    extension = os.path.splitext(chemin)[1].lower().lstrip(".")
    mime = {"jpg": "jpeg", "jpeg": "jpeg", "png": "png", "webp": "webp",
            "avif": "avif"}.get(extension, "jpeg")
    return f"data:image/{mime};base64," + base64.b64encode(contenu).decode("ascii")


def get_uploaded_images(property_id):
    """Chemins des images uploadees d'une propriete, d'apres la table
    property_images, avec repli sur le contenu du dossier."""
    if not property_id:
        return []
    chemins = []
    try:
        result = db_manager.execute_query(
            "SELECT image_path FROM property_images WHERE property_id = %s ORDER BY id",
            (property_id,),
            fetch='all',
        )
        chemins = [r['image_path'] for r in result] if result else []
    except DatabaseError:
        chemins = []

    if chemins:
        return chemins

    prop_dir = os.path.join(UPLOAD_DIR, str(property_id))
    if not os.path.isdir(prop_dir):
        return []
    fichiers = sorted(
        f for f in os.listdir(prop_dir)
        if f.lower().endswith(EXTENSIONS_AUTORISEES)
    )
    return [os.path.join(prop_dir, f) for f in fichiers]


def save_image_set(property_id, uploaded_files):
    """Enregistre les images d'une propriete : sur le disque et en base."""
    if not uploaded_files:
        return []

    prop_dir = os.path.join(UPLOAD_DIR, str(property_id))
    os.makedirs(prop_dir, exist_ok=True)
    ecrits = []

    for i, f in enumerate(uploaded_files):
        nom = f"{i}_{_nom_sur(f.name)}"
        chemin = os.path.join(prop_dir, nom)
        try:
            with open(chemin, "wb") as out:
                out.write(f.getbuffer())
        except OSError:
            continue
        ecrits.append(chemin)

    for chemin in ecrits:
        try:
            db_manager.execute_query(
                "INSERT INTO property_images (property_id, image_path) VALUES (%s, %s)",
                (property_id, chemin),
            )
        except DatabaseError:
            pass

    return ecrits


def property_image_uri(prop, index=0):
    """Image principale d'une propriete, pretee a etre placee dans un src.

    Les images importees sont servies en URL de donnees : le navigateur
    peut les afficher, ce qu'un chemin de fichier local ne permettait pas.
    """
    identifiant = prop['id'] if isinstance(prop, dict) else prop[0]
    type_bien = prop.get('type_bien') if isinstance(prop, dict) else (prop[4] if len(prop) > 4 else None)
    type_bien = type_bien or "Maison"

    importees = get_uploaded_images(identifiant)
    if importees and index < len(importees):
        chemin = importees[index]
        try:
            uri = _data_uri(chemin, os.path.getmtime(chemin))
        except OSError:
            uri = None
        if uri:
            return uri

    pool = TYPE_IMAGES.get(type_bien, DEFAULT_IMAGES)
    photo_id, _ = pool[(identifiant + index) % len(pool)]
    return _img_url(photo_id)


def fmt_prix(value):
    """680000.0 -> '680 000 EUR'."""
    if value is None:
        return "-"
    try:
        n = abs(float(value))
        if n == 0:
            return "0 EUR"
        s = f"{n:,.0f}".replace(",", " ")
        return f"{s} EUR"
    except (TypeError, ValueError):
        return "-"


# Ancien nom conserve pour les appels existants.
fmt_fcfa = fmt_prix


def prix_affichage(prop):
    """Prix formate selon le type de transaction (vente ou location)."""
    valeur = fmt_prix(prop['prix'] if isinstance(prop, dict) else prop[9])
    transaction = prop.get('transaction_type') if isinstance(prop, dict) else prop[6]
    if transaction == "location":
        return f"{valeur}<span class='prop-chip-mini'>/mois</span>"
    return valeur
