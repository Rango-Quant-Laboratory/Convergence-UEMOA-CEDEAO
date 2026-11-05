# Data.md — journal des données (on ajoute, on n'efface jamais : on amende)


## FILTRAGE (contrôles bloquants OK) — 2026-11-05

- 4590 lignes = 15 pays × 34 ans × 9 variables
- fichier PWT : pwt110.dta
- 15 codes ISO3 uniques, 34 années par pays, zéro doublon, pays PWT retrouvés par code


## LECTURE DE LA HEATMAP (diagnostic, non gelé) — 2026-11-05

- Pays éligibles coupe de base (σ, β) : N = 14 {'UEMOA': 7, 'HORS': 7} -> ['BEN', 'BFA', 'CIV', 'CPV', 'GHA', 'GIN', 'GMB', 'LBR', 'MLI', 'NER', 'NGA', 'SEN', 'SLE', 'TGO']
- Covariables du cœur ['popgrow_wdi', 'csh_i_pwt'] (∩ base) : {'popgrow_wdi': ['BEN', 'BFA', 'CIV', 'CPV', 'GHA', 'GIN', 'GMB', 'LBR', 'MLI', 'NER', 'NGA', 'SEN', 'SLE', 'TGO'], 'csh_i_pwt': ['BEN', 'BFA', 'CIV', 'CPV', 'GHA', 'GIN', 'GMB', 'LBR', 'MLI', 'NER', 'NGA', 'SEN', 'SLE', 'TGO']}
- Extensions (∩ base) : {'inv_wdi': ['BEN', 'BFA', 'CIV', 'GHA', 'GIN', 'GMB', 'MLI', 'NER', 'SEN', 'SLE', 'TGO'], 'trade_wdi': ['BEN', 'BFA', 'CIV', 'CPV', 'GHA', 'GIN', 'GMB', 'MLI', 'NER', 'SEN', 'SLE', 'TGO'], 'hc_pwt': ['BEN', 'BFA', 'CIV', 'GHA', 'GMB', 'LBR', 'MLI', 'NER', 'NGA', 'SEN', 'SLE', 'TGO']}
- Conditionnel : N commun = 14 {'UEMOA': 7, 'HORS': 7}, k = 4, ddl = 10, réalisable = True
- Panel : N = 15 {'UEMOA': 8, 'HORS': 7} -> ['BEN', 'BFA', 'CIV', 'CPV', 'GHA', 'GIN', 'GMB', 'GNB', 'LBR', 'MLI', 'NER', 'NGA', 'SEN', 'SLE', 'TGO']

### Pays frontière (à un cran d'un seuil) -> robustesse ±1 cran
aucun

### Anomalies systémiques (alertes)
aucune

### Pays × variable absents (parade 4.3, pas une alerte)
- CPV / hc_pwt : variable entièrement absente -> pays perdu pour cette covariable (parade 4.3)
- GIN / hc_pwt : variable entièrement absente -> pays perdu pour cette covariable (parade 4.3)
- GNB / hc_pwt : variable entièrement absente -> pays perdu pour cette covariable (parade 4.3)
- CPV / inv_wdi : variable entièrement absente -> pays perdu pour cette covariable (parade 4.3)
- LBR / inv_wdi : variable entièrement absente -> pays perdu pour cette covariable (parade 4.3)
- NGA / inv_wdi : variable entièrement absente -> pays perdu pour cette covariable (parade 4.3)
- LBR / trade_wdi : variable entièrement absente -> pays perdu pour cette covariable (parade 4.3)
- NGA / trade_wdi : variable entièrement absente -> pays perdu pour cette covariable (parade 4.3)

### Alertes rubrique 4.6
aucune

### Conclusion pour l'étape 4
Aucune alerte : valeurs de départ gelables telles quelles.


## AMENDEMENT H3 — 2026-11-05 [VALIDÉ]

- remplace l'amendement « option B » (proposé, jamais validé)
- motif (fait nouveau sur les données, pas un résultat) :
  - capital humain PWT 11 (hc) : absent en entier pour CPV, GIN, GNB
  - investissement WDI (NE.GDI.FTOT.ZS) : absent en entier pour CPV, LBR, NGA
  - avec les trois covariables initiales : N commun = 10, k = 5, ddl = 5 < 8 -> conditionnel abandonné
