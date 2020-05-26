import scobra, csv
from xlwt import Workbook
import objective_scan, correlations, modeling_phased

m = scobra.Model("../Final_Files/Constrained_Model_FINAL.json")

with open("../Final_Files/Reacs to Examine.csv") as csvfile:
    reader = csv.reader(csvfile)
    next(reader)
    reacs = [l[0] for l in reader]
csvfile.close()
objective_scan.write(m, [1,2,3,2], 1000, reacs)

#print(correlations.corr(m, [1,2,4,2], 7000, anchors=["CO2_tx", "RIBULOSE_BISPHOSPHATE_CARBOXYLASE_RXN_p", "PEPCARBOX_RXN_c"]))

objectives = [1, 
              2, 
              4, 
              2, 
              -1000]

m.SetObjective({"CO2_tx1_phase1": objectives[0], 
                "CO2_tx1_phase2": objectives[1], 
                "CO2_tx1_phase3": objectives[2], 
                "CO2_tx1_phase4": objectives[3]})

m.SetObjective ({"phloem_biomass": objectives[4]})
m.SetObjDirec("Min")
m.MinFluxSolve()

print(m.GetStatusMsg())
print(m.GetObjective())
print(m.GetObjVal())

m.PrintSol(f="CO2_tx",IncZeroes=False)
m.PrintSol(f="phloem_biomass",IncZeroes=True)
modeling_phased.DisplaySolution(m, filters=["link","tx","RIBULOSE_BISPHOSPHATE_CARBOXYLASE_RXN_p1_phase", "RXN_961_p", "PEP"])














