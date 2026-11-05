"""Étape 4 — Éligibilité et gel (04_eligibilite). TROIS commandes, dans CET ordre :

  python 04_eligibilite.py preparer
      Applique mécaniquement les seuils et ÉCRIT LUI-MÊME dans Data.md : l'amendement H3 (si amendement_H3.md existe à la
      racine du projet) et l'entrée « GEL [BROUILLON] ». Rien à copier-coller. Une relecture est alors possible.
  python 04_eligibilite.py sceller --validateur "Nom Prénom"
      Fait le commit 2 (git add src + Data.md), lit son identifiant, l'écrit dans Data.md avec le nom du validateur,
      passe l'entrée en [SCELLÉ] et fait un 2e commit pour consigner le sceau. Aucun hash à noter à la main.
      Le validateur doit être une AUTRE personne que l'auteur git ; sinon --solo consigne une « validation solo » (déviation).
  python 04_eligibilite.py appliquer [--cran +1|-1]
      REFUSE de tourner si : gel non scellé, hash des seuils différent, commit introuvable, ou config.py modifié depuis le
      commit 2. Produit éligibilité, journal des pays perdus et drapeaux. --cran = robustesse ±1 cran (jamais en base)."""
import argparse, datetime as dt, json, re, subprocess
import pandas as pd
import config as C
import regles as R

def git(*a):
    try:
        return subprocess.run(["git", *a], cwd=C.ROOT, capture_output=True, text=True)
    except FileNotFoundError:
        raise SystemExit("git n'est pas installé ou pas dans le PATH.")

def exiger_depot():
    r = git("rev-parse", "--is-inside-work-tree")
    if r.returncode != 0:
        raise SystemExit(f"{C.ROOT} n'est pas un dépôt git. Lance une fois : git init  (dans ce dossier), puis recommence.")
    gi = C.ROOT / ".gitignore"
    if not gi.exists():
        gi.write_text("__pycache__/\n*.pyc\n", encoding="utf-8")

def calculer(cran=0):
    flags = pd.read_csv(C.PROC / "long.csv", usecols=["iso3", "year", "variable", "source", "observe", "in_source"])
    crit = R.evaluer_criteres(R.stats_completude(flags), cran=cran)
    elig = R.eligibilite(crit)
    return crit, elig, R.synthese(elig)

# ---------- lecture de Data.md ----------
def bloc(txt, motif):
    """Dernier bloc dont le titre (## ...) correspond à `motif` ; renvoie (début, fin, texte) ou None."""
    ms = list(re.finditer(rf"(?m)^## {motif}.*$", txt))
    if not ms:
        return None
    d = ms[-1].start()
    nxt = re.search(r"(?m)^## ", txt[ms[-1].end():])
    f = ms[-1].end() + nxt.start() if nxt else len(txt)
    return d, f, txt[d:f]

