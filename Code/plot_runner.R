source("plotting.R")

weight <- "1242"
df <- import.scan(weight)

plot.reacs(weight, df, title=expression(bold("CO"[2]*" Transfer Scan (Objective Ratio: 1:1:1:1)")))

plot.reacs(weight, df, title=expression(bold("CO"[2]*" Transfer Scan (Objective Ratio: 1:2:2:2)")))

plot.reacs(weight, df, title=expression(bold("CO"[2]*" Transfer Scan (Objective Ratio: 1:2:4:2)")))

plot.reacs(weight, df, type="phloem", reac.list = c("phloem_biomass"),
           title="Phloem Biomass Scan (Objective Ratio: 1:2:4:2)")

plot.reacs(weight, df, type="link", reac.list = c("Malate_link"),
           title="Malate Link Scan (Objective Ratio: 1:2:4:2)")

plot.reacs(weight, df, type="link", reac.list = c("Starch_link"),
           title="Starch Link Scan (Objective Ratio: 1:2:4:2)")

plot.reacs(weight, df, type="phase", reac.list = c("RIBULOSE_BISPHOSPHATE_CARBOXYLASE_RXN_p"),
           title="Rubisco Scan (Objective Ratio: 1:2:4:2)")

