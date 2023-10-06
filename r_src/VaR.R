MatrixCorrelation <- function( riskfactors, data.in.columns=TRUE){
  count <- nrow(riskfactors);
  ln <- log(riskfactors[2:count,]/riskfactors[1:count-1,]);
  x <- cor(ln); 
  return( x );
}

MatrixCorrelationReturns <- function( riskfactors, data.in.columns=TRUE){
  x <- cor(riskfactors); 
  return( x );
}

DecayCor <- function( riskfactors, data.in.columns=TRUE){
  count <- nrow(riskfactors);
  ln <- log(riskfactors[2:count,]/riskfactors[1:count-1,]);
  count <- nrow(ln);
  nn <- seq(count,1);
  df <- ((1-.94)*.94^(nn-1))^.5;
  df_ln <- ln*df;
  covmat <- t(df_ln)%*%df_ln;
  x <- cov2cor(covmat);
  return( x );
}

DecayCov <- function( riskfactors, data.in.columns=TRUE){
  count <- nrow(riskfactors);
  ln <- log(riskfactors[2:count,]/riskfactors[1:count-1,]);
  count <- nrow(ln);
  nn <- seq(count,1);
  df <- ((1-.94)*.94^(nn-1))^.5;
  df_ln <- ln*df;
  covmat <- t(df_ln)%*%df_ln;
  x <- covmat;
  return( x );
}


MatrixCovariance <- function( riskfactors, data.in.columns=TRUE){
  count <- nrow(riskfactors);
  ln <- log(riskfactors[2:count,]/riskfactors[1:count-1,]);
  x <- cov(ln); 
  return( x );
}

PortStDev <- function ( riskfactors, rfid, exposure, data.in.columns=TRUE){ 
  mat <- cov(riskfactors); 
  posmat <- mat[c(rfid),c(rfid)];
  x <- sqrt(t(exposure)%*%(posmat%*%exposure));
  return( x ); 
}

PortStDevPrice <- function ( riskfactors, rfid, exposure, data.in.columns=TRUE){ 
  count <- nrow(riskfactors);
  ln <- log(riskfactors[2:count,]/riskfactors[1:count-1,]);
  mat <- cov(ln); 
  posmat <- mat[c(rfid),c(rfid)];
  x <- sqrt(t(exposure)%*%(posmat%*%exposure));
  return( x ); 
}

VaR95 <- function ( riskfactors, rfid, exposure, data.in.columns=TRUE){ 
  mat <- cov(riskfactors); 
  posmat <- mat[c(rfid),c(rfid)];
  x <- sqrt(t(exposure)%*%(posmat%*%exposure))*1.644854;
  return( x );
}

VaR99 <- function ( riskfactors, rfid, exposure, data.in.columns=TRUE){ 
  mat <- cov(riskfactors); 
  posmat <- mat[c(rfid),c(rfid)];
  x <- sqrt(t(exposure)%*%(posmat%*%exposure))*2.326348;
  return( x );
}

DecayVaR95 <- function ( riskfactors, rfid, exposure, data.in.columns=TRUE){
  count <- nrow(riskfactors);
  ln <- log(riskfactors[2:count,]/riskfactors[1:count-1,]);
  count <- nrow(ln);
  nn <- seq(count,1);
  df <- ((1-.94)*.94^(nn-1))^.5;
  df_ln <- ln*df;
  mat <- t(df_ln)%*%df_ln;
  posmat <- mat[c(rfid),c(rfid)];
  x <- sqrt(t(exposure)%*%(posmat%*%exposure))*1.644854;
  return( x );
}

DecayVaR99 <- function ( riskfactors, rfid, exposure, data.in.columns=TRUE){
  count <- nrow(riskfactors);
  ln <- log(riskfactors[2:count,]/riskfactors[1:count-1,]);
  count <- nrow(ln);
  nn <- seq(count,1);
  df <- ((1-.94)*.94^(nn-1))^.5;
  df_ln <- ln*df;
  mat <- t(df_ln)%*%df_ln;
  posmat <- mat[c(rfid),c(rfid)];
  x <- sqrt(t(exposure)%*%(posmat%*%exposure))*2.326348;
  return( x );
}

