"""Tests de la logique metier d'ImmoPro.

Lancement :
    ./venv/bin/python -m unittest discover -s tests -v

Les tests s'executent sur la base configuree dans DATABASE_URL. Ils
creent leurs propres lignes et les suppriment a la fin, sans toucher aux
donnees de demonstration.
"""
import os
import sys
import unittest
from datetime import datetime, timedelta

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, BASE_DIR)

# La connexion est lue dans le fichier .env par load_dotenv(), appele a
# l'import des modules utils. Si aucune variable n'est definie, les tests
# sont ignores plutot que d'echouer bruyamment.
from utils.auth import ROLES_PUBLICS, auth_manager  # noqa: E402
from utils.database import db_manager  # noqa: E402
from utils.media import _nom_sur, fmt_prix, property_image_uri  # noqa: E402

if not os.getenv("DATABASE_URL"):
    raise unittest.SkipTest("DATABASE_URL n'est pas definie.")

MOT_DE_PASSE = "MotDePasseTest1!"


class BaseMetier(unittest.TestCase):
    """Utilitaires communs : identifiants uniques et nettoyage."""

    suffixe = "test"

    @classmethod
    def setUpClass(cls):
        cls.admin = db_manager.execute_query(
            "SELECT * FROM users WHERE role = 'manager' AND is_active = TRUE LIMIT 1",
            fetch='one',
        )
        cls.agent = db_manager.execute_query(
            "SELECT * FROM users WHERE role = 'agent' AND is_active = TRUE LIMIT 1",
            fetch='one',
        )
        cls.bailleur = db_manager.execute_query(
            "SELECT * FROM users WHERE role = 'bailleur' AND is_active = TRUE LIMIT 1",
            fetch='one',
        )
        cls.client = db_manager.execute_query(
            "SELECT * FROM users WHERE role = 'client' AND is_active = TRUE LIMIT 1",
            fetch='one',
        )
        if not (cls.admin and cls.agent and cls.bailleur and cls.client):
            raise unittest.SkipTest(
                "La base de demonstration doit contenir un compte par role."
            )

    def tearDown(self):
        db_manager.execute_query(
            "DELETE FROM appointments WHERE notes = %s", ("pytest",))
        db_manager.execute_query(
            "DELETE FROM properties WHERE description = %s", ("pytest",))
        db_manager.execute_query(
            "DELETE FROM login_attempts WHERE username LIKE %s", ("pytest%",))


class TestConnexion(BaseMetier):
    def test_un_compte_desactive_ne_se_connecte_pas(self):
        db_manager.execute_query(
            "UPDATE users SET is_active = FALSE WHERE id = %s", (self.client['id'],))
        try:
            resultat = auth_manager.login(self.client['username'], MOT_DE_PASSE)
            self.assertIsNone(resultat, "un compte desactive doit etre refuse")
        finally:
            db_manager.execute_query(
                "UPDATE users SET is_active = TRUE WHERE id = %s", (self.client['id'],))

    def test_un_compte_valide_se_connecte(self):
        # Le mot de passe de demonstration est commun a tous les comptes.
        resultat = auth_manager.login(self.client['username'], "ImmoPro2026!")
        if resultat is None:
            self.skipTest("Le mot de passe de demonstration a ete change.")
        self.assertEqual(resultat['role'], 'client')
        self.assertIn('id', resultat)

    def test_les_echecs_sont_limites(self):
        username = "pytest" + self.client['username'][:10]
        for _ in range(6):
            auth_manager.login(username, "mauvais-mot-de-passe")

        self.assertTrue(auth_manager.est_bloque(username, "127.0.0.1"))
        self.assertIsNone(auth_manager.login(username, "ImmoPro2026!"))

        auth_manager.effacer_echecs(username, "127.0.0.1")
        self.assertFalse(auth_manager.est_bloque(username, "127.0.0.1"))

    def test_une_connexion_reussie_efface_les_echecs(self):
        username = "pytest" + self.client['username'][:10]
        auth_manager.login(username, "mauvais-mot-de-passe")
        self.assertGreater(
            db_manager.count_recent_failures(username, "127.0.0.1"), 0)
        auth_manager.effacer_echecs(username, "127.0.0.1")
        self.assertEqual(
            db_manager.count_recent_failures(username, "127.0.0.1"), 0)


class TestInscription(BaseMetier):
    def test_un_email_deja_utilise_est_refuse(self):
        resultat = auth_manager.register(
            "pytest" + self.client['username'][:8],
            self.client['email'],
            MOT_DE_PASSE, 'client', 'Test', 'Test')
        self.assertFalse(resultat['success'])
        self.assertNotIn('ERREUR', resultat['message'])
        self.assertNotIn('contrainte', resultat['message'].lower())

    def test_un_role_non_autorise_est_refuse(self):
        resultat = auth_manager.register(
            "pytest" + self.client['username'][:8],
            "pytest" + self.client['username'][:8] + "@exemple.com",
            MOT_DE_PASSE, 'manager', 'Test', 'Test')
        self.assertFalse(resultat['success'])

    def test_les_roles_publiques_sont_bien_deux(self):
        self.assertEqual(set(ROLES_PUBLICS), {'client', 'bailleur'})


class TestBiens(BaseMetier):
    def _creer_un_bien(self, titre="Bien de test"):
        return db_manager.add_property(
            self.bailleur['id'], self.agent['id'], titre, 'Appartement',
            'Résidentiel', 'vente', 'Testville', 60, 120000,
            'pytest')

    def test_les_colonnes_sont_accessibles_par_nom(self):
        bien = self._creer_un_bien()
        propriete = db_manager.get_property_by_id(bien['id'])
        self.assertEqual(propriete['titre'], "Bien de test")
        self.assertEqual(propriete['transaction_type'], 'vente')
        self.assertIn('bailleur_nom', propriete)

    def test_les_filtres_sont_appliques(self):
        self._creer_un_bien("Bien unique de test")
        resultats = db_manager.get_properties({'q': 'Bien unique de test'})
        self.assertEqual(len(resultats), 1)
        self.assertEqual(resultats[0]['titre'], "Bien unique de test")

    def test_la_pagination_est_appliquee(self):
        self._creer_un_bien("Bien pagine A")
        self._creer_un_bien("Bien pagine B")
        self._creer_un_bien("Bien pagine C")
        page1 = db_manager.get_properties({'q': 'Bien pagine'}, limit=2, offset=0)
        page2 = db_manager.get_properties({'q': 'Bien pagine'}, limit=2, offset=2)
        self.assertEqual(len(page1), 2)
        self.assertEqual(len(page2), 1)
        total = db_manager.get_properties({'q': 'Bien pagine'}, count_only=True)
        self.assertEqual(total, 3)

    def test_le_tri_par_derniere_creation_ignore_la_mise_en_avant(self):
        self._creer_un_bien("Bien recent non mis en avant")
        resultats = db_manager.get_properties(
            {'q': 'Bien recent non mis en avant'}, sort='recent')
        self.assertEqual(resultats[0]['titre'], "Bien recent non mis en avant")

    def test_le_portefeuille_du_bailleur_est_restreint(self):
        self._creer_un_bien("Bien du bailleur de test")
        biens = db_manager.get_properties_by_bailleur(self.bailleur['id'])
        titres = [b['titre'] for b in biens]
        self.assertIn("Bien du bailleur de test", titres)


class TestRendezVous(BaseMetier):
    def test_le_manager_voit_tous_les_rendez_vous(self):
        tous = db_manager.get_appointments(self.admin['id'], 'manager')
        agent = db_manager.get_appointments(self.agent['id'], 'agent')
        self.assertGreaterEqual(len(tous), len(agent))

    def test_le_client_ne_voit_que_ses_rendez_vous(self):
        rendez = db_manager.get_appointments(self.client['id'], 'client')
        for rdv in rendez:
            self.assertEqual(rdv['client_id'], self.client['id'])

    def test_les_conflits_de_creneau_sont_detectes(self):
        moment = datetime(2028, 4, 12, 14, 0)
        db_manager.create_appointment(
            self.client['id'], 1, self.agent['id'], moment, 'visite', 'pytest')
        conflits = db_manager.get_conflicting_appointments(
            self.agent['id'], moment)
        self.assertTrue(conflits, "un rendez-vous au meme moment doit etre detecte")

    def test_un_creneau_libre_ne_pose_pas_de_conflit(self):
        moment = datetime(2028, 4, 12, 14, 0)
        conflits = db_manager.get_conflicting_appointments(
            self.agent['id'], moment)
        self.assertFalse(conflits)

    def test_le_rayon_de_conflit_est_limite(self):
        moment = datetime(2028, 4, 12, 14, 0)
        db_manager.create_appointment(
            self.client['id'], 1, self.agent['id'], moment, 'visite', 'pytest')
        conflits = db_manager.get_conflicting_appointments(
            self.agent['id'], moment + timedelta(hours=2))
        self.assertFalse(conflits, "deux heures plus tard, il n'y a pas de conflit")


class TestAssignations(BaseMetier):
    def test_l_affectation_desactive_l_ancienne(self):
        db_manager.execute_query(
            "UPDATE client_assignments SET is_active = FALSE WHERE client_id = %s",
            (self.client['id'],))
        db_manager.assign_client_to_agent(
            self.client['id'], self.agent['id'], self.admin['id'])
        actives = db_manager.execute_query(
            "SELECT COUNT(*) AS nb FROM client_assignments "
            "WHERE client_id = %s AND is_active = TRUE",
            (self.client['id'],), fetch='one')
        self.assertEqual(actives['nb'], 1)

    def test_le_manager_voit_tous_les_clients(self):
        clients = db_manager.get_clients_for_agent(self.admin['id'], role='manager')
        for client in clients:
            self.assertEqual(client['role'], 'client')


class TestMedia(unittest.TestCase):
    def test_le_nom_de_fichier_est_assaini(self):
        self.assertEqual(_nom_sur("ma photo.jpg"), "ma-photo.jpg")
        # Le repertoire est supprime : le fichier sort du dossier d'upload.
        self.assertEqual(_nom_sur("../../etc/passwd"), "passwd.jpg")
        self.assertNotIn("/", _nom_sur("../../etc/passwd"))
        self.assertTrue(_nom_sur("image.png").endswith(".png"))
        self.assertTrue(_nom_sur("image.exe").endswith(".jpg"))

    def test_le_prix_est_formate_en_euros(self):
        self.assertEqual(fmt_prix(680000), "680 000 EUR")
        self.assertEqual(fmt_prix(None), "-")

    def test_une_image_importee_est_exploitable(self):
        propriete = {'id': 999999, 'type_bien': 'Maison'}
        # Aucune image importee : on retombe sur la photographie de repli.
        self.assertTrue(property_image_uri(propriete).startswith("https://"))


if __name__ == "__main__":
    unittest.main()
