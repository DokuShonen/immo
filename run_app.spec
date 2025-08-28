# run_app.spec (version finale et renforcée)

# -*- mode: python ; coding: utf-8 -*-

from PyInstaller.utils.hooks import collect_data_files

block_cipher = None

# --- Configuration Renforcée ---

# 1. Données à inclure (fichiers et dossiers)
datas_to_include = [
    ('app.py', '.'),
    ('utils', 'utils'),
    ('uploads', 'uploads'),
    ('.streamlit', '.streamlit'),
    ('.env', '.')
]
# Ajouter les données de Plotly, qui sont souvent manquées
datas_to_include += collect_data_files('plotly')

# 2. Imports cachés que PyInstaller pourrait manquer
hidden_imports_list = [
    'pandas', 
    'plotly', 
    'bcrypt', 
    'psycopg2',
    'psycopg2._psycopg', # Forcer l'inclusion du module C
    'python-dotenv',
    # Imports cachés souvent nécessaires pour pandas et plotly
    'pandas.io.json._json',
    'plotly.graph_objs',
    'plotly.io'
]
# --- Fin de la configuration ---

a = Analysis(['run_app.py'],
             pathex=['C:\\wamp64\\www\\projets\\Immo'],
             binaries=[],
             datas=datas_to_include,
             hiddenimports=hidden_imports_list,
             hookspath=[],
             hooksconfig={},
             runtime_hooks=[],
             excludes=[],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher,
             noarchive=False)
pyz = PYZ(a.pure, a.zipped_data,
          cipher=block_cipher)
exe = EXE(pyz,
          a.scripts,
          [],
          a.zipfiles,
          a.datas,
          [],
          name='GestionImmobiliere',
          debug=False,
          bootloader_ignore_signals=False,
          strip=False,
          upx=True,
          upx_exclude=[],
          runtime_tmpdir=None,
          console=False,
          icon=r'C:\Users\kinda\Images\ixo.ico')