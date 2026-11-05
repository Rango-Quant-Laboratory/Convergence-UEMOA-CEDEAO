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
