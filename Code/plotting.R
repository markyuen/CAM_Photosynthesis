library("readxl")
library("plotrix")
library("RColorBrewer")
library("ggplot2")

df <- data.frame(read_excel("../Final_Files/1242-1000-corr.xlsx", sheet=2))

#Remove extra CO2_tx and set row index as reac name, also remove 0.175 values
rows <- dim(df)[1]
df <- df[-c((rows - 3):rows),-10]
rownames(df) <- df$CO2.Weight.Multiplier

#Grab breakpoints except 0.175
top <- data.frame(read_excel("../Final_Files/1242-1000-corr.xlsx", sheet=2, n_max=1, col_names=FALSE))
top <- top[,-10]

plott <- function(x, y, pch, col, lwd=1.6, cex=0.8, lty=1) {
  #Plot lines
  points(x, y, pch=pch, col=col, type="l", lwd=lwd, lty=lty)
  #Plot points
  points(x, y, pch=pch, col=col, type="p", cex=cex)
}

plot.CO2tx <- function(reac_list=list("CO2_tx")) {
  #Expand reaction name to four phases
  reacs <- c()
  for (i in 1:length(reac_list)) {
    reacs <- c(reacs, paste(reac_list[[i]], "1", sep=""))
    reacs <- c(reacs, paste(reac_list[[i]], "2", sep=""))
    reacs <- c(reacs, paste(reac_list[[i]], "3", sep=""))
    reacs <- c(reacs, paste(reac_list[[i]], "4", sep=""))
  }
  
  #Extract vectors from df
  len <- length(reacs)
  vectors <- vector("list", len)
  for (i in 1:len) {
    reac <- reacs[i]
    vectors[[i]] <- as.numeric(df[reac,-1])
  }
  
  #Expand vectors to include all points
  multiplier <- as.numeric(top[,-1])
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
  
  #Plotting
  png(file="mygraphic.png", width=3000, height=1500, res=360)
  
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
  plot(mult1, full_vectors[[1]][[1]], pch=pch[1], col=pal[1], 
       xaxt="n", yaxt="n", ylim=range(yat), xlim=range(xgap), 
       main=expression("CO"[2]*" Transfer Scan"), xlab="Water Stress Coefficient", 
       ylab=expression("CO"[2]*" Solution Flux"), type="l", lwd=1.7)
  plott(mult1, full_vectors[[1]][[1]], pch[1], pal[1])
  plott(mult2, full_vectors[[1]][[2]], pch[1], pal[1])
  
  #Plot the dashed portion
  last <- length(full_vectors[[1]][[1]])
  xdash <- c(mult1[length(mult1)], mult2[1])
  ydash <- c(full_vectors[[1]][[1]][last],
             full_vectors[[1]][[2]][1])
  plott(xdash, ydash, pch[1], pal[1], lty=2)
  
  #Plot the rest of the reactions
  for (i in 2:len) {
    plott(mult1, full_vectors[[i]][[1]], pch[i], pal[i])
    plott(mult2, full_vectors[[i]][[2]], pch[i], pal[i])
    ydash <- c(full_vectors[[i]][[1]][last],
               full_vectors[[i]][[2]][1])
    plott(xdash, ydash, pch[i], pal[i], lty=2)
  }
  
  #Set the axes ticks and labels, and add legend
  axis(1, at=xat, labels=xlab)
  axis(2, at=yat, labels=yat)
  axis.break(1, breakpos=0.55, style="slash")
  abline(h=0, lty=2)
  #ppreacs <- c(expression("CO"[2]*" tx1"), expression("CO"[2]*" tx2"), 
  #             expression("CO"[2]*" tx3"), expression("CO"[2]*" tx4"))
  legend("topright", legend=c("Phase 1", "Phase 2", "Phase 3", "Phase 4"), 
         col=pal, pch=pch, ncol=4)
  dev.off()
}

