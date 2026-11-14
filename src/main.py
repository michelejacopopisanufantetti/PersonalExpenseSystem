import sys
import logging
from datetime import datetime
import psycopg2
from psycopg2 import errors, Error

# Librerie facoltative 
try:
    import pandas as pd
    import matplotlib.pyplot as plt
    from sqlalchemy import create_engine
    HAS_PANDAS_MATPLOTLIB = True
except ImportError:
    HAS_PANDAS_MATPLOTLIB = False

# ------------------------------------------------------------------------------
# 1. CONFIGURAZIONE DEL LOGGING (tracciamento professionale su file e console)
# ------------------------------------------------------------------------------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[
        logging.FileHandler("app.log", encoding="utf-8"),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger("ExpenseManager")

# ------------------------------------------------------------------------------
# 2. CONFIGURAZIONE CREDENZIALI DATABASE POSTGRESQL
# ------------------------------------------------------------------------------
DB_CONFIG = {
    "dbname": "gestione_spese", # nome impostato in pgadmin
    "user": "postgres",  #admin impostato in pgAdmin
    "password": "1234",  # password impostata in pgAdmin
    "host": "localhost",
    "port": "5432" #porta imposta in PgAdmin
}

def connetti_db():
    """Crea e restituisce una connessione al database PostgreSQL."""
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        return conn
    except Error as e:
        logger.error(f"Connessione a PostgreSQL fallita: {e}")
        print("\n[ERRORE] Impossibile connettersi al database PostgreSQL.")
        print("Verificare che il server sia attivo e che le credenziali in DB_CONFIG siano corrette.")
        return None

# ------------------------------------------------------------------------------
# 3. MODULO 1 — GESTIONE DELLE CATEGORIE
# ------------------------------------------------------------------------------
def gestione_categorie():
    print("\n--- MODULO 1: GESTIONE CATEGORIE ---")
    nome_cat = input("Inserisci il nome della categoria: ").strip()

    # Validazione: verifica che il nome non sia vuoto
    if not nome_cat:
        print("[ERRORE] Il nome della categoria non può essere vuoto.")
        return

    conn = connetti_db()
    if not conn:
        return

    try:
        cur = conn.cursor()
        # Controllo dell'esistenza della categoria (SQL SELECT)
        cur.execute("SELECT id_categoria FROM Categorie WHERE LOWER(nome_categoria) = LOWER(%s);", (nome_cat,))
        if cur.fetchone():
            print("Errore: la categoria esiste già.")
            logger.warning(f"Tentativo di inserire una categoria duplicata: '{nome_cat}'")
            return

        # Inserimento della categoria se valida (SQL INSERT)
        cur.execute("INSERT INTO Categorie (nome_categoria) VALUES (%s);", (nome_cat,))
        conn.commit()
        print("Categoria inserita correttamente.")
        logger.info(f"Categoria '{nome_cat}' inserita con successo.")

    except errors.UniqueViolation:
        conn.rollback()
        print("Errore: la categoria esiste già.")
        logger.warning(f"UniqueViolation intercettata per categoria: '{nome_cat}'")
    except Error as e:
        conn.rollback()
        print(f"Errore del database durante l'inserimento: {e}")
        logger.error(f"Errore SQL in gestione_categorie: {e}")
    finally:
        cur.close()
        conn.close()

