source("plotting.R")

weight <- "1242"
df <- import.scan(weight)

plot.reacs(weight)
plot.reacs(weight, type="phloem", reac.list = c("phloem_biomass"),title="Phloem Biomass Scan")
plot.reacs(weight, type="link", reac.list = c("Malate_link"),title="Malate Link Scan")
plot.reacs(weight, type="link", reac.list = c("Starch_link"),title="Starch Link Scan")

plot.reacs(weight, type="phase", reac.list = c("O2_tx"),title=expression("O"[2]*" Transfer Scan"))
