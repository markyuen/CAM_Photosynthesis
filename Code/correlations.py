import scobra, modeling_phased
import pandas as pd
from scipy.stats import pearsonr
from xlsxwriter import Workbook

def corr(m, CO2_obj, phloem_obj, filtersp, anchors=["CO2_tx"], filtersc=["link", "phase"], sig=0.05):
    assert(len(CO2_obj) == 4)
    assert(phloem_obj <= 0)
    
    m.SetObjective({"phloem_biomass": phloem_obj})
    m.SetObjDirec("Min")
    m.MinFluxSolve()
    
    df = modeling_phased.create_df_from_sol(m, filtersp)
    labels = [l for l in df.index.values]
    
    dfp = modeling_phased.oneddf(m, filtersp)
    labelsp = [l for l in dfp.index.values]
    labelslenp = len(labelsp)
    
    dfc = modeling_phased.oneddf(m, filtersc)
    labelsc = [l for l in dfc.index.values]
    labelslenc = len(labelsc)
    vectors = {l: [] for l in labelsc}
    
    subset = set(labelsp).issubset(labelsc)
    print("Is subset? {}".format(str(subset)))
    
    book = Workbook("{}{}{}{}-{}-corr.xlsx".format(CO2_obj[0], CO2_obj[1], CO2_obj[2], CO2_obj[3], abs(phloem_obj)))
    sheets = [0,1,2]
    sheets[0] = book.add_worksheet("Run Info")
    sheets[1] = book.add_worksheet("{}-{}-{}-{} Scan".format(CO2_obj[0], CO2_obj[1], CO2_obj[2], CO2_obj[3]))
    sheets[2] = book.add_worksheet("Correlations")
    
    ''' Populating info sheet '''
    sheets[0].write(0,0,"CO2 base weights: {}".format(CO2_obj))
    sheets[0].write(1,0,"Phloem objective value: {}".format(phloem_obj))
    sheets[0].write(2,0,"Iterations: {}".format(100))
    sheets[0].write(3,0,"Fixed photon flux: {}".format(m.GetSol(f='Photon_tx',IncZeroes=True)))
    sheets[0].write(4,0,"Fixed ATPase flux: {}".format(m.GetSol(f='ATPase_tx',IncZeroes=True)))
    sheets[0].write(5,0,"Fixed NADPH flux: {}".format(m.GetSol(f='NADPHoxc_tx',IncZeroes=True)))
    sheets[0].write(6,0,"Reactions printed: {}".format(labels))
    sheets[0].write(7,0,"Correlations included: {}".format(anchors))
    
    ''' Populating scan sheet '''
    first_row_names = ["CO2 Weight Multiplier", "ObjVal", "phloem_biomass", "CO2_tx1", "CO2_tx2", "CO2_tx3", "CO2_tx4"]
    row_names1 = first_row_names + [l.replace("1_phase", "") for l in labelsp]
    for j in range(len(row_names1)):
        sheets[1].write(j,0,row_names1[j])
    
    ''' Writing scans to sheet '''
    prev = [0,0,0,0]
    col = 1
    breakpoints = []
    for i in range(0, 101):
        objectives = [x * i / 100 for x in CO2_obj]
        
        m.SetObjective({'CO2_tx1_phase1': objectives[0], 
                    'CO2_tx1_phase2': objectives[1], 
                    "CO2_tx1_phase3": objectives[2], 
                    "CO2_tx1_phase4": objectives[3]})
        m.SetObjDirec("Min")
        m.MinFluxSolve()
        
        if m.GetStatusMsg() == "no solution":
            sys.stderr.write("ERROR")
        else:
            cont = False
            dfc = modeling_phased.oneddf(m, filtersc)
            CO2_tx = [dfc.loc["CO2_tx1_phase1", "Flux"], dfc.loc["CO2_tx1_phase2", "Flux"], 
                      dfc.loc["CO2_tx1_phase3", "Flux"], dfc.loc["CO2_tx1_phase4", "Flux"]]
            for j in range(4):
                if CO2_tx[j] - prev[j] > 10e-8:
                    cont = True
            
            ''' Only continue to update vectors and print if new breakpoint '''
            if cont:
                ''' Append to vectors for correlations later '''
                for j in range(labelslenc):
                    flux = round(dfc.loc[labelsc[j], "Flux"], 5)
                    vectors[labelsc[j]].append(flux)
                
                ''' Write scans to sheet '''
                phloembiomass = m.GetSol(f = "phloem_biomass",IncZeroes=True)["phloem_biomass"]
                sheets[1].write(0,col,i / 100)
                sheets[1].write(1,col,m.GetObjVal())
                sheets[1].write(2,col,phloembiomass)
                sheets[1].write(3,col,CO2_tx[0])
                sheets[1].write(4,col,CO2_tx[1])
                sheets[1].write(5,col,CO2_tx[2])
                sheets[1].write(6,col,CO2_tx[3])
                
                ''' Not always necessary to make new df '''
                if subset:
                    for j in range(labelslenp):
                        flux = round(dfc.loc[labelsp[j], "Flux"], 5)
                        sheets[1].write(j+7,col,flux)
                else:
                    dfp = modeling_phased.oneddf(m, filtersp)
                    for j in range(labelslenp):
                        flux = round(dfp.loc[labelsp[j], "Flux"], 5)
                        sheets[1].write(j+7,col,flux)
                
                ''' Update prev, col, and breakpoints '''
                prev = CO2_tx
                col = col + 1
                breakpoints.append(i/100)
        
        print(i)
        print(objectives)
        print(m.GetStatusMsg())
    
    ''' Expanding anchors to four phases '''
    phased = []
    for a in anchors:
        for i in range(1, 5):
            phased.append(a + "1_phase" + str(i))
    
    ''' Calculating correlations for each anchor '''
    correlations = {}
    for a in phased:
        anchor = vectors[a]
        c = {}
        for reac,flux in vectors.items():
            ''' Include self here '''
            if len(set(flux)) != 1:
                correlation = pearsonr(anchor, flux)[1]
                if correlation <= sig:
                    c[reac.replace("1_phase", "")] = flux
        ''' Clean reaction names here and above '''
        correlations[a.replace("1_phase", "")] = c
    
    ''' Populating correlation sheet, must be done after iters to calculate breakpoints '''
    second_column_names = ["Anchor", "Correlated Flux"]
    column_names2 = second_column_names + breakpoints
    for j in range(len(column_names2)):
        sheets[2].write(0,j,column_names2[j])
    
    ''' Writing correlations to sheet '''
    breakpointslen = len(breakpoints)
    row = 1
    for anchor,corrs in correlations.items():
        ''' If no correlations, then will not appear on sheet and Pearsonr will sound warning '''
        for reac,flux in corrs.items():
            sheets[2].write(row,0,anchor)
            sheets[2].write(row,1,reac)
            for i in range(breakpointslen):
                sheets[2].write(row,i+2,flux[i])
            row = row + 1
    
    book.close()
    print("Book saved")

