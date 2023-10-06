FactorResidualBetas <- function(factors, factorPrices, positions, positionPrices){
  count <- nrow(factorPrices);
  factorReturns <- factorPrices[2:count,]/factorPrices[1:count-1,]-1;
  positionReturns <- positionPrices[2:count,]/positionPrices[1:count-1,]-1;
#  betaEquity <- cov(positionReturns,factorReturns[,2])/var(factorReturns[,2]);
  countCol <- ncol(factorReturns);
#  factorEquityBeta <- cov(factorReturns[,3:countCol],factorReturns[,2])/var(factorReturns[,2]);
#  factorEquityBetaMat <- t(matrix(rep(factorEquityBeta,count-1),ncol=count-1));
#  residualReturns <- (factorReturns[,3:countCol])-((factorReturns[,2])*factorEquityBetaMat);
  factorReturnsRF <- factorReturns[,2:countCol] - factorReturns[,1];
  positionReturnsRF <- positionReturns - factorReturns[,1];
  betaEquity <- cov(positionReturnsRF,factorReturnsRF[,1])/var(factorReturnsRF[,1]);
  countCol <- ncol(factorReturnsRF);
  factorEquityBeta <- cov(factorReturnsRF[,2:countCol],factorReturnsRF[,1])/var(factorReturnsRF[,1]);
  factorEquityBetaMat <- t(matrix(rep(factorEquityBeta,count-1),ncol=count-1));
  residualReturns <- factorReturnsRF[,2:countCol]-factorReturnsRF[,1]*factorEquityBetaMat;
  betaFactors <- numeric(0);
  for(i in 1:ncol(residualReturns)){
    for(n in 1:ncol(positionReturnsRF)){
      betaFactors <- c(betaFactors,cov(positionReturnsRF[,n],residualReturns[,i])/var(residualReturns[,i]));
    }
  }
  factors <- matrix(c('Factors',factors),ncol=1);
  betaFactors <- t(matrix(betaFactors,ncol=ncol(residualReturns)));
  x <- t(matrix(c(positions,betaEquity),ncol=2));
  x <- rbind(x,betaFactors);
  x <- cbind(factors,x);
  x <- t(x);
  return( x );
}

FactorBetas <- function(factors, factorPrices, positions, positionPrices){
  count <- nrow(factorPrices);
  factorReturns <- factorPrices[2:count,]/factorPrices[1:count-1,]-1;
  positionReturns <- positionPrices[2:count,]/positionPrices[1:count-1,]-1;
  countCol <- ncol(factorReturns);
  factorReturnsRF <- factorReturns[,2:countCol] - factorReturns[,1];
  positionReturnsRF <- positionReturns - factorReturns[,1];
  betaFactors <- numeric(0);
  for(i in 1:ncol(factorReturnsRF)){
    for(n in 1:ncol(positionReturnsRF)){
      betaFactors <- c(betaFactors,cov(positionReturnsRF[,n],factorReturnsRF[,i])/var(factorReturnsRF[,i]));
    }
  }
  factors <- matrix(c('Factors',factors),ncol=1);
  betaFactors <- t(matrix(betaFactors,ncol=ncol(factorReturnsRF)));
  x <- rbind(positions,betaFactors);
  x <- cbind(factors,x);
  x <- t(x);
  return( x );
}


FundLevelBetas <- function(factors, factorPrices, positions, positionPrices, rfid, exposure, AUM){
  count <- nrow(factorPrices);
  factorReturns <- factorPrices[2:count,]/factorPrices[1:count-1,]-1;
  positionReturns <- positionPrices[2:count,]/positionPrices[1:count-1,]-1;
  fundPNL <- HistSeries(positionPrices,rfid,exposure);
  fundRtn <- fundPNL/AUM;
  positionReturns <- cbind(positionReturns,fundRtn);
  positions <- c(positions, 'Fund');
  betaEquity <- cov(positionReturns,factorReturns[,1])/var(factorReturns[,1]);
  countCol <- ncol(factorPrices);
  factorEquityBeta <- cov(factorReturns[,2:countCol],factorReturns[,1])/var(factorReturns[,1]);
  factorEquityBetaMat <- t(matrix(rep(factorEquityBeta,count-1),ncol=count-1));
  residualReturns <- factorReturns[,2:countCol]-factorReturns[,1]*factorEquityBetaMat;
  betaFactors <- numeric(0);
  for(i in 1:ncol(residualReturns)){
    for(n in 1:ncol(positionReturns)){
      betaFactors <- c(betaFactors,cov(positionReturns[,n],residualReturns[,i])/var(residualReturns[,i]));
    }
  }
  factors <- matrix(c('Factors',factors),ncol=1);
  betaFactors <- t(matrix(betaFactors,ncol=ncol(residualReturns)));
  x <- t(matrix(c(positions,betaEquity),ncol=2));
  x <- rbind(x,betaFactors);
  x <- cbind(factors,x);
  x <- t(x);
  return( x );
}