plot.link <- function(reac_list=list("Malate_link")) {
  #Expand reaction name to four phases
  reacs <- c()
  for (i in 1:length(reac_list)) {
    reacs <- c(reacs, paste(reac_list[[i]], "1_2", sep=""))
    reacs <- c(reacs, paste(reac_list[[i]], "2_3", sep=""))
    reacs <- c(reacs, paste(reac_list[[i]], "3_4", sep=""))
    reacs <- c(reacs, paste(reac_list[[i]], "4_1", sep=""))
  }
  
  #Extract vectors from df
  len <- length(reacs)
  vectors <- vector("list", len)
  for (i in 1:len) {
    reac <- reacs[i]
    vectors[[i]] <- list(reac, as.numeric(df[reac,-1]))
  }
  
  #Expand vectors to include all points
  multiplier <- as.numeric(top[,-1])
  full_vectors <- vector("list", len)
  for (i in 1:(length(multiplier) - 1)) {
    diff <- (multiplier[i + 1] - multiplier[i]) * 100
    #Iterate through each reaction
    for (j in 1:len) {
      val <- vectors[[j]][[2]][i]
      #Duplicate the value
      for (k in 1:diff) {
        full_vectors[[j]] <- c(full_vectors[[j]], val)
      }
    }
  }
  #Adding last breakpoint and name
  vlen <- length(multiplier)
  for (i in 1:len) {
    newv <- c(full_vectors[[i]], vectors[[i]][[2]][vlen])
    full_vectors[[i]] <- list(vectors[[i]][[1]], newv)
  }
  
  #Building x values
  full_mult <- seq(0, multiplier[vlen], by=0.01)
  
  #Remove extra values for a break
  rm <- ifelse(full_mult > 0.6 & full_mult < 2, FALSE, TRUE)
  full_mult <- full_mult[rm]
  for (i in 1:len) {
    full_vectors[[i]][[2]] <- full_vectors[[i]][[2]][rm]
  }
  
  #Setting axes
  all <- c()
  for (i in 1:len) {
    all <- c(all, full_vectors[[i]][[2]])
  }
  yat <- pretty(all)
  xgap <- ifelse(full_mult > 0.6, full_mult - 1.4, full_mult)
  xat <- pretty(xgap)
  xlab <- ifelse(xat > 0.6, xat + 1.4, xat)
  
  #Plotting
  pal <- brewer.pal(len, "Set1")
  for (i in 1:len) {
    pal[i] <- paste(pal[i], "FF", sep="")
  }
  plot(xgap, full_vectors[[1]][[2]], pch=16, col=pal[1], 
       xaxt="n", yaxt="n", ylim=c(min(yat), max(yat) + 0.05), 
       main=reac_list[[1]], xlab="Water stress coefficient", 
       ylab="Malate link solution flux", xlim=c(0, 0.7))
  for (i in 2:len) {
    points(xgap, full_vectors[[i]][[2]], pch=16, col=pal[i])
  }
  axis(1, at=xat, labels=xlab)
  axis(2, at=yat, labels=yat)
  axis.break(1, breakpos=0.55, style="slash")
  abline(h=0, lty=2)
  legend("topleft", legend=reacs, inset=c(0,0), 
         col=c(pal[1],pal[2],pal[3],pal[4]), pch=16, ncol=1)
}

plot.phloem <- function(reac_list=list("phloem_biomass")) {
  #Expand reaction name to four phases
  reacs <- c("phloem_biomass")
  
  #Extract vectors from df
  len <- length(reacs)
  vectors <- vector("list", len)
  for (i in 1:len) {
    reac <- reacs[i]
    vectors[[i]] <- list(reac, as.numeric(df[reac,-1]))
  }
  
  #Expand vectors to include all points
  multiplier <- as.numeric(top[,-1])
  full_vectors <- vector("list", len)
  for (i in 1:(length(multiplier) - 1)) {
    diff <- (multiplier[i + 1] - multiplier[i]) * 100
    #Iterate through each reaction
    for (j in 1:len) {
      val <- vectors[[j]][[2]][i]
      #Duplicate the value
      for (k in 1:diff) {
        full_vectors[[j]] <- c(full_vectors[[j]], val)
      }
    }
  }
  #Adding last breakpoint and name
  vlen <- length(multiplier)
  for (i in 1:len) {
    newv <- c(full_vectors[[i]], vectors[[i]][[2]][vlen])
    full_vectors[[i]] <- list(vectors[[i]][[1]], newv)
  }
  
  #Building x values
  full_mult <- seq(0, multiplier[vlen], by=0.01)
  
  #Remove extra values for a break
  rm <- ifelse(full_mult > 0.6 & full_mult < 2, FALSE, TRUE)
  full_mult <- full_mult[rm]
  for (i in 1:len) {
    full_vectors[[i]][[2]] <- full_vectors[[i]][[2]][rm]
  }
  
  #Setting axes
  all <- c()
  for (i in 1:len) {
    all <- c(all, full_vectors[[i]][[2]])
  }
  yat <- pretty(all)
  xgap <- ifelse(full_mult > 0.6, full_mult - 1.4, full_mult)
  xat <- pretty(xgap)
  xlab <- ifelse(xat > 0.6, xat + 1.4, xat)
  
  #Plotting
  pal <- brewer.pal(len, "Set1")
  for (i in 1:len) {
    pal[i] <- paste(pal[i], "FF", sep="")
  }
  ggplot(xgap, full_vectors[[1]][[2]], pch=16, col=pal[1], 
       xaxt="n", yaxt="n", ylim=c(min(yat), max(yat) + 0.0), 
       main=reac_list[[1]], xlab="Water stress coefficient", 
       ylab="Phloem biomass solution flux", xlim=c(0, 0.7))
  axis(1, at=xat, labels=xlab)
  axis(2, at=yat, labels=yat)
  axis.break(1, breakpos=0.55, style="slash")
  abline(h=0, lty=2)
  legend("topright", legend=reacs, inset=c(0,0), 
         col=c(pal[1],pal[2],pal[3],pal[4]), pch=16, ncol=1)
}
