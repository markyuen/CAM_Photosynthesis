import scobra
from xlwt import Workbook
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import ast

pd.set_option('display.max_columns', None)  # or 1000
pd.set_option('display.max_rows', None)  # or 1000
pd.set_option('display.max_colwidth', None)  # or 199
pd.set_option('display.width', 1000)

m = scobra.Model("../Final_Files/Constrained_Model_FINAL.json")

'''  For writing solutions to Excel file  '''
def WriteSolution(file_name):
    book = Workbook()
    Solution = book.add_sheet("Solution")
    GetState = book.add_sheet('GetState')
    Metabolites = book.add_sheet("Metabolite Flux")
    Reactions = book.add_sheet("Reaction List")
    
    Solution.write(0, 0, "Reaction")
    Solution.write(0, 1, "Solution")
    
    i = 1
    for reac, sol in m.GetSol(IncZeroes = True).items():
        Solution.write(i, 0, reac)
        Solution.write(i, 1, sol)
        i += 1
    
    GetState.write(0, 0, m.GetState().keys()[0])
    GetState.write(0, 1, m.GetState().keys()[1])
    GetState.write(0, 2, m.GetState().keys()[2])
    GetState.write(0, 3, m.GetState().keys()[3])
    GetState.write(0, 4, m.GetState().keys()[4])
    GetState.write(0, 5, "objective")
    GetState.write(0, 6, m.GetState().keys()[5])
    GetState.write(0, 7, m.GetState().keys()[6])
    GetState.write(0, 8, "lower_bound")
    GetState.write(0, 9, "upper_bound")
    #GetState.write(0,10, "Solution")
    
    GetState.write(1, 0, m.GetState()["objective_direction"])
    #GetState.write(1, 1, str(m.GetState()["solver"]))
    GetState.write(1, 2, m.GetState()["bounds"])
    GetState.write(1, 3, str(m.GetState()["solution"]))
    
    i = 1
    for reac, obj in m.GetState()["objective"].items():
        GetState.write(i, 4, reac)
        GetState.write(i, 5, obj)
        i += 1
    
    GetState.write(1, 6, str(m.GetState()["quaduatic_component"]))
    
    i = 1
    for reac, bound in m.GetState()["constraints"].items():
        GetState.write(i, 7, reac)
        GetState.write(i, 8, bound[0])
        GetState.write(i, 9, bound[1])
        i += 1
    '''
    for i in range(len(m.GetSol(IncZeroes = True))):
        GetState.write(i + 1, 10, Formula("VLOOKUP(H" + str(i + 2) + ",Solution!A:B,2,FALSE)"))
    '''
    Metabolites.write(0, 0, "Metabolite")
    Metabolites.write(0, 1, "Flux Sum")
    
    for i in range(len(m.Metabolites())):
        Metabolites.write(i + 1, 0, m.GetMetaboliteName(m.Metabolites()[i]))
        #Returns abs of metabolite fluxsum
        Metabolites.write(i + 1, 1, m.FluxSum(m.GetMetaboliteName(m.Metabolites()[i])))
    
    Reactions.write(0, 0, "Abbreviation")
    Reactions.write(0, 1, "Reaction")
    
    for i in range(len(m.Reactions())):
        Reactions.write(i + 1, 0, m.GetReactionName(m.Reactions()[i]))
        Reactions.write(i + 1, 1, str(m.GetReaction(m.Reactions()[i])))
    
    book.save(file_name)

'''  For displaying some solutions  '''
def DisplaySolution(filters, flux_min=0):
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
    
    large_flux_dict = {}
    for i in range(len(df.columns)):
        total_flux = abs(df.iat[0, i]) + abs(df.iat[1, i]) + abs(df.iat[2, i]) + abs(df.iat[3, i])
        
        if total_flux > flux_min:
            large_flux_dict[df.columns[i]] = total_flux
    
    df = df.T
    
    print(df)
    print("\n" + str(len(large_flux_dict)) + "/" + str(len(df.index)) + " Fluxes Greater Than " + str(flux_min) + ": ")
    print(large_flux_dict)
    
    return (df, large_flux_dict)