StyleFactors <- function(factorPrices,positionPrices){
  count <- nrow(factorPrices);
  factorReturns <- factorPrices[2:count,]/factorPrices[1:count-1,]-1;
  positionReturns <- positionPrices[2:count,]/positionPrices[1:count-1,]-1;
  factorReturnsRF <- factorReturns[,2:6] - factorReturns[,1];
  positionReturnsRF <- positionReturns - factorReturns[,1];
  betasEquity <- cov(positionReturnsRF,factorReturnsRF[,1])/var(factorReturnsRF[,1]);
  countCol <- ncol(factorReturnsRF);
  factorEquityBeta <- cov(factorReturnsRF[,2:countCol],factorReturnsRF[,1])/var(factorReturnsRF[,1]);
  factorEquityBetaMat <- t(matrix(rep(factorEquityBeta,count-1),ncol=count-1));
  residualReturns <- factorReturnsRF[,2:countCol]-factorReturnsRF[,1]*factorEquityBetaMat;
  sizeReturns <- residualReturns[,1] - residualReturns[,2];
  valueReturns <- residualReturns[,3] - residualReturns[,4];
  betaSize <- numeric(0);
  betaValue <- numeric(0);
    for(n in 1:ncol(positionReturnsRF)){
      betaSize <- c(betaSize,cov(positionReturns[,n],sizeReturns)/var(sizeReturns));
      betaValue <- c(betaValue,cov(positionReturns[,n],valueReturns)/var(valueReturns));
    }
  betas <- matrix(c(betasEquity, betaSize, betaValue),ncol=3);
  x <- betas;
  return(x);
}

StyleAndResidualFactors <- function(factors, factorPrices, positions, positionPrices){
  count <- nrow(factorPrices);
  factorReturns <- factorPrices[2:count,]/factorPrices[1:count-1,]-1;
  positionReturns <- positionPrices[2:count,]/positionPrices[1:count-1,]-1;
  countCol <- ncol(factorReturns);
  factorReturnsRF <- factorReturns[,2:countCol] - factorReturns[,1];
  positionReturnsRF <- positionReturns - factorReturns[,1];
  betaEquity <- cov(positionReturnsRF,factorReturnsRF[,1])/var(factorReturnsRF[,1]);
  countCol <- ncol(factorReturnsRF);
  factorEquityBeta <- cov(factorReturnsRF[,2:countCol],factorReturnsRF[,1])/var(factorReturnsRF[,1]);
  factorEquityBetaMat <- t(matrix(rep(factorEquityBeta,count-1),ncol=count-1));
  residualReturns <- factorReturnsRF[,2:countCol]-factorReturnsRF[,1]*factorEquityBetaMat;
  sizeReturns <- residualReturns[,1] - residualReturns[,2];
  valueReturns <- residualReturns[,3] - residualReturns[,4];
  betaFactors <- numeric(0);
  betaSize <- numeric(0);
  betaValue <- numeric(0);
  for(n in 1:ncol(positionReturnsRF)){
    betaSize <- c(betaSize,cov(positionReturns[,n],sizeReturns)/var(sizeReturns));
    betaValue <- c(betaValue,cov(positionReturns[,n],valueReturns)/var(valueReturns));
  }
  for(i in 5:ncol(residualReturns)){
    for(n in 1:ncol(positionReturnsRF)){
      betaFactors <- c(betaFactors,cov(positionReturnsRF[,n],residualReturns[,i])/var(residualReturns[,i]));
    }
  }
  factors <- matrix(c('Factors',factors),ncol=1);
  betaFactors <- t(matrix(betaFactors,ncol=(ncol(residualReturns)-4)));
  x <- t(matrix(c(positions,betaEquity, betaSize, betaValue),ncol=4));
  x <- rbind(x,betaFactors);
  x <- cbind(factors,x);
  x <- t(x);
  return( x );
}

