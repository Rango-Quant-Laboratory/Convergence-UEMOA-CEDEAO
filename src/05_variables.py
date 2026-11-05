"""Étape 5 — Construction des variables (05_variables).
Coupe : revenu initial = moyenne des logs 1990–94, final = 2019–23, durée T = 29 ans.
Panel : six blocs de 5 ans (moyenne des logs, valide si ≥ 3 années sur 5), blocs valides CONSÉCUTIFS.
Marquer plutôt que supprimer : tous les pays sont écrits, avec leurs drapeaux d'éligibilité.
Sorties : coupe_wdi.csv, coupe_pwt.csv, blocs_wdi.csv, blocs_pwt.csv, annuel_pib.csv (processed/).
Option --stats-manuelles : min/max du PIB/hab. par pays, À LIRE UNE FOIS À LA MAIN après le gel."""
import argparse
import numpy as np
import pandas as pd
import config as C
import regles as R

def moyenne_fenetre(g, col, fen):
    s = g.loc[g["year"].between(*fen), col].dropna()
    return (s.mean(), len(s)) if len(s) >= C.SEUILS["bloc_valide_min"] else (np.nan, len(s))

def construire_coupe(pib, wide, col, flags):
    rows = []
    for iso, g in pib.groupby("iso3"):
        y0, n0 = moyenne_fenetre(g, col, C.FENETRE_INIT)
        y1, n1 = moyenne_fenetre(g, col, C.FENETRE_FIN)
        rows.append(dict(iso3=iso, groupe=C.GROUPE[iso], uemoa=int(C.GROUPE[iso] == "UEMOA"),
                         groupe_constant=C.groupe_constant(iso), y_init=y0, n_init=n0, y_fin=y1, n_fin=n1,
                         croissance_ann=(y1 - y0) / C.T_COUPE))
    df = pd.DataFrame(rows)
    # HYPOTHÈSE À VALIDER dans equations.md : covariables = moyennes sur toute la fenêtre 1990–2023
    cov = wide.groupby("iso3").agg(csh_i_moy=("csh_i_pwt", "mean"), inv_moy=("inv_wdi", "mean"), popgrow_moy=("popgrow_wdi", "mean"),
                                   hc_moy=("hc_pwt", "mean"), ouverture_moy=("trade_wdi", "mean")).reset_index()
    df = df.merge(cov, on="iso3")
    # transformations PROVISOIRES (log type Solow-MRW) — à confirmer dans equations.md
    df["ln_s"] = np.log(df["csh_i_moy"])                      # cœur : csh_i (PWT, déjà une fraction)
    df["ln_s_wdi"] = np.log(df["inv_moy"] / 100)              # extension : investissement WDI (en %)
    df["ln_ngd"] = np.log(df["popgrow_moy"] / 100 + C.CONSTANTE_POP)
    df["ln_hc"] = np.log(df["hc_moy"])
    return df.merge(flags, on="iso3", how="left")

def construire_blocs(pib, col):
    rows = []
    for iso, g in pib.groupby("iso3"):
        for k, (a, b) in enumerate(C.BLOCS):
            s = g.loc[g["year"].between(a, b), col].dropna()
            valide = len(s) >= C.SEUILS["bloc_valide_min"]
            part = float(np.mean([C.uemoa_en_annee(iso, y) for y in range(a, b + 1)]))
            rows.append(dict(iso3=iso, bloc=k, debut=a, fin=b, n_obs=len(s), valide=valide,
                             lny=s.mean() if valide else np.nan, part_uemoa=part))
    d = pd.DataFrame(rows).sort_values(["iso3", "bloc"])
    # CAS NON PRÉVU (GNB, bloc 1995–99 à cheval sur 1997) : règle « majorité des années » — À CONSIGNER/VALIDER dans Data.md
    d["uemoa"] = (d["part_uemoa"] >= 0.5).astype(int)
    mixtes = d[(d["part_uemoa"] > 0) & (d["part_uemoa"] < 1)]
    if len(mixtes):
        print("CAS NON PRÉVU — blocs à appartenance mixte :\n", mixtes[["iso3", "debut", "fin", "part_uemoa", "uemoa"]].to_string(index=False))
    d["lny_debut_bloc"] = d.groupby("iso3")["lny"].shift(1)
    d["valide_prec"] = d.groupby("iso3")["valide"].shift(1).fillna(False).astype(bool)
    d["intervalle_ok"] = d["valide"] & d["valide_prec"]
    d["croissance_ann"] = np.where(d["intervalle_ok"], (d["lny"] - d["lny_debut_bloc"]) / 5, np.nan)
    ok = d.groupby("iso3")["valide"].apply(lambda s: (R.plus_longue_suite(s) == s.sum()) and s.sum() >= C.SEUILS["panel_blocs_min"])
    d["dans_panel"] = d["iso3"].map(ok)                        # blocs valides consécutifs et ≥ 5 sur 6
    return d

def main(stats_manuelles=False):
    for f in ("long_flags.csv", "eligibilite.csv"):
        if not (C.PROC / f).exists():
            raise SystemExit(f"{f} absent : l'étape 4 (appliquer) doit tourner avant.")
    long = pd.read_csv(C.PROC / "long_flags.csv")
    elig = pd.read_csv(C.PROC / "eligibilite.csv")
    flags = R.flags_elig(elig)
    wide = long.pivot(index=["iso3", "year"], columns="variable", values="value").reset_index()
    pib = R.series_pib(wide)                                   # vérifie que le log porte sur un NIVEAU par habitant
    pib.to_csv(C.PROC / "annuel_pib.csv", index=False)
    construire_coupe(pib, wide, "ln_wdi", flags).to_csv(C.PROC / "coupe_wdi.csv", index=False)
    construire_coupe(pib, wide, "ln_pwt_o", flags).to_csv(C.PROC / "coupe_pwt.csv", index=False)
    bw, bp = construire_blocs(pib, "ln_wdi"), construire_blocs(pib, "ln_pwt_o")
    bw.to_csv(C.PROC / "blocs_wdi.csv", index=False); bp.to_csv(C.PROC / "blocs_pwt.csv", index=False)

    # contrôles de fin de chaîne
    wdi = long[long["variable"] == "gdppc_wdi"]
    base = set(elig[(elig["niveau"] == "coupe_base") & elig["eligible"]].iso3)
    assert len(wdi) == len(C.ISO3) * C.N_ANNEES, "panel complet de départ ≠ 15 × 34 = 510"
    assert len(wdi[wdi["iso3"].isin(base)]) == len(base) * C.N_ANNEES, "lignes de base ≠ N × 34"
    print(f"Contrôles OK : {len(wdi)} lignes de départ ; base en coupe = {len(base)} × 34 = {len(base) * C.N_ANNEES}")
    j = pd.read_csv(C.PROC / "journal_pays_perdus.csv")
    print(f"Journal : {len(j)} exclusions (pays × niveau × variable) — à reprendre dans Data.md")
    if stats_manuelles:
        print("\nÀ LIRE UNE FOIS À LA MAIN (unité aberrante, ligne d'agrégat) :")
        print(wdi.groupby("iso3")["value"].agg(["min", "max"]).round(0).to_string())

if __name__ == "__main__":
    ap = argparse.ArgumentParser(); ap.add_argument("--stats-manuelles", action="store_true")
    main(ap.parse_args().stats_manuelles)