DecayStDev <- function ( riskfactors, rfid, exposure, data.in.columns=TRUE){
  count <- nrow(riskfactors);
  ln <- log(riskfactors[2:count,]/riskfactors[1:count-1,]);
  count <- nrow(ln);
  nn <- seq(count,1);
  df <- ((1-.94)*.94^(nn-1))^.5;
  df_ln <- ln*df;
  mat <- t(df_ln)%*%df_ln;
  posmat <- mat[c(rfid),c(rfid)];  
  x <- sqrt(t(exposure)%*%(posmat%*%exposure));
  return( x );
}

DecayCompVaR95 <- function ( riskfactors, rfid, exposure, data.in.columns=TRUE){
  count <- nrow(riskfactors);
  ln <- log(riskfactors[2:count,]/riskfactors[1:count-1,]);
  count <- nrow(ln);
  nn <- seq(count,1);
  df <- ((1-.94)*.94^(nn-1))^.5;
  df_ln <- ln*df;
  mat <- t(df_ln)%*%df_ln;
  posmat <- mat[c(rfid),c(rfid)];  
  mVaR <- (posmat%*%exposure);
  vol <- sqrt(t(exposure)%*%(posmat%*%exposure));
  x <- mVaR / vol[1,1] * exposure * 1.644854;
  return( x );
}

DecayCompVaR99 <- function ( riskfactors, rfid, exposure, data.in.columns=TRUE){
  count <- nrow(riskfactors);
  ln <- log(riskfactors[2:count,]/riskfactors[1:count-1,]);
  count <- nrow(ln);
  nn <- seq(count,1);
  df <- ((1-.94)*.94^(nn-1))^.5;
  df_ln <- ln*df;
  mat <- t(df_ln)%*%df_ln;
  posmat <- mat[c(rfid),c(rfid)];
  mVaR <- (posmat%*%exposure);
  vol <- sqrt(t(exposure)%*%(posmat%*%exposure));
  x <- mVaR / vol[1,1] * exposure * 2.326348;
  return( x );
}

FilterStDev <- function ( riskfactors, filter, filterRange, rfid, exposure, data.in.columns=TRUE){
  count <- nrow(riskfactors);
  ln <- log(riskfactors[2:count,]/riskfactors[1:count-1,]);
  count <- nrow(ln);
  nn <- seq(count,1);
  df <- ((1-.94)*.94^(nn-1))^.5;
  df_ln <- ln*df;
  mat <- t(df_ln)%*%df_ln;
  posmat <- mat[c(rfid),c(rfid)];
  filterexp <- (filterRange==filter)*exposure;
  x <- sqrt(t(filterexp)%*%(posmat%*%filterexp));
  x[is.na(x)] <- 0;
  return( x );
}

FilterIsoVaR95 <- function ( riskfactors, filter, filterRange, rfid, exposure, data.in.columns=TRUE){
  count <- nrow(riskfactors);
  ln <- log(riskfactors[2:count,]/riskfactors[1:count-1,]);
  count <- nrow(ln);
  nn <- seq(count,1);
  df <- ((1-.94)*.94^(nn-1))^.5;
  df_ln <- ln*df;
  mat <- t(df_ln)%*%df_ln;
  posmat <- mat[c(rfid),c(rfid)];
  filterexp <- (filterRange==filter)*exposure;
  x <- sqrt(t(filterexp)%*%(posmat%*%filterexp))*1.644854;
  x[is.na(x)] <- 0;
  return( x );
}

FilterIsoVaR99 <- function ( riskfactors, filter, filterRange, rfid, exposure, data.in.columns=TRUE){
  count <- nrow(riskfactors);
  ln <- log(riskfactors[2:count,]/riskfactors[1:count-1,]);
  count <- nrow(ln);
  nn <- seq(count,1);
  df <- ((1-.94)*.94^(nn-1))^.5;
  df_ln <- ln*df;
  mat <- t(df_ln)%*%df_ln;
  posmat <- mat[c(rfid),c(rfid)];
  filterexp <- (filterRange==filter)*exposure;
  x <- sqrt(t(filterexp)%*%(posmat%*%filterexp))*2.326348;
  x[is.na(x)] <- 0;
  return( x );
}

FilterIncVaR95 <- function ( riskfactors, filter, filterRange, rfid, exposure, data.in.columns=TRUE){
  count <- nrow(riskfactors);
  ln <- log(riskfactors[2:count,]/riskfactors[1:count-1,]);
  count <- nrow(ln);
  nn <- seq(count,1);
  df <- ((1-.94)*.94^(nn-1))^.5;
  df_ln <- ln*df;
  mat <- t(df_ln)%*%df_ln;
  posmat <- mat[c(rfid),c(rfid)];
  filterexp <- (filterRange!=filter)*exposure;
  x <- sqrt(t(exposure)%*%(posmat%*%exposure))*1.644854-sqrt(t(filterexp)%*%(posmat%*%filterexp))*1.644854;
  x[is.na(x)] <- 0;
  return( x );
}

