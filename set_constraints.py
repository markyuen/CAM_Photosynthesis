import scobra
from cobra import Reaction
from six import iteritems

m = scobra.Model("Final_Files/Phased_Model_FINAL.xls")

m.SetReacsFixedRatio({"RIBULOSE_BISPHOSPHATE_CARBOXYLASE_RXN_p1_phase1":3, "RXN_961_p1_phase1":1})
m.SetReacsFixedRatio({"RIBULOSE_BISPHOSPHATE_CARBOXYLASE_RXN_p1_phase2":3, "RXN_961_p1_phase2":1})
m.SetReacsFixedRatio({"RIBULOSE_BISPHOSPHATE_CARBOXYLASE_RXN_p1_phase3":3, "RXN_961_p1_phase3":1})
m.SetReacsFixedRatio({"RIBULOSE_BISPHOSPHATE_CARBOXYLASE_RXN_p1_phase4":3, "RXN_961_p1_phase4":1})

reacs_to_constrain = [("Biomass_tx1_phase",0,0), 
                      ("CO2_tx1_phase",-1000,1000), 
                      ("Ca_tx1_phase",0,0), 
                      ("GLC_tx1_phase",0,0), 
                      ("H2O_tx1_phase",-1000,1000), 
                      ("H_tx1_phase",-1000,1000), 
                      ("K_tx1_phase",0,0), 
                      ("Mg_tx1_phase",0,0), 
                      ("NH4_tx1_phase",0,0), 
                      ("Nitrate_tx1_phase",0,1000), 
                      ("O2_tx1_phase",-1000,1000), 
                      ("Phloem_output_tx1_phase",-1000,1000), 
                      ("Pi_tx1_phase",0,1000), 
                      ("SO4_tx1_phase",0,1000), 
                      ("Sucrose_tx1_phase",0,0),
                      #new
                      ('unlProtHYPO_c1_phase',0,0),
                      ('H_ic1_phase',None,None)]

for reac in range(len(reacs_to_constrain)):
    for i in range(4):
        m.SetConstraint(reacs_to_constrain[reac][0] + str(i + 1), reacs_to_constrain[reac][1], reacs_to_constrain[reac][2])

ATP = 0.0306

m.SetConstraint("ATPase_tx1_phase1",ATP*12,ATP*12)
m.SetConstraint("ATPase_tx1_phase2",ATP*1,ATP*1)
m.SetConstraint("ATPase_tx1_phase3",ATP*8,ATP*8)
m.SetConstraint("ATPase_tx1_phase4",ATP*3,ATP*3)

m.SetConstraint("NADPHoxc_tx1_phase1",ATP*12/9,ATP*12/9)
m.SetConstraint("NADPHoxc_tx1_phase2",ATP*1/9,ATP*1/9)
m.SetConstraint("NADPHoxc_tx1_phase3",ATP*8/9,ATP*8/9)
m.SetConstraint("NADPHoxc_tx1_phase4",ATP*3/9,ATP*3/9)

m.SetConstraint("NADPHoxm_tx1_phase1",ATP*12/9,ATP*12/9)
m.SetConstraint("NADPHoxm_tx1_phase2",ATP*1/9,ATP*1/9)
m.SetConstraint("NADPHoxm_tx1_phase3",ATP*8/9,ATP*8/9)
m.SetConstraint("NADPHoxm_tx1_phase4",ATP*3/9,ATP*3/9)

m.SetConstraint("NADPHoxp_tx1_phase1",ATP*12/9,ATP*12/9)
m.SetConstraint("NADPHoxp_tx1_phase2",ATP*1/9,ATP*1/9)
m.SetConstraint("NADPHoxp_tx1_phase3",ATP*8/9,ATP*8/9)
m.SetConstraint("NADPHoxp_tx1_phase4",ATP*3/9,ATP*3/9)

m.SetConstraint("Photon_tx1_phase1",0,0)
m.SetConstraint("Photon_tx1_phase2",0,1000)
m.SetConstraint("Photon_tx1_phase3",0,1000)
m.SetConstraint("Photon_tx1_phase4",0,1000)
m.SetReacsFixedRatio({"Photon_tx1_phase2":1,"Photon_tx1_phase3":16,"Photon_tx1_phase4":3})
m.SetSumReacsConstraint({"Photon_tx1_phase2":1,"Photon_tx1_phase3":1,"Photon_tx1_phase4":1}, 8.64)

#m.SetConstraint("phloem_biomass",0.236603103,0.236603103)
m.SetConstraint("phloem_biomass",0,1000)

def SplitReactions(reacs_to_split):
    reactions_to_add = []
    coefficients = {}
    
    for reaction in m.GetReactions(reacs_to_split):
        if reaction.lower_bound < 0:
            reverse_reaction = Reaction(reaction.id + "_reverse")
            reverse_reaction.lower_bound = min(0, reaction.upper_bound) * -1
            reverse_reaction.upper_bound = reaction.lower_bound * -1
            coefficients[reverse_reaction] = reaction.objective_coefficient * -1
            reaction.lower_bound = 0
            reaction.upper_bound = max(0, reaction.upper_bound)
            #Make the directions aware of each other
            reaction.reflection = reverse_reaction
            reverse_reaction.reflection = reaction
            reaction.notes["reflection"] = reverse_reaction.id
            reverse_reaction.notes["reflection"] = reaction.id
            reaction_dict = {k: v * -1
                             for k, v in iteritems(reaction._metabolites)}
            reverse_reaction.add_metabolites(reaction_dict)
            reverse_reaction._model = reaction._model
            reverse_reaction._genes = reaction._genes
            for gene in reaction._genes:
                gene._reaction.add(reverse_reaction)
            reverse_reaction._gene_reaction_rule = reaction._gene_reaction_rule
            reverse_reaction.subsystem = reaction.subsystem
            reactions_to_add.append(reverse_reaction)
        m.add_reactions(reactions_to_add)
        m.SetObjective(coefficients)

SplitReactions(["CO2_tx1_phase1","CO2_tx1_phase2","CO2_tx1_phase3","CO2_tx1_phase4"])

m.WriteModel("Constrained_Model_FINAL.xls")





