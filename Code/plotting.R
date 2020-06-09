library("readxl")
library("plotrix")
library("RColorBrewer")

df <- data.frame(read_excel("../Final_Files/1242-1000-corr.xlsx", sheet=2))

#Remove extra CO2_tx and set row index as reac name, also remove 0.175 values
rows <- dim(df)[1]
df <- df[-c((rows-3):rows),-10]
rownames(df) <- df$CO2.Weight.Multiplier

#Grab breakpoints except 0.175
top <- data.frame(read_excel("../Final_Files/1242-1000-corr.xlsx", sheet=2, n_max=1, col_names=FALSE))
top <- top[,-10]


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
  rm1 <- ifelse(full_mult < 0.54, TRUE, FALSE)
  rm2 <- ifelse(full_mult > 2.015, TRUE, FALSE)
  mult1 <- full_mult[rm1]
  mult2 <- full_mult[rm2] - 1.45
  for (i in 1:len) {
    full_vectors[[i]][[2]] <- list(full_vectors[[i]][[2]][rm1], 
                                   full_vectors[[i]][[2]][rm2])
  }
  
  #Setting axes
  all <- c()
  for (i in 1:len) {
    all <- c(all, full_vectors[[i]][[2]][[1]], full_vectors[[i]][[2]][[2]])
  }
  yat <- pretty(all)
  xgap <- c(mult1, mult2)
  xat <- pretty(xgap)
  xlab <- ifelse(xat > 0.55, xat + 1.45, xat)
  
  #Plotting
  pal <- brewer.pal(len, "Set1")
  for (i in 1:len) {
    pal[i] <- paste(pal[i], "FF", sep="")
  }
  pch <- c(16, 17, 18, 15)
  #pch <- c(1,2,5,6)
  plot(mult1, full_vectors[[1]][[2]][[1]], pch=pch[1], col=pal[1], 
       xaxt="n", yaxt="n", ylim=c(min(yat), max(yat) + 0.05), 
       main="CO2_tx", xlab="Water stress coefficient", 
       ylab="CO2 solution flux", xlim=range(xgap), type="o")
  points(mult2, full_vectors[[1]][[2]][[2]], pch=pch[1], col=pal[1], type="o")
  for (i in 2:len) {
    points(mult1, full_vectors[[i]][[2]][[1]], pch=pch[i], col=pal[i], type="o")
    points(mult2, full_vectors[[i]][[2]][[2]], pch=pch[i], col=pal[i], type="o")
  }
  axis(1, at=xat, labels=xlab)
  axis(2, at=yat, labels=yat)
  axis.break(1, breakpos=0.55, style="slash")
  abline(h=0, lty=2)
  abline(v=0.55, col="black", lwd=3, lty=2)
  legend("topright", legend=reacs, 
         col=c(pal[1],pal[2],pal[3],pal[4]), pch=pch, ncol=4)
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
  rm1 <- ifelse(full_mult < 0.54, TRUE, FALSE)
  rm2 <- ifelse(full_mult > 2.015, TRUE, FALSE)
  mult1 <- full_mult[rm1]
  mult2 <- full_mult[rm2] - 1.45
  for (i in 1:len) {
    full_vectors[[i]][[2]] <- list(full_vectors[[i]][[2]][rm1], 
                                   full_vectors[[i]][[2]][rm2])
  }
  
  #Setting axes
  all <- c()
  for (i in 1:len) {
    all <- c(all, full_vectors[[i]][[2]][[1]], full_vectors[[i]][[2]][[2]])
  }
  yat <- pretty(all)
  xgap <- c(mult1, mult2)
  xat <- pretty(xgap)
  xlab <- ifelse(xat > 0.55, xat + 1.45, xat)
  
  #Plotting
  pal <- brewer.pal(len, "Set1")
  for (i in 1:len) {
    pal[i] <- paste(pal[i], "FF", sep="")
  }
  pch <- c(16, 17, 18, 15)
  pch <- c(1,0,5,6)
  plot(mult1, full_vectors[[1]][[2]][[1]], pch=pch[1], col=pal[1], 
       xaxt="n", yaxt="n", ylim=c(min(yat), max(yat) + 0.05), 
       main="CO2_tx", xlab="Water stress coefficient", 
       ylab="CO2 solution flux", xlim=range(xgap), type="o")
  points(mult2, full_vectors[[1]][[2]][[2]], pch=pch[1], col=pal[1], type="o")
  xdash <- c(mult1[length(mult1)], mult2[1])
  ydash <- c(full_vectors[[1]][[2]][[1]][length(full_vectors[[1]][[2]][[1]])],
             full_vectors[[1]][[2]][[2]][1])
  points(xdash, ydash, pch=pch[1], col=pal[1], type="o", lty=2)
  for (i in 2:len) {
    points(mult1, full_vectors[[i]][[2]][[1]], pch=pch[i], col=pal[i], type="o")
    points(mult2, full_vectors[[i]][[2]][[2]], pch=pch[i], col=pal[i], type="o")
    ydash <- c(full_vectors[[i]][[2]][[1]][length(full_vectors[[i]][[2]][[1]])],
               full_vectors[[i]][[2]][[2]][1])
    points(xdash, ydash, pch=pch[i], col=pal[i], type="o", lty=2)
  }
  axis(1, at=xat, labels=xlab)
  axis(2, at=yat, labels=yat)
  axis.break(1, breakpos=0.55, style="slash")
  abline(h=0, lty=2)
  abline(v=0.55, col="black", lwd=3, lty=2)
  legend("topright", legend=reacs, 
         col=c(pal[1],pal[2],pal[3],pal[4]), pch=pch, ncol=4)
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
  plot(xgap, full_vectors[[1]][[2]], pch=16, col=pal[1], 
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
