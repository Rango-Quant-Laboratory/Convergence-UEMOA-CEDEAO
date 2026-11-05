"""Étape 7 — Tests sur jouet (AVANT les vraies données).
T1 : σ à la main sur 3 pays vs fonction du script.
T2 : données simulées avec vitesse de convergence connue -> l'estimateur la retrouve.
T3 : données simulées avec trou volontaire -> le script le détecte et journalise le pays.
Usage : python 07_tests_jouet.py   (s'arrête avec une erreur si un test échoue)"""
import numpy as np
import pandas as pd
import config as C
import regles as R

def test_sigma_main():
    # Calcul « Excel » à la main : STDEV.S de ln(1000), ln(2000), ln(4000) = ln 2 = 0.693147 ; puis ln(1000), ln(1500), ln(2250) = ln 1.5 = 0.405465
    df = pd.DataFrame({"iso3": list("ABC") * 2, "year": [2000] * 3 + [2001] * 3,
                       "y": [1000, 2000, 4000, 1000, 1500, 2250]})
    df["ln"] = np.log(df["y"])
    s = R.sigma_dispersion(df, "ln", ddof=1)
    assert abs(s[2000] - 0.693147) < 1e-5, s
    assert abs(s[2001] - 0.405465) < 1e-5, s
    s0 = R.sigma_dispersion(df, "ln", ddof=0)                       # écart-type de population = h·√(2/3)
    assert abs(s0[2000] - 0.693147 * np.sqrt(2 / 3)) < 1e-5
    assert s[2001] < s[2000]                                        # la dispersion baisse : σ-convergence
    try:                                                            # composition variable -> doit lever une erreur
        R.sigma_dispersion(df.iloc[:5], "ln"); raise AssertionError("composition variable non détectée")
    except ValueError:
        pass

def test_vitesse_connue(seed=0, n=5000, T=C.T_COUPE):
    rng = np.random.default_rng(seed)
    for lam in (0.0, 0.01, 0.03):
        y0 = rng.normal(7.5, 0.6, n); ystar = 9.0
        yT = np.exp(-lam * T) * y0 + (1 - np.exp(-lam * T)) * ystar + rng.normal(0, 0.1, n)
        g = (yT - y0) / T                                           # croissance annualisée
        b = R.ols(g, y0)[1]
        lam_hat = R.vitesse_depuis_beta(b, T)
        assert abs(lam_hat - lam) < 0.002, f"λ vrai {lam}, retrouvé {lam_hat:.4f}"
        print(f"   λ vrai = {lam:.3f} -> retrouvé = {lam_hat:.4f} (β = {b:.5f})")

def test_trou_volontaire():
    rows = []
    trous = {"AAA": range(1999, 2004), "BBB": range(1990, 1994), "CCC": []}   # AAA : trou interne de 5 ans ; BBB : début manquant
    for iso, t in trous.items():
        for y in C.ANNEES:
            rows.append(dict(iso3=iso, year=y, variable="gdppc_wdi", source="WDI", observe=y not in t, in_source=True))
    flags = pd.DataFrame(rows)
    st = R.stats_completude(flags).set_index("iso3")
    assert st.loc["AAA", "annees_trous"] == "1999,2000,2001,2002,2003" and st.loc["AAA", "gap_max"] == 5
    assert st.loc["BBB", "premiere_annee"] == 1994 and st.loc["BBB", "n_obs_debut"] == 1
    assert st.loc["CCC", "gap_max"] == 0
    elig = R.eligibilite(R.evaluer_criteres(st.reset_index()))
    journal = elig[(~elig["eligible"]) & (elig["niveau"] == "coupe_base")].set_index("iso3")
    assert set(journal.index) == {"AAA", "BBB"}, journal            # CCC non journalisé
    assert "gap_max" in journal.loc["AAA", "regle_declenchee"]
    assert "n_obs_debut" in journal.loc["BBB", "regle_declenchee"]
    print("   journal :", journal["regle_declenchee"].to_dict())

if __name__ == "__main__":
    tests = [("T1 σ à la main (3 pays)", test_sigma_main),
             ("T2 vitesse de convergence connue retrouvée", test_vitesse_connue),
             ("T3 trou volontaire détecté et journalisé", test_trou_volontaire)]
    for nom, f in tests:
        f(); print(f"OK  {nom}")
    print("Les 3 tests passent.")
