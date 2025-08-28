@echo off
REM --- Configuration ---
SET URL_A_LANCER=http://127.0.0.1:5000/
SET PORT=5000
SET DELAI_EN_SECONDES=5
SET ENV_FILE=.env
REM -------------------

echo =======================================================
echo Lancement de la Plateforme de Gestion Immobiliere...
echo Ne fermez pas cette fenetre.
echo =======================================================

REM Se place dans le dossier ou se trouve ce script
cd /d "%~dp0"

REM Verifie si l'environnement virtuel existe
IF NOT EXIST venv (
    echo.
    echo ERREUR : Le dossier de l'environnement virtuel 'venv' est introuvable.
    pause
    exit /b
)

REM Verifie si le fichier .env existe
IF NOT EXIST %ENV_FILE% (
    echo.
    echo ERREUR : Le fichier de configuration '%ENV_FILE%' est introuvable.
    echo Veuillez creer ce fichier avec votre chaine de connexion.
    echo Exemple : DATABASE_URL="postgresql://user:password@host:port/dbname"
    pause
    exit /b
)

REM --- SECTION IMPORTANTE : LECTURE DU FICHIER .ENV ---
echo.
echo Configuration de la connexion a la base de donnees...
FOR /F "usebackq tokens=*" %%A IN (`type %ENV_FILE%`) DO (
    SET %%A
)
REM ----------------------------------------------------

echo.
echo Activation de l'environnement virtuel...
call venv\Scripts\activate.bat

echo.
echo Demarrage du serveur de l'application (sur le port %PORT%)...
echo Attendez un instant, le navigateur va s'ouvrir automatiquement.

REM On lance le navigateur manuellement apres un delai
echo Lancement du navigateur dans %DELAI_EN_SECONDES% secondes...
ping 127.0.0.1 -n %DELAI_EN_SECONDES% > nul
start "" "%URL_A_LANCER%"

REM Lance l'application Streamlit SANS qu'elle n'ouvre le navigateur elle-meme
python -m streamlit run app.py --server.port %PORT% --server.headless true

echo.
echo L'application a ete arretee. Vous pouvez fermer cette fenetre.
pause