# ---------- 1) preparer ----------
def preparer():
    exiger_depot()
    crit, elig, S = calculer()
    txt = C.DATA_MD.read_text(encoding="utf-8") if C.DATA_MD.exists() else ""
    b = bloc(txt, "GEL")
    if b and "[SCELLÉ]" in b[2].splitlines()[0]:
        raise SystemExit("Un gel est déjà SCELLÉ. Toute modification = amendement daté (fait nouveau, 2e validation), pas un nouveau gel.")
    if b:                                                          # un brouillon n'est pas un fait : on le remplace
        txt = txt[:b[0]].rstrip() + "\n" + txt[b[1]:]
        C.DATA_MD.write_text(txt, encoding="utf-8")
    am = C.ROOT / "amendement_H3.md"
    if am.exists() and "## AMENDEMENT H3" not in txt:
        with open(C.DATA_MD, "a", encoding="utf-8") as f:
            f.write("\n\n" + am.read_text(encoding="utf-8").strip() + "\n")
    elif not am.exists() and "## AMENDEMENT H3" not in txt:
        print("ATTENTION : aucun amendement H3 dans Data.md ni amendement_H3.md à la racine.")
    ecarts = {k: (C.SEUILS_DEPART[k], v, C.MOTIFS_ECARTS.get(k, "MOTIF MANQUANT")) for k, v in C.SEUILS.items() if v != C.SEUILS_DEPART[k]}
    perdus, front = elig[~elig["eligible"]], crit[crit["frontiere"]]
    L = [f"- commit2: À REMPLIR", f"- hash_seuils: {C.hash_seuils()}", f"- seuils_finaux: {json.dumps(C.SEUILS)}",
         f"- ecarts_vs_depart: {json.dumps(ecarts, ensure_ascii=False) if ecarts else 'aucun'}",
         f"- covariables_coeur: {C.COVARIABLES_COEUR}",
         "- pays_perdus_par_variable (règle déclenchée) :"]
    L += [f"  - {r.iso3} | {r.niveau} | {r.variable} | {r.regle_declenchee}" for r in perdus.itertuples()] or ["  - aucun"]
    L += [f"- N_coupe: {S['n_base']} {S['n_groupes_base']}", f"- N_panel: {S['n_panel']} {S['n_groupes_panel']}",
          f"- conditionnel: N={S['n_cond']} {S['n_groupes_cond']}, k={S['k']}, ddl={S['ddl']}, realisable={S['conditionnel_ok']}",
          f"- extensions (N par extension): { {v: len(s) for v, s in S['par_extension'].items()} }",
          "- pays_frontiere (à un cran d'un seuil) :"]
    L += [f"  - {r.iso3} | {r.variable} | {r.critere}={r.valeur:g} vs {r.seuil:g}" for r in front.itertuples()] or ["  - aucun"]
    L += [f"- alertes_4.6: {S['alertes'] or 'aucune'}", "- valide_par: À REMPLIR"]
    R.consigner("GEL", L, statut="BROUILLON")
    (C.TABLES / "gel_brouillon.md").write_text("\n".join(L), encoding="utf-8")
    print("\n".join(L))
    print(f"\n>>> Écrit dans {C.DATA_MD}. Fais relire la section GEL (et l'amendement H3) par une AUTRE personne, puis :\n"
          '    python 04_eligibilite.py sceller --validateur "Nom Prénom"')

# ---------- 2) sceller ----------
def sceller_bloc(txt, motif, h, mention):
    b = bloc(txt, motif)
    if not b:
        return txt
    nouveau = (b[2].replace("[BROUILLON]", "[SCELLÉ]", 1).replace("[PROPOSÉ]", "[VALIDÉ]", 1)
               .replace("- commit2: À REMPLIR", f"- commit2: {h}").replace("- valide_par: À REMPLIR", f"- valide_par: {mention}"))
    return txt[:b[0]] + nouveau + txt[b[1]:]

def sceller(validateur, solo):
    exiger_depot()
    if not validateur:
        raise SystemExit('Précise --validateur "Nom Prénom" (la personne qui a relu).')
    txt = C.DATA_MD.read_text(encoding="utf-8")
    b = bloc(txt, "GEL")
    if not b or "[BROUILLON]" not in b[2].splitlines()[0]:
        raise SystemExit("Pas de brouillon de gel dans Data.md : lance d'abord `preparer`.")
    if C.hash_seuils() not in b[2]:
        raise SystemExit("config.py a changé depuis `preparer` : relance `preparer` (le brouillon n'est plus valable).")
    auteur = git("config", "user.name").stdout.strip()
    if not solo and validateur.strip().lower() == auteur.lower():
        raise SystemExit("Le validateur doit être une AUTRE personne que l'auteur du commit. "
                         "Si tu travailles seul : --solo (consigné comme déviation au protocole).")
    mention = validateur if not solo else f"{validateur} (VALIDATION SOLO — déviation au protocole, à écrire dans les limites)"
    git("add", "src", "Data.md", ".gitignore")
    r = git("commit", "-m", "Commit 2 : gel des seuils et amendement H3")
    if r.returncode != 0:
        raise SystemExit("Commit 2 impossible :\n" + (r.stderr or r.stdout))
    h = git("rev-parse", "--short", "HEAD").stdout.strip()
    for titre in ("GEL", "AMENDEMENT H3", "CAS NON PRÉVU"):         # scelle aussi les cas non prévus consignés
        txt = sceller_bloc(txt, titre, h, mention)
    C.DATA_MD.write_text(txt, encoding="utf-8")
    git("add", "Data.md")
    git("commit", "-m", f"Data.md : sceau du gel (commit 2 = {h})")
    print(f"Gel SCELLÉ. Commit 2 = {h} ; validé par : {mention}")

