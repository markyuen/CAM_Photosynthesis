import scobra

m = scobra.Model("../Final_Files/Constrained_Model_FINAL.xls")

#CO2 weight of 1:1:1:1
objectives = [1, 
              1, 
              1, 
              1, 
              -886]

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
print("\n")

#Above there is a solution, for some reason on this run there is suddenly no solution
m.SetObjective({"phloem_biomass": -886})
m.SetObjDirec("Min")
m.MinFluxSolve()
print(m.GetStatusMsg())
print(m.GetObjective())
print(m.GetObjVal())
print("\n")

#This can be mimicked with -887... If we run like this then we get no solution
m.SetObjective({"phloem_biomass": -887})
m.SetObjDirec("Min")
m.MinFluxSolve()
print(m.GetStatusMsg())
print(m.GetObjective())
print(m.GetObjVal())
print("\n")

#If we reimport the model and set the SAME objectives, we will find there is indeed a solution
m = scobra.Model("../Final_Files/Constrained_Model_FINAL.xls")
#Have to set CO2 objectives again
m.SetObjective({'CO2_tx1_phase1': objectives[0], 
                'CO2_tx1_phase2': objectives[1], 
                "CO2_tx1_phase3": objectives[2], 
                "CO2_tx1_phase4": objectives[3]})
#Again, set fresh to -887
m.SetObjective ({"phloem_biomass": -887})
m.SetObjDirec("Min")
m.MinFluxSolve()
print(m.GetStatusMsg())
print(m.GetObjective())
print(m.GetObjVal())
print("\n")
