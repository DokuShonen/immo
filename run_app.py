# run_app.py
import subprocess
import sys
import os

def get_path(relative_path):
    """ Obtenir le chemin absolu vers une ressource, fonctionne pour le dev et pour PyInstaller """
    try:
        # PyInstaller crée un dossier temporaire et stocke le chemin dans _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)

if __name__ == '__main__':
    # Chemin vers le script principal de l'application Streamlit
    app_path = get_path('app.py')

    # Commande pour lancer Streamlit
    # On utilise sys.executable pour être sûr d'utiliser le Python embarqué dans l'exécutable
    command = [
        sys.executable,
        "-m", "streamlit", "run",
        app_path,
        "--server.port", "5000",
        "--server.headless", "true" # Important pour ne pas ouvrir de nouvelles fenêtres de terminal
    ]

    # Lancer le processus Streamlit
    try:
        print("Lancement de l'application...")
        process = subprocess.Popen(command)
        process.wait() # Attend que le processus se termine
    except KeyboardInterrupt:
        print("Arrêt de l'application.")
        process.terminate()
    except Exception as e:
        print(f"Une erreur est survenue: {e}")