FilterIncVaR99 <- function ( riskfactors, filter, filterRange, rfid, exposure, data.in.columns=TRUE){
  count <- nrow(riskfactors);
  ln <- log(riskfactors[2:count,]/riskfactors[1:count-1,]);
  count <- nrow(ln);
  nn <- seq(count,1);
  df <- ((1-.94)*.94^(nn-1))^.5;
  df_ln <- ln*df;
  mat <- t(df_ln)%*%df_ln;
  posmat <- mat[c(rfid),c(rfid)];
  filterexp <- (filterRange!=filter)*exposure;
  x <- sqrt(t(exposure)%*%(posmat%*%exposure))*2.326348-sqrt(t(filterexp)%*%(posmat%*%filterexp))*2.326348;
  x[is.na(x)] <- 0;
  return( x );
}

FilterCompVaR95 <- function ( riskfactors, filter, filterRange, rfid, exposure, data.in.columns=TRUE){
  count <- nrow(riskfactors);
  ln <- log(riskfactors[2:count,]/riskfactors[1:count-1,]);
  count <- nrow(ln);
  nn <- seq(count,1);
  df <- ((1-.94)*.94^(nn-1))^.5;
  df_ln <- ln*df;
  mat <- t(df_ln)%*%df_ln;
  posmat <- mat[c(rfid),c(rfid)];  
  mVaR <- (posmat%*%exposure);
  vol <- sqrt(t(exposure)%*%(posmat%*%exposure));
  compVaR <- mVaR / vol[1,1] * exposure * 1.644854;
  x <- sum((filterRange==filter)*compVaR);
  x[is.na(x)] <- 0;
  return( x );
}

FilterCompVaR99 <- function ( riskfactors, filter, filterRange, rfid, exposure, data.in.columns=TRUE){
  count <- nrow(riskfactors);
  ln <- log(riskfactors[2:count,]/riskfactors[1:count-1,]);
  count <- nrow(ln);
  nn <- seq(count,1);
  df <- ((1-.94)*.94^(nn-1))^.5;
  df_ln <- ln*df;
  mat <- t(df_ln)%*%df_ln;
  posmat <- mat[c(rfid),c(rfid)];  
  mVaR <- (posmat%*%exposure);
  vol <- sqrt(t(exposure)%*%(posmat%*%exposure));
  compVaR <- mVaR / vol[1,1] * exposure * 2.326348;
  x <- sum((filterRange==filter)*compVaR);
  x[is.na(x)] <- 0;
  return( x );
}

DblFilterIncVaR95 <- function ( riskfactors, filter, filterRange, strat, stratRange, rfid, exposure, data.in.columns=TRUE){
  count <- nrow(riskfactors);
  ln <- log(riskfactors[2:count,]/riskfactors[1:count-1,]);
  count <- nrow(ln);
  nn <- seq(count,1);
  df <- ((1-.94)*.94^(nn-1))^.5;
  df_ln <- ln*df;
  mat <- t(df_ln)%*%df_ln;
  posmat <- mat[c(rfid),c(rfid)];
  stratexp <- (stratRange==strat)*exposure;
  filterexp <- (filterRange!=filter)*stratexp;
  x <- sqrt(t(stratexp)%*%(posmat%*%stratexp))*1.644854-sqrt(t(filterexp)%*%(posmat%*%filterexp))*1.644854;
  x[is.na(x)] <- 0;
  return( x );
}

DblFilterIncVaR99 <- function ( riskfactors, filter, filterRange, strat, stratRange, rfid, exposure, data.in.columns=TRUE){
  count <- nrow(riskfactors);
  ln <- log(riskfactors[2:count,]/riskfactors[1:count-1,]);
  count <- nrow(ln);
  nn <- seq(count,1);
  df <- ((1-.94)*.94^(nn-1))^.5;
  df_ln <- ln*df;
  mat <- t(df_ln)%*%df_ln;
  posmat <- mat[c(rfid),c(rfid)];
  stratexp <- (stratRange==strat)*exposure;
  filterexp <- (filterRange!=filter)*stratexp;
  x <- sqrt(t(stratexp)%*%(posmat%*%stratexp))*2.326348-sqrt(t(filterexp)%*%(posmat%*%filterexp))*2.326348;
  x[is.na(x)] <- 0;
  return( x );
}

