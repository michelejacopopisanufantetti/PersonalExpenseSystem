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

-- Inserimento di alcune categorie base di test
INSERT INTO Categorie (nome_categoria) VALUES ('Alimentari'), ('Trasporti'), ('Svago');