# ------------------------------------------------------------------------------
# 4. MODULO 2 — INSERIMENTO DI UNA SPESA
# ------------------------------------------------------------------------------
def inserisci_spesa():
    print("\n--- MODULO 2: INSERISCI SPESA ---")
    
    # Input Data (YYYY-MM-DD)
    data_str = input("Inserisci la data (YYYY-MM-DD): ").strip()
    try:
        data_valida = datetime.strptime(data_str, "%Y-%m-%d").date()
    except ValueError:
        print("[ERRORE] Formato data non valido. Usare il formato YYYY-MM-DD (es. 2026-11-01).")
        return

    # Input Importo
    try:
        importo = float(input("Inserisci l'importo (€): "))
    except ValueError:
        print("[ERRORE] L'importo deve essere un numero valido.")
        return

    # Validazione importo > 0
    if importo <= 0:
        print("Errore: l'importo deve essere maggiore di zero.")
        return

    # Input Nome Categoria e Descrizione facoltativa
    nome_cat = input("Inserisci il nome della categoria: ").strip()
    descrizione = input("Inserisci una descrizione (facoltativa): ").strip()
    if not descrizione:
        descrizione = None

    conn = connetti_db()
    if not conn:
        return

    try:
        cur = conn.cursor()
        # Controllo dell'esistenza della categoria (SQL SELECT)
        cur.execute("SELECT id_categoria FROM Categorie WHERE LOWER(nome_categoria) = LOWER(%s);", (nome_cat,))
        res = cur.fetchone()
        if not res:
            print("Errore: la categoria non esiste.")
            logger.warning(f"Tentativo di inserire spesa per categoria inesistente: '{nome_cat}'")
            return

        id_categoria = res[0]

        # Inserimento della spesa (SQL INSERT con chiave esterna)
        cur.execute(
            "INSERT INTO Spese (data, importo, id_categoria, descrizione) VALUES (%s, %s, %s, %s);",
            (data_valida, importo, id_categoria, descrizione)
        )
        conn.commit()
        print("Spesa inserita correttamente.")
        logger.info(f"Spesa di €{importo:.2f} per '{nome_cat}' registrata.")

    except errors.CheckViolation:
        conn.rollback()
        print("Errore: l'importo deve essere maggiore di zero.")
    except errors.ForeignKeyViolation:
        conn.rollback()
        print("Errore: la categoria non esiste.")
    except Error as e:
        conn.rollback()
        print(f"Errore del database durante l'inserimento della spesa: {e}")
        logger.error(f"Errore SQL in inserisci_spesa: {e}")
    finally:
        cur.close()
        conn.close()

# ------------------------------------------------------------------------------
# 5. MODULO 3 — DEFINIZIONE DEL BUDGET MENSILE
# ------------------------------------------------------------------------------
def definisci_budget():
    print("\n--- MODULO 3: DEFINISCI BUDGET MENSILE ---")
    
    # Input Mese (YYYY-MM)
    mese_str = input("Inserisci il mese (YYYY-MM): ").strip()
    try:
        datetime.strptime(mese_str, "%Y-%m")
    except ValueError:
        print("[ERRORE] Formato mese non valido. Usare il formato YYYY-MM (es. 2026-11).")
        return

    nome_cat = input("Inserisci il nome della categoria: ").strip()

    # Input Importo Budget
    try:
        budget_val = float(input("Inserisci l'importo del budget (€): "))
    except ValueError:
        print("[ERRORE] L'importo del budget deve essere un numero valido.")
        return

    # Validazione budget > 0
    if budget_val <= 0:
        print("[ERRORE] L'importo del budget deve essere maggiore di zero.")
        return

    conn = connetti_db()
    if not conn:
        return

    try:
        cur = conn.cursor()
        # Controllo dell'esistenza della categoria (SQL SELECT)
        cur.execute("SELECT id_categoria FROM Categorie WHERE LOWER(nome_categoria) = LOWER(%s);", (nome_cat,))
        res = cur.fetchone()
        if not res:
            print("Errore: la categoria non esiste.")
            logger.warning(f"Tentativo di impostare budget per categoria inesistente: '{nome_cat}'")
            return

        id_categoria = res[0]

        # Inserimento o aggiornamento del record di budget (UPSERT PostgreSQL)
        query = """
            INSERT INTO Budget (mese, importo_budget, id_categoria)
            VALUES (%s, %s, %s)
            ON CONFLICT (mese, id_categoria)
            DO UPDATE SET importo_budget = EXCLUDED.importo_budget;
        """
        cur.execute(query, (mese_str, budget_val, id_categoria))
        conn.commit()
        print("Budget mensile salvato correttamente.")
        logger.info(f"Budget di €{budget_val:.2f} per '{nome_cat}' nel mese {mese_str} salvato.")

    except Error as e:
        conn.rollback()
        print(f"Errore del database durante il salvataggio del budget: {e}")
        logger.error(f"Errore SQL in definisci_budget: {e}")
    finally:
        cur.close()
        conn.close()

# ------------------------------------------------------------------------------
# 6. MODULO 4 — VISUALIZZAZIONE DEI REPORT
# ------------------------------------------------------------------------------
def report_totale_spese_categoria(conn):
    """REPORT 1 — Totale delle Spese per Categoria (SUM e GROUP BY)."""
    try:
        cur = conn.cursor()
        query = """
            SELECT c.nome_categoria, COALESCE(SUM(s.importo), 0) AS totale_speso
            FROM Categorie c
            LEFT JOIN Spese s ON c.id_categoria = s.id_categoria
            GROUP BY c.id_categoria, c.nome_categoria
            ORDER BY totale_speso DESC;
        """
        cur.execute(query)
        risultati = cur.fetchall()

        print("\n--- REPORT 1: TOTALE SPESE PER CATEGORIA ---")
        print(f"{'Categoria':<25} {'Totale Speso (€)':>15}")
        print("-" * 42)
        for riga in risultati:
            print(f"{riga[0]:<25} {riga[1]:>15.2f}")
        print("-" * 42)
    except Error as e:
        print(f"Errore nella generazione del report: {e}")
        logger.error(f"Errore SQL in report 1: {e}")
    finally:
        cur.close()

def report_spese_vs_budget(conn):
    """REPORT 2 — Spese Mensili vs Budget (confronto e stato di superamento)."""
    mese_str = input("\nInserisci il mese da analizzare (YYYY-MM): ").strip()
    try:
        datetime.strptime(mese_str, "%Y-%m")
    except ValueError:
        print("[ERRORE] Formato mese non valido. Usare YYYY-MM.")
        return

    try:
        cur = conn.cursor()
        query = """
            SELECT 
                c.nome_categoria,
                b.importo_budget,
                COALESCE(SUM(s.importo), 0) AS totale_speso
            FROM Budget b
            JOIN Categorie c ON b.id_categoria = c.id_categoria
            LEFT JOIN Spese s ON c.id_categoria = s.id_categoria 
                             AND TO_CHAR(s.data, 'YYYY-MM') = %s
            WHERE b.mese = %s
            GROUP BY c.id_categoria, c.nome_categoria, b.importo_budget;
        """
        cur.execute(query, (mese_str, mese_str))
        risultati = cur.fetchall()

        print(f"\n--- REPORT 2: SPESE MENSILI VS BUDGET ({mese_str}) ---")
        if not risultati:
            print(f"Nessun budget definito per il mese {mese_str}.")
            return

        for riga in risultati:
            nome_cat, budget, speso = riga[0], float(riga[1]), float(riga[2])
            stato = "SUPERAMENTO BUDGET" if speso > budget else "IN BUDGET"
            print(f"\nMese: {mese_str}")
            print(f"Categoria: {nome_cat}")
            print(f"Budget: €{budget:.2f}")
            print(f"Speso: €{speso:.2f}")
            print(f"Stato: {stato}")
            print("-" * 35)

    except Error as e:
        print(f"Errore nella generazione del report budget: {e}")
        logger.error(f"Errore SQL in report 2: {e}")
    finally:
        cur.close()

def report_elenco_spese_ordinate(conn):
    """REPORT 3 — Elenco Completo delle Spese ordinate per data."""
    try:
        cur = conn.cursor()
        query = """
            SELECT s.data, c.nome_categoria, s.importo, COALESCE(s.descrizione, '-')
            FROM Spese s
            JOIN Categorie c ON s.id_categoria = c.id_categoria
            ORDER BY s.data ASC, s.id_spesa ASC;
        """
        cur.execute(query)
        risultati = cur.fetchall()

        print("\n--- REPORT 3: ELENCO COMPLETO DELLE SPESE ---")
        if not risultati:
            print("Nessuna spesa presente nel database.")
            return

        print(f"{'Data':<12} {'Categoria':<20} {'Importo (€)':>12} {'Descrizione':<30}")
        print("-" * 76)
        for riga in risultati:
            data_str = str(riga[0])
            print(f"{data_str:<12} {riga[1]:<20} {riga[2]:>12.2f} {riga[3]:<30}")
        print("-" * 76)

    except Error as e:
        print(f"Errore durante l'estrazione delle spese: {e}")
        logger.error(f"Errore SQL in report 3: {e}")
    finally:
        cur.close()

