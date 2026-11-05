"""regles.py — fonctions courtes, une par contrôle/règle, partagées par les scripts 01–07.
Aucune valeur économique n'est lue ici pour décider du sort d'un pays (seulement des drapeaux)."""
from __future__ import annotations
import numpy as np
import pandas as pd
import config as C

# ---------- Complétude --------------------------------------------------------
def gaps_internes(annees, obs):
    """Plus longue suite de NA INTERNES (entre première et dernière obs) + années des trous."""
    idx = np.flatnonzero(obs)
    if idx.size == 0:
        return 0, []
    seg_a, seg_o = annees[idx[0]: idx[-1] + 1], obs[idx[0]: idx[-1] + 1]
    runs, cur = [], []
    for a, o in zip(seg_a, seg_o):
        if o:
            if cur:
                runs.append(cur); cur = []
        else:
            cur.append(int(a))
    return max((len(r) for r in runs), default=0), [a for r in runs for a in r]

def plus_longue_suite(flags):
    best = cur = 0
    for f in flags:
        cur = cur + 1 if f else 0
        best = max(best, cur)
    return best

def blocs_valides(annees, obs):
    """Bloc valide = au moins `bloc_valide_min` années observées sur 5."""
    m = C.SEUILS["bloc_valide_min"]
    return [int(obs[(annees >= a) & (annees <= b)].sum()) >= m for a, b in C.BLOCS]

def stats_completude(flags: pd.DataFrame) -> pd.DataFrame:
    """flags : iso3, year, variable, source, observe (bool), in_source (bool). Une ligne par pays × variable."""
    rows = []
    for (iso, var), g in flags.groupby(["iso3", "variable"]):
        g = g.sort_values("year")
        an, obs = g["year"].to_numpy(), g["observe"].to_numpy(dtype=bool)
        gap, gap_years = gaps_internes(an, obs)
        bv = blocs_valides(an, obs)
        run = plus_longue_suite(bv)
        deb = (an >= C.FENETRE_INIT[0]) & (an <= C.FENETRE_INIT[1])
        fin = (an >= C.FENETRE_FIN[0]) & (an <= C.FENETRE_FIN[1])
        rows.append(dict(
            iso3=iso, variable=var, source=g["source"].iloc[0],
            premiere_annee=int(an[obs].min()) if obs.any() else np.nan,
            derniere_annee=int(an[obs].max()) if obs.any() else np.nan,
            n_obs=int(obs.sum()), n_annees=len(an), gap_max=gap,
            annees_trous=",".join(map(str, gap_years)),
            n_obs_debut=int(obs[deb].sum()), n_obs_fin=int(obs[fin].sum()),
            blocs_valides=int(sum(bv)), blocs_suite_max=run, blocs_consecutifs=bool(run == sum(bv)),
            in_source=bool(g["in_source"].any())))
    return pd.DataFrame(rows)

# ---------- Critères & éligibilité -------------------------------------------
def evaluer_criteres(st: pd.DataFrame, cran: int = 0) -> pd.DataFrame:
    """Un critère = une ligne. cran=+1 : seuils plus stricts d'un cran ; -1 : plus lâches (robustesse ±1)."""
    S, out = C.SEUILS, []
    def add(r, niveau, critere, valeur, seuil, sens):
        s_eff = seuil + cran if sens == ">=" else seuil - cran
        marge = (valeur - s_eff) if sens == ">=" else (s_eff - valeur)
        out.append(dict(iso3=r.iso3, variable=r.variable, niveau=niveau, critere=critere,
                        valeur=valeur, seuil=s_eff, sens=sens, passe=bool(marge >= 0),
                        marge=marge, frontiere=bool(marge in (0, -1))))  # à un cran d'un seuil
    for r in st.itertuples():
        role = C.VARIABLES.get(r.variable, {}).get("role")
        if role in ("pib", "pib_controle"):
            add(r, "coupe", "n_obs", r.n_obs, S["pib_n_obs"], ">=")
            add(r, "coupe", "gap_max", r.gap_max, S["pib_gap_max"], "<=")
            add(r, "coupe", "n_obs_debut", r.n_obs_debut, S["pib_bord_min"], ">=")
            add(r, "coupe", "n_obs_fin", r.n_obs_fin, S["pib_bord_min"], ">=")
            add(r, "panel", "blocs_consecutifs_valides", r.blocs_suite_max, S["panel_blocs_min"], ">=")
        elif role in ("covariable", "extension"):
            add(r, "covariable", "n_obs", r.n_obs, S["covar_n_obs"], ">=")
    return pd.DataFrame(out)

