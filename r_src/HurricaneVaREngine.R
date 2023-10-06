HurricaneVaREngine <- function() {
  # rm(list = setdiff(ls(), lsf.str())) 
  
  
  
  #Libraries
  suppressMessages(library(RODBC))
  suppressMessages(library(RCurl))
  suppressMessages(library(dplyr))
  suppressMessages(library(reshape))
  suppressMessages(library(tidyverse))
  suppressMessages(library(lubridate))  
  
  control <- c("Strat","Sector","Country","MarketCap","Industry","Positions")
  
  
  positions <- read.csv(file = "\\\\10.45.95.15\\public\\Hurricane\\RVaR\\positions.csv") 
  riskfactors <- read.csv(file = "\\\\10.45.95.15\\public\\Hurricane\\RVaR\\prices.csv")
  tradedate <- as.character(as.Date(positions[1,1], "%m/%d/%Y"))
  client <- as.character(positions[1,2])
  rfid <- as.vector(positions[,c("RFID")])
  exposure <- as.vector(positions[,c("VaRExposure")])
  
  #PositionCovarianceMatrix 
  count <- nrow(riskfactors)
  ln <- log(riskfactors[2:count,]/riskfactors[1:count-1,])
  count <- nrow(ln)
  nn <- seq(count,1)
  df <- ((1-.94)*.94^(nn-1))^.5
  df_ln <- as.matrix(ln*df)
  df_ln <- df_ln
  mat <- t(df_ln)%*%df_ln
  posmat <- mat[c(rfid),c(rfid)]
  rm(count,ln,nn,df_ln,df,riskfactors)
  
  VaR_Data <- data.frame(matrix(ncol = 8, nrow = 0))
  x <- c("TradeDate","Client","Strat","VaRType","VaRSubType","AttributeType","AttributeValue","VaRValue")
  colnames(VaR_Data) <- x
  rm(x)
  
  #FirmLevelTotals
  StDev <- sqrt(t(exposure)%*%(posmat%*%exposure))
  VaR_Data[1,] <- c(tradedate,client,"FirmLevel","StDev","Total","Total","Fund",StDev)
  VaR95 <- StDev * 1.644854
  VaR_Data <- rbind(VaR_Data,c(tradedate,client,"FirmLevel","95VaR","Total","Total","Fund",VaR95))
  VaR99 <- StDev * 2.326348
  VaR_Data <- rbind(VaR_Data,c(tradedate,client,"FirmLevel","99VaR","Total","Total","Fund",VaR99))
  
  #CompVaR
  mVaR <- (posmat%*%exposure)
  compVaR <- mVaR / StDev[1,1] * exposure
  
  #FirmLevel
  for(k in unlist(control)){
    filter <- as.data.frame(unique(positions[match(TRUE,names(positions)==k)]))
    for(i in unlist(filter)){
      
      #Isolated
      filterPos <- positions[positions[match(TRUE,names(positions)==k)]==i,]
      rfid <- as.vector(filterPos[,c("RFID")])
      exposure <- as.vector(filterPos[,c("VaRExposure")])
      posmat <- mat[c(rfid),c(rfid)]
      x <- sqrt(t(exposure)%*%(posmat%*%exposure))
      x[is.na(x)] <- 0
      y <- x * 1.644854 
      VaR_Data <- rbind(VaR_Data,c(tradedate,client,"FirmLevel","95VaR","Isolated",k,i,y))
      y <- x * 2.326348
      VaR_Data <- rbind(VaR_Data,c(tradedate,client,"FirmLevel","99VaR","Isolated",k,i,y))
      
      #Component
      x <- sum((positions[match(TRUE,names(positions)==k)]==i)*compVaR)
      x[is.na(x)] <- 0
      y <- x * 1.644854 
      VaR_Data <- rbind(VaR_Data,c(tradedate,client,"FirmLevel","95VaR","Component",k,i,y))
      y <- x * 2.326348
      VaR_Data <- rbind(VaR_Data,c(tradedate,client,"FirmLevel","99VaR","Component",k,i,y))
      
      #Incremental
      filterPos <- positions[positions[match(TRUE,names(positions)==k)]!=i,]
      rfid <- as.vector(filterPos[,c("RFID")])
      exposure <- as.vector(filterPos[,c("VaRExposure")])
      posmat <- mat[c(rfid),c(rfid)]
      x <- sqrt(t(exposure)%*%(posmat%*%exposure))
      x[is.na(x)] <- 0
      y <- (StDev - x) * 1.644854 
      VaR_Data <- rbind(VaR_Data,c(tradedate,client,"FirmLevel","95VaR","Incremental",k,i,y))
      y <- (StDev - x) * 2.326348
      VaR_Data <- rbind(VaR_Data,c(tradedate,client,"FirmLevel","99VaR","Incremental",k,i,y))
      
    }
  }
  rm(k,i,x,y,filterPos,rfid,exposure,posmat,filter)
  
  #StratLevel
  strats <- as.data.frame(unique(positions$Strat))
  control <- control[-1]
  
  for(s in unlist(strats)){
    stratPos <- positions[positions$Strat==s,]
    rfid <- as.vector(stratPos[,c("RFID")])
    exposure <- as.vector(stratPos[,c("VaRExposure")])
    posmat <- mat[c(rfid),c(rfid)]
    
    #StratLevelTotals
    StDev <- sqrt(t(exposure)%*%(posmat%*%exposure))
    VaR_Data <- rbind(VaR_Data,c(tradedate,client,s,"StDev","Total","Total","Strat",StDev))
    VaR95 <- StDev * 1.644854
    VaR_Data <- rbind(VaR_Data,c(tradedate,client,s,"95VaR","Total","Total","Strat",VaR95))
    VaR99 <- StDev * 2.326348
    VaR_Data <- rbind(VaR_Data,c(tradedate,client,s,"99VaR","Total","Total","Strat",VaR99))
    
    #CompVaR
    mVaR <- (posmat%*%exposure)
    compVaR <- mVaR / StDev[1,1] * exposure
    
    for(k in unlist(control)){
      filter <- as.data.frame(unique(stratPos[match(TRUE,names(stratPos)==k)]))
      for(i in unlist(filter)){
        
        #Isolated
        filterPos <- stratPos[stratPos[match(TRUE,names(stratPos)==k)]==i,]
        rfid <- as.vector(filterPos[,c("RFID")])
        exposure <- as.vector(filterPos[,c("VaRExposure")])
        posmat <- mat[c(rfid),c(rfid)]
        x <- sqrt(t(exposure)%*%(posmat%*%exposure))
        x[is.na(x)] <- 0
        y <- x * 1.644854 
        VaR_Data <- rbind(VaR_Data,c(tradedate,client,s,"95VaR","Isolated",k,i,y))
        y <- x * 2.326348
        VaR_Data <- rbind(VaR_Data,c(tradedate,client,s,"99VaR","Isolated",k,i,y))
        
        #Component
        x <- sum((stratPos[match(TRUE,names(stratPos)==k)]==i)*compVaR)
        x[is.na(x)] <- 0
        y <- x * 1.644854 
        VaR_Data <- rbind(VaR_Data,c(tradedate,client,s,"95VaR","Component",k,i,y))
        y <- x * 2.326348
        VaR_Data <- rbind(VaR_Data,c(tradedate,client,s,"99VaR","Component",k,i,y))
        
        #Incremental
        filterPos <- stratPos[stratPos[match(TRUE,names(stratPos)==k)]!=i,]
        rfid <- as.vector(filterPos[,c("RFID")])
        exposure <- as.vector(filterPos[,c("VaRExposure")])
        posmat <- mat[c(rfid),c(rfid)]
        x <- sqrt(t(exposure)%*%(posmat%*%exposure))
        x[is.na(x)] <- 0
        y <- (StDev - x) * 1.644854 
        VaR_Data <- rbind(VaR_Data,c(tradedate,client,s,"95VaR","Incremental",k,i,y))
        y <- (StDev - x) * 2.326348
        VaR_Data <- rbind(VaR_Data,c(tradedate,client,s,"99VaR","Incremental",k,i,y))
        
      }
    }
    rm(k,i,x,y,filterPos,rfid,exposure,posmat,filter)
    
  }
  
  write.csv(VaR_Data,paste0("\\\\10.45.95.15\\public\\Hurricane\\RVaR\\VaR_Data.csv"), row.names = FALSE)
  write.csv(VaR_Data,paste0("\\\\10.45.95.15\\public\\Hurricane\\RVaR\\VaR_Data_",tradedate,".csv"), row.names = FALSE)  
}
