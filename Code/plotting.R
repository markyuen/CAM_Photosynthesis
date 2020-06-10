library("readxl")
library("plotrix")
library("RColorBrewer")

df <- data.frame(read_excel("../Final_Files/1242-1000-corr.xlsx", sheet=2, col_names=FALSE))

#Remove extra CO2_tx and set row index as reac name, also remove 0.175 values
rows <- dim(df)[1]
df <- df[-c((rows - 3):rows),-10]
rownames(df) <- df[,1]
df <- df[,-1]
#Grab breakpoints
top <- df[1,]

plott <- function(x, y, pch, col, lwd=1.8, cex=0.8, lty=1) {
  #Plot points
  points(x, y, pch=pch, col=col, type="p", cex=cex)
  #Plot lines
  points(x, y, pch=pch, col=col, type="l", lwd=lwd, lty=lty)
}

plot.reacs <- function(type="phase", reac_list=list("CO2_tx"), title=expression("CO"[2]*" Transfer Scan")) {
  #Expand reaction name to four phases
  reacs <- c()
  if (type == "phloem") {
    reacs <- c(reacs, "phloem_biomass")
  } else if (type == "phase") {
    for (i in 1:length(reac_list)) {
      reacs <- c(reacs, paste(reac_list[[i]], "1", sep=""))
      reacs <- c(reacs, paste(reac_list[[i]], "2", sep=""))
      reacs <- c(reacs, paste(reac_list[[i]], "3", sep=""))
      reacs <- c(reacs, paste(reac_list[[i]], "4", sep=""))
    }
  } else if (type == "link") {
    for (i in 1:length(reac_list)) {
      reacs <- c(reacs, paste(reac_list[[i]], "1_2", sep=""))
      reacs <- c(reacs, paste(reac_list[[i]], "2_3", sep=""))
      reacs <- c(reacs, paste(reac_list[[i]], "3_4", sep=""))
      reacs <- c(reacs, paste(reac_list[[i]], "4_1", sep=""))
    }
  } else {
    stop("Invalid type.")
  }
  
  #Extract vectors from df
  len <- length(reacs)
  vectors <- vector("list", len)
  for (i in 1:len) {
    reac <- reacs[i]
    vectors[[i]] <- as.numeric(df[reac,])
  }
  
  #Expand vectors to include all points
  multiplier <- as.numeric(top)
  full_vectors <- vector("list", len)
  for (i in 1:(length(multiplier) - 1)) {
    diff <- (multiplier[i + 1] - multiplier[i]) * 100
    #Iterate through each reaction
    for (j in 1:len) {
      val <- vectors[[j]][i]
      #Duplicate the value
      for (k in 1:diff) {
        full_vectors[[j]] <- c(full_vectors[[j]], val)
      }
    }
  }
  #Adding last breakpoint and name
  vlen <- length(multiplier)
  for (i in 1:len) {
    full_vectors[[i]] <- c(full_vectors[[i]], vectors[[i]][vlen])
  }
  
  #Building x values
  full_mult <- seq(0, multiplier[vlen], by=0.01)
  
  #Remove extra values for a break
  rm1 <- ifelse(full_mult < 0.54, TRUE, FALSE)
  rm2 <- ifelse(full_mult > 2.015, TRUE, FALSE)
  mult1 <- full_mult[rm1]
  mult2 <- full_mult[rm2] - 1.45
  for (i in 1:len) {
    full_vectors[[i]] <- list(full_vectors[[i]][rm1], full_vectors[[i]][rm2])
  }
  
  #Setting axes
  all <- c()
  for (i in 1:len) {
    all <- c(all, full_vectors[[i]][[1]], full_vectors[[i]][[2]])
  }
  yat <- pretty(all)
  xgap <- c(mult1, mult2)
  xat <- pretty(xgap)
  xlab <- ifelse(xat > 0.55, xat + 1.45, xat)
  
  #PLOTTING
  filename <- gsub("  ", " ", gsub("\\*", "", gsub("\"", "", toString(title))))
  png(file=paste(filename, ".png", sep=""), width=5000, height=2500, res=600)
  
  #Set font and colors
  windowsFonts(TNR=windowsFont("Times New Roman"))
  par(family="TNR")
  pal <- brewer.pal(len, "Set1")
  #Adjust opacity
  for (i in 1:len) {
    pal[i] <- paste(pal[i], "FF", sep="")
  }
  #Set shapes
  pch <- c(1,0,5,6)
  
  #Initialize plot
  plot(0, xaxt="n", yaxt="n", ylim=range(yat), xlim=range(xgap), 
       main=title, xlab="Water Stress Coefficient", 
       ylab=expression("Solution Flux (mol/m"^2*")"))
  
  #Plot the dashed portion
  last <- length(full_vectors[[1]][[1]])
  xdash <- c(mult1[length(mult1)], mult2[1])
  #Plot reactions
  for (i in 1:len) {
    plott(mult1, full_vectors[[i]][[1]], pch[i], pal[i])
    plott(mult2, full_vectors[[i]][[2]], pch[i], pal[i])
    ydash <- c(full_vectors[[i]][[1]][last],
               full_vectors[[i]][[2]][1])
    plott(xdash, ydash, pch[i], pal[i], lty=2)
  }
  
  #Plot lines for CAM phases
  abline(v=0.165, lty=2) #C3
  #abline(v=0.255, lty=2) #CAM Cycling
  abline(v=0.315, lty=2) #CAM Idling
  abline(v=0.615, lty=2) #CAM
  
  #Writing
  text(c(0.08, 0.47), c(-0.19), cex=0.8, labels=c(expression("C"[3]), "CAM"))
  
  #Set the axes ticks and labels, and add legend
  axis(1, at=xat, labels=xlab)
  axis(2, at=yat, labels=yat)
  axis.break(1, breakpos=0.55, style="slash")
  abline(h=0, lty=2)
  if (type != "phloem") {
    legend("topright", legend=c("Phase 1", "Phase 2", "Phase 3", "Phase 4"), 
           col=pal, pch=pch, cex=0.8, ncol=4)
  }
  dev.off()
}


