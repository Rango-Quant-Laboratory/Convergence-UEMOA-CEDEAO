"""config.py — paramètres saisis par l'équipe (décisions, pas des données).
Source : « Données et accès » rubriques 2, 3, 4.2. Après le commit 2, toute modification
de SEUILS = amendement daté dans Data.md (le hash change, 04_eligibilite.py refusera de tourner)."""
from pathlib import Path
import hashlib, json

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "raw"
PROC = ROOT / "data" / "processed"
GRAPHS = ROOT / "Results" / "Graphs"
TABLES = ROOT / "Results" / "Tables"
DATA_MD = ROOT / "Data.md"
for _p in (RAW, PROC, GRAPHS, TABLES):
    _p.mkdir(parents=True, exist_ok=True)

# --- Échantillon (liste FERMÉE ISO3) -----------------------------------------
UEMOA = ["BEN", "BFA", "CIV", "GNB", "MLI", "NER", "SEN", "TGO"]
HORS_UEMOA = ["CPV", "GMB", "GHA", "GIN", "LBR", "NGA", "SLE"]
ISO3 = UEMOA + HORS_UEMOA
GROUPE = {**{c: "UEMOA" for c in UEMOA}, **{c: "HORS" for c in HORS_UEMOA}}
ADHESION_UEMOA = {"GNB": 1997}  # À CONFIRMER (doc : « de mémoire »)

def uemoa_en_annee(iso, annee):
    """Appartenance variable dans le temps (panel). Hors UEMOA avant l'adhésion."""
    if iso in ADHESION_UEMOA:
        return annee >= ADHESION_UEMOA[iso]
    return GROUPE[iso] == "UEMOA"

def groupe_constant(iso):
    """Critère de statut constant sur la fenêtre (coupe de base)."""
    return iso not in ADHESION_UEMOA or ADHESION_UEMOA[iso] <= Y0

# --- Fenêtres -----------------------------------------------------------------
Y0, Y1 = 1990, 2023
ANNEES = list(range(Y0, Y1 + 1))
N_ANNEES = len(ANNEES)                      # 34
FENETRE_INIT = (1990, 1994)
FENETRE_FIN = (2019, 2023)
T_COUPE = 29                                # 1992 -> 2021
BLOCS = [(1990, 1994), (1995, 1999), (2000, 2004), (2005, 2009), (2010, 2014), (2015, 2019)]

# --- Variables ----------------------------------------------------------------
# role : pib | pib_controle | covariable | extension | support
VARIABLES = {
    "gdppc_wdi":   dict(source="WDI", code="NY.GDP.PCAP.PP.KD", role="pib"),
    "inv_wdi":     dict(source="WDI", code="NE.GDI.FTOT.ZS",    role="extension"),    # investissement WDI : extension (absent CPV, LBR, NGA)
    "popgrow_wdi": dict(source="WDI", code="SP.POP.GROW",       role="covariable"),
    "trade_wdi":   dict(source="WDI", code="NE.TRD.GNFS.ZS",    role="extension"),
    "hc_pwt":      dict(source="PWT", code="hc",                role="extension"),    # capital humain : extension (absent CPV, GIN, GNB)
    "csh_i_pwt":   dict(source="PWT", code="csh_i",             role="covariable"),   # part de formation brute de capital (PPA courantes)
    "rgdpo_pwt":   dict(source="PWT", code="rgdpo",             role="pib_controle"), # niveaux entre pays
    "rgdpna_pwt":  dict(source="PWT", code="rgdpna",            role="pib_controle"), # dynamique intra-pays
    "pop_pwt":     dict(source="PWT", code="pop",               role="support"),      # pour passer en « par habitant »
}
COVARIABLES_COEUR = [k for k, v in VARIABLES.items() if v["role"] == "covariable"]   # démographie (WDI) + csh_i (PWT)
PWT_DYNAMIQUE = "rgdpna_pwt"
CONSTANTE_POP = 0.05                        # croissance technique + dépréciation

# --- Seuils (valeurs de départ, rubrique 4.2) ---------------------------------
SEUILS_DEPART = dict(
    N_min=12, N_min_groupe=5, df_min=8,
    pib_n_obs=31, pib_gap_max=2, pib_bord_min=3,
    covar_n_obs=27,
    panel_pays_min=12, panel_blocs_min=5, bloc_valide_min=3,
    rupture_dlog=0.15, dominant_part=0.30,
)
SEUILS = dict(SEUILS_DEPART)                # ÉDITER ICI seulement AVANT le gel, avec motif :
MOTIFS_ECARTS = {}                          # ex. {"pib_n_obs": "année absente pour tous : ..."}
K_BASE = 2                                  # paramètres de base du modèle conditionnel groupé

def hash_seuils():
    payload = dict(seuils=SEUILS, iso3=ISO3, adhesion=ADHESION_UEMOA, fen_init=FENETRE_INIT,
                   fen_fin=FENETRE_FIN, blocs=BLOCS, T=T_COUPE,
                   covariables_coeur=COVARIABLES_COEUR)
    return hashlib.sha256(json.dumps(payload, sort_keys=True).encode()).hexdigest()
