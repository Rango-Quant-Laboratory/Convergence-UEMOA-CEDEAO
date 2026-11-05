"""Étape 6 — Ruptures de niveau et sources croisées (06_ruptures).
(1) Alertes |Δ ln PIB/hab.| > seuil, WDI vs PWT (rgdpna/pop) : présente dans les deux = « réelle », dans une seule = « artefact ».
(2) Moyennes sur 5 ans WDI vs PWT : corrélation de rang des pays par bloc.
(3) Signe du coefficient principal (β absolu) et de l'interaction de groupe, WDI vs PWT : signe différent -> « FRAGILE ».
(4) Indicatif : pays dominants (part du PIB du groupe, PWT rgdpo).
JAMAIS de correction manuelle."""
import numpy as np
import pandas as pd
import config as C
import regles as R

def table_dlog(ann, col, source):
    d = ann[["iso3", "year", col]].sort_values(["iso3", "year"]).copy()
    d["dlog"] = d.groupby("iso3")[col].diff()                      # NaN si l'année précédente manque (pas d'interpolation)
    d["alerte"] = d["dlog"].abs() > C.SEUILS["rupture_dlog"]
    return d.drop(columns=col).rename(columns={"dlog": f"dlog_{source}", "alerte": f"alerte_{source}"})

def classer(r):
    aw, ap = r["alerte_wdi"], r["alerte_pwt"]
    if aw and ap:
        return "réelle (deux sources)"
    if aw:
        return "artefact WDI (à estimer avec et sans)" if pd.notna(r["dlog_pwt"]) else "NON TESTABLE (PWT absent) — cas non prévu, à consigner"
    return "artefact PWT (à estimer avec et sans)" if pd.notna(r["dlog_wdi"]) else "NON TESTABLE (WDI absent) — cas non prévu, à consigner"

def ruptures():
    ann = pd.read_csv(C.PROC / "annuel_pib.csv")
    m = table_dlog(ann, "ln_wdi", "wdi").merge(table_dlog(ann, "ln_pwt_na", "pwt"), on=["iso3", "year"])
    a = m[m["alerte_wdi"] | m["alerte_pwt"]].copy()
    a["classement"] = a.apply(classer, axis=1)
    a["ampleur_wdi"], a["ampleur_pwt"] = a["dlog_wdi"].round(3), a["dlog_pwt"].round(3)
    a = a[["iso3", "year", "ampleur_wdi", "ampleur_pwt", "classement"]]
    a.to_csv(C.PROC / "ruptures.csv", index=False)
    print(f"\n[1] Alertes de rupture (seuil {C.SEUILS['rupture_dlog']}) : {len(a)}")
    print(a.to_string(index=False) if len(a) else "aucune")
    return [f"### Alertes de rupture (seuil {C.SEUILS['rupture_dlog']}) : {len(a)} (pays, année, ampleur par source, classement)", "```",
            a.to_string(index=False) if len(a) else "aucune", "```"]

def comparer_blocs():
    bw, bp = pd.read_csv(C.PROC / "blocs_wdi.csv"), pd.read_csv(C.PROC / "blocs_pwt.csv")
    m = bw.merge(bp, on=["iso3", "bloc"], suffixes=("_wdi", "_pwt"))
    rows = []
    for k, g in m.dropna(subset=["lny_wdi", "lny_pwt"]).groupby("bloc"):
        rho = g["lny_wdi"].rank().corr(g["lny_pwt"].rank()) if len(g) >= 3 else np.nan   # corrélation de rang (Spearman)
        rows.append(dict(bloc=k, periode=f"{C.BLOCS[k][0]}–{C.BLOCS[k][1]}", n_pays=len(g), rho_rang=round(rho, 3)))
    out = pd.DataFrame(rows); out.to_csv(C.PROC / "comparaison_blocs.csv", index=False)
    print("\n[2] Classement des pays WDI vs PWT (niveaux attendus différents : rondes PPA distinctes, ce n'est pas une erreur)")
    print(out.to_string(index=False))
    return ["### Classement des pays WDI vs PWT (corrélation de rang des moyennes de bloc ; niveaux différents attendus)", "```", out.to_string(index=False), "```"]

def coefs(df):
    g, y0, u = df["croissance_ann"].to_numpy(), df["y_init"].to_numpy(), df["uemoa"].to_numpy()
    b_abs = R.ols(g, y0)[1]                                         # coefficient principal (β absolu)
    d_int = R.ols(g, np.column_stack([y0, u, y0 * u]))[3]           # interaction groupe × revenu initial
    return b_abs, d_int

def signes():
    w, p = pd.read_csv(C.PROC / "coupe_wdi.csv"), pd.read_csv(C.PROC / "coupe_pwt.csv")
    base = w["elig_coupe_base_gdppc_wdi"] == 1
    m = w[base][["iso3", "uemoa", "y_init", "croissance_ann"]].merge(
        p[["iso3", "y_init", "croissance_ann"]], on="iso3", suffixes=("_w", "_p")).dropna()
    bw, dw = coefs(m.rename(columns={"y_init_w": "y_init", "croissance_ann_w": "croissance_ann"}))
    bp, dp = coefs(m.rename(columns={"y_init_p": "y_init", "croissance_ann_p": "croissance_ann"}))
    res = pd.DataFrame([dict(source="WDI", beta_abs=bw, interaction=dw), dict(source="PWT", beta_abs=bp, interaction=dp)])
    res.to_csv(C.PROC / "signes_sources.csv", index=False)
    print(f"\n[3] Signes WDI vs PWT sur N={len(m)} pays (coupe de base)")
    print(res.round(5).to_string(index=False))
    verdicts = []
    for nom, a, b in (("β absolu", bw, bp), ("interaction de groupe", dw, dp)):
        v = f"  {nom} : {'signes identiques' if np.sign(a) == np.sign(b) else 'SIGNES DIFFÉRENTS -> résultat « FRAGILE », on ne rattrape pas'}"
        print(v); verdicts.append("- " + v.strip())
    return [f"### Signes WDI vs PWT (coupe de base, N = {len(m)})", "```", res.round(5).to_string(index=False), "```"] + verdicts

def dominants():
    long = pd.read_csv(C.PROC / "long_flags.csv")
    o = long[long["variable"] == "rgdpo_pwt"].groupby("iso3")["value"].mean()
    base = pd.read_csv(C.PROC / "eligibilite.csv")
    base = set(base[(base["niveau"] == "coupe_base") & base["eligible"]]["iso3"])
    d = pd.DataFrame({"pib_moy": o}).loc[sorted(base)].assign(groupe=lambda x: x.index.map(C.GROUPE))
    d["part_groupe"] = d["pib_moy"] / d.groupby("groupe")["pib_moy"].transform("sum")
    d["dominant"] = d["part_groupe"] > C.SEUILS["dominant_part"]
    d.round(3).to_csv(C.PROC / "dominants.csv")
    print("\n[4] Pays dominants (indicatif ; MCO non pondérée en base, retrait un par un en robustesse — jamais exclus de la base)")
    print(d[d["dominant"]].round(3).to_string() if d["dominant"].any() else "aucun")
    return ["### Pays dominants (indicatif ; repérés, jamais exclus de la base)", "```",
            d[d["dominant"]].round(3).to_string() if d["dominant"].any() else "aucun", "```"]

if __name__ == "__main__":
    lignes = ruptures() + comparer_blocs() + signes() + dominants()
    R.consigner("RUPTURES ET SOURCES CROISÉES (étape 6)", lignes)