NIVEAUX_FIXES = [("coupe_base", "gdppc_wdi", "coupe"), ("panel", "gdppc_wdi", "panel"),
                 ("robustesse_pwt", "rgdpo_pwt", "coupe")]

def eligibilite(crit: pd.DataFrame) -> pd.DataFrame:
    """Applique les parades SANS choix discrétionnaire : tous les critères du niveau doivent passer."""
    combos = NIVEAUX_FIXES + [("covariable", v, "covariable") for v, i in C.VARIABLES.items()
                              if i["role"] in ("covariable", "extension")]
    out = []
    for niveau, var, nc in combos:
        sub = crit[(crit["variable"] == var) & (crit["niveau"] == nc)]
        if sub.empty:
            continue
        for iso in sorted(sub["iso3"].unique()):
            s = sub[sub["iso3"] == iso]
            ech = s[~s["passe"]]
            regle = " ; ".join(f"{e.critere}={e.valeur:g} (exigé {e.sens} {e.seuil:g})" for e in ech.itertuples())
            ok = ech.empty
            if niveau == "coupe_base" and not C.groupe_constant(iso):
                ok, regle = False, ("statut_groupe_non_constant" + (" ; " + regle if regle else ""))
            out.append(dict(iso3=iso, niveau=niveau, variable=var, eligible=ok, regle_declenchee=regle))
    return pd.DataFrame(out)

def flags_elig(elig: pd.DataFrame) -> pd.DataFrame:
    e = elig.assign(cle="elig_" + elig["niveau"] + "_" + elig["variable"], v=elig["eligible"].astype(int))
    return e.pivot(index="iso3", columns="cle", values="v").reset_index()

def synthese(elig: pd.DataFrame) -> dict:
    S = C.SEUILS
    def ok(niveau, var):
        m = (elig["niveau"] == niveau) & (elig["variable"] == var) & elig["eligible"]
        return set(elig.loc[m, "iso3"])
    par_groupe = lambda ens: {g: sum(C.GROUPE[c] == g for c in ens) for g in ("UEMOA", "HORS")}
    base = ok("coupe_base", "gdppc_wdi")
    covars = [v for v, i in C.VARIABLES.items() if i["role"] == "covariable"]
    par_cov = {v: base & ok("covariable", v) for v in covars}
    commun = base.intersection(*par_cov.values()) if par_cov else set(base)
    ext = [v for v, i in C.VARIABLES.items() if i["role"] == "extension"]
    par_ext = {v: sorted(base & ok("covariable", v)) for v in ext}
    k = C.K_BASE + len(covars)
    n_cond, ddl = len(commun), len(commun) - k
    panel = ok("panel", "gdppc_wdi")
    alertes = []
    if len(base) < S["N_min"]:
        alertes.append(f"N coupe = {len(base)} < {S['N_min']}")
    for g, n in par_groupe(base).items():
        if n < S["N_min_groupe"]:
            alertes.append(f"groupe {g} : {n} pays < {S['N_min_groupe']}")
    if len(panel) < S["panel_pays_min"]:
        alertes.append(f"panel = {len(panel)} pays < {S['panel_pays_min']}")
    return dict(base=sorted(base), n_base=len(base), n_groupes_base=par_groupe(base),
                par_covariable={v: sorted(s) for v, s in par_cov.items()},
                commun_conditionnel=sorted(commun), n_groupes_cond=par_groupe(commun), par_extension=par_ext, n_cond=n_cond, k=k, ddl=ddl,
                conditionnel_ok=bool(n_cond >= S["N_min"] and ddl >= S["df_min"]),
                panel=sorted(panel), n_panel=len(panel), n_groupes_panel=par_groupe(panel), alertes=alertes)

