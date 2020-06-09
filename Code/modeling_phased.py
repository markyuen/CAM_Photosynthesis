import scobra
from xlwt import Workbook
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

pd.set_option('display.max_columns', None)  # or 1000
pd.set_option('display.max_rows', None)  # or 1000
pd.set_option('display.max_colwidth', None)  # or 199
pd.set_option('display.width', 1000)

def oneddf(m, filters):
    rtp = []
    for f in filters:
        for x in [r.id for r in m.reactions if f in r.id]:
            rtp.append(x)
    sol = m.GetSol(IncZeroes = True, AsMtx = True, reacs = rtp)
    df = pd.DataFrame(sol)
    
    if "CO2_tx1_phase1" and "CO2_tx1_phase2" and "CO2_tx1_phase3" and "CO2_tx1_phase4" and "CO2_tx1_phase1_reverse" and \
    "CO2_tx1_phase2_reverse" and "CO2_tx1_phase3_reverse" and "CO2_tx1_phase4_reverse" in rtp:
        CO2_phase1 = df.loc["CO2_tx1_phase1", "Flux"] - df.loc["CO2_tx1_phase1_reverse", "Flux"]
        CO2_phase2 = df.loc["CO2_tx1_phase2", "Flux"] - df.loc["CO2_tx1_phase2_reverse", "Flux"]
        CO2_phase3 = df.loc["CO2_tx1_phase3", "Flux"] - df.loc["CO2_tx1_phase3_reverse", "Flux"]
        CO2_phase4 = df.loc["CO2_tx1_phase4", "Flux"] - df.loc["CO2_tx1_phase4_reverse", "Flux"]
        
        CO2_combined = pd.DataFrame({"Flux": [CO2_phase1, CO2_phase2, CO2_phase3, CO2_phase4]}, 
                                        index = ["CO2_tx1_phase1", "CO2_tx1_phase2", "CO2_tx1_phase3", "CO2_tx1_phase4"])                                          
        
        df = df.drop(["CO2_tx1_phase1", "CO2_tx1_phase2", "CO2_tx1_phase3", "CO2_tx1_phase4", 
                 "CO2_tx1_phase1_reverse", "CO2_tx1_phase2_reverse", "CO2_tx1_phase3_reverse", "CO2_tx1_phase4_reverse"])
        
        df = df.append(CO2_combined, verify_integrity = True)
    
    return df

def create_df_from_sol(m, filters):
    df = oneddf(m, filters)
    
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

'''  For writing solutions to Excel file  '''
def WriteSolution(m, file_name):
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

'''  For displaying some solutions | filters = ["link", "phase"] for all solutions less phloem_biomass '''
def DisplaySolution(m, filters, flux_min=0):
    df = create_df_from_sol(m, filters).T
    large_flux_dict = {}
    for i in range(len(df.columns)):
        total_flux = abs(df.iat[0, i]) + abs(df.iat[1, i]) + abs(df.iat[2, i]) + abs(df.iat[3, i])
        if total_flux > flux_min:
            large_flux_dict[df.columns[i]] = total_flux

    print(df.T)
    print("\n" + str(len(large_flux_dict)) + "/" + str(len(df.columns)) + " Fluxes Greater Than " + str(flux_min) + ": ")
    print(large_flux_dict)

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

