import scobra
import pandas as pd
from scipy.stats import pearsonr

def create_df_from_sol(m, filters):
    rtp = []
    for f in filters:
        for x in [r.id for r in m.reactions if f in r.id]:
            rtp.append(x)
    
    sol = m.GetSol(IncZeroes = True, AsMtx = True, reacs = rtp)
    df = pd.DataFrame(sol)
    
    if "CO2_tx1_phase1" and "CO2_tx1_phase2" and "CO2_tx1_phase3" and "CO2_tx1_phase4" and "CO2_tx1_phase1_reverse" and "CO2_tx1_phase2_reverse" and "CO2_tx1_phase3_reverse" and "CO2_tx1_phase4_reverse" in rtp:
        CO2_phase1 = df.loc["CO2_tx1_phase1", "Flux"] - df.loc["CO2_tx1_phase1_reverse", "Flux"]
        CO2_phase2 = df.loc["CO2_tx1_phase2", "Flux"] - df.loc["CO2_tx1_phase2_reverse", "Flux"]
        CO2_phase3 = df.loc["CO2_tx1_phase3", "Flux"] - df.loc["CO2_tx1_phase3_reverse", "Flux"]
        CO2_phase4 = df.loc["CO2_tx1_phase4", "Flux"] - df.loc["CO2_tx1_phase4_reverse", "Flux"]
        
        CO2_combined = pd.DataFrame({"Flux": [CO2_phase1, CO2_phase2, CO2_phase3, CO2_phase4]}, 
                                        index = ["CO2_tx1_phase1", "CO2_tx1_phase2", "CO2_tx1_phase3", "CO2_tx1_phase4"])                                          
        
        df = df.drop(["CO2_tx1_phase1", "CO2_tx1_phase2", "CO2_tx1_phase3", "CO2_tx1_phase4", 
                 "CO2_tx1_phase1_reverse", "CO2_tx1_phase2_reverse", "CO2_tx1_phase3_reverse", "CO2_tx1_phase4_reverse"])
        
        df = df.append(CO2_combined, verify_integrity = True)
    
    #Changes matrix from Phased Reaction x Flux to be Phased Flux x Reaction
    count = 0
    fluxes = []
    newdf = {}
    for row in df.itertuples():
        fluxes.append(row[1])
        count += 1
        
        if count % 4 == 0:
            newdf[row[0]] = fluxes
            fluxes = []
    
    df = pd.DataFrame(newdf, index = ['Phase 1', 'Phase 2', "Phase 3", "Phase 4"])
    
    rename_reacs = {}
    for i in range(len(df.columns)): #list(df)[i]=df.columns[i]=list(df.columns)[i], list(df.index)[i]=df.index[i]
        if "1_phase4" in df.columns[i]:
            rename_reacs[df.columns[i]] = df.columns[i].replace("1_phase4", "")
        elif "4_1" in df.columns[i]:
            rename_reacs[df.columns[i]] = df.columns[i].replace("4_1", "")
        else:
            raise Exception
    
    df = df.rename(index = str, columns = rename_reacs)
    
    return df.T

def corr(m, CO2_obj, phloem_obj, sig=0.05, anchors=["CO2_tx"], filters=["link", "phase"]):
    assert(len(CO2_obj) == 4)
    assert(phloem_obj >= 0)
    
    m.SetObjective({"phloem_biomass": -phloem_obj})
    m.SetObjective({"CO2_tx1_phase1": CO2_obj[0], 
                    "CO2_tx1_phase2": CO2_obj[1], 
                    "CO2_tx1_phase3": CO2_obj[2], 
                    "CO2_tx1_phase4": CO2_obj[3]})
    m.SetObjDirec("Min")
    m.MinFluxSolve()
    print(m.GetStatusMsg())
    
    df = create_df_from_sol(m, filters)
    labels = [l for l in df.index.values]
    fluxes = {l: df.loc[l].tolist() for l in labels}
    
    correlations = {}
    for a in anchors:
        anchor = fluxes[a]
        c = {}
        for reac,flux in fluxes.items():
            correlation = pearsonr(anchor, flux)[1]
            if correlation <= sig:
                c[reac] = flux
        correlations[a] = (anchor, c)
    
    return correlations