# ---------- Lecture PWT / séries PIB -----------------------------------------
def lire_pwt(path):
    path = str(path)
    if path.lower().endswith(".dta"):
        return pd.read_stata(path)
    xl = pd.ExcelFile(path)
    if "Data" not in xl.sheet_names:
        raise ValueError(f"Feuille 'Data' absente de {path}; feuilles : {xl.sheet_names}")
    return xl.parse("Data")

def verifier_niveau(s: pd.Series, nom: str):
    """Garde-fou : le log doit porter sur un NIVEAU par habitant, pas sur une croissance ou un indice (heuristique)."""
    v = s.dropna()
    if (v <= 0).any():
        raise ValueError(f"{nom} : valeurs <= 0, le log n'a pas de sens")
    if v.median() < 300:
        raise ValueError(f"{nom} : médiane {v.median():.1f} — ressemble à une croissance/un indice, pas à un niveau")

def series_pib(wide: pd.DataFrame) -> pd.DataFrame:
    out = wide[["iso3", "year"]].copy()
    out["wdi"] = wide["gdppc_wdi"]
    out["pwt_o"] = wide["rgdpo_pwt"] / wide["pop_pwt"]     # niveaux (σ, revenu initial)
    out["pwt_na"] = wide["rgdpna_pwt"] / wide["pop_pwt"]   # dynamique
    for c in ("wdi", "pwt_o", "pwt_na"):
        verifier_niveau(out[c], c)
        out["ln_" + c] = np.log(out[c])
    return out

# ---------- Statistique minimale ---------------------------------------------
def sigma_dispersion(df: pd.DataFrame, col_log: str, ddof: int = 1) -> pd.Series:
    """σ_t = écart-type inter-pays de ln(PIB/hab.) par année. Échantillon IDENTIQUE chaque année (sinon erreur).
    ddof=1 par défaut — À ALIGNER sur equations.md."""
    d = df.dropna(subset=[col_log])
    n = d.groupby("year")["iso3"].nunique()
    if n.nunique() != 1:
        raise ValueError(f"Composition variable selon les années : {n.to_dict()}")
    return d.groupby("year")[col_log].std(ddof=ddof)

def ols(y, X):
    """MCO avec constante ; renvoie [const, b1, b2, ...]."""
    y = np.asarray(y, float)
    X = np.column_stack([np.ones(len(y)), np.asarray(X, float)])
    return np.linalg.lstsq(X, y, rcond=None)[0]

def vitesse_depuis_beta(b, T):
    """b = coef. du log initial dans la croissance ANNUALISÉE ; λ = -ln(1+bT)/T (Barro–Sala-i-Martin).
    À ALIGNER sur equations.md."""
    return -np.log(1 + b * T) / T if (1 + b * T) > 0 else np.nan

# ---------- Journal Data.md (écrit PAR LES SCRIPTS, jamais reconstruit de mémoire) ----------
def consigner(titre, lignes, statut=None):
    """Ajoute une section DATÉE à Data.md. Data.md est un journal tenu au fil de l'eau : on ajoute, on n'efface pas."""
    import datetime as dt
    if not C.DATA_MD.exists():
        C.DATA_MD.write_text("# Data.md — journal des données (on ajoute, on n'efface jamais : on amende)\n", encoding="utf-8")
    corps = lignes if isinstance(lignes, str) else "\n".join(lignes)
    corps = corps.replace("\n## ", "\n### ")                     # pas de titres de niveau 2 dans le corps
    tete = f"\n\n## {titre} — {dt.date.today().isoformat()}" + (f" [{statut}]" if statut else "")
    with open(C.DATA_MD, "a", encoding="utf-8") as f:
        f.write(tete + "\n\n" + corps + "\n")
