"""Étape 2 — Filtrage strict par liste ISO3 (02_filtrage).
Liste FERMÉE (jamais « exclure les agrégats »). Contrôles bloquants :
15 codes uniques ; 34 années par pays ; zéro doublon pays-année ; tous les pays PWT retrouvés par ISO3.
Sortie : processed/long.csv (format long : iso3, year, variable, source, value, observe, in_source)."""
import json
import pandas as pd
import config as C
import regles as R

def lire_wdi_long():
    p = C.RAW / "wdi_raw.csv"
    if not p.exists():
        raise SystemExit("raw/wdi_raw.csv absent : lancer 01_collecte.py")
    w = pd.read_csv(p)
    code2var = {v["code"]: k for k, v in C.VARIABLES.items() if v["source"] == "WDI"}
    larg = w.melt(id_vars=["economy", "series"], var_name="yr", value_name="value")
    larg["year"] = larg["yr"].str.replace("YR", "", regex=False).astype(int)
    larg["variable"] = larg["series"].map(code2var)
    if larg["variable"].isna().any():
        raise ValueError("Indicateur WDI non reconnu dans le fichier brut")
    return larg.rename(columns={"economy": "iso3"})[["iso3", "year", "variable", "value"]]

def trouver_pwt():
    cands = [p for p in C.RAW.iterdir() if p.name.lower().startswith("pwt") and p.suffix.lower() in (".xlsx", ".dta")]
    if len(cands) != 1:
        raise SystemExit(f"Un (et un seul) fichier PWT attendu dans raw/, trouvé : {[p.name for p in cands]}")
    return cands[0]

# ---------- contrôles bloquants (une fonction par contrôle) --------------------
def controle_codes(df, nom):
    codes = set(df["iso3"].unique())
    if codes != set(C.ISO3) or len(codes) != 15:
        raise ValueError(f"[{nom}] codes ≠ liste ISO3 : en trop {codes - set(C.ISO3)}, manquants {set(C.ISO3) - codes}")

def controle_doublons(df, cles, nom):
    d = df.duplicated(cles).sum()
    if d:
        raise ValueError(f"[{nom}] {d} doublons sur {cles}")

def controle_annees(df, nom):
    for (iso, var), g in df.groupby(["iso3", "variable"]):
        if sorted(g["year"].unique()) != C.ANNEES:
            raise ValueError(f"[{nom}] {iso}/{var} : années ≠ {C.Y0}–{C.Y1} ({g['year'].nunique()} années)")

def main():
    # --- WDI
    wdi = lire_wdi_long()
    wdi = wdi[wdi["iso3"].isin(C.ISO3)].copy()                       # filtrage par liste fermée
    controle_codes(wdi, "WDI"); controle_doublons(wdi, ["iso3", "year", "variable"], "WDI")
    controle_annees(wdi, "WDI")
    wdi["source"] = "WDI"
    # pays « absent de la source » : aucune observation, toutes variables WDI confondues
    a_des_obs = wdi.groupby("iso3")["value"].apply(lambda s: s.notna().any())
    wdi["in_source"] = wdi["iso3"].map(a_des_obs)

    # --- PWT (fusion sur le code ISO3, jamais sur le nom)
    pwt_f = trouver_pwt()
    pwt = R.lire_pwt(pwt_f)
    codes_pwt = {v["code"]: k for k, v in C.VARIABLES.items() if v["source"] == "PWT"}
    manque = (set(codes_pwt) | {"countrycode", "year"}) - set(pwt.columns)
    if manque:
        raise ValueError(f"Colonnes PWT absentes : {manque}")
    pwt = pwt[pwt["countrycode"].isin(C.ISO3)].copy()
    absents = set(C.ISO3) - set(pwt["countrycode"])
    if absents:
        raise SystemExit(f"Pays absents de PWT (à remonter à l'équipe, rubrique 4.6) : {absents}")
    controle_doublons(pwt, ["countrycode", "year"], "PWT")
    pwt = pwt.rename(columns={"countrycode": "iso3"})
    grille = pd.MultiIndex.from_product([C.ISO3, C.ANNEES], names=["iso3", "year"]).to_frame(index=False)
    morceaux = [wdi[["iso3", "year", "variable", "source", "value", "in_source"]]]
    cles = pwt[["iso3", "year"]].assign(_present=True)
    for code, var in codes_pwt.items():
        g = grille.merge(pwt[["iso3", "year", code]].rename(columns={code: "value"}), how="left", on=["iso3", "year"])
        g = g.merge(cles, how="left", on=["iso3", "year"])
        g["in_source"] = g.pop("_present").fillna(False).astype(bool)  # ligne absente de PWT = hors source
        g["variable"], g["source"] = var, "PWT"
        morceaux.append(g[["iso3", "year", "variable", "source", "value", "in_source"]])
    # WDI : compléter la grille (au cas où) puis concaténer
    long = pd.concat(morceaux, ignore_index=True)
    long["observe"] = long["value"].notna()
    controle_codes(long, "LONG"); controle_doublons(long, ["iso3", "year", "variable"], "LONG")
    controle_annees(long, "LONG")
    attendu = len(C.ISO3) * C.N_ANNEES * len(C.VARIABLES)
    if len(long) != attendu:
        raise ValueError(f"Lignes = {len(long)}, attendu {attendu} (15 × 34 × {len(C.VARIABLES)})")
    long.to_csv(C.PROC / "long.csv", index=False)
    json.dump(dict(lignes=len(long), pays=len(C.ISO3), annees=C.N_ANNEES, variables=list(C.VARIABLES),
                   pwt_fichier=pwt_f.name, controles="OK"),
              open(C.PROC / "controles_02.json", "w"), indent=2)
    R.consigner("FILTRAGE (contrôles bloquants OK)", [f"- {len(long)} lignes = 15 pays × 34 ans × {len(C.VARIABLES)} variables", f"- fichier PWT : {pwt_f.name}", "- 15 codes ISO3 uniques, 34 années par pays, zéro doublon, pays PWT retrouvés par code"])
    print(f"OK — {len(long)} lignes ({len(C.ISO3)} pays × {C.N_ANNEES} ans × {len(C.VARIABLES)} variables)")

if __name__ == "__main__":
    main()