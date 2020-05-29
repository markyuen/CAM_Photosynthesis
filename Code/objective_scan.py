import scobra, sys, modeling_phased
import pandas as pd
from xlsxwriter import Workbook

def write(m, CO2_obj, phloem_obj, filters):
    assert(len(CO2_obj) == 4)
    assert(phloem_obj <= 0)
    
    m.SetObjective({"phloem_biomass": phloem_obj})
    m.SetObjDirec("Min")
    m.MinFluxSolve()
    df = modeling_phased.oneddf(m, filters)
    labels = [l for l in df.index.values]
    labelslen = len(labels)
    
    book = Workbook("{}{}{}{}-{}-complete_scan.xlsx".format(CO2_obj[0], CO2_obj[1], CO2_obj[2], CO2_obj[3], abs(phloem_obj)))
    sheets = [0,1]
    sheets[0] = book.add_worksheet("Run Info")
    sheets[1] = book.add_worksheet("{}-{}-{}-{}".format(CO2_obj[0], CO2_obj[1], CO2_obj[2], CO2_obj[3]))
    
    ''' Populating first sheet '''
    sheets[0].write(0,0,"CO2 base weights: {}".format(CO2_obj))
    sheets[0].write(1,0,"Phloem objective value: {}".format(phloem_obj))
    sheets[0].write(2,0,"Iterations: {}".format(100))
    sheets[0].write(3,0,"Fixed photon flux: {}".format(m.GetSol(f='Photon_tx',IncZeroes=True)))
    sheets[0].write(4,0,"Fixed ATPase flux: {}".format(m.GetSol(f='ATPase_tx',IncZeroes=True)))
    sheets[0].write(5,0,"Fixed NADPH flux: {}".format(m.GetSol(f='NADPHoxc_tx',IncZeroes=True)))
    sheets[0].write(6,0,"Reactions included: {}".format(labels))
    
    ''' Populating second sheet '''
    first_column_names = ["CO2 Weight Multiplier", "phloem_biomass", "CO2_tx1", "CO2_tx2", "CO2_tx3", "CO2_tx4", "ObjVal"]
    column_names = first_column_names + [l.replace("1_phase", "") for l in labels]
    for j in range(len(column_names)):
        sheets[1].write(0,j,column_names[j])
    
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
            phloembiomass = m.GetSol(f = "phloem_biomass",IncZeroes=True)["phloem_biomass"]
            
            phase1sum = m.GetSol(f = "CO2_tx1_phase1",IncZeroes=True)
            phase1sum["CO2_tx1_phase1_reverse"] = -phase1sum["CO2_tx1_phase1_reverse"]
            phase1sum = sum(phase1sum.values())
            phase2sum = m.GetSol(f = "CO2_tx1_phase2",IncZeroes=True)
            phase2sum["CO2_tx1_phase2_reverse"] = -phase2sum["CO2_tx1_phase2_reverse"]
            phase2sum = sum(phase2sum.values())
            phase3sum = m.GetSol(f = "CO2_tx1_phase3",IncZeroes=True)
            phase3sum["CO2_tx1_phase3_reverse"] = -phase3sum["CO2_tx1_phase3_reverse"]
            phase3sum = sum(phase3sum.values())
            phase4sum = m.GetSol(f = "CO2_tx1_phase4",IncZeroes=True)
            phase4sum["CO2_tx1_phase4_reverse"] = -phase4sum["CO2_tx1_phase4_reverse"]
            phase4sum = sum(phase4sum.values())
            
            sheets[1].write(i+1,0,i / 100)
            sheets[1].write(i+1,1,phloembiomass)
            sheets[1].write(i+1,2,phase1sum)
            sheets[1].write(i+1,3,phase2sum)
            sheets[1].write(i+1,4,phase3sum)
            sheets[1].write(i+1,5,phase4sum)
            sheets[1].write(i+1,6,m.GetObjVal())
            
            df = modeling_phased.oneddf(m, filters)
            for j in range(labelslen):
                flux = round(df.loc[labels[j], "Flux"], 5)
                sheets[1].write(i+1,j+7,flux)
            
        print(i)
        print(objectives)
        print(m.GetStatusMsg())
    
    book.close()