'''  For plotting  '''
def HourlyIntervals(df):
    hourlydata = {}
    for i in range(len(df.T.columns)):
        hourlylist = []
        
        for j in range(12):
            interval = (df.T.iat[1, i] - df.T.iat[0, i]) / 12
            hourlylist.append(df.T.iat[0, i] + interval * j)
        
        hourlylist.append(df.T.iat[1, i])
        
        for j in range(8):
            interval = (df.T.iat[3, i] - df.T.iat[2, i]) / 8
            hourlylist.append(df.T.iat[2, i] + interval * j)
        
        for j in range(3):
            interval = (df.T.iat[0, i] - df.T.iat[3, i]) / 3
            hourlylist.append(df.T.iat[3, i] + interval * j)
        
        hourlydata[df.T.columns[i]] = hourlylist
    
    hourlyindex = []
    for i in range(24):
        if i == 0:
            hourlyindex.append("Phase 1")
        elif i == 12:
            hourlyindex.append("Phase 2")
        elif i == 13:
            hourlyindex.append("Phase 3")
        elif i == 21:
            hourlyindex.append("Phase 4")
        else:
            hourlyindex.append("")
    
    hourlydf = pd.DataFrame(hourlydata, index = hourlyindex)
    
    return hourlydf

objectives = [1, 
              2, 
              4, 
              2, 
              -3192]

m.SetObjective({'CO2_tx1_phase1': objectives[0], 
                'CO2_tx1_phase2': objectives[1], 
                "CO2_tx1_phase3": objectives[2], 
                "CO2_tx1_phase4": objectives[3]})

m.SetObjective ({"phloem_biomass": objectives[4]})
m.SetObjDirec("Min")
m.MinFluxSolve()
 
print(m.GetStatusMsg())
print(m.GetObjective())
print(m.GetObjVal())

m.PrintSol(f='CO2_tx',IncZeroes=False)
m.PrintSol(f='phloem_biomass',IncZeroes=True)
DisplaySolution(filters=["link","tx","X_Phloem","RIBULOSE_BISPHOSPHATE_CARBOXYLASE_RXN_p1_phase", "RXN_961_p"])

