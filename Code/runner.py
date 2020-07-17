import scobra, csv
import objective_scan, correlations, modeling_phased, correlationsfull

m = scobra.Model("../Final_Files/Constrained_Model_FINAL_v1.json")

# #Does not contain phloem_biomass, phloem_biomass already included by default
# with open("../Final_Files/Reacs to Examine.csv") as csvfile:
#     reader = csv.reader(csvfile)
#     next(reader)
#     reacs = [l[0] for l in reader]
# csvfile.close()

anchors=["CO2_tx", "RIBULOSE_BISPHOSPHATE_CARBOXYLASE_RXN_p", "PEPCARBOX_RXN_c", "phloem_biomass", "Starch_link", "Malate_link"]
correlationsfull.corrfull(m, [1,2,4,2], -1000, filtersp=["link","phase"], anchors=anchors, lo=0, step=0.01, iters=300, tol=0.9)
# 
# objectives = [1, 
#               2, 
#               4, 
#               2, 
#               -3000]
#  
# m.SetObjective({"CO2_tx1_phase1": objectives[0], 
#                 "CO2_tx1_phase2": objectives[1], 
#                 "CO2_tx1_phase3": objectives[2], 
#                 "CO2_tx1_phase4": objectives[3]})
#  
# m.SetObjective ({"phloem_biomass": objectives[4]})
# m.SetObjDirec("Min")
# m.MinFluxSolve()
#  
# print(m.GetStatusMsg())
# print(m.GetObjective())
# print(m.GetObjVal())
#  
# m.PrintSol(f="CO2_tx",IncZeroes=False)
# m.PrintSol(f="phloem_biomass",IncZeroes=True)
# modeling_phased.DisplaySolution(m, filters=["link","tx","RIBULOSE_BISPHOSPHATE_CARBOXYLASE_RXN_p1_phase", "RXN_961_p", "PEP"])