StyleAndResidualFactorsDecay <- function(factors, factorPrices, positions, positionPrices){
  count <- nrow(factorPrices);
  factorReturns <- factorPrices[2:count,]/factorPrices[1:count-1,]-1;
  positionReturns <- positionPrices[2:count,]/positionPrices[1:count-1,]-1;
  countCol <- ncol(factorReturns);
  factorReturnsRF <- factorReturns[,2:countCol] - factorReturns[,1];
  positionReturnsRF <- positionReturns - factorReturns[,1];
  nn <- seq(count-1,1);
  df <- ((1-.94)*.94^(nn-1))^0.5;
  factorReturnsRF <- factorReturnsRF * df;
  positionReturnsRF <- positionReturnsRF * df;
  betaEquity <- cov(positionReturnsRF,factorReturnsRF[,1])/var(factorReturnsRF[,1]);
  countCol <- ncol(factorReturnsRF);
  factorEquityBeta <- cov(factorReturnsRF[,2:countCol],factorReturnsRF[,1])/var(factorReturnsRF[,1]);
  factorEquityBetaMat <- t(matrix(rep(factorEquityBeta,count-1),ncol=count-1));
  residualReturns <- factorReturnsRF[,2:countCol]-factorReturnsRF[,1]*factorEquityBetaMat;
  sizeReturns <- (residualReturns[,1] - residualReturns[,2]);
  valueReturns <- (residualReturns[,3] - residualReturns[,4]);
  betaFactors <- numeric(0);
  betaSize <- numeric(0);
  betaValue <- numeric(0);
  for(n in 1:ncol(positionReturnsRF)){
    betaSize <- c(betaSize,cov(positionReturnsRF[,n],sizeReturns)/var(sizeReturns));
    betaValue <- c(betaValue,cov(positionReturnsRF[,n],valueReturns)/var(valueReturns));
  }
  for(i in 5:ncol(residualReturns)){
    for(n in 1:ncol(positionReturnsRF)){
      betaFactors <- c(betaFactors,cov(positionReturnsRF[,n],residualReturns[,i])/var(residualReturns[,i]));
    }
  }
  factors <- matrix(c('Factors',factors),ncol=1);
  betaFactors <- t(matrix(betaFactors,ncol=(ncol(residualReturns)-4)));
  x <- t(matrix(c(positions,betaEquity, betaSize, betaValue),ncol=4));
  x <- rbind(x,betaFactors);
  x <- cbind(factors,x);
  x <- t(x);
  return( x );
}

FactorReturns <- function(factors, factorPrices){
  count <- nrow(factorPrices);
  factorReturns <- factorPrices[2:count,]/factorPrices[1:count-1,]-1;
  countCol <- ncol(factorReturns);
  factorReturnsRF <- factorReturns[,2:countCol] - factorReturns[,1];
  countCol <- ncol(factorReturnsRF);
  factorEquityBeta <- cov(factorReturnsRF[,2:countCol],factorReturnsRF[,1])/var(factorReturnsRF[,1]);
  factorEquityBetaMat <- t(matrix(rep(factorEquityBeta,count-1),ncol=count-1));
  residualReturns <- factorReturnsRF[,2:countCol]-factorReturnsRF[,1]*factorEquityBetaMat;
  sizeReturns <- residualReturns[,1] - residualReturns[,2];
  valueReturns <- residualReturns[,3] - residualReturns[,4];
  allReturns <- cbind(factorReturnsRF[,1],sizeReturns,valueReturns,residualReturns[,5:ncol(residualReturns)]);
  allReturns <- rbind(t(factors),allReturns);
  x <- allReturns;
  x <- as.matrix(x);
  x <- matrix(x, ncol = ncol(x), dimnames = NULL);
#  count <- nrow(factorPrices);
#  factorReturns <- factorPrices[2:count,]/factorPrices[1:count-1,]-1;
#  countCol <- ncol(factorReturns);
#  factorEquityBeta <- cov(factorReturns[,3:countCol],factorReturns[,2])/var(factorReturns[,2]);
#  factorEquityBetaMat <- t(matrix(rep(factorEquityBeta,count-1),ncol=count-1));
#  residualReturns <- (factorReturns[,3:countCol])-((factorReturns[,2])*factorEquityBetaMat);
#  allReturns <- cbind(factorReturnsRF[,2],sizeReturns,valueReturns,residualReturns);
#  allReturns <- rbind(factors,allReturns);
#  x <- allReturns;
  return( x );
}

