"""Étape 3 — Complétude, heatmap et fiche de lecture (03_completude).
RÈGLE : ce script ne CHARGE PAS la colonne `value` : il est incapable de regarder une valeur économique.
Sorties : processed/completude.csv, Results/Graphs/heatmap_completude.png,
Results/Tables/fiche_lecture.csv, fiche_trous_a_annoter.csv, fiche_synthese.md."""
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.colors import ListedColormap
from matplotlib.patches import Patch
import config as C
import regles as R

def heatmap(flags, chemin):
    variables = list(C.VARIABLES)
    ncols = 2; nrows = -(-len(variables) // ncols)
    fig, axes = plt.subplots(nrows, ncols, figsize=(16, 3.3 * nrows), squeeze=False)
    couleurs = ["#d9534f", "#5cb85c", "#bdbdbd"]                    # 0 manquant, 1 observé, 2 hors source
    for ax, var in zip(axes.ravel(), variables):
        d = flags[flags["variable"] == var].copy()
        d["etat"] = np.where(~d["in_source"], 2, np.where(d["observe"], 1, 0))
        m = d.pivot(index="iso3", columns="year", values="etat").reindex(C.ISO3)
        ax.imshow(m.values, aspect="auto", cmap=ListedColormap(couleurs), vmin=0, vmax=2, interpolation="nearest")
        ax.set_yticks(range(len(m))); ax.set_yticklabels(m.index, fontsize=7)
        xt = list(range(0, len(m.columns), 5))
        ax.set_xticks(xt); ax.set_xticklabels([m.columns[i] for i in xt], fontsize=7, rotation=90)
        ax.axhline(len(C.UEMOA) - 0.5, color="black", lw=0.8)       # séparation UEMOA / hors UEMOA
        ax.set_title(f"{var} — {C.VARIABLES[var]['source']}", fontsize=9)
    for ax in axes.ravel()[len(variables):]:
        ax.axis("off")
    fig.legend(handles=[Patch(color=c, label=l) for c, l in zip(couleurs, ["manquant", "observé", "hors source"])],
               loc="lower center", ncol=3)
    fig.tight_layout(rect=(0, 0.04, 1, 1)); fig.savefig(chemin, dpi=150); plt.close(fig)

def anomalies_systemiques(flags):
    """Renvoie (alertes 4.6, infos). Alerte : année absente pour tous, pays absent d'une SOURCE entière,
    variable absente de tous les pays. Info : pays × variable absent -> parade 4.3 (perdu pour cette covariable seulement)."""
    alertes, infos = [], []
    for var, g in flags.groupby("variable"):
        par_an = g[g["in_source"]].groupby("year")["observe"].sum()
        for a in par_an[par_an == 0].index:
            alertes.append(f"année absente pour TOUS les pays : {var}, {a} (problème de source/publication)")
        par_pays = g.groupby("iso3")["observe"].sum()
        if (par_pays == 0).all():
            alertes.append(f"variable absente de tous les pays : {var}")
        for c in par_pays[par_pays == 0].index:
            infos.append(f"{c} / {var} : variable entièrement absente -> pays perdu pour cette covariable (parade 4.3)")
    par_src = flags.groupby(["iso3", "source"])["observe"].sum()
    for (c, s), n in par_src[par_src == 0].items():
        alertes.append(f"pays absent d'une source entière : {c} / {s}")
    return alertes, infos

def main():
    flags = pd.read_csv(C.PROC / "long.csv", usecols=["iso3", "year", "variable", "source", "observe", "in_source"])
    st = R.stats_completude(flags)
    st.to_csv(C.PROC / "completude.csv", index=False)
    heatmap(flags, C.GRAPHS / "heatmap_completude.png")

    crit = R.evaluer_criteres(st)                                   # diagnostic avec les valeurs de DÉPART
    echecs = {}
    for r in crit[~crit["passe"]].itertuples():
        echecs.setdefault((r.iso3, r.variable), []).append(f"{r.niveau}:{r.critere}={r.valeur:g} (exigé {r.sens} {r.seuil:g})")
    fiche = st.copy()
    fiche["criteres_echoues"] = [" | ".join(echecs.get((r.iso3, r.variable), [])) or "aucun" for r in fiche.itertuples()]
    fiche["n_obs_sur_34"] = fiche["n_obs"].astype(str) + "/" + fiche["n_annees"].astype(str)
    fiche.to_csv(C.TABLES / "fiche_lecture.csv", index=False)
    trous = st[st["annees_trous"] != ""][["iso3", "variable", "annees_trous"]].assign(conflit_ou_effondrement_coincide="")
    trous.to_csv(C.TABLES / "fiche_trous_a_annoter.csv", index=False)   # à annoter À LA MAIN (limite de biais de sélection)

    elig = R.eligibilite(crit); S = R.synthese(elig)
    front = crit[crit["frontiere"]][["iso3", "variable", "niveau", "critere", "valeur", "seuil"]]
    anom, infos = anomalies_systemiques(flags)
    md = ["# Synthèse de lecture (diagnostic sur valeurs de DÉPART, non gelé)", "",
          f"- Pays éligibles coupe de base (σ, β) : N = {S['n_base']} {S['n_groupes_base']} -> {S['base']}",
          f"- Covariables du cœur {C.COVARIABLES_COEUR} (∩ base) : {S['par_covariable']}",
          f"- Extensions (∩ base) : {S['par_extension']}",
          f"- Conditionnel : N commun = {S['n_cond']} {S['n_groupes_cond']}, k = {S['k']}, ddl = {S['ddl']}, réalisable = {S['conditionnel_ok']}",
          f"- Panel : N = {S['n_panel']} {S['n_groupes_panel']} -> {S['panel']}", "",
          "## Pays frontière (à un cran d'un seuil) -> robustesse ±1 cran", front.to_string(index=False) if len(front) else "aucun", "",
          "## Anomalies systémiques (alertes)", "\n".join("- " + a for a in anom) or "aucune",
          "", "## Pays × variable absents (parade 4.3, pas une alerte)", "\n".join("- " + i for i in infos) or "aucun", "",
          "## Alertes rubrique 4.6", "\n".join("- " + a for a in S["alertes"]) or "aucune",
          "", "## Conclusion pour l'étape 4",
          "Aucune alerte : valeurs de départ gelables telles quelles." if not S["alertes"] and not anom
          else "ALERTE : remonter à l'équipe AVANT de continuer (aucun ajustement ad hoc)."]
    (C.TABLES / "fiche_synthese.md").write_text("\n".join(md), encoding="utf-8")
    R.consigner("LECTURE DE LA HEATMAP (diagnostic, non gelé)", md[2:])
    print("\n".join(md))
    print(f"\nHeatmap : {C.GRAPHS / 'heatmap_completude.png'}")

if __name__ == "__main__":
    main()