- ancienne H3 : coefficient négatif après contrôle de l'investissement, de la démographie et du capital humain
- nouvelle H3 : coefficient négatif après contrôle de la démographie (WDI SP.POP.GROW) et de la part de formation brute de capital (PWT csh_i), et plus fort en valeur absolue que le coefficient absolu sur le même échantillon (les 14 pays de la base)
- extensions (sous-échantillons propres, chacune comparée à son propre modèle absolu, descriptives) : capital humain hc (N = 12) ; investissement WDI (N = 11), test de sensibilité sur la mesure de l'investissement
- chiffres de départ (non gelés) : cœur N = 14 (7 UEMOA / 7 hors UEMOA), k = 4, ddl = 10
- alternatives écartées : (a) démographie + hc : N = 12 (7/5), ddl = 8, pile sur trois planchers, sans variable d'épargne ; (b) trois covariables : conditionnel abandonné
- source ajoutée au tableau des variables : csh_i (PWT 11), part de formation brute de capital aux PPA courantes
- limites à écrire : csh_i aux PPA courantes mélange quantité et prix relatif de l'investissement ; drapeau i_cig : 17 années sur 34 extrapolées pour 8 pays (BFA, CPV, GHA, GMB, GNB, LBR, NER, TGO) ; couverture complète ≠ mesure complète ; capital humain seulement en extension
- valide_par: Armando (VALIDATION SOLO — déviation au protocole, à écrire dans les limites)
## COLLECTE WDI — 2026-11-05

- source: WDI (API wbgapi, db=2)
- date_telechargement: 2026-11-05T12:32:16
- indicateurs: ['NY.GDP.PCAP.PP.KD', 'NE.GDI.FTOT.ZS', 'SP.POP.GROW', 'NE.TRD.GNFS.ZS']
- pays: ['BEN', 'BFA', 'CIV', 'GNB', 'MLI', 'NER', 'SEN', 'TGO', 'CPV', 'GMB', 'GHA', 'GIN', 'LBR', 'NGA', 'SLE']
- periode: [1990, 2023]
- wbgapi_version: 1.0.14
- derniere_maj_source: 2026-10-08


## FILTRAGE (contrôles bloquants OK) — 2026-11-05

- 4590 lignes = 15 pays × 34 ans × 9 variables
- fichier PWT : pwt110.dta
- 15 codes ISO3 uniques, 34 années par pays, zéro doublon, pays PWT retrouvés par code


## LECTURE DE LA HEATMAP (diagnostic, non gelé) — 2026-11-05

- Pays éligibles coupe de base (σ, β) : N = 14 {'UEMOA': 7, 'HORS': 7} -> ['BEN', 'BFA', 'CIV', 'CPV', 'GHA', 'GIN', 'GMB', 'LBR', 'MLI', 'NER', 'NGA', 'SEN', 'SLE', 'TGO']
- Covariables du cœur ['popgrow_wdi', 'csh_i_pwt'] (∩ base) : {'popgrow_wdi': ['BEN', 'BFA', 'CIV', 'CPV', 'GHA', 'GIN', 'GMB', 'LBR', 'MLI', 'NER', 'NGA', 'SEN', 'SLE', 'TGO'], 'csh_i_pwt': ['BEN', 'BFA', 'CIV', 'CPV', 'GHA', 'GIN', 'GMB', 'LBR', 'MLI', 'NER', 'NGA', 'SEN', 'SLE', 'TGO']}
- Extensions (∩ base) : {'inv_wdi': ['BEN', 'BFA', 'CIV', 'GHA', 'GIN', 'GMB', 'MLI', 'NER', 'SEN', 'SLE', 'TGO'], 'trade_wdi': ['BEN', 'BFA', 'CIV', 'CPV', 'GHA', 'GIN', 'GMB', 'MLI', 'NER', 'SEN', 'SLE', 'TGO'], 'hc_pwt': ['BEN', 'BFA', 'CIV', 'GHA', 'GMB', 'LBR', 'MLI', 'NER', 'NGA', 'SEN', 'SLE', 'TGO']}
- Conditionnel : N commun = 14 {'UEMOA': 7, 'HORS': 7}, k = 4, ddl = 10, réalisable = True
- Panel : N = 15 {'UEMOA': 8, 'HORS': 7} -> ['BEN', 'BFA', 'CIV', 'CPV', 'GHA', 'GIN', 'GMB', 'GNB', 'LBR', 'MLI', 'NER', 'NGA', 'SEN', 'SLE', 'TGO']

