"""Étape 1 — Collecte brute (01_collecte).
WDI par API (wbgapi), PWT = fichier téléchargé à la main, copié tel quel dans data/raw/.
raw/ n'est JAMAIS modifié : si un fichier existe, on refuse (un remplacement = amendement daté dans Data.md).
Usage :
    python 01_collecte.py --pwt /chemin/vers/pwt110.xlsx      # WDI + PWT
    python 01_collecte.py                                     # WDI seul
    python 01_collecte.py --remplacer                         # amendement (retéléchargement)
"""
import argparse, datetime as dt, json, shutil
from pathlib import Path
import config as C
import regles as R

def collecter_wdi(remplacer=False):
    import wbgapi as wb
    cible = C.RAW / "wdi_raw.csv"
    if cible.exists() and not remplacer:
        raise SystemExit(f"{cible} existe déjà. raw/ n'est jamais modifié. Pour remplacer : --remplacer "
                         "puis consigner l'AMENDEMENT daté dans Data.md.")
    code2var = {v["code"]: k for k, v in C.VARIABLES.items() if v["source"] == "WDI"}
    df = wb.data.DataFrame(list(code2var), economy=C.ISO3, time=range(C.Y0, C.Y1 + 1),
                           db=2, labels=False, skipBlanks=False, skipAggs=False)
    df = df.reset_index()                                   # colonnes : economy, series, YR1990 ... YR2023
    recus = set(df["series"].unique())
    if recus != set(code2var):                              # contrôle bloquant (ex. code « à confirmer » invalide)
        raise SystemExit(f"Indicateurs manquants dans la réponse WDI : {set(code2var) - recus}")
    df.to_csv(cible, index=False)                           # tel quel, sans renommage
    try:
        maj = wb.source.get(2).get("lastupdated")
    except Exception as e:
        maj = f"indisponible ({e})"
    meta = dict(source="WDI (API wbgapi, db=2)", date_telechargement=dt.datetime.now().isoformat(timespec="seconds"),
                indicateurs=list(code2var), pays=C.ISO3, periode=[C.Y0, C.Y1],
                wbgapi_version=getattr(wb, "__version__", "?"), derniere_maj_source=maj)
    (C.RAW / "meta_wdi.json").write_text(json.dumps(meta, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"WDI : {df.shape[0]} lignes (pays × indicateur) -> {cible}")
    R.consigner("COLLECTE WDI", [f"- {k}: {v}" for k, v in meta.items()])

def copier_pwt(chemin, remplacer=False):
    src = Path(chemin)
    dest = C.RAW / src.name                                 # nom d'origine conservé
    if dest.exists() and not remplacer:
        raise SystemExit(f"{dest} existe déjà (raw/ jamais modifié).")
    shutil.copy2(src, dest)
    pwt = R.lire_pwt(dest)
    print("Colonnes PWT :", list(pwt.columns))              # lire d'abord les noms exacts
    attendus = {v["code"] for v in C.VARIABLES.values() if v["source"] == "PWT"} | {"countrycode", "year"}
    manquants = attendus - set(pwt.columns)
    if manquants:
        raise SystemExit(f"Noms PWT introuvables : {manquants}. Corriger config.VARIABLES d'après la liste ci-dessus.")
    meta = dict(source="PWT (téléchargement manuel)", fichier=dest.name,
                date_copie=dt.datetime.now().isoformat(timespec="seconds"),
                variables_demandees=sorted(attendus), version="À RELIRE dans la documentation PWT",
                annees=[int(pwt["year"].min()), int(pwt["year"].max())])
    (C.RAW / "meta_pwt.json").write_text(json.dumps(meta, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"PWT copié -> {dest}")
    R.consigner("COLLECTE PWT", [f"- {k}: {v}" for k, v in meta.items()])

if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--pwt", help="chemin du fichier PWT 11 (.xlsx ou .dta)")
    ap.add_argument("--remplacer", action="store_true", help="amendement : écrase raw/ (à consigner dans Data.md)")
    a = ap.parse_args()
    collecter_wdi(a.remplacer)
    if a.pwt:
        copier_pwt(a.pwt, a.remplacer)
    else:
        print("PWT non fourni : copier le fichier avec --pwt avant l'étape 2.")