def genera_grafico_pandas_matplotlib():
    """REPORT GRAFICO (Opzionale) con Pandas e Matplotlib (dal tutorial del PDF)."""
    if not HAS_PANDAS_MATPLOTLIB:
        print("\n[AVVISO] Le librerie pandas, matplotlib o sqlalchemy non sono installate.")
        print("Per attivare i grafici visuali esegui: pip install pandas matplotlib sqlalchemy")
        return

    try:
        db_url = f"postgresql+psycopg2://{DB_CONFIG['user']}:{DB_CONFIG['password']}@{DB_CONFIG['host']}:{DB_CONFIG['port']}/{DB_CONFIG['dbname']}"
        engine = create_engine(db_url)
        query = """
            SELECT c.nome_categoria AS categoria, COALESCE(SUM(s.importo), 0) AS spesa_totale
            FROM Categorie c
            LEFT JOIN Spese s ON c.id_categoria = s.id_categoria
            GROUP BY c.id_categoria, c.nome_categoria
            HAVING SUM(s.importo) > 0
            ORDER BY spesa_totale DESC;
        """
        df = pd.read_sql(query, con=engine)
        if df.empty:
            print("\nNessuna spesa da visualizzare nel grafico.")
            return

        plt.figure(figsize=(8, 5))
        barre = plt.bar(df['categoria'], df['spesa_totale'], color='skyblue', edgecolor='navy', width=0.5)
        plt.title("Analisi Spese per Categoria", fontsize=14, fontweight='bold', pad=15)
        plt.xlabel("Categoria", fontsize=12)
        plt.ylabel("Totale Speso (€)", fontsize=12)
        plt.grid(axis='y', linestyle='--', alpha=0.7)

        for barra in barre:
            h = barra.get_height()
            plt.text(barra.get_x() + barra.get_width() / 2, h + 0.5, f"€{h:.2f}", ha='center', va='bottom', fontsize=10)

        plt.tight_layout()
        plt.show()
        logger.info("Grafico Matplotlib generato con successo.")
    except Exception as e:
        print(f"Errore durante la generazione del grafico: {e}")
        logger.error(f"Errore in grafico pandas/matplotlib: {e}")

def visualizza_report():
    conn = connetti_db()
    if not conn:
        return

    while True:
        print("\n===============================")
        print("      MENU DEI REPORT")
        print("===============================")
        print("1. Totale spese per categoria")
        print("2. Spese mensili vs budget")
        print("3. Elenco completo delle spese ordinate per data")
        print("4. Grafico visivo spese (Pandas + Matplotlib)")
        print("5. Ritorna al menu principale")
        
        scelta = input("\nSeleziona un report (1-5): ").strip()
        if scelta == "1":
            report_totale_spese_categoria(conn)
        elif scelta == "2":
            report_spese_vs_budget(conn)
        elif scelta == "3":
            report_elenco_spese_ordinate(conn)
        elif scelta == "4":
            genera_grafico_pandas_matplotlib()
        elif scelta == "5":
            break
        else:
            print("Scelta non valida. Riprovare.")

    conn.close()

# ------------------------------------------------------------------------------
# 7. MENU PRINCIPALE (Ciclo iterativo e Gestione Scelta)
# ------------------------------------------------------------------------------
def main():
    logger.info("Avvio del Sistema di Gestione Spese Personali.")
    print("\n=========================================")
    print(" BENVENUTO NEL SISTEMA SPESE PERSONALI")
    print("=========================================")

    while True:
        print("\n-------------------------")
        print("SISTEMA SPESE PERSONALI")
        print("-------------------------")
        print("1. Gestione Categorie")
        print("2. Inserisci Spesa")
        print("3. Definisci Budget Mensile")
        print("4. Visualizza Report")
        print("5. Esci")
        print("-------------------------")

        scelta = input("Inserisci la tua scelta: ").strip()

        if scelta == "1":
            gestione_categorie()
        elif scelta == "2":
            inserisci_spesa()
        elif scelta == "3":
            definisci_budget()
        elif scelta == "4":
            visualizza_report()
        elif scelta == "5":
            print("\nUscita dal programma. Arrivederci!")
            logger.info("Uscita dall'applicazione.")
            break
        else:
            print("Scelta non valida. Riprovare.")

if __name__ == "__main__":
    main()