'''
book = Workbook()
s1 = book.add_sheet("First")
s1.write(0,0,str(m.GetObjective()))
s1.write(1,0,str(m.GetObjVal()))
s1.write(2,0,str(m.GetSol(f='CO2_tx',IncZeroes=True)))
s1.write(3,0,str(m.GetSol(f='phloem_biomass',IncZeroes=True)))
s1.write(4,0,str(m.GetSol(f='Photon_tx',IncZeroes=True)))

sheet = [2,3]

sheet[0] = book.add_sheet("1-1-1-1")
sheet[1] = book.add_sheet("1-2-4-2")

column_names = ["phloem_biomass Obj", "phloem_biomass Sol", "CO2_tx1 Sol", "CO2_tx2 Sol", "CO2_tx3 Sol", "CO2_tx4 Sol", "ObjVal","phloem_output1 Sol","phloem_output2 Sol","phloem_output3 Sol","phloem_output4 Sol", "phloem_output Sum", "O2_tx1 Sol", "O2_tx2 Sol", "O2_tx3 Sol", "O2_tx4 Sol", "O2_tx Sum"]

for i in range(len(sheet)):
    for j in range(len(column_names)):
        sheet[i].write(0,j,column_names[j])

for i in range(0, 2500):
    m.SetObjective({"phloem_biomass": i * -1})
    m.SetObjDirec("Min")
    m.MinFluxSolve()
    
    if m.GetStatusMsg() == "no solution":
        print("HHHHHHHHHH")
    else:
    
        phloembiomasssum = ast.literal_eval(str(m.GetSol(f = "phloem_biomass",IncZeroes=True)))
        phloembiomasssum = sum(phloembiomasssum.values())
        
        phase1sum = ast.literal_eval(str(m.GetSol(f = "CO2_tx1_phase1",IncZeroes=True)))
        phase1sum["CO2_tx1_phase1_reverse"] = -phase1sum["CO2_tx1_phase1_reverse"]
        phase1sum = sum(phase1sum.values())
        phase2sum = ast.literal_eval(str(m.GetSol(f = "CO2_tx1_phase2",IncZeroes=True)))
        phase2sum["CO2_tx1_phase2_reverse"] = -phase2sum["CO2_tx1_phase2_reverse"]
        phase2sum = sum(phase2sum.values())
        phase3sum = ast.literal_eval(str(m.GetSol(f = "CO2_tx1_phase3",IncZeroes=True)))
        phase3sum["CO2_tx1_phase3_reverse"] = -phase3sum["CO2_tx1_phase3_reverse"]
        phase3sum = sum(phase3sum.values())
        phase4sum = ast.literal_eval(str(m.GetSol(f = "CO2_tx1_phase4",IncZeroes=True)))
        phase4sum["CO2_tx1_phase4_reverse"] = -phase4sum["CO2_tx1_phase4_reverse"]
        phase4sum = sum(phase4sum.values())
        
        phloem1 = ast.literal_eval(str(m.GetSol(f = "Phloem_output_tx1_phase1",IncZeroes=True)))
        phloem1 = sum(phloem1.values())
        phloem2 = ast.literal_eval(str(m.GetSol(f = "Phloem_output_tx1_phase2",IncZeroes=True)))
        phloem2 = sum(phloem2.values())
        phloem3 = ast.literal_eval(str(m.GetSol(f = "Phloem_output_tx1_phase3",IncZeroes=True)))
        phloem3 = sum(phloem3.values())
        phloem4 = ast.literal_eval(str(m.GetSol(f = "Phloem_output_tx1_phase4",IncZeroes=True)))
        phloem4 = sum(phloem4.values())
        
    #     ox1 = ast.literal_eval(str(m.GetSol(f = "O2_tx1_phase1",IncZeroes=True)))
    #     ox1 = sum(ox1.values())
    #     ox2 = ast.literal_eval(str(m.GetSol(f = "O2_tx1_phase2",IncZeroes=True)))
    #     ox2 = sum(ox2.values())
    #     ox3 = ast.literal_eval(str(m.GetSol(f = "O2_tx1_phase3",IncZeroes=True)))
    #     ox3 = sum(ox3.values())
    #     ox4 = ast.literal_eval(str(m.GetSol(f = "O2_tx1_phase4",IncZeroes=True)))
    #     ox4 = sum(ox4.values())
        
        sheet[0].write(i+1,0,m.GetObjective(IncZeroes=True)["phloem_biomass"])
        sheet[0].write(i+1,1,phloembiomasssum)
        sheet[0].write(i+1,2,phase1sum)
        sheet[0].write(i+1,3,phase2sum)
        sheet[0].write(i+1,4,phase3sum)
        sheet[0].write(i+1,5,phase4sum)
        sheet[0].write(i+1,6,m.GetObjVal())
        sheet[0].write(i+1,7,phloem1)
        sheet[0].write(i+1,8,phloem2)
        sheet[0].write(i+1,9,phloem3)
        sheet[0].write(i+1,10,phloem4)
        sheet[0].write(i+1,11,phloem1 + phloem2 + phloem3 + phloem4)
    #     sheet[0].write(i+1,12,ox1)
    #     sheet[0].write(i+1,13,ox2)
    #     sheet[0].write(i+1,14,ox3)
    #     sheet[0].write(i+1,15,ox4)
    #     sheet[0].write(i+1,16,ox1 + ox2 + ox3 + ox4)
    
    print(i)
    print(m.GetStatusMsg())

book.save("1111.xls")
'''



