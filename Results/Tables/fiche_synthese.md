# Synthèse de lecture (diagnostic sur valeurs de DÉPART, non gelé)

- Pays éligibles coupe de base (σ, β) : N = 14 {'UEMOA': 7, 'HORS': 7} -> ['BEN', 'BFA', 'CIV', 'CPV', 'GHA', 'GIN', 'GMB', 'LBR', 'MLI', 'NER', 'NGA', 'SEN', 'SLE', 'TGO']
- Covariables du cœur ['popgrow_wdi', 'csh_i_pwt'] (∩ base) : {'popgrow_wdi': ['BEN', 'BFA', 'CIV', 'CPV', 'GHA', 'GIN', 'GMB', 'LBR', 'MLI', 'NER', 'NGA', 'SEN', 'SLE', 'TGO'], 'csh_i_pwt': ['BEN', 'BFA', 'CIV', 'CPV', 'GHA', 'GIN', 'GMB', 'LBR', 'MLI', 'NER', 'NGA', 'SEN', 'SLE', 'TGO']}
- Extensions (∩ base) : {'inv_wdi': ['BEN', 'BFA', 'CIV', 'GHA', 'GIN', 'GMB', 'MLI', 'NER', 'SEN', 'SLE', 'TGO'], 'trade_wdi': ['BEN', 'BFA', 'CIV', 'CPV', 'GHA', 'GIN', 'GMB', 'MLI', 'NER', 'SEN', 'SLE', 'TGO'], 'hc_pwt': ['BEN', 'BFA', 'CIV', 'GHA', 'GMB', 'LBR', 'MLI', 'NER', 'NGA', 'SEN', 'SLE', 'TGO']}
- Conditionnel : N commun = 14 {'UEMOA': 7, 'HORS': 7}, k = 4, ddl = 10, réalisable = True
- Panel : N = 15 {'UEMOA': 8, 'HORS': 7} -> ['BEN', 'BFA', 'CIV', 'CPV', 'GHA', 'GIN', 'GMB', 'GNB', 'LBR', 'MLI', 'NER', 'NGA', 'SEN', 'SLE', 'TGO']

## Pays frontière (à un cran d'un seuil) -> robustesse ±1 cran
aucun

## Anomalies systémiques (alertes)
aucune

## Pays × variable absents (parade 4.3, pas une alerte)
- CPV / hc_pwt : variable entièrement absente -> pays perdu pour cette covariable (parade 4.3)
- GIN / hc_pwt : variable entièrement absente -> pays perdu pour cette covariable (parade 4.3)
- GNB / hc_pwt : variable entièrement absente -> pays perdu pour cette covariable (parade 4.3)
- CPV / inv_wdi : variable entièrement absente -> pays perdu pour cette covariable (parade 4.3)
- LBR / inv_wdi : variable entièrement absente -> pays perdu pour cette covariable (parade 4.3)
- NGA / inv_wdi : variable entièrement absente -> pays perdu pour cette covariable (parade 4.3)
- LBR / trade_wdi : variable entièrement absente -> pays perdu pour cette covariable (parade 4.3)
- NGA / trade_wdi : variable entièrement absente -> pays perdu pour cette covariable (parade 4.3)

## Alertes rubrique 4.6
aucune

## Conclusion pour l'étape 4
Aucune alerte : valeurs de départ gelables telles quelles.