### Pays frontière (à un cran d'un seuil) -> robustesse ±1 cran
aucun

### Anomalies systémiques (alertes)
aucune

### Pays × variable absents (parade 4.3, pas une alerte)
- CPV / hc_pwt : variable entièrement absente -> pays perdu pour cette covariable (parade 4.3)
- GIN / hc_pwt : variable entièrement absente -> pays perdu pour cette covariable (parade 4.3)
- GNB / hc_pwt : variable entièrement absente -> pays perdu pour cette covariable (parade 4.3)
- CPV / inv_wdi : variable entièrement absente -> pays perdu pour cette covariable (parade 4.3)
- LBR / inv_wdi : variable entièrement absente -> pays perdu pour cette covariable (parade 4.3)
- NGA / inv_wdi : variable entièrement absente -> pays perdu pour cette covariable (parade 4.3)
- LBR / trade_wdi : variable entièrement absente -> pays perdu pour cette covariable (parade 4.3)
- NGA / trade_wdi : variable entièrement absente -> pays perdu pour cette covariable (parade 4.3)

### Alertes rubrique 4.6
aucune

### Conclusion pour l'étape 4
Aucune alerte : valeurs de départ gelables telles quelles.


## GEL — 2026-11-05 [SCELLÉ]

- commit2: 5800e2f
- hash_seuils: 411422bf5cf4dc3086b0b8ee91b434d18ed0f6739edea47061fe63a89e389765
- seuils_finaux: {"N_min": 12, "N_min_groupe": 5, "df_min": 8, "pib_n_obs": 31, "pib_gap_max": 2, "pib_bord_min": 3, "covar_n_obs": 27, "panel_pays_min": 12, "panel_blocs_min": 5, "bloc_valide_min": 3, "rupture_dlog": 0.15, "dominant_part": 0.3}
- ecarts_vs_depart: aucun
- covariables_coeur: ['popgrow_wdi', 'csh_i_pwt']
- pays_perdus_par_variable (règle déclenchée) :
  - GNB | coupe_base | gdppc_wdi | statut_groupe_non_constant
  - CPV | covariable | inv_wdi | n_obs=0 (exigé >= 27)
  - LBR | covariable | inv_wdi | n_obs=0 (exigé >= 27)
  - NGA | covariable | inv_wdi | n_obs=0 (exigé >= 27)
  - LBR | covariable | trade_wdi | n_obs=0 (exigé >= 27)
  - NGA | covariable | trade_wdi | n_obs=0 (exigé >= 27)
  - CPV | covariable | hc_pwt | n_obs=0 (exigé >= 27)
  - GIN | covariable | hc_pwt | n_obs=0 (exigé >= 27)
  - GNB | covariable | hc_pwt | n_obs=0 (exigé >= 27)
