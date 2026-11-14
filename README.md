# Sistema di Gestione delle Spese Personali (Expense Manager)

Un'applicazione console sviluppata in **Python** e basata su database **PostgreSQL** per tracciare, organizzare e analizzare le spese personali ed il budget mensile.

---

##  Indice delle Sezioni
1. [Descrizione del Progetto](#descrizione-del-progetto)
2. [Struttura del Repository](#struttura-del-repository)
3. [Requisiti di Sistema](#requisiti-di-sistema)
4. [Installazione e Configurazione](#installazione-e-configurazione)
5. [Schema del Database e Vincoli SQL](#schema-del-database-e-vincoli-sql)
6. [Guida all'Uso e Moduli dell'Applicazione](#guida-alluso-e-moduli-dellapplicazione)
7. [Logging e Gestione degli Errori](#logging-e-gestione-degli-errori)
8. [Demo](#demo)

---

##  Descrizione del Progetto

Il **Sistema di Gestione delle Spese Personali** e progettato per aiutare gli utenti a monitorare le proprie uscite finanziarie. L'applicazione offre una robusta interfaccia a riga di comando (CLI) collegata a un database PostgreSQL.

L'architettura garantisce l'integrita dei dati tramite vincoli relazionali SQL (`PRIMARY KEY`, `FOREIGN KEY`, `CHECK`, `UNIQUE`, `NOT NULL`), la gestione sicura delle transazioni con rollback automatico in caso di errore, e la generazione di report analitici sia testuali che grafici.

---

## Struttura del Repository


```text
PersonalExpenseSystem/
│
├── src/
│   └── main.py              # Codice sorgente principale dell'applicazione Python
│
├── sql/
│   └── database.sql         # Script DDL/DML per la creazione delle tabelle e dei vincoli PostgreSQL
│
├── demo/
│   └── demo_video.mp4       # Video dimostrativo dell'esecuzione del programma
│
├── app.log                  # File di registro prodotto dal modulo logging (generato all'avvio)
└── README.md                # Documentazione ufficiale del progetto
```

---

## Requisiti di Sistema

### Requisiti Software
- **Python**: Versione 3.8 o superiore
- **PostgreSQL**: Versione 12 o superiore (consigliato **pgAdmin 4** per la gestione visiva)

### Librerie Python Richieste
- **psycopg2-binary**: Driver ufficiale di connessione a PostgreSQL per Python.

### Librerie Python Opzionali (per i report grafici)
- **pandas**: Manipolazione ed estrazione analitica dei dati.
- **matplotlib**: Generazione di grafici a barre delle spese.
- **sqlalchemy**: Interfaccia di connessione tra Pandas e PostgreSQL.

Installazione rapida delle dipendenze da terminale:

```bash
pip install psycopg2-binary pandas matplotlib sqlalchemy
```

---

##  Installazione e Configurazione

### 1. Preparazione Repository
Creare la cartella del progetto e organizzare i file secondo la struttura sopra indicata:
```bash
mkdir PersonalExpenseSystem
cd PersonalExpenseSystem
```

### 2. Configurazione del Database PostgreSQL
1. Apri **pgAdmin 4** (o la riga di comando `psql`).
2. Crea un nuovo database denominato **`gestione_spese`**:
   - In pgAdmin: tasto destro su *Databases* -> *Create* -> *Database...* -> Inserisci `gestione_spese` -> *Save*.
3. Apri lo strumento query (*Query Tool*) sul database `gestione_spese`.
4. Esegui lo script SQL contenuto in `sql/database.sql` per creare le tabelle e popolare i dati iniziali di prova.

### 3. Configurazione delle Credenziali in Python
Apri il file `src/main.py` e aggiorna il dizionario di configurazione con le credenziali del tuo PostgreSQL locale:

```python
DB_CONFIG = {
    'dbname': 'gestione_spese',
    'user': 'postgres',
    'password': 'LA_TUA_PASSWORD',
    'host': 'localhost',
    'port': '5432'
}
```

### 4. Esecuzione dell'Applicazione
Avvia l'applicazione da terminale posizionandoti nella root del progetto:

```bash
python src/main.py
```

---

##  Schema del Database e Vincoli SQL

Il database e strutturato su 3 tabelle relazionali progettate con vincoli espliciti di integrita dei dati:

```sql
-- 1. Tabella Categorie
CREATE TABLE IF NOT EXISTS Categorie (
    id_categoria SERIAL PRIMARY KEY,
    nome_categoria VARCHAR(100) NOT NULL UNIQUE
);

-- 2. Tabella Spese
CREATE TABLE IF NOT EXISTS Spese (
    id_spesa SERIAL PRIMARY KEY,
    data DATE NOT NULL,
    importo NUMERIC(10, 2) NOT NULL CHECK (importo > 0),
    id_categoria INT NOT NULL,
    descrizione TEXT,
    FOREIGN KEY (id_categoria) REFERENCES Categorie(id_categoria) ON DELETE RESTRICT
);

-- 3. Tabella Budget Mensile
CREATE TABLE IF NOT EXISTS Budget (
    id_budget SERIAL PRIMARY KEY,
    mese VARCHAR(7) NOT NULL, -- Formato YYYY-MM
    importo_budget NUMERIC(10, 2) NOT NULL CHECK (importo_budget > 0),
    id_categoria INT NOT NULL,
    FOREIGN KEY (id_categoria) REFERENCES Categorie(id_categoria) ON DELETE RESTRICT,
    CONSTRAINT unique_mese_categoria UNIQUE (mese, id_categoria)
);
```

### Dettaglio Vincoli di Integrita:
- **`PRIMARY KEY` (`SERIAL PRIMARY KEY`)**: Genera identificativi univoci progressivi per ogni riga.
- **`NOT NULL`**: Impedisce l'inserimento di dati mancanti in campi obbligatori (date, importi, nomi).
- **`UNIQUE`**: 
  - Su `nome_categoria`: evita categorie duplicate.
  - Su `(mese, id_categoria)` nella tabella `Budget`: garantisce un solo budget per categoria nello stesso mese.
- **`CHECK (importo > 0)`**: Assicura che gli importi inseriti siano strettamente positivi.
- **`FOREIGN KEY ... ON DELETE RESTRICT`**: Impedisce la cancellazione accidentale di una categoria se vi sono ancora spese o budget collegati.

---

##  Guida all'Uso e Moduli dell'Applicazione

All'avvio dell'applicazione viene presentato il **Menu Principale**:

```text
-------------------------
SISTEMA SPESE PERSONALI
-------------------------
1. Gestione Categorie
2. Inserisci Spesa
3. Definisci Budget Mensile
4. Visualizza Report
5. Esci
-------------------------
```

### Modulo 1  Gestione Categorie
Consente di aggiungere nuove categorie di spesa (es. *Alimentari*, *Trasporti*, *Svago*).
- **Controlli**: Verifica che il nome non sia vuoto e che non esista gia nel database.
- **Messaggi di output**: `Categoria inserita correttamente.` oppure `Errore: la categoria esiste gia.`.

###  Modulo 2  Inserimento Spesa
Permette di registrare una nuova spesa definendo data (`YYYY-MM-DD`), importo (€), categoria e descrizione facoltativa.
- **Controlli**: Valida la data, impone `importo > 0` e controlla l'esistenza della categoria prima dell'inserimento.
- **Messaggi di errore**: `Errore: l'importo deve essere maggiore di zero.` / `Errore: la categoria non esiste.`.

###  Modulo 3  Definizione Budget Mensile
Consente di impostare o aggiornare un tetto massimo di spesa per una categoria in un determinato mese (`YYYY-MM`).
- **Funzionalita**: Utilizza la clausola SQL `ON CONFLICT (mese, id_categoria) DO UPDATE` (*UPSERT*) per aggiornare automaticamente il valore se il budget per quel mese esiste gia.

###  Modulo 4  Visualizzazione Report
Fornisce un sottomenu dedicato all'analisi dei dati:
1. **Totale spese per categoria**: Calcola la somma totale speso per ciascuna categoria tramite query `SUM` e `GROUP BY`.
2. **Spese mensili vs budget**: Confronta lo speso del mese con il budget prefissato e stampa lo stato (`IN BUDGET` o `SUPERAMENTO BUDGET`).
3. **Elenco completo delle spese**: Stampa la lista cronologica di tutte le spese ordinate per data (`ORDER BY data`).
4. **Grafico visivo (Pandas + Matplotlib)**: Genera una finestra con un grafico a barre colorato con i totali spesi.

---

##  Logging e Gestione degli Errori

- **Eccezioni**: Il codice Python gestisce le eccezioni di PostgreSQL tramite il modulo `psycopg2.errors` (`UniqueViolation`, `ForeignKeyViolation`, `CheckViolation`).
- **Transazioni**: In caso di errore durante qualsiasi operazione SQL, viene eseguito il rollback (`conn.rollback()`) per preservare l'integrita del database.
- **File di Log (`app.log`)**: Tutte le operazioni di sistema, i messaggi di successo e gli eventuali errori vengono registrati sia a schermo sia nel file `app.log` completo di timestamp.

---

##  Demo:
1. Avvio del programma `main.py`.
2. Navigazione nei menu interattivi.
3. Inserimento di categorie, spese e budget di test.
4. Generazione dei report di spesa e visualizzazione del grafico.