FactorVolHist <- function(factors, factorPrices1Y){
  volHist <- numeric(0)
  i <- 128
  n <- 1
  for(n in 1:129){
    factorPrices <- factorPrices1Y[n:i,]
    count <- nrow(factorPrices);
    factorReturns <- factorPrices[2:count,]/factorPrices[1:count-1,]-1;
    countCol <- ncol(factorReturns);
    factorReturnsRF <- factorReturns[,2:countCol] - factorReturns[,1];
    countCol <- ncol(factorReturnsRF);
    factorEquityBeta <- cov(factorReturnsRF[,2:countCol],factorReturnsRF[,1])/var(factorReturnsRF[,1]);
    factorEquityBetaMat <- t(matrix(rep(factorEquityBeta,count-1),ncol=count-1));
    residualReturns <- factorReturnsRF[,2:countCol]-factorReturnsRF[,1]*factorEquityBetaMat;
    sizeReturns <- as.vector(residualReturns[,1] - residualReturns[,2]);
    valueReturns <- as.vector(residualReturns[,3] - residualReturns[,4]);
    allReturns <- cbind(factorReturnsRF[,1],sizeReturns,valueReturns,residualReturns[,5:ncol(residualReturns)]);
    allReturns <- matrix(allReturns, ncol = ncol(allReturns), dimnames = NULL)
    allReturns <- as.data.frame(allReturns)
    factors <- t(factors);
    names(allReturns) <- factors;
    volatilities <- as.matrix(sapply(allReturns, sd))
    volatilities <- matrix(volatilities, ncol = ncol(volatilities), dimnames = NULL);
    volHist <- cbind(volHist,volatilities)
    i <- i+1
  }
  volHist <- as.data.frame(t(volHist))
  names(volHist) <- factors
  return( volHist );
}


PositionReturns <- function(positions, positionPrices){
  count <- nrow(positionPrices);
  positionReturns <- positionPrices[2:count,]/positionPrices[1:count-1,]-1;
  allReturns <- rbind(positions,positionReturns);
  x <- allReturns;
  x <- as.matrix(x);
  x <- matrix(x, ncol = ncol(x), dimnames = NULL);
  return( x );
}