'''  Testing different objectives for CO2_tx1_phase1 and phloem_biomass  
book = Workbook()
s1 = book.add_sheet("First")
s1.write(0,0,str(m.GetObjective()))
s1.write(1,0,str(m.GetObjVal()))
s1.write(2,0,str(m.GetSol(f='CO2_tx',IncZeroes=True)))
s1.write(3,0,str(m.GetSol(f='phloem_biomass',IncZeroes=True)))
s1.write(4,0,str(m.GetSol(f='Photon_tx',IncZeroes=True)))

sheet = [2,3,4,5,6,7,8,9,10,11,12]

CO2phase1Obj = []
for i in range(11):
    CO2phase1Obj.append(round(0 + (((1/12)/10)*i),4))
CO2phase1Obj.reverse()

column_names = ["CO2_tx_phase1 Obj","phloem_biomass Obj","phloem_biomass Sol","CO2_phase1 Sol","CO2_phase2 Sol","CO2_phase3 Sol","CO2_phase4 Sol","ObjVal"]

for i in range(11):
    sheet[i] = book.add_sheet(str(CO2phase1Obj[i]))

for i in range(11):
    for j in range(8):
        sheet[i].write(0,j,column_names[j])

for j in range(11):
    m.SetObjective({"CO2_tx1_phase1": CO2phase1Obj[j], "CO2_tx1_phase1_reverse": CO2phase1Obj[j]})
    
    for i in range(500):
        print(str(j) + " - " + str(i))
        
        m.SetObjective({"phloem_biomass": -1 * (i+1)})
        m.SetObjDirec("Min")
        m.Solve()
        
        phloembiomasssum = ast.literal_eval(str(m.GetSol(f = "phloem_biomass",IncZeroes=True)))
        phloembiomasssum = sum(phloembiomasssum.values())
        phase1sum = ast.literal_eval(str(m.GetSol(f = "CO2_tx1_phase1",IncZeroes=True)))
        phase1sum["CO2_tx1_phase1_reverse"] = -phase1sum["CO2_tx1_phase1_reverse"]
        phase1sum = sum(phase1sum.values())
        phase2sum = ast.literal_eval(str(m.GetSol(f = "CO2_tx1_phase2",IncZeroes=True)))
        phase2sum["CO2_tx1_phase2_reverse"] = -phase2sum["CO2_tx1_phase2_reverse"]
        phase2sum = sum(phase2sum.values())
        phase3sum = ast.literal_eval(str(m.GetSol(f = "CO2_tx1_phase3",IncZeroes=True)))
        phase3sum["CO2_tx1_phase3_reverse"] = -phase3sum["CO2_tx1_phase3_reverse"]
        phase3sum = sum(phase3sum.values())
        phase4sum = ast.literal_eval(str(m.GetSol(f = "CO2_tx1_phase4",IncZeroes=True)))
        phase4sum["CO2_tx1_phase4_reverse"] = -phase4sum["CO2_tx1_phase4_reverse"]
        phase4sum = sum(phase4sum.values())
        
        sheet[j].write(i+1,0,m.GetObjective(IncZeroes=True)["CO2_tx1_phase1"])
        sheet[j].write(i+1,1,m.GetObjective(IncZeroes=True)["phloem_biomass"])
        sheet[j].write(i+1,2,phloembiomasssum)
        sheet[j].write(i+1,3,phase1sum)
        sheet[j].write(i+1,4,phase2sum)
        sheet[j].write(i+1,5,phase3sum)
        sheet[j].write(i+1,6,phase4sum)
        sheet[j].write(i+1,7,m.GetObjVal())
    
    book.save("run" + str(j) + ".xls")

book.save("test.xls")
'''