DblFilterCompVaR95 <- function ( riskfactors, filter, filterRange, strat, stratRange, rfid, exposure, data.in.columns=TRUE){
  count <- nrow(riskfactors);
  ln <- log(riskfactors[2:count,]/riskfactors[1:count-1,]);
  count <- nrow(ln);
  nn <- seq(count,1);
  df <- ((1-.94)*.94^(nn-1))^.5;
  df_ln <- ln*df;
  mat <- t(df_ln)%*%df_ln;
  posmat <- mat[c(rfid),c(rfid)];  
  stratexp <- (stratRange==strat)*exposure;
  mVaR <- (posmat%*%stratexp);
  vol <- sqrt(t(stratexp)%*%(posmat%*%stratexp));
  compVaR <- mVaR / vol[1,1] * stratexp * 1.644854;
  x <- sum((filterRange==filter)*compVaR);
  x[is.na(x)] <- 0;
  return( x );
}

DblFilterCompVaR99 <- function ( riskfactors, filter, filterRange, strat, stratRange, rfid, exposure, data.in.columns=TRUE){
  count <- nrow(riskfactors);
  ln <- log(riskfactors[2:count,]/riskfactors[1:count-1,]);
  count <- nrow(ln);
  nn <- seq(count,1);
  df <- ((1-.94)*.94^(nn-1))^.5;
  df_ln <- ln*df;
  mat <- t(df_ln)%*%df_ln;
  posmat <- mat[c(rfid),c(rfid)];  
  stratexp <- (stratRange==strat)*exposure;
  mVaR <- (posmat%*%stratexp);
  vol <- sqrt(t(stratexp)%*%(posmat%*%stratexp));
  compVaR <- mVaR / vol[1,1] * stratexp * 2.326348;
  x <- sum((filterRange==filter)*compVaR);
  x[is.na(x)] <- 0;
  return( x );
}

DblFilterIsoVaR95 <- function ( riskfactors, filter, filterRange, strat, stratRange, rfid, exposure, data.in.columns=TRUE){
  count <- nrow(riskfactors);
  ln <- log(riskfactors[2:count,]/riskfactors[1:count-1,]);
  count <- nrow(ln);
  nn <- seq(count,1);
  df <- ((1-.94)*.94^(nn-1))^.5;
  df_ln <- ln*df;
  mat <- t(df_ln)%*%df_ln;
  posmat <- mat[c(rfid),c(rfid)];
  stratexp <- (stratRange==strat)*exposure;
  filterexp <- (filterRange==filter)*stratexp;
  x <- sqrt(t(filterexp)%*%(posmat%*%filterexp))*1.644854;
  x[is.na(x)] <- 0;
  return( x );
}

DblFilterIsoVaR99 <- function ( riskfactors, filter, filterRange, strat, stratRange, rfid, exposure, data.in.columns=TRUE){
  count <- nrow(riskfactors);
  ln <- log(riskfactors[2:count,]/riskfactors[1:count-1,]);
  count <- nrow(ln);
  nn <- seq(count,1);
  df <- ((1-.94)*.94^(nn-1))^.5;
  df_ln <- ln*df;
  mat <- t(df_ln)%*%df_ln;
  posmat <- mat[c(rfid),c(rfid)];
  stratexp <- (stratRange==strat)*exposure;
  filterexp <- (filterRange==filter)*stratexp;
  x <- sqrt(t(filterexp)%*%(posmat%*%filterexp))*2.326348;
  x[is.na(x)] <- 0;
  return( x );
}

DblFilter <- function (strat, stratRange, filterRange){
  bool <- stratRange==strat;
  filter <- filterRange[bool];
  x <- unique(filter)
  return( x );
}

HistVaR95 <- function ( riskfactors, rfid, exposure, data.in.columns=TRUE){ 
  count <- nrow(riskfactors);
  ln <- log(riskfactors[2:count,]/riskfactors[1:count-1,]);
  count <- nrow(ln);
  Hist_Rtn_Mtx <- ln[,c(rfid)];
  Hist_Rtn <- Hist_Rtn_Mtx %*% exposure;
  Sorted <- sort(Hist_Rtn, decreasing = FALSE);
  x <- -Sorted[ceiling(count/20)];
  return( x );
}

