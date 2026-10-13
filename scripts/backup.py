#!/usr/bin/env python3
"""SQLite online backup; restoration requires the application server to be stopped."""
import argparse
import datetime
import os
from pathlib import Path
import sqlite3
ROOT=Path(__file__).resolve().parents[1]
DB=Path(os.environ.get('TOEIC_DB',ROOT/'data/toeic.sqlite3'))

def copy_database(source,destination):
    if not source.is_file(): raise ValueError(f'Base introuvable : {source}')
    if source.resolve()==destination.resolve(): raise ValueError('Source et destination identiques.')
    with sqlite3.connect(f'file:{source}?mode=ro',uri=True) as src:
        if src.execute('PRAGMA integrity_check').fetchone()[0]!='ok': raise ValueError('Base invalide.')
        tables={r[0] for r in src.execute("SELECT name FROM sqlite_master WHERE type='table'")}
        if not {'settings','sessions','attempts','reviews','drafts','lesson_progress'}<=tables:
            raise ValueError('Ce fichier ne contient pas une sauvegarde TOEIC complète.')
        destination.parent.mkdir(parents=True,exist_ok=True)
        with sqlite3.connect(destination) as dst: src.backup(dst)

def backup():
    stamp=datetime.datetime.now().strftime('%Y%m%d-%H%M%S-%f')
    path=DB.parent/'backups'/f'toeic-{stamp}.sqlite3'
    copy_database(DB,path)
    return path

if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--restore',type=Path,help='Serveur arrêté uniquement. Sauvegarde l’état courant avant remplacement.')
    args=parser.parse_args()
    try:
        if args.restore:
            if args.restore.resolve()==DB.resolve(): raise ValueError('Choisissez un fichier de sauvegarde distinct.')
            # Validate the incoming backup before creating any replacement.
            with sqlite3.connect(f'file:{args.restore.resolve()}?mode=ro',uri=True) as source:
                if source.execute('PRAGMA integrity_check').fetchone()[0]!='ok': raise ValueError('Sauvegarde corrompue.')
            if DB.exists(): print('État précédent conservé :',backup())
            copy_database(args.restore,DB)
            print('Restauration terminée :',DB)
        else: print('Sauvegarde créée :',backup())
    except (ValueError,sqlite3.Error) as error: parser.exit(1,str(error)+'\n')