# def corr(m, CO2_obj, phloem_obj, anchors=["CO2_tx"], sig=0.05, filters=["link", "phase"]):
#     assert(len(CO2_obj) == 4)
#     assert(phloem_obj <= 0)
#     
#     m.SetObjective({"phloem_biomass": phloem_obj})
#     m.SetObjective({"CO2_tx1_phase1": CO2_obj[0], 
#                     "CO2_tx1_phase2": CO2_obj[1], 
#                     "CO2_tx1_phase3": CO2_obj[2], 
#                     "CO2_tx1_phase4": CO2_obj[3]})
#     m.SetObjDirec("Min")
#     m.MinFluxSolve()
#     print(m.GetStatusMsg())
#     
#     df = modeling_phased.create_df_from_sol(m, filters)
#     labels = [l for l in df.index.values]
#     fluxes = {l: df.loc[l].tolist() for l in labels}
#     
#     correlations = {}
#     for a in anchors:
#         anchor = fluxes[a]
#         c = {}
#         for reac,flux in fluxes.items():
#             if len(set(flux)) != 1 and reac != a:
#                 correlation = pearsonr(anchor, flux)[1]
#                 if correlation <= sig:
#                     c[reac] = flux
#         correlations[a] = (anchor, c)
#     
#     for anchor,tuple in correlations.items():
#         flux = [round(f, 5) for f in tuple[0]]
#         print("\n{}: {}".format(anchor, flux))
#         for reac,flux in tuple[1].items():
#             flux = [round(f, 5) for f in flux]
#             print("\t{}: {}".format(reac, flux))
#     
#     return correlations