HistVaR99 <- function ( riskfactors, rfid, exposure, data.in.columns=TRUE){ 
  count <- nrow(riskfactors);
  ln <- log(riskfactors[2:count,]/riskfactors[1:count-1,]);
  count <- nrow(ln);
  Hist_Rtn_Mtx <- ln[,c(rfid)];
  Hist_Rtn <- Hist_Rtn_Mtx %*% exposure;
  Sorted <- sort(Hist_Rtn, decreasing = FALSE);
  x <- -Sorted[ceiling(count/100)];
  return( x );
}

HistWorst <- function ( riskfactors, rfid, exposure, data.in.columns=TRUE){ 
  count <- nrow(riskfactors);
  ln <- log(riskfactors[2:count,]/riskfactors[1:count-1,]);
  count <- nrow(ln);
  Hist_Rtn_Mtx <- ln[,c(rfid)];
  Hist_Rtn <- Hist_Rtn_Mtx %*% exposure;
  Sorted <- sort(Hist_Rtn, decreasing = FALSE);
  x <- -Sorted[1];
  return( x );
}

HistSeries <- function ( riskfactors, rfid, exposure, data.in.columns=TRUE){ 
  count <- nrow(riskfactors);
  ln <- log(riskfactors[2:count,]/riskfactors[1:count-1,]);
  count <- nrow(ln);
  Hist_Rtn_Mtx <- ln[,c(rfid)];
  Hist_Rtn <- Hist_Rtn_Mtx %*% exposure;
  x <- Hist_Rtn;
  return( x );
}


FilterHistVaR95 <- function ( riskfactors, filter, filterRange, rfid, exposure, data.in.columns=TRUE){ 
  count <- nrow(riskfactors);
  ln <- log(riskfactors[2:count,]/riskfactors[1:count-1,]);
  count <- nrow(ln);
  Hist_Rtn_Mtx <- ln[,c(rfid)];
  filterexp <- (filterRange==filter)*exposure;
  Hist_Rtn <- Hist_Rtn_Mtx %*% filterexp;
  Sorted <- sort(Hist_Rtn, decreasing = FALSE);
  x <- -Sorted[ceiling(count/20)];
  return( x );
}

FilterHistVaR99 <- function ( riskfactors, filter, filterRange, rfid, exposure, data.in.columns=TRUE){ 
  count <- nrow(riskfactors);
  ln <- log(riskfactors[2:count,]/riskfactors[1:count-1,]);
  count <- nrow(ln);
  Hist_Rtn_Mtx <- ln[,c(rfid)];
  filterexp <- (filterRange==filter)*exposure;
  Hist_Rtn <- Hist_Rtn_Mtx %*% filterexp;
  Sorted <- sort(Hist_Rtn, decreasing = FALSE);
  x <- -Sorted[ceiling(count/100)];
  return( x );
}

FilterHistWorst <- function ( riskfactors, filter, filterRange, rfid, exposure, data.in.columns=TRUE){ 
  count <- nrow(riskfactors);
  ln <- log(riskfactors[2:count,]/riskfactors[1:count-1,]);
  count <- nrow(ln);
  Hist_Rtn_Mtx <- ln[,c(rfid)];
  filterexp <- (filterRange==filter)*exposure;
  Hist_Rtn <- Hist_Rtn_Mtx %*% filterexp;
  Sorted <- sort(Hist_Rtn, decreasing = FALSE);
  x <- -Sorted[1];
  return( x );
}

StressTest <- function ( sectype, value, S, X, T, Vol, rf, type, priceMult, quantity, priceShock){
  if (sectype[i]=="Fixed Income" |  sectype[i]=="Futures" |  sectype=="Future" | sectype=="Equity") {
  shockValue <- value * (1+priceShock);
  x <- shockValue - value;
} else if (sectype=="Option") {
S <- S * (1+priceShock);
d1<-(log(S/X) + rf * T)/(Vol*sqrt(T))+Vol*sqrt(T)/2;
d2<-d1-Vol*sqrt(T);
if (type=="Call" | type=="C" | type=="c") {
  shockPrice <- S*pnorm(d1)-exp(-rf*T)*X*pnorm(d2);
  shockValue <- shockPrice * priceMult * quantity;
  x <- shockValue - value;
} else if (type=="Put" | type=="P" | type=="p") {
  shockPrice <- X*exp(-rf*T)*pnorm(-d2) - S*pnorm(-d1);
  shockValue <- shockPrice * priceMult * quantity;
  x <- shockValue - value;
} else
  x<-"N/A";
} else
  x<-"N/A";
return ( x );
}