'''  Displaying and plotting
#Display Solutions
sol_filters = ["CO2_tx", "O2_tx", "H2O_tx", "Photon_tx", "ATPase_tx", "Pi_tx", "H_tx", "Nitrate_tx", "Phloem_output_tx", "SO4_tx", "link", "MALATE_DEH_RXN", "MALATE_DEHYDROGENASE_NADPs_RXN", "CITSYN_RXN", "RIBULOSE_BISPHOSPHATE_CARBOXYLASE_RXN_p", "RXN_961_p", "PEPCARBOX_RXN_c", 'MALIC_NADP_RXN_c'] #Other tx rxns set to 0
#To print all *except for phloem_biomass*
#sol_filters = ["phase", "link"]
#m.PrintSol(f='CO2_tx')

displayed = DisplaySolution(sol_filters, 20)
df = displayed[0] #returns pandas DataFrame as printed
large_flux_dict = displayed[1] #returns dict of large reactions

#Plotting Graph
large_flux_list = list(large_flux_dict.keys())

small_flux_list = []
for i in range(len(list(df.index))):
    if df.index[i] not in large_flux_list:
        small_flux_list.append(df.index[i])

hourlydf = HourlyIntervals(df.drop(small_flux_list)) #returns df of hourly intervals


selected_list = []
for i in range(len(list(df.index))):
    if df.index[i] not in ["CO2_tx", "MALATE_DEHYDROGENASE_NADPs_RXN_p", "Photon_tx", "O2_tx", "Starch_link"]:
        selected_list.append(df.index[i])
hourlydf = HourlyIntervals(df.drop(selected_list))

ax = hourlydf.plot(secondary_y = ["Photon_tx"], xticks = [0, 12, 13, 21], figsize = (16, 9), fontsize=14)
ax.set_ylabel('Flux', fontsize=14)
ax.right_ax.set_ylabel('Photon Flux', fontsize=14)
ax.set_xticklabels(ax.get_xticklabels(), rotation=40, ha="right", fontsize=14)

phbsol = ast.literal_eval(str(m.GetSol(f = "phloem_biomass",IncZeroes=True)))
phbsol = sum(phbsol.values())
phbsol = round(phbsol, 5)

props = dict(boxstyle='round', facecolor='lightcyan', alpha=0.5)
#ax.text(0.78, 0.95, "Phloem Biomass = " + str(phbsol), transform=ax.transAxes, fontsize=12, verticalalignment='top', bbox = props)
ax.text(0.78, 0.8, "Phloem Biomass = " + str(phbsol), transform=ax.transAxes, fontsize=12, verticalalignment='top', bbox = props)
plot_name = "CO2obj_" + str([round(i, 2) for i in objectives]) + ".png"
#plt.savefig(plot_name, bbox_inches = "tight")
plt.show()
'''

'''  Some random code playing with the pareto functions
CO2_obj = {'CO2_tx1_phase1': objectives[0], 
           "CO2_tx1_phase1_reverse": objectives[0], 
           'CO2_tx1_phase2': objectives[1], 
           'CO2_tx1_phase2_reverse': objectives[1], 
           "CO2_tx1_phase3": objectives[2], 
           "CO2_tx1_phase3_reverse": objectives[2], 
           "CO2_tx1_phase4": objectives[3], 
           "CO2_tx1_phase4_reverse": objectives[3]}

phloem_obj = {"phloem_biomass": objectives[4]}

run = 4
pareto = m.Pareto([CO2_obj, phloem_obj], objdirec = "Min", runs = run, GetPoints = False).T
same = []
for i in range(len(pareto[0])):
    q = []
    for j in range(run-1):
        if pareto.iat[i,j] == pareto.iat[i,j+1]:
            q.append(True)
        else:
            q.append(False)
    if all(k == True for k in q):
        same.append(True)
    else:
        same.append(False)
pareto["Same"] = same
#pareto["Same"] = np.where(pareto[0] == pareto[1],True,False)
print pareto

pareto = m.Pareto([CO2_obj, phloem_obj], objdirec = "Min", runs = run, GetPoints = True)
print pareto
'''