# ---------- 3) appliquer ----------
def verifier_gel():
    if not C.DATA_MD.exists():
        raise SystemExit("Data.md introuvable : lance `preparer` puis `sceller`.")
    b = bloc(C.DATA_MD.read_text(encoding="utf-8"), "GEL")
    if not b or "[SCELLÉ]" not in b[2].splitlines()[0]:
        raise SystemExit("Gel non scellé : lance `preparer`, fais relire, puis `sceller`.")
    e = b[2]
    commit = re.search(r"(?m)^- commit2:\s*([0-9a-f]{7,40})\s*$", e)
    h = re.search(r"(?m)^- hash_seuils:\s*([0-9a-f]{64})", e)
    if not commit: raise SystemExit("Entrée de gel sans commit 2 valide.")
    if not h or h.group(1) != C.hash_seuils():
        raise SystemExit("Les paramètres de config.py ≠ ceux gelés. Après gel : amendement daté (fait nouveau, 2e validation).")
    if git("cat-file", "-e", f"{commit.group(1)}^{{commit}}").returncode != 0:
        raise SystemExit(f"Commit {commit.group(1)} introuvable dans git.")
    if git("diff", "--quiet", commit.group(1), "--", "src/config.py").returncode != 0:
        raise SystemExit("src/config.py a été modifié depuis le commit 2. Retouche silencieuse interdite : amendement daté.")
    print(f"Gel vérifié : commit {commit.group(1)}, config.py identique au commit 2.")

def appliquer(cran=0):
    verifier_gel()
    crit, elig, S = calculer(cran)
    if S["alertes"]:
        raise SystemExit("ALERTES rubrique 4.6 -> remonter à l'équipe : " + " ; ".join(S["alertes"]))
    suf = "" if cran == 0 else f"_cran{cran:+d}"
    elig.to_csv(C.PROC / f"eligibilite{suf}.csv", index=False)
    crit.to_csv(C.PROC / f"criteres{suf}.csv", index=False)
    elig[~elig["eligible"]].assign(date=dt.date.today().isoformat()).to_csv(C.PROC / f"journal_pays_perdus{suf}.csv", index=False)
    json.dump(S, open(C.PROC / f"synthese_gel{suf}.json", "w"), indent=2, ensure_ascii=False)
    if cran == 0:                                                   # marquer plutôt que supprimer
        long = pd.read_csv(C.PROC / "long.csv")
        w = elig.assign(v=elig["eligible"].astype(int)).pivot_table(index=["iso3", "variable"], columns="niveau", values="v", aggfunc="first")
        w.columns = [f"elig_{c}" for c in w.columns]
        long.merge(w.reset_index(), on=["iso3", "variable"], how="left").to_csv(C.PROC / "long_flags.csv", index=False)
    print(f"N coupe = {S['n_base']} {S['n_groupes_base']} | panel = {S['n_panel']} | conditionnel réalisable = {S['conditionnel_ok']} (N={S['n_cond']}, ddl={S['ddl']})")

if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("mode", choices=["preparer", "sceller", "appliquer"])
    ap.add_argument("--validateur"); ap.add_argument("--solo", action="store_true")
    ap.add_argument("--cran", type=int, default=0, choices=[-1, 0, 1])
    a = ap.parse_args()
    if a.mode == "preparer": preparer()
    elif a.mode == "sceller": sceller(a.validateur, a.solo)
    else: appliquer(a.cran)