BetaStressTest <- function ( sectype, value, S, X, T, Vol, rf, type, priceMult, quantity, priceShock, beta){
  if (sectype[i]=="Fixed Income" |  sectype[i]=="Futures" | sectype=="Future" | sectype=="Equity") {
  shockValue <- value * (1+priceShock*beta);
  x <- shockValue - value;
} else if (type=="Put" | type=="P" | type=="Call" | type=="C" | sectype=="Option") {
S <- S * (1+priceShock);
d1<-(log(S/X) + rf * T)/(Vol*sqrt(T))+Vol*sqrt(T)/2;
d2<-d1-Vol*sqrt(T);
if (type=="Call" | type=="C" | type=="c") {
  shockPrice <- S*pnorm(d1)-exp(-rf*T)*X*pnorm(d2);
  shockValue <- shockPrice * priceMult * quantity;
  x <- shockValue - value;
} else if (type=="Put" | type=="P" | type=="p") {
  shockPrice <- X*exp(-rf*T)*pnorm(-d2) - S*pnorm(-d1);
  shockValue <- shockPrice * priceMult * quantity;
  x <- shockValue - value;
} else
  x<-"N/A";
} else
  x<-"N/A";
return ( x );
}




FilterStressTestPriceVol <- function ( filter, filterRange, sectype, value, S, X, T, Vol, rf, type, priceMult, quantity, fx, priceShock, volShock){
  stress <- numeric(0);
  for(i in 1:length(sectype)){
    if (sectype[i]=="Fixed Income" |  sectype[i]=="Futures" |  sectype[i]=="Future" | sectype[i]=="Equity" | sectype[i]=="Equities" | sectype[i]=="EQUITIES") {
    shockValue <- quantity[i] * fx[i] * S[i] * priceMult[i] * (1+priceShock);
    stress <- c(stress,shockValue - (quantity[i] * fx[i] * S[i] * priceMult[i]));
  } else if ( sectype[i]=="Put" | sectype[i]=="Call" | sectype[i]=="P" | sectype[i]=="C" | sectype[i]=="Option" | sectype[i]=="Options" | sectype[i]=="OPTIONS") {
    Si <- S[i]*(1+priceShock);
    Voli <- Vol[i]*(1+volShock);
    shockPrice <- OptionPrice( Si, X[i], T[i], Voli, rf[i], type[i]);
    shockValue <- shockPrice * priceMult[i] * quantity[i] * fx[i];
    stress <- c(stress,shockValue - value[i]);
  } else if ( sectype[i]=="Cash" )  {
    stress<- c(stress,0);
  } else
    stress<- c(stress,0);
  }
  stress <- (filterRange==filter)*stress;
  x <- sum(stress);
  return ( x );
}

FilterStressTestPriceVolGrid <- function (filter, filterRange, value, S, X, T, Vol, rf, type, priceMult, quantity, fx, priceShocks, volShocks, AUM){
  priceShocks <- as.vector(priceShocks);
  volShocks <- as.vector(volShocks);
  stressGrid <- numeric(0);
   for(i in 1:length(priceShocks)){
      for(j in 1:length(volShocks)){
        stress <- FilterStressTestPriceVol(filter, filterRange, type, value, S, X, T, Vol, rf, type, priceMult, quantity, fx, priceShocks[i], volShocks[j]) / AUM;
        stressGrid <- c(stressGrid,stress);
      }
   }
  x <- matrix(stressGrid,nrow=length(volShocks)); 
  return ( x );
}

FilterStressTestBetaPriceVol <- function ( filter, filterRange, sectype, value, S, X, T, Vol, rf, type, priceMult, quantity, fx, beta, priceShock, volShock){
  stress <- numeric(0);
  for(i in 1:length(sectype)){
    if (sectype[i]=="Fixed Income" |  sectype[i]=="Futures" |  sectype[i]=="Future" | sectype[i]=="Equity" | sectype[i]=="Equities" | sectype[i]=="EQUITIES") {
    shockValue <- quantity[i] * fx[i] * S[i] * priceMult[i] * (1+priceShock * beta[i]);
    stress <- c(stress,shockValue - (quantity[i] * fx[i] * S[i] * priceMult[i]));
  } else if ( sectype[i]=="Put" | sectype[i]=="Call" | sectype[i]=="P" | sectype[i]=="C" | sectype[i]=="Option" | sectype[i]=="Options" | sectype[i]=="OPTIONS") {
    Si <- max(c(0.1,S[i]*(1+priceShock * beta[i])));
    Voli <- Vol[i]*(1+volShock);
    shockPrice <- OptionPrice( Si, X[i], T[i], Voli, rf[i], type[i]);
    shockValue <- shockPrice * priceMult[i] * quantity[i] * fx[i];
    stress <- c(stress,shockValue - value[i]);
  } else
    stress<- c(stress,0);
  }
  stress <- (filterRange==filter)*stress;
  x <- sum(stress);
  return ( x );
}

