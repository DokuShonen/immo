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

# Types d'images acceptes, par extension.
MIMES_AUTORISES = {
    "jpg": "image/jpeg",
    "jpeg": "image/jpeg",
    "png": "image/png",
    "webp": "image/webp",
    "avif": "image/avif",
}

# Garde-fous : une annonce ne peut pas remplir la base avec des photos
# trop lourdes ou trop nombreuses.
TAILLE_MAX_IMAGE = 4 * 1024 * 1024
NOMBRE_MAX_IMAGES = 8


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


def _mime_pour(nom):
    extension = os.path.splitext(nom or "")[1].lower().lstrip(".")
    return MIMES_AUTORISES.get(extension, "image/jpeg")


def _source(chemin=None, donnees=None, mime=None, identifiant=None):
    """Description d'une image, qu'elle vienne du disque ou de la base."""
    return {
        "chemin": chemin,
        "donnees": donnees,
        "mime": mime,
        "id": identifiant,
    }


def _uri_source(source):
    """URL de donnees d'une image.

    L'image est d'abord cherchee dans la base : c'est le seul endroit qui
    survit au redemarrage d'une instance cloud. Le disque sert de repli
    pour les photos importees avant cette evolution.
    """
    if not source:
        return None

    donnees = source.get("donnees")
    if donnees:
        mime = source.get("mime") or "image/jpeg"
        return ("data:" + mime + ";base64,"
                + base64.b64encode(donnees).decode("ascii"))

    chemin = source.get("chemin")
    if chemin:
        try:
            return _data_uri(chemin, os.path.getmtime(chemin))
        except OSError:
            return None

    return None


def get_uploaded_images(property_id):
    """Images d'une propriete, d'apres la table property_images, avec
    repli sur le contenu du dossier."""
    if not property_id:
        return []

    sources = []
    try:
        result = db_manager.execute_query(
            "SELECT id, image_path, image_data, mime_type FROM property_images "
            "WHERE property_id = %s ORDER BY id",
            (property_id,),
            fetch='all',
        )
        for row in result or []:
            sources.append(_source(
                chemin=row['image_path'],
                donnees=row['image_data'],
                mime=row['mime_type'],
                identifiant=row['id'],
            ))
    except DatabaseError:
        sources = []

    if sources:
        return sources

    prop_dir = os.path.join(UPLOAD_DIR, str(property_id))
    if not os.path.isdir(prop_dir):
        return []
    fichiers = sorted(
        f for f in os.listdir(prop_dir)
        if f.lower().endswith(EXTENSIONS_AUTORISEES)
    )
    return [_source(chemin=os.path.join(prop_dir, f)) for f in fichiers]


def get_uploaded_images_map(property_ids):
    """Images de plusieurs proprietes en une seule requete.

    Sans cela, chaque carte affichee declenchait une requete vers la base :
    la page prenait autant de requetes que de biens affiches.
    """
    ids = [int(i) for i in property_ids if i]
    if not ids:
        return {}

    try:
        result = db_manager.execute_query(
            "SELECT id, property_id, image_path, image_data, mime_type "
            "FROM property_images WHERE property_id = ANY(%s) ORDER BY id",
            (ids,),
            fetch='all',
        )
    except DatabaseError:
        result = []

    images = {}
    for row in result or []:
        images.setdefault(row['property_id'], []).append(_source(
            chemin=row['image_path'],
            donnees=row['image_data'],
            mime=row['mime_type'],
            identifiant=row['id'],
        ))

    for identifiant in ids:
        if identifiant not in images:
            prop_dir = os.path.join(UPLOAD_DIR, str(identifiant))
            if os.path.isdir(prop_dir):
                fichiers = sorted(
                    f for f in os.listdir(prop_dir)
                    if f.lower().endswith(EXTENSIONS_AUTORISEES)
                )
                if fichiers:
                    images[identifiant] = [
                        _source(chemin=os.path.join(prop_dir, f))
                        for f in fichiers]

    return images


def save_image_set(property_id, uploaded_files):
    """Enregistre les images d'une propriete : en base et sur le disque.

    Les octets sont conserves en base : sur une instance cloud, le disque
    local est efface a chaque redemarrage. Le fichier sur le disque reste
    utile en developpement et pour les annonces importees avant.
    """
    if not uploaded_files:
        return []

    prop_dir = os.path.join(UPLOAD_DIR, str(property_id))
    sources = []

    for i, f in enumerate(list(uploaded_files)[:NOMBRE_MAX_IMAGES]):
        nom = _nom_sur(f.name)
        donnees = None
        try:
            donnees = f.getvalue()
        except Exception:
            try:
                donnees = bytes(f.getbuffer())
            except Exception:
                donnees = None

        if not donnees:
            continue
        if len(donnees) > TAILLE_MAX_IMAGE:
            continue

        chemin = os.path.join(prop_dir, f"{i}_{nom}")
        try:
            os.makedirs(prop_dir, exist_ok=True)
            with open(chemin, "wb") as out:
                out.write(donnees)
        except OSError:
            chemin = ""

        mime = _mime_pour(nom)
        try:
            db_manager.execute_query(
                "INSERT INTO property_images "
                "(property_id, image_path, image_data, mime_type, file_name) "
                "VALUES (%s, %s, %s, %s, %s)",
                (property_id, chemin or f"import/{i}_{nom}", donnees, mime, nom),
            )
        except DatabaseError:
            pass

        sources.append(_source(chemin=chemin or None, donnees=donnees,
                               mime=mime))

    return sources


def property_image_uri(prop, index=0, images=None):
    """Image principale d'une propriete, pretee a etre placee dans un src.

    Les images importees sont servies en URL de donnees : le navigateur
    peut les afficher, ce qu'un chemin de fichier local ne permettait pas.
    """
    identifiant = prop['id'] if isinstance(prop, dict) else prop[0]
    type_bien = prop.get('type_bien') if isinstance(prop, dict) else (prop[4] if len(prop) > 4 else None)
    type_bien = type_bien or "Maison"

    if images is None:
        images = get_uploaded_images(identifiant)
    if images and index < len(images):
        source = images[index]
        if isinstance(source, dict):
            uri = _uri_source(source)
        else:
            # compatibilite : une liste de chemins de fichiers
            try:
                uri = _data_uri(source, os.path.getmtime(source))
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