StyleAndResidualFactorsLoop <- function(factors, factorPrices, positions, positionPrices, dateCol){
  count <- nrow(factorPrices);
  factorReturns <- factorPrices[2:count,]/factorPrices[1:count-1,]-1;
  positionReturns <- positionPrices[2:count,]/positionPrices[1:count-1,]-1;
  countCol <- ncol(factorReturns);
  factorReturnsRF <- factorReturns[,2:countCol] - factorReturns[,1];
  positionReturnsRF <- positionReturns - factorReturns[,1];
  betaAllFactorsAgg <- numeric(0);
  
  for(k in 1:(count-127)){
    date <- dateCol[k+127];
    j <- k+126;
    betaEquity <- cov(positionReturnsRF[k:j,],factorReturnsRF[k:j,1])/var(factorReturnsRF[k:j,1]);
    countCol <- ncol(factorReturnsRF);
    factorEquityBeta <- cov(factorReturnsRF[k:j,2:countCol],factorReturnsRF[k:j,1])/var(factorReturnsRF[k:j,1]);
    factorEquityBetaMat <- t(matrix(rep(factorEquityBeta,127),ncol=127));
    residualReturns <- factorReturnsRF[k:j,2:countCol]-factorReturnsRF[k:j,1]*factorEquityBetaMat;
    sizeReturns <- residualReturns[,1] - residualReturns[,2];
    valueReturns <- residualReturns[,3] - residualReturns[,4];
    betaFactors <- numeric(0);
    betaSize <- numeric(0);
    betaValue <- numeric(0);
    for(n in 1:ncol(positionReturnsRF)){
      betaSize <- c(betaSize,cov(positionReturns[k:j,n],sizeReturns)/var(sizeReturns));
      betaValue <- c(betaValue,cov(positionReturns[k:j,n],valueReturns)/var(valueReturns));
    }
    for(i in 5:ncol(residualReturns)){
      for(n in 1:ncol(positionReturnsRF)){
        betaFactors <- c(betaFactors,cov(positionReturnsRF[k:j,n],residualReturns[,i])/var(residualReturns[,i]));
      }
    }
    betaFactors <- t(matrix(betaFactors,ncol=(ncol(residualReturns)-4)));
    betaFirstFourFactors <- t(matrix(c(positions,betaEquity, betaSize, betaValue),ncol=4));
    betaAllFactors <- rbind(betaFirstFourFactors,betaFactors);
    betaAllFactors <- rbind(matrix(date,ncol=ncol(positions)),betaAllFactors);
    betaAllFactorsAgg <- cbind(betaAllFactorsAgg,betaAllFactors)
  }


  factors <- matrix(c('Date','Factors',factors),ncol=1);
  x <- cbind(factors, betaAllFactorsAgg);
  x <- t(x);
  return( x );
}


PositionResidualVolatility <- function(factors, factorPrices, positions, positionPrices){
  count <- nrow(factorPrices);
  factorReturns <- factorPrices[2:count,]/factorPrices[1:count-1,]-1;
  positionReturns <- positionPrices[2:count,]/positionPrices[1:count-1,]-1;
  countCol <- ncol(factorReturns);
  factorReturnsRF <- factorReturns[,2:countCol] - factorReturns[,1];
  positionReturnsRF <- positionReturns - factorReturns[,1];
  betaEquity <- cov(positionReturnsRF,factorReturnsRF[,1])/var(factorReturnsRF[,1]);
  countCol <- ncol(factorReturnsRF);
  factorEquityBeta <- cov(factorReturnsRF[,2:countCol],factorReturnsRF[,1])/var(factorReturnsRF[,1]);
  factorEquityBetaMat <- t(matrix(rep(factorEquityBeta,count-1),ncol=count-1));
  residualReturns <- factorReturnsRF[,2:countCol]-factorReturnsRF[,1]*factorEquityBetaMat;
  countCol <- ncol(residualReturns);
  sizeReturns <- as.vector(residualReturns[,1] - residualReturns[,2]);
  valueReturns <- as.vector(residualReturns[,3] - residualReturns[,4]);
  factorReturns <- cbind(factorReturnsRF[,1],unname(cbind(sizeReturns,valueReturns)),residualReturns[,5:countCol])
  betaFactors <- numeric(0);
  for(i in 1:ncol(factorReturns)){
    for(n in 1:ncol(positionReturnsRF)){
      betaFactors <- c(betaFactors,cov(positionReturnsRF[,n],factorReturns[,i])/var(factorReturns[,i]));
    }
  }
  factors <- matrix(c('ResVol',factors),ncol=1);
  betaFactors <- matrix(betaFactors,ncol=(ncol(factorReturns)));
  residualPosVol <- numeric(0);
  for(i in 1:ncol(factorReturns)){
    for(n in 1:ncol(positionReturnsRF)){
      if(n == 1 & i == 1){
        residualPosVol <- c(residualPosVol,sd(positionReturnsRF[,n] - factorReturns[,i]*betaFactors[n,i]));
      } else {
        residualPosVol <- c(residualPosVol,sd(positionReturnsRF[,n] - factorReturns[,1]*betaFactors[n,1] - factorReturns[,i]*betaFactors[n,i]));
      }
      
    }
  }
  residualPosVol <- matrix(residualPosVol,ncol=(ncol(factorReturns)));
  x <- matrix(c(positions),ncol=1);
  x <- cbind(x,residualPosVol);
  x <- rbind(t(factors),x);
  return( x );
}