library("readxl")
library("plotrix")
library("RColorBrewer")

import.scan <- function(weight) {
  path <- paste("../Final_Files/", weight, "-1000-corr.xlsx", sep="")
  df <- data.frame(read_excel(path, sheet=2, col_names=FALSE))
  #Remove extra CO2_tx and set row index as reac name
  rows <- dim(df)[1]
  df <- df[-c((rows - 3):rows),]
  rownames(df) <- df[,1]
  df <- df[,-1]
  return(df)
}

plot.pl <- function(x, y, pch, col, lwd=1.8, cex=0.8, lty=1) {
  #Plot points
  points(x, y, pch=pch, col=col, type="p", cex=cex)
  #Plot lines
  points(x, y, pch=pch, col=col, type="l", lwd=lwd, lty=lty)
}

plot.reacs <- function(weight, type="phase", reac.list=c("CO2_tx"), 
                       title=expression("CO"[2]*" Transfer Scan")) {
  #Grab breakpoints
  top <- df[1,]
  
  #Expand reaction name to four phases
  reacs <- c()
  if (type == "phloem") {
    reacs <- c(reacs, "phloem_biomass")
  } else if (type == "phase") {
    for (i in 1:length(reac.list)) {
      reacs <- c(reacs, paste(reac.list[i], "1", sep=""))
      reacs <- c(reacs, paste(reac.list[i], "2", sep=""))
      reacs <- c(reacs, paste(reac.list[i], "3", sep=""))
      reacs <- c(reacs, paste(reac.list[i], "4", sep=""))
    }
  } else if (type == "link") {
    for (i in 1:length(reac.list)) {
      reacs <- c(reacs, paste(reac.list[i], "1_2", sep=""))
      reacs <- c(reacs, paste(reac.list[i], "2_3", sep=""))
      reacs <- c(reacs, paste(reac.list[i], "3_4", sep=""))
      reacs <- c(reacs, paste(reac.list[i], "4_1", sep=""))
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
  #Adding last breakpoint + some extra to inf
  vlen <- length(multiplier)
  for (i in 1:len) {
    extra <- rep(vectors[[i]][vlen], 9)
    full_vectors[[i]] <- c(full_vectors[[i]], vectors[[i]][vlen], extra)
  }
  
  #Building x values
  full_mult <- seq(0, multiplier[vlen] + 0.01 * 9, by=0.01)
  
  #Remove extra values for a break
  if (weight == "1111") {
    fb <- 0.74
    minus <- 1.25
  } else if (weight == "1222" | weight == "1242") {
    fb <- 0.54
    minus <- 1.45
  } else {
    stop("Invalid weight.")
  }
  rm1 <- ifelse(full_mult < fb, TRUE, FALSE)
  rm2 <- ifelse(full_mult > 2.015 & full_mult < 2.085, TRUE, FALSE)
  rm3 <- ifelse(full_mult > 2.115 & full_mult < 2.155, TRUE, FALSE)
  mult1 <- full_mult[rm1]
  mult2 <- full_mult[rm2] - minus
  mult3 <- full_mult[rm3] - minus
  for (i in 1:len) {
    full_vectors[[i]] <- list(full_vectors[[i]][rm1], full_vectors[[i]][rm2], full_vectors[[i]][rm3])
  }
  
  #Setting axes
  all <- c()
  for (i in 1:len) {
    all <- c(all, full_vectors[[i]][[1]], full_vectors[[i]][[2]], full_vectors[[i]][[3]])
  }
  yat <- pretty(all)
  gap <- yat[length(yat)] - yat[length(yat) - 1]
  yat <- c(yat[1] - gap, yat, yat[length(yat)] + gap)
  xgap <- c(mult1, mult2, mult3)
  gaps <- floor(round(xgap[length(xgap)], 2) * 10 / 1) + 1
  xat <- seq(0, by=0.1, length.out=gaps)
  xlab <- ifelse(xat > fb + 0.01, xat + minus, xat)
  
  #PLOTTING
  filename <- gsub("\\)", "", gsub(" \\(", "_", gsub(":", "", gsub("\\* ", "", gsub("\"", "", toString(title))))))
  png(file=paste(filename, ".png", sep=""), width=5000, height=2500, res=600)
  
  #Set font and colors
  windowsFonts(TNR=windowsFont("Times New Roman"))
  par(family="TNR")
  pal <- brewer.pal(len, "Set1")
  rects <- brewer.pal(4, "Set3")
  #Adjust opacity of shading
  for (i in 1:4) {
    rects[i] <- paste(rects[i], "33", sep="")
  }
  #Set shapes
  pch <- c(1,0,5,6,16,15,18,17)
  
  #Initialize plot
  plot(0, xaxt="n", yaxt="n", ylim=range(yat), xlim=range(xgap), 
       main=title, xlab="Water Stress Coefficient", 
       ylab=expression("Solution Flux (mol/m"^2*")"), cex.lab=0.9)
  
  #Writing and shading
  if (weight == "1242") {
    rect(xleft=c(-1,0.165,0.315,0.615), xright=c(0.165,0.315,0.615,10), ybottom=c(-10), ytop=c(10), 
         col=rects, border=NA)
    text(c(0.08, 0.24, 0.47, 0.67), c(yat[1]), cex=0.8, 
         labels=c(expression("C"[3]), expression("C"[3]*"-CAM Transition"), "CAM", "CAM Idling"))
  } else if (weight == "1222") {
    rectst <- c(rects[1], rects[3], rects[4])
    rect(xleft=c(-1,0.505,0.615), xright=c(0.505,0.615,10), ybottom=c(-10), ytop=c(10), 
         col=rectst, border=NA)
    text(c(0.25, 0.56, 0.67), c(yat[1]), cex=0.8, 
         labels=c(expression("C"[3]), "CAM", "CAM Idling"))
  } else if (weight == "1111") {
    rectst <- c(rects[1], rects[4])
    rect(xleft=c(-1,0.815), xright=c(0.815,10), ybottom=c(-10), ytop=c(10), 
         col=rectst, border=NA)
    text(c(0.4, 0.87), c(yat[1]), cex=0.8, 
         labels=c(expression("C"[3]), "CAM Idling"))
  }
  
  #Plot the dashed portion
  last1 <- length(full_vectors[[1]][[1]])
  last2 <- length(full_vectors[[1]][[2]])
  xdash1 <- c(mult1[length(mult1)], mult2[1])
  xdash2 <- c(mult2[length(mult2)], mult3[1])
  #Plot reactions
  for (i in 1:len) {
    #First line
    plot.pl(mult1, full_vectors[[i]][[1]], pch[i], pal[i])
    #First break
    ydash1 <- c(full_vectors[[i]][[1]][last1],
               full_vectors[[i]][[2]][1])
    plot.pl(xdash1, ydash1, pch[i], pal[i], lty=2)
    #Second line
    plot.pl(mult2, full_vectors[[i]][[2]], pch[i], pal[i])
    #Second break
    ydash2 <- c(full_vectors[[i]][[2]][last2],
               full_vectors[[i]][[3]][1])
    plot.pl(xdash2, ydash2, pch[i], pal[i], lty=2)
    #Third line
    plot.pl(mult3, full_vectors[[i]][[3]], pch[i], pal[i])
  }
  
  #Plot lines for CAM phases
  if (weight == "1242") {
    abline(v=0.165, lty=2) #C3
    abline(v=0.315, lty=2) #CAM transition
    abline(v=0.615, lty=2) #CAM
  } else if (weight == "1222") {
    abline(v=0.505, lty=2) #C3
    abline(v=0.615, lty=2) #CAM
  } else if (weight == "1111") {
    abline(v=0.815, lty=2) #C3
  }
  
  #Set the axes ticks and labels, and add legend
  axis(1, at=xat[-length(xat)], labels=xlab[-length(xlab)])
  axis(1, at=xat[length(xat)], labels=expression(10))
  axis(2, at=yat, labels=yat)
  axis.break(1, breakpos=fb + 0.01, style="slash")
  axis.break(1, breakpos=fb + 0.01 + 0.1, style="slash")
  abline(h=0, lty=2)
  if (type != "phloem") {
    legend("topright", legend=c("Phase 1", "Phase 2", "Phase 3", "Phase 4"), 
           col=pal, pch=pch, cex=0.8, ncol=4)
  }
  dev.off()
}
