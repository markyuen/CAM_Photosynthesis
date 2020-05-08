import scobra

m = scobra.Model("Final_Files/diel_model.xls")

""" Also new """
m.DelReactions(["HEXOKINASE_RXN_MANNOSE_c1","HEXOKINASE_RXN_MANNOSE_c2"])
m.AddReaction("HEXOKINASE_RXN_MANNOSE_c1", {"ATP_c1":-0.65, "MANNOSE_c1":-1, "aATP_c1":-0.35, "ADP_c1":0.8, "MANNOSE_6P_c1":1, "PROTON_c1":1.15, "aADP_c1":0.2}, rev=False)

m.AddReaction("H_vc1",{"PROTON_v1":-1, "PROTON_c1":1}, rev=False)
m.AddReaction("H_ec1",{"PROTON_e1":-1, "PROTON_c1":1}, rev=False)

reactions = m.Reactions()
metabolites = m.Metabolites()

for i in range(len(reactions)):
    if (reactions[i].endswith("1") != True):
        m.DelReaction(reactions[i])

newm = m.DuplicateModel(["_phase1","_phase2","_phase3","_phase4"])

newm.AddReaction('Citrate_link1_2',{'CIT_v1_phase1':-.5,"aCIT_v1_phase1":-.5,'CIT_v1_phase2':.5,"aCIT_v1_phase2":.5})
newm.AddReaction('Citrate_link2_3',{'CIT_v1_phase2':-.5,"aCIT_v1_phase2":-.5,'CIT_v1_phase3':.5,"aCIT_v1_phase3":.5})
newm.AddReaction('Citrate_link3_4',{'CIT_v1_phase3':-.5,"aCIT_v1_phase3":-.5,'CIT_v1_phase4':.5,"aCIT_v1_phase4":.5})
newm.AddReaction('Citrate_link4_1',{'CIT_v1_phase4':-.5,"aCIT_v1_phase4":-.5,'CIT_v1_phase1':.5,"aCIT_v1_phase1":.5})

newm.AddReaction('Malate_link1_2',{'MAL_v1_phase1':-.7,"aMAL_v1_phase1":-.3,'MAL_v1_phase2':.7,"aMAL_v1_phase2":.3})
newm.AddReaction('Malate_link2_3',{'MAL_v1_phase2':-.7,"aMAL_v1_phase2":-.3,'MAL_v1_phase3':.7,"aMAL_v1_phase3":.3})
newm.AddReaction('Malate_link3_4',{'MAL_v1_phase3':-.7,"aMAL_v1_phase3":-.3,'MAL_v1_phase4':.7,"aMAL_v1_phase4":.3})
newm.AddReaction('Malate_link4_1',{'MAL_v1_phase4':-.7,"aMAL_v1_phase4":-.3,'MAL_v1_phase1':.7,"aMAL_v1_phase1":.3})

newm.AddReaction('Nitrate_link1_2',{'NITRATE_v1_phase1':-1,'NITRATE_v1_phase2':1})
newm.AddReaction('Nitrate_link2_3',{'NITRATE_v1_phase2':-1,'NITRATE_v1_phase3':1})
newm.AddReaction('Nitrate_link3_4',{'NITRATE_v1_phase3':-1,'NITRATE_v1_phase4':1})
newm.AddReaction('Nitrate_link4_1',{'NITRATE_v1_phase4':-1,'NITRATE_v1_phase1':1})

newm.AddReaction('Sucrose_link1_2',{'SUCROSE_v1_phase1':-1,'SUCROSE_v1_phase2':1})
newm.AddReaction('Sucrose_link2_3',{'SUCROSE_v1_phase2':-1,'SUCROSE_v1_phase3':1})
newm.AddReaction('Sucrose_link3_4',{'SUCROSE_v1_phase3':-1,'SUCROSE_v1_phase4':1})
newm.AddReaction('Sucrose_link4_1',{'SUCROSE_v1_phase4':-1,'SUCROSE_v1_phase1':1})

newm.AddReaction('Starch_link1_2',{'STARCH_p1_phase1':-1,'STARCH_p1_phase2':1})
newm.AddReaction('Starch_link2_3',{'STARCH_p1_phase2':-1,'STARCH_p1_phase3':1})
newm.AddReaction('Starch_link3_4',{'STARCH_p1_phase3':-1,'STARCH_p1_phase4':1})
newm.AddReaction('Starch_link4_1',{'STARCH_p1_phase4':-1,'STARCH_p1_phase1':1})

""" New things """
newm.AddReaction("Oxygen_Molecule_e_link1_2", {"OXYGEN_MOLECULE_e1_phase1":-1, "OXYGEN_MOLECULE_e2_phase2":1}, rev=False)
newm.AddReaction("Oxygen_Molecule_e_link2_3", {"OXYGEN_MOLECULE_e1_phase2":-1, "OXYGEN_MOLECULE_e2_phase3":1}, rev=False)
newm.AddReaction("Oxygen_Molecule_e_link3_4", {"OXYGEN_MOLECULE_e1_phase3":-1, "OXYGEN_MOLECULE_e2_phase4":1}, rev=False)
newm.AddReaction("Oxygen_Molecule_e_link4_1", {"OXYGEN_MOLECULE_e1_phase4":-1, "OXYGEN_MOLECULE_e2_phase1":1}, rev=False)

newm.AddReaction("Proton_v_link1_2",{"PROTON_v1_phase1":-1, "PROTON_v2_phase2":1}, rev=False)
newm.AddReaction("Proton_v_link2_3",{"PROTON_v1_phase2":-1, "PROTON_v2_phase3":1}, rev=False)
newm.AddReaction("Proton_v_link3_4",{"PROTON_v1_phase3":-1, "PROTON_v2_phase4":1}, rev=False)
newm.AddReaction("Proton_v_link4_1",{"PROTON_v1_phase4":-1, "PROTON_v2_phase1":1}, rev=False)

'''  diel_biomass reaction  '''
newm.AddReaction('phloem_biomass',{'X_Phloem_contribution_t1_t_phase1':-12,'X_Phloem_contribution_t1_t_phase2':-3, "X_Phloem_contribution_t1_t_phase3":-24, "X_Phloem_contribution_t1_t_phase4":-9})

newm.WriteModel("Phased_Model_FINAL.xls")

#Test if model works
newm.SetConstraints({'Phloem_output_tx1_phase1':(1,1000),'Phloem_output_tx1_phase2':(1,1000), 'Phloem_output_tx1_phase3':(1,1000), 'Phloem_output_tx1_phase4':(1,1000)})
newm.SetObjDirec("Min")
newm.Solve()




