import scobra, modeling_phased
import pandas as pd
from scipy.stats import pearsonr

def corr(m, CO2_obj, phloem_obj, anchors=["CO2_tx"], sig=0.05, filters=["link", "phase"]):
    assert(len(CO2_obj) == 4)
    assert(phloem_obj <= 0)
    
    m.SetObjective({"phloem_biomass": phloem_obj})
    m.SetObjective({"CO2_tx1_phase1": CO2_obj[0], 
                    "CO2_tx1_phase2": CO2_obj[1], 
                    "CO2_tx1_phase3": CO2_obj[2], 
                    "CO2_tx1_phase4": CO2_obj[3]})
    m.SetObjDirec("Min")
    m.MinFluxSolve()
    print(m.GetStatusMsg())
    
    df = modeling_phased.create_df_from_sol(m, filters)
    labels = [l for l in df.index.values]
    fluxes = {l: df.loc[l].tolist() for l in labels}
    
    correlations = {}
    for a in anchors:
        anchor = fluxes[a]
        c = {}
        for reac,flux in fluxes.items():
            if len(set(flux)) != 1 and reac != a:
                correlation = pearsonr(anchor, flux)[1]
                if correlation <= sig:
                    c[reac] = flux
        correlations[a] = (anchor, c)
    
    for anchor,tuple in correlations.items():
        flux = [round(f, 5) for f in tuple[0]]
        print("\n{}: {}".format(anchor, flux))
        for reac,flux in tuple[1].items():
            flux = [round(f, 5) for f in flux]
            print("\t{}: {}".format(reac, flux))
    
    return correlations




