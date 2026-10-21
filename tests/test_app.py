"""Tests de rendu de l'interface avec le moteur de test de Streamlit.

Ils verifient que chaque espace se charge sans exception, ce qui couvre
l'ensemble des vues de l'application.
"""
import os
import sys
import unittest

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, BASE_DIR)
os.chdir(BASE_DIR)

from streamlit.testing.v1 import AppTest  # noqa: E402

from utils.database import db_manager  # noqa: E402


def _utilisateur(role):
    resultat = db_manager.execute_query(
        "SELECT * FROM users WHERE role = %s AND is_active = TRUE LIMIT 1",
        (role,), fetch='one')
    if not resultat:
        raise unittest.SkipTest(f"Aucun compte de role {role} dans la base.")
    return {
        'id': resultat['id'],
        'username': resultat['username'],
        'email': resultat['email'],
        'role': resultat['role'],
        'nom': resultat['nom'],
        'prenom': resultat['prenom'],
        'raison_sociale': resultat.get('raison_sociale'),
        'telephone': resultat.get('telephone'),
        'adresse': resultat.get('adresse'),
        'is_active': True,
    }


def _lancer(role=None, page=None):
    at = AppTest.from_file('app.py', default_timeout=90)
    if role:
        at.session_state['user'] = _utilisateur(role)
    if page:
        at.session_state['page'] = page
    at.run()
    return at


class TestRenduPublic(unittest.TestCase):
    def test_la_page_publique_se_charge(self):
        at = _lancer()
        self.assertEqual(len(at.exception), 0, [str(e.value) for e in at.exception])
        self.assertGreater(len(at.markdown), 0)

    def test_les_biens_sont_affiches(self):
        at = _lancer()
        html = "\n".join(m.value for m in at.markdown)
        self.assertIn("prop-card", html)
        self.assertNotIn("<script>alert", html)


class TestRenduParRole(unittest.TestCase):
    def _verifier(self, role, page=None):
        at = _lancer(role, page)
        self.assertEqual(
            len(at.exception), 0,
            f"exceptions pour {role} : {[str(e.value) for e in at.exception]}")
        return at

    def test_espace_client(self):
        self._verifier('client')

    def test_espace_client_favoris(self):
        self._verifier('client', 'favorites')

    def test_espace_client_rendez_vous(self):
        self._verifier('client', 'appointments')

    def test_espace_bailleur(self):
        self._verifier('bailleur', 'my_properties')

    def test_espace_agent(self):
        self._verifier('agent', 'my_clients')

    def test_espace_agent_rendez_vous(self):
        self._verifier('agent', 'appointments')

    def test_espace_manager_utilisateurs(self):
        self._verifier('manager', 'manage_users')

    def test_espace_manager_statistiques(self):
        self._verifier('manager', 'statistics')


if __name__ == "__main__":
    unittest.main()