- N_coupe: 14 {'UEMOA': 7, 'HORS': 7}
- N_panel: 15 {'UEMOA': 8, 'HORS': 7}
- conditionnel: N=14 {'UEMOA': 7, 'HORS': 7}, k=4, ddl=10, realisable=True
- extensions (N par extension): {'inv_wdi': 11, 'trade_wdi': 12, 'hc_pwt': 12}
- pays_frontiere (à un cran d'un seuil) :
  - aucun
- alertes_4.6: aucune
- valide_par: Armando (VALIDATION SOLO — déviation au protocole, à écrire dans les limites)


## CONSTRUCTION DES VARIABLES (étape 5) — 2026-11-05

- coupe WDI : 14 pays de la base avec revenu initial (moy. logs (1990, 1994)) et final ((2019, 2023)), T = 29 ans
- panel WDI : 15 pays, 75 intervalles de croissance valides (max 75)
- panel PWT (rgdpo/pop) : 15 pays, 75 intervalles de croissance valides (max 75)
- blocs à appartenance mixte (cas non prévu, règle « majorité des années ») : GNB 1995–1999 (part UEMOA 0.6 -> UEMOA)
- covariables : moyennes sur 1990–2023 ; ln_s (csh_i), ln_ngd (croissance démographique + 0,05), ln_hc : transformations PROVISOIRES, à confirmer dans equations.md
- contrôles de fin de chaîne OK (510 lignes de départ ; base = 14 × 34 = 476)
- journal des pays perdus : 9 lignes (processed/journal_pays_perdus.csv)
- statistiques min/max du PIB/hab. affichées pour lecture manuelle : non (option --stats-manuelles non utilisée)


## CONSTRUCTION DES VARIABLES (étape 5) — 2026-11-05

- coupe WDI : 14 pays de la base avec revenu initial (moy. logs (1990, 1994)) et final ((2019, 2023)), T = 29 ans
- panel WDI : 15 pays, 75 intervalles de croissance valides (max 75)
- panel PWT (rgdpo/pop) : 15 pays, 75 intervalles de croissance valides (max 75)
- blocs à appartenance mixte (cas non prévu, règle « majorité des années ») : GNB 1995–1999 (part UEMOA 0.6 -> UEMOA)
- covariables : moyennes sur 1990–2023 ; ln_s (csh_i), ln_ngd (croissance démographique + 0,05), ln_hc : transformations PROVISOIRES, à confirmer dans equations.md
- contrôles de fin de chaîne OK (510 lignes de départ ; base = 14 × 34 = 476)
- journal des pays perdus : 9 lignes (processed/journal_pays_perdus.csv)
- statistiques min/max du PIB/hab. affichées pour lecture manuelle : non (option --stats-manuelles non utilisée)


## RUPTURES ET SOURCES CROISÉES (étape 6) — 2026-11-05

### Alertes de rupture (seuil 0.15) : 20 (pays, année, ampleur par source, classement)
```
iso3  year  ampleur_wdi  ampleur_pwt                            classement
 CPV  1994        0.155        0.047 artefact WDI (à estimer avec et sans)
 CPV  2020       -0.234       -0.234                 réelle (deux sources)
 CPV  2022        0.141        0.155 artefact PWT (à estimer avec et sans)
 GNB  1998       -0.273       -0.204                 réelle (deux sources)
 LBR  1992       -0.490       -0.490                 réelle (deux sources)
 LBR  1993       -0.439       -0.439                 réelle (deux sources)
 LBR  1994       -0.243       -0.243                 réelle (deux sources)
 LBR  1997        0.646        0.646                 réelle (deux sources)
 LBR  1998        0.163        0.163                 réelle (deux sources)
 LBR  2000        0.215        0.215                 réelle (deux sources)
 LBR  2003       -0.367       -0.367                 réelle (deux sources)
 LBR  2007        0.041        0.282 artefact PWT (à estimer avec et sans)
 MLI  1995       -0.014        0.295 artefact PWT (à estimer avec et sans)
 MLI  1996        0.040        0.162 artefact PWT (à estimer avec et sans)
 SLE  1992       -0.192       -0.082 artefact WDI (à estimer avec et sans)
 SLE  1996        0.013       -0.290 artefact PWT (à estimer avec et sans)
 SLE  1997       -0.073       -0.206 artefact PWT (à estimer avec et sans)
 SLE  2002        0.178        0.177                 réelle (deux sources)
 SLE  2013        0.112        0.164 artefact PWT (à estimer avec et sans)
 TGO  1993       -0.152       -0.172                 réelle (deux sources)
```
### Classement des pays WDI vs PWT (corrélation de rang des moyennes de bloc ; niveaux différents attendus)
```
 bloc   periode  n_pays  rho_rang
    0 1990–1994      15     0.471
    1 1995–1999      15     0.521
    2 2000–2004      15     0.600
    3 2005–2009      15     0.914
    4 2010–2014      15     0.929
    5 2015–2019      15     0.961
```
### Signes WDI vs PWT (coupe de base, N = 14)
```
source  beta_abs  interaction
   WDI  -0.00391     -0.00426
   PWT  -0.01981      0.01145
```
- β absolu : signes identiques
- interaction de groupe : SIGNES DIFFÉRENTS -> résultat « FRAGILE », on ne rattrape pas
### Pays dominants (indicatif ; repérés, jamais exclus de la base)
```
         pib_moy groupe  part_groupe  dominant
iso3                                          
CIV    76864.439  UEMOA        0.331      True
NGA   598490.633   HORS        0.785      True
```


## TESTS SUR JOUET (étape 7) — 2026-11-05

- OK : T1 σ à la main (3 pays)
- OK : T2 vitesse de convergence connue retrouvée
- OK : T3 trou volontaire détecté et journalisé
- ces tests doivent être lancés AVANT les vraies données : l'ordre se lit par les dates des sections de ce journal


## RUPTURES ET SOURCES CROISÉES (étape 6) — 2026-11-05

### Alertes de rupture (seuil 0.15) : 20 (pays, année, ampleur par source, classement)
```
iso3  year  ampleur_wdi  ampleur_pwt                            classement
 CPV  1994        0.155        0.047 artefact WDI (à estimer avec et sans)
 CPV  2020       -0.234       -0.234                 réelle (deux sources)
 CPV  2022        0.141        0.155 artefact PWT (à estimer avec et sans)
 GNB  1998       -0.273       -0.204                 réelle (deux sources)
 LBR  1992       -0.490       -0.490                 réelle (deux sources)
 LBR  1993       -0.439       -0.439                 réelle (deux sources)
 LBR  1994       -0.243       -0.243                 réelle (deux sources)
 LBR  1997        0.646        0.646                 réelle (deux sources)
 LBR  1998        0.163        0.163                 réelle (deux sources)
 LBR  2000        0.215        0.215                 réelle (deux sources)
 LBR  2003       -0.367       -0.367                 réelle (deux sources)
 LBR  2007        0.041        0.282 artefact PWT (à estimer avec et sans)
 MLI  1995       -0.014        0.295 artefact PWT (à estimer avec et sans)
 MLI  1996        0.040        0.162 artefact PWT (à estimer avec et sans)
 SLE  1992       -0.192       -0.082 artefact WDI (à estimer avec et sans)
 SLE  1996        0.013       -0.290 artefact PWT (à estimer avec et sans)
 SLE  1997       -0.073       -0.206 artefact PWT (à estimer avec et sans)
 SLE  2002        0.178        0.177                 réelle (deux sources)
 SLE  2013        0.112        0.164 artefact PWT (à estimer avec et sans)
 TGO  1993       -0.152       -0.172                 réelle (deux sources)
```
### Classement des pays WDI vs PWT (corrélation de rang des moyennes de bloc ; niveaux différents attendus)
```
 bloc   periode  n_pays  rho_rang
    0 1990–1994      15     0.471
    1 1995–1999      15     0.521
    2 2000–2004      15     0.600
    3 2005–2009      15     0.914
    4 2010–2014      15     0.929
    5 2015–2019      15     0.961
```
### Signes WDI vs PWT (coupe de base, N = 14)
```
source  beta_abs  interaction
   WDI  -0.00391     -0.00426
   PWT  -0.01981      0.01145
```
- β absolu : signes identiques
- interaction de groupe : SIGNES DIFFÉRENTS -> résultat « FRAGILE », on ne rattrape pas
### Pays dominants (indicatif ; repérés, jamais exclus de la base)
```
         pib_moy groupe  part_groupe  dominant
iso3                                          
CIV    76864.439  UEMOA        0.331      True
NGA   598490.633   HORS        0.785      True
```


## TESTS SUR JOUET (étape 7) — 2026-11-05

- OK : T1 σ à la main (3 pays)
- OK : T2 vitesse de convergence connue retrouvée
- OK : T3 trou volontaire détecté et journalisé
- ces tests doivent être lancés AVANT les vraies données : l'ordre se lit par les dates des sections de ce journal
