import sqlite3
from colors import Colors 
import os
import subprocess
colors = Colors()
# DB VER 1.0.0
class Database:
    DBpath = f'/home/{os.getlogin()}/nob_db.db'
    """ if not os.path.exists(DBpath):
        try:
            r = subprocess.run(['sudo', 'touch', DBpath ], text=True, capture_output=True)
            if not r.returncode == 0:
                print(f"{colors.RED}==> ERROR{colors.END} : Error while trying to create db file")
                pass
            subprocess.run(['sudo', 'chmod', '666', DBpath], text=True, capture_output=True) #Allowing user & programs to edit it without root permissions.
        except Exception as e:
            print(f"{colors.RED}==> ERROR{colors.END} : Error while trying to create db file : {e}")"""
    connection = sqlite3.connect(DBpath)
    cursor = connection.cursor()
    def add_db(pkg : str , pkg_version: str):
        cursor = Database.cursor
        cursor.execute("CREATE TABLE IF NOT EXISTS pkgs (name TEXT, version TEXT)")
        cursor.execute("SELECT * FROM pkgs")
        try :
            cursor.execute(
            "SELECT 1 FROM pkgs WHERE name = ?",
            (pkg,)
            )
            row = cursor.fetchone()
            if row: 
                version = row[0]
                if pkg_version != version:
                    cursor.execute(
                    "UPDATE pkgs SET version = ? WHERE name = ?",
                    (pkg_version, pkg)
                    )
                    Database.connection.commit()
            else : 
                cursor.execute(
                "INSERT INTO pkgs (name, version) VALUES (?, ?)",
                (pkg, pkg_version)
                )
                Database.connection.commit()

        except sqlite3.OperationalError:
            cursor.execute(
                "INSERT INTO pkgs (name, version) VALUES (?, ?)",
                (pkg, pkg_version)
            )
            Database.connection.commit()

    def read_db():
        try:
            cursor = Database.cursor
            cursor.execute("SELECT * FROM pkgs")
            rows = cursor.fetchall()
            pkgs =  []
            for pkg_name, pkg_ver in rows:
                pkgs.append((pkg_name, pkg_ver))
            return pkgs
        except sqlite3.OperationalError:
            return []
        
    def remove_db(pkg : str):
        cursor = Database.cursor
        cursor.execute("CREATE TABLE IF NOT EXISTS pkgs (name TEXT, version TEXT)")
        cursor.execute("SELECT * FROM pkgs")
        cursor.execute(
            "SELECT 1 FROM pkgs WHERE name = ?",
            (pkg,)
        )
        row = cursor.fetchone()
        if not row : return
        cursor.execute(
            "DELETE FROM pkgs WHERE name = ?",
            (pkg,)
        )
        Database.connection.commit()