FilterStressTestBetaPriceVolGrid <- function (filter, filterRange, value, S, X, T, Vol, rf, type, priceMult, quantity, fx, beta, priceShocks, volShocks, AUM){
  priceShocks <- as.vector(priceShocks);
  volShocks <- as.vector(volShocks);
  stressGrid <- numeric(0);
   for(i in 1:length(priceShocks)){
      for(j in 1:length(volShocks)){
        stress <- FilterStressTestBetaPriceVol(filter, filterRange, type, value, S, X, T, Vol, rf, type, priceMult, quantity, fx, beta, priceShocks[i], volShocks[j]) / AUM;
        stressGrid <- c(stressGrid,stress);
      }
   }
  x <- matrix(stressGrid,nrow=length(volShocks)); 
  return ( x );
}


StressTestExpPriceVol <- function ( sectype, value, S, X, T, Vol, rf, type, priceMult, quantity, fx, priceShock, volShock){
  stress <- numeric(0);
  for(i in 1:length(sectype)){
    if (sectype[i]=="Fixed Income" |  sectype[i]=="Futures" |  sectype[i]=="Future" | sectype[i]=="Equity" | sectype[i]=="Equities" | sectype[i]=="EQUITIES") {
    shockValue <- quantity[i] * fx[i] * S[i] * priceMult[i] * (1+priceShock);
    stress <- c(stress,shockValue);
  } else if ( sectype[i]=="Put" | sectype[i]=="Call" | sectype[i]=="P" | sectype[i]=="C" | sectype[i]=="Option" | sectype[i]=="Options" | sectype[i]=="OPTIONS") {
    Si <- S[i]*(1+priceShock);
    Voli <- Vol[i]*(1+volShock);
    shockDelta <- OptionDelta( Si, X[i], T[i], Voli, rf[i], type[i]);
    shockValue <- Si * priceMult[i] * quantity[i] * fx[i] * shockDelta;
    stress <- c(stress,shockValue);
  } else
    stress<- c(stress, value[i]);
  }
  x <- sum(stress);
  return ( x );
}


FilterStressTestExpPriceVol <- function ( filter, filterRange, sectype, value, S, X, T, Vol, rf, type, priceMult, quantity, fx, priceShock, volShock){
  stress <- numeric(0);
  for(i in 1:length(sectype)){
    if (sectype[i]=="Fixed Income" |  sectype[i]=="Futures" | sectype[i]=="Future" | sectype[i]=="Equity" | sectype[i]=="Equities" | sectype[i]=="EQUITIES") {
    shockValue <- quantity[i] * fx[i] * S[i] * priceMult[i] * (1+priceShock);
    stress <- c(stress,shockValue);
  } else if ( sectype[i]=="Put" | sectype[i]=="Call" | sectype[i]=="P" | sectype[i]=="C" | sectype[i]=="Option" | sectype[i]=="Options" | sectype[i]=="OPTIONS") {
    Si <- S[i]*(1+priceShock);
    Voli <- Vol[i]*(1+volShock);
    shockDelta <- OptionDelta( Si, X[i], T[i], Voli, rf[i], type[i]);
    shockValue <- Si * priceMult[i] * quantity[i] * fx[i] * shockDelta;
    stress <- c(stress,shockValue);
  } else
    stress<- c(stress,value[i]);
  }
  stress <- (filterRange==filter)*stress;
  x <- sum(stress);
  return ( x );
}

FilterStressTestExpPriceVolGrid <- function (filter, filterRange, value, S, X, T, Vol, rf, type, priceMult, quantity, fx, priceShocks, volShocks, AUM){
  priceShocks <- as.vector(priceShocks);
  volShocks <- as.vector(volShocks);
  stressGrid <- numeric(0);
   for(i in 1:length(priceShocks)){
      for(j in 1:length(volShocks)){
        stress <- FilterStressTestExpPriceVol(filter, filterRange, type, value, S, X, T, Vol, rf, type, priceMult, quantity, fx, priceShocks[i], volShocks[j]) / AUM;
        stressGrid <- c(stressGrid,stress);
      }
   }
  x <- matrix(stressGrid,nrow=length(volShocks)); 
  return ( x );
}

DblFilterStressTestPriceVol <- function (filter, filterRange, filter2, filterRange2, sectype, value, S, X, T, Vol, rf, priceMult, quantity, fx, priceShock, volShock){
  stress <- numeric(0);
  for(i in 1:length(sectype)){
    if (sectype[i]=="Fixed Income" |  sectype[i]=="Futures" |  sectype[i]=="Future" | sectype[i]=="Equity" | sectype[i]=="Equities" | sectype[i]=="EQUITIES") {
    shockValue <- quantity[i] * fx[i] * S[i] * priceMult[i] * (1+priceShock);
    stress <- c(stress,shockValue - (quantity[i] * fx[i] * S[i] * priceMult[i]));
  } else if ( sectype[i]=="Put" | sectype[i]=="Call" | sectype[i]=="P" | sectype[i]=="C" | sectype[i]=="Option" | sectype[i]=="Options" | sectype[i]=="OPTIONS") {
    Si <- S[i]*(1+priceShock);
    Voli <- Vol[i]*(1+volShock);
    shockPrice <- OptionPrice( Si, X[i], T[i], Voli, rf[i], sectype[i]);
    shockValue <- shockPrice * priceMult[i] * quantity[i] * fx[i];
    stress <- c(stress,shockValue - value[i]);
  } else
    stress<- c(stress,0);
  }
  stress2 <- (filterRange==filter)*(filterRange2==filter2)*stress;
  x <- sum(stress2);
  return ( x );
}


StressTestPriceVol <- function (sectype, value, S, X, T, Vol, rf,  priceMult, quantity, fx, priceShock, volShock){
  stress <- numeric(0);
  for(i in 1:length(sectype)){
    if ( sectype[i]=="Put" | sectype[i]=="Call" | sectype[i]=="P" | sectype[i]=="C" | sectype[i]=="Option" | sectype[i]=="Options" | sectype[i]=="OPTIONS") {
    Si <- S[i]*(1+priceShock);
    Voli <- Vol[i]*(1+volShock);
    shockPrice <- OptionPrice( Si, X[i], T[i], Voli, rf[i], sectype[i]);
    shockValue <- shockPrice * priceMult[i] * quantity[i] * fx[i];
    stress <- c(stress,shockValue - value[i]);
  } else if (sectype[i]=="Fixed Income" |  sectype[i]=="Futures" |  sectype[i]=="Future" | sectype[i]=="Equity" | sectype[i]=="Equities" | sectype[i]=="EQUITIES") {
    shockValue <- quantity[i] * fx[i] * S[i] * priceMult[i] * (1+priceShock);
    stress <- c(stress,shockValue - (quantity[i] * fx[i] * S[i] * priceMult[i]));
  } else
    stress<- c(stress,0);
  }
  x <- sum(stress);
  return ( x );
}

StressTestBetaPriceVol <- function (sectype, value, S, X, T, Vol, rf,  priceMult, quantity, fx, beta, priceShock, volShock){
  stress <- numeric(0);
  for(i in 1:length(sectype)){
    if ( sectype[i]=="Put" | sectype[i]=="Call" | sectype[i]=="P" | sectype[i]=="C" | sectype[i]=="Option" | sectype[i]=="Options" | sectype[i]=="OPTIONS") {
    Si <- S[i]*(1+priceShock * beta[i]);
    Voli <- Vol[i]*(1+volShock);
    shockPrice <- OptionPrice( Si, X[i], T[i], Voli, rf[i], sectype[i]);
    shockValue <- shockPrice * priceMult[i] * quantity[i] * fx[i];
    stress <- c(stress,shockValue - value[i]);
  } else if (sectype[i]=="Fixed Income" |  sectype[i]=="Futures" |  sectype[i]=="Future" | sectype[i]=="Equity" | sectype[i]=="Equities" | sectype[i]=="EQUITIES")  {
    shockValue <- quantity[i] * fx[i] * S[i] * priceMult[i] * (1+priceShock * beta[i]);
    stress <- c(stress,shockValue - (quantity[i] * fx[i] * S[i] * priceMult[i]));
  } else
    stress<- c(stress,0);
  }
  x <- sum(stress);
  return ( x );
}