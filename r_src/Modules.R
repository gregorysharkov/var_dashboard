FilterExposureBox <- function (filter, filterRange, values){
  items <- unique(filterRange);
  long <- numeric(0);
  short <- numeric(0);
  gross <- numeric(0);
  net <- numeric(0);
  for(i in items){
    long <- c(long,FltLongExp(i, filterRange, values));
    short <- c(short,FltShortExp(i, filterRange, values));
    gross <- c(gross,FltGrossExp(i, filterRange, values));  
    net <- c(net,FltNetExp(i, filterRange, values));
  }
  x <- cbind(items, long, short, gross, net);
  x <- as.matrix(x);
  x <- matrix(x, ncol = ncol(x), dimnames = NULL);
  x <- x[order(as.numeric(x[,5]), decreasing = TRUE),];
    if(is.vector(x)){
    x<-t(x);
    }
  x <- rbind(c(paste(filter, "Exposure", sep=" "),'Long','Short','Gross','Net'),x,c('Total',sum(long),sum(short),sum(gross),sum(net)));
  return( x );
}

DblFilterExposureBox <- function (strat, stratRange, filter, filterRange, values){
  bool <- stratRange==strat;
  filtered <- filterRange[bool];
  items <- unique(filtered);
  long <- numeric(0);
  short <- numeric(0);
  gross <- numeric(0);
  net <- numeric(0);
  for(i in items){  
    long <- c(long,DblFltLongExp(strat, stratRange, i, filterRange, values));
    short <- c(short,DblFltShortExp(strat, stratRange, i, filterRange, values));
    gross <- c(gross,DblFltGrossExp(strat, stratRange, i, filterRange, values));
    net <- c(net,DblFltNetExp(strat, stratRange, i, filterRange, values));
  }
  x <- cbind(items, long, short, gross, net); 
  x <- as.matrix(x);
  x <- matrix(x, ncol = ncol(x), dimnames = NULL);
  x <- x[order(as.numeric(x[,5]), decreasing = TRUE),];
    if(is.vector(x)){
    x<-t(x);
    }
  x <- rbind(c(paste(filter, "Exposure", sep=" "),'Long','Short','Gross','Net'),x,c('Total',sum(long),sum(short),sum(gross),sum(net))); 
  return( x );
}


VaRBox <- function (strat, attributeType, varData){
  m <- varData;
  m <- m[m[,1]==strat,];
  m <- m[m[,2]=='95VaR',];
  m <- m[m[,3]=='Incremental',];
  a <- m[m[,4]==attributeType,];
  m <- varData;
  m <- m[m[,1]==strat,];
  m <- m[m[,2]=='99VaR',];
  m <- m[m[,3]=='Incremental',];
  b <- m[m[,4]==attributeType,];
  m <- varData;
  m <- m[m[,1]==strat,];
  m <- m[m[,2]=='95VaR',];
  m <- m[m[,3]=='Isolated',];
  c <- m[m[,4]==attributeType,];
  m <- varData;
  m <- m[m[,1]==strat,];
  m <- m[m[,2]=='99VaR',];
  m <- m[m[,3]=='Isolated',];
  d <- m[m[,4]==attributeType,];
  m <- varData;
  m <- m[m[,1]==strat,];
  m <- m[m[,2]=='95VaR',];
  m <- m[m[,3]=='Component',];
  e <- m[m[,4]==attributeType,];
  m <- varData;
  m <- m[m[,1]==strat,];
  m <- m[m[,2]=='99VaR',];
  m <- m[m[,3]=='Component',];
  f <- m[m[,4]==attributeType,];
  if(is.vector(a)){
    x<-c(a[5],a[6],b[6],c[6],d[6],e[6],f[6])
    Totals <- c(' ',' ',' ',' ',x[6],x[7]);
    Totals <- c('Total', Totals);
    Totals <- as.matrix(Totals);
    Totals <- matrix(Totals, ncol = ncol(Totals), dimnames = NULL);
    x <- rbind(c(paste(attributeType, "VaR", sep=" "),'Inc95','Inc99','Iso95','Iso99','Comp95','Comp99'),x,t(Totals));
  } else {
    x <- cbind(a[,5:6],b[,6],c[,6],d[,6],e[,6],f[,6]);
    Totals <- c(' ',' ',' ',' ',sum(unlist(e[,6])),sum(unlist(f[,6])));
    Totals <- c('Total', Totals);
    Totals <- as.matrix(Totals);
    Totals <- matrix(Totals, ncol = ncol(Totals), dimnames = NULL);
    x <- x[order(unlist(x[,3]), decreasing = TRUE),];
    x <- rbind(c(paste(attributeType, "VaR", sep=" "),'Inc95','Inc99','Iso95','Iso99','Comp95','Comp99'),x,t(Totals));
  }
  return( x );
}



Top10VaRBox <- function (strat, attributeType, varData){
  m <- varData;
  m <- m[m[,1]==strat,];
  m <- m[m[,2]=='95VaR',];
  m <- m[m[,3]=='Component',];
  m <- m[m[,4]=='Positions',];
  m <- m[order(unlist(m[,6]), decreasing = TRUE ),];
  m <- m[,5:6];
  n <- varData;
  n <- n[n[,1]==strat,];
  n <- n[n[,2]=='99VaR',];
  n <- n[n[,3]=='Component',];
  n <- n[n[,4]=='Positions',];
  n <- n[order(unlist(n[,6]), decreasing = TRUE ),];
  n <- n[,5:6];
  x <- cbind(m,n[,2]);
  x <- x[x[,2]>=0,];
  if(is.vector(x)){
    x<-t(x);
    x<-rbind(x,c('','',''));
  }
  if (nrow(x)<10){
    Blanks <- matrix(rep(' ',3*(10-nrow(x))),ncol=3);
    x <- rbind(c('Top10 VaR Contributors','95VaR','99VaR'),x,Blanks);
  } else {
    x <- rbind(c('Top10 VaR Contributors','95VaR','99VaR'),x);
  }
  return( x );
}

Bottom10VaRBox <- function (strat, attributeType, varData){
  m <- varData;
  m <- m[m[,1]==strat,];
  m <- m[m[,2]=='95VaR',];
  m <- m[m[,3]=='Component',];
  m <- m[m[,4]=='Positions',];
  m <- m[order(unlist(m[,6])),];
  m <- m[,5:6];
  n <- varData;
  n <- n[n[,1]==strat,];
  n <- n[n[,2]=='99VaR',];
  n <- n[n[,3]=='Component',];
  n <- n[n[,4]=='Positions',];
  n <- n[order(unlist(n[,6])),];
  n <- n[,5:6];
  x <- cbind(m,n[,2]);
  x <- x[x[,2]<0,];
  if(is.vector(x)){
    x<-t(x);
    x<-rbind(x,c('','',''));
  }
  if (nrow(x)<10){
    Blanks <- matrix(rep(' ',3*(10-nrow(x))),ncol=3);
    x <- rbind(c('Top10 VaR Diversifiers','95VaR','99VaR'),x,Blanks);
  } else{  
    x <- rbind(c('Top10 VaR Diversifiers','95VaR','99VaR'),x);
  }
  return( x );
}




FilterExposureBoxPct <- function (filter, filterRange, values, AUM){
  items <- unique(filterRange);
  values <- values/AUM;
  long <- numeric(0);
  short <- numeric(0);
  gross <- numeric(0);
  net <- numeric(0);
  for(i in items){
    long <- c(long,FltLongExp(i, filterRange, values));
    short <- c(short,FltShortExp(i, filterRange, values));
    gross <- c(gross,FltGrossExp(i, filterRange, values));  
    net <- c(net,FltNetExp(i, filterRange, values));
  }
  x <- cbind(items, long, short, gross, net);
  x <- as.matrix(x);
  x <- matrix(x, ncol = ncol(x), dimnames = NULL);
  x <- x[order(as.numeric(x[,5]), decreasing = TRUE),];
    if(is.vector(x)){
    x<-t(x);
    }
  x <- rbind(c(paste(filter, "Exposure", sep=" "),'Long','Short','Gross','Net'),x,c('Total',sum(long),sum(short),sum(gross),sum(net)));
  return( x );
}

FilterBetaExposureBoxPct <- function (filter, filterRange, betaFactor, betaRange, values, AUM){
  items <- unique(filterRange);
  values <- values*betaRange;
  values <- values/AUM;
  long <- numeric(0);
  short <- numeric(0);
  gross <- numeric(0);
  net <- numeric(0);
  for(i in items){
    long <- c(long,FltLongExp(i, filterRange, values));
    short <- c(short,FltShortExp(i, filterRange, values));
    gross <- c(gross,FltGrossExp(i, filterRange, values));  
    net <- c(net,FltNetExp(i, filterRange, values));
  }
  x <- cbind(items, long, short, gross, net);
  x <- as.matrix(x);
  x <- matrix(x, ncol = ncol(x), dimnames = NULL);
  x <- x[order(as.numeric(x[,5]), decreasing = TRUE),];
    if(is.vector(x)){
    x<-t(x);
    }
  x <- rbind(c(paste(betaFactor, filter, "Exposure", sep=" "),'Long','Short','Gross','Net'),x,c('Total',sum(long),sum(short),sum(gross),sum(net)));
  return( x );
}

DblFilterExposureBoxPct <- function (strat, stratRange, filter, filterRange, values, AUM){
  bool <- stratRange==strat;
  filtered <- filterRange[bool];
  items <- unique(filtered);
  values <- values/AUM;
  long <- numeric(0);
  short <- numeric(0);
  gross <- numeric(0);
  net <- numeric(0);
  for(i in items){  
    long <- c(long,DblFltLongExp(strat, stratRange, i, filterRange, values));
    short <- c(short,DblFltShortExp(strat, stratRange, i, filterRange, values));
    gross <- c(gross,DblFltGrossExp(strat, stratRange, i, filterRange, values));
    net <- c(net,DblFltNetExp(strat, stratRange, i, filterRange, values));
  }
  x <- cbind(items, long, short, gross, net); 
  x <- as.matrix(x);
  x <- matrix(x, ncol = ncol(x), dimnames = NULL);
  x <- x[order(as.numeric(x[,5]), decreasing = TRUE),];
    if(is.vector(x)){
    x<-t(x);
    }
  x <- rbind(c(paste(filter, "Exposure", sep=" "),'Long','Short','Gross','Net'),x,c('Total',sum(long),sum(short),sum(gross),sum(net))); 
  return( x );
}

VaRBoxPct <- function (strat, attributeType, varData, AUM){
  varData <- cbind(varData[,1:5],unlist(varData[,6])/AUM);
  m <- varData;
  m <- m[m[,1]==strat,];
  m <- m[m[,2]=='95VaR',];
  m <- m[m[,3]=='Incremental',];
  a <- m[m[,4]==attributeType,];
  m <- varData;
  m <- m[m[,1]==strat,];
  m <- m[m[,2]=='99VaR',];
  m <- m[m[,3]=='Incremental',];
  b <- m[m[,4]==attributeType,];
  m <- varData;
  m <- m[m[,1]==strat,];
  m <- m[m[,2]=='95VaR',];
  m <- m[m[,3]=='Isolated',];
  c <- m[m[,4]==attributeType,];
  m <- varData;
  m <- m[m[,1]==strat,];
  m <- m[m[,2]=='99VaR',];
  m <- m[m[,3]=='Isolated',];
  d <- m[m[,4]==attributeType,];
  m <- varData;
  m <- m[m[,1]==strat,];
  m <- m[m[,2]=='95VaR',];
  m <- m[m[,3]=='Component',];
  e <- m[m[,4]==attributeType,];
  m <- varData;
  m <- m[m[,1]==strat,];
  m <- m[m[,2]=='99VaR',];
  m <- m[m[,3]=='Component',];
  f <- m[m[,4]==attributeType,];
  if(is.vector(a)){
    x<-c(a[5],a[6],b[6],c[6],d[6],e[6],f[6])
    Totals <- c(' ',' ',' ',' ',x[6],x[7]);
    Totals <- c('Total', Totals);
    Totals <- as.matrix(Totals);
    Totals <- matrix(Totals, ncol = ncol(Totals), dimnames = NULL);
    if(is.vector(x)){
    x<-t(x);
    }
    x <- rbind(c(paste(attributeType, "VaR", sep=" "),'Inc95','Inc99','Iso95','Iso99','Comp95','Comp99'),x,t(Totals));
  } else {
    x <- cbind(a[,5:6],b[,6],c[,6],d[,6],e[,6],f[,6]);
    Totals <- c(' ',' ',' ',' ',sum(unlist(e[,6])),sum(unlist(f[,6])));
    Totals <- c('Total', Totals);
    Totals <- as.matrix(Totals);
    Totals <- matrix(Totals, ncol = ncol(Totals), dimnames = NULL);
    x <- x[order(unlist(x[,3]), decreasing = TRUE),];
    x <- rbind(c(paste(attributeType, "VaR", sep=" "),'Inc95','Inc99','Iso95','Iso99','Comp95','Comp99'),x,t(Totals));
  }
  return( x );
}

Top10VaRBoxPct <- function (strat, attributeType, varData, AUM){
  varData <- cbind(varData[,1:5],unlist(varData[,6])/AUM);
  m <- varData;
  m <- m[m[,1]==strat,];
  m <- m[m[,2]=='95VaR',];
  m <- m[m[,3]=='Incremental',];
  m <- m[m[,4]=='Positions',];
    if(is.vector(m)){
    m <- m[5:6];
    } else {
    m <- m[order(unlist(m[,6]), decreasing = TRUE ),];
    m <- m[,5:6];
    }
  n <- varData;
  n <- n[n[,1]==strat,];
  n <- n[n[,2]=='99VaR',];
  n <- n[n[,3]=='Incremental',];
  n <- n[n[,4]=='Positions',];
    if(is.vector(n)){
    n <- n[5:6];
    x <- c(m,n[2]);
    x<-t(x);
    x <- x[x[,2]>=0,];
#   x<-rbind(x,c(' ',' ',' '));
    } else {
    n <- n[order(unlist(n[,6]), decreasing = TRUE ),];
    n <- n[,5:6];
    x <- cbind(m,n[,2]);
    x <- x[x[,2]>=0,];
    } 
  if(is.vector(x)){
    x<-t(x);
  }
  if (nrow(x)<10){
    Blanks <- matrix(rep(' ',3*(10-nrow(x))),ncol=3);
    x <- rbind(c('Top10 VaR Contributors','95VaR','99VaR'),x,Blanks);
  } else {
    x <- rbind(c('Top10 VaR Contributors','95VaR','99VaR'),x);
  }
  return( x );
}

Bottom10VaRBoxPct <- function (strat, attributeType, varData, AUM){
  varData <- cbind(varData[,1:5],unlist(varData[,6])/AUM);
  m <- varData;
  m <- m[m[,1]==strat,];
  m <- m[m[,2]=='95VaR',];
  m <- m[m[,3]=='Incremental',];
  m <- m[m[,4]=='Positions',];
    if(is.vector(m)){
    m <- m[5:6];
    } else {
    m <- m[order(unlist(m[,6])),];
    m <- m[,5:6];
    }
  n <- varData;
  n <- n[n[,1]==strat,];
  n <- n[n[,2]=='99VaR',];
  n <- n[n[,3]=='Incremental',];
  n <- n[n[,4]=='Positions',];
    if(is.vector(n)){
    n <- n[5:6];
    x <- c(m,n[2]);
    x<-t(x);
    x <- x[x[,2]<0,];
#    x<-rbind(x,c(' ',' ',' '));
    } else {
    n <- n[order(unlist(n[,6])),];
    n <- n[,5:6];
    x <- cbind(m,n[,2]);
    x <- x[x[,2]<0,];
    } 
  if(is.vector(x)){
    x<-t(x);
  }
  if (nrow(x)<10){
    Blanks <- matrix(rep(' ',3*(10-nrow(x))),ncol=3);
    x <- rbind(c('Top10 VaR Diversifiers','95VaR','99VaR'),x,Blanks);
  } else {
    x <- rbind(c('Top10 VaR Diversifiers','95VaR','99VaR'),x);
  }
  return( x );
}


DblFilterUndl <- function (stratRange, filterRange){
  cols <- cbind(stratRange, filterRange);
  x <- unique(cols);
  return( x );
}


DblFilterUndlExposureBox <- function (stratRange, filter, filterRange, values){
  strat <- unique(stratRange);
  x <- c('Strategy',paste(filter, "Exposure", sep=" "),'Long','Short','Gross','Net')
  for(s in strat){
  bool <- stratRange==s;
  filtered <- filterRange[bool];
  items <- unique(filtered);
  long <- numeric(0);
  short <- numeric(0);
  gross <- numeric(0);
  net <- numeric(0);
  for(i in items){  
    long <- c(long,DblFltLongExp(s, stratRange, i, filterRange, values));
    short <- c(short,DblFltShortExp(s, stratRange, i, filterRange, values));
    gross <- c(gross,DblFltGrossExp(s, stratRange, i, filterRange, values));
    net <- c(net,DblFltNetExp(s, stratRange, i, filterRange, values));
  }
  y <- cbind(s, items, long, short, gross, net);
  x <- rbind(x,y)
  }
  return( x );
}


FundNettedExposureBox <- function (filterRange, values){
  items <- unique(filterRange);
  long <- numeric(0);
  short <- numeric(0);
  gross <- numeric(0);
  net <- numeric(0);
  undlLong <- numeric(0);
  undlShort <- numeric(0);
  undlGross <- numeric(0);
  for(i in items){
    long <- c(long,FltLongExp(i, filterRange, values));
    short <- c(short,FltShortExp(i, filterRange, values));
    gross <- c(gross,FltGrossExp(i, filterRange, values));  
    net <- c(net,FltNetExp(i, filterRange, values));
  }
  undlLong <- (net>=0)*net;
  undlShort <- (net<0)*net;
  undlGross <- abs(net);
  x <- rbind(c('Fund Exposure','Long','Short','Gross','Net'),c('Exposures',sum(long),sum(short),sum(gross),sum(net)),c('Netted',sum(undlLong),sum(undlShort),sum(undlGross),sum(net)));
  return( x );
}

FundNettedExposures <- function (filterRange, values){
  items <- unique(filterRange);
  net <- numeric(0);
  undlLong <- numeric(0);
  undlShort <- numeric(0);
  undlGross <- numeric(0);
  for(i in items){
    net <- c(net,FltNetExp(i, filterRange, values));
  }
  undlLong <- (net>=0)*net;
  undlShort <- (net<0)*net;
  undlGross <- abs(net);
  x <- c(sum(undlLong),sum(undlShort),sum(undlGross),sum(net));
  x <- t(x);
  return( x );
}

StratNettedExposures <- function (strat, stratRange, filterRange, values){
  bool <- stratRange==strat;
  filtered <- filterRange[bool];
  items <- unique(filtered);
  net <- numeric(0);
  undlLong <- numeric(0);
  undlShort <- numeric(0);
  undlGross <- numeric(0);
  for(i in items){
    net <- c(net,DblFltNetExp(strat, stratRange, i, filterRange, values));
  }
  undlLong <- (net>=0)*net;
  undlShort <- (net<0)*net;
  undlGross <- abs(net);
  x <- c(sum(undlLong),sum(undlShort),sum(undlGross),sum(net));
  x <- t(x);
  return( x );
}

StratNettedExposureBox <- function (strat, stratRange, filterRange, values){
  bool <- stratRange==strat;
  filtered <- filterRange[bool];
  items <- unique(filtered);
  long <- numeric(0);
  short <- numeric(0);
  gross <- numeric(0);
  net <- numeric(0);
  undlLong <- numeric(0);
  undlShort <- numeric(0);
  undlGross <- numeric(0);
  for(i in items){  
    long <- c(long,DblFltLongExp(strat, stratRange, i, filterRange, values));
    short <- c(short,DblFltShortExp(strat, stratRange, i, filterRange, values));
    gross <- c(gross,DblFltGrossExp(strat, stratRange, i, filterRange, values));
    net <- c(net,DblFltNetExp(strat, stratRange, i, filterRange, values));
  }
  undlLong <- (net>=0)*net;
  undlShort <- (net<0)*net;
  undlGross <- abs(net);
  x <- rbind(c(paste(strat, "Exposure", sep=" "),'Long','Short','Gross','Net'),c('Exposures',sum(long),sum(short),sum(gross),sum(net)),c('Netted',sum(undlLong),sum(undlShort),sum(undlGross),sum(net))); 
  return( x );
}

StratNettedGross <- function (strat, stratRange, filterRange, values){
  bool <- stratRange==strat;
  filtered <- filterRange[bool];
  items <- unique(filtered);
  net <- numeric(0);
  undlGross <- numeric(0);
  for(i in items){  
    net <- c(net,DblFltNetExp(strat, stratRange, i, filterRange, values));
  }
  undlGross <- abs(net);
  x <- sum(undlGross);
  return( x );
}



TopNettedPos <- function (strat, stratRange, excludedRange, filterRange, values){
  filtered <- filterRange[stratRange==strat & excludedRange!='ETP'];
  items <- unique(filtered);
  net <- numeric(0);
  undlGross <- numeric(0);
  for(i in items){  
    net <- c(net,DblFltNetExp(strat, stratRange, i, filterRange, values));
  }
  undlGross <- abs(net);
  m <- undlGross;
  m <- m[order(undlGross, decreasing = TRUE)];
  x <- m[1];
  x <- as.matrix(x);
  x <- matrix(x, ncol = ncol(x), dimnames = NULL);
  return( x );
}

Top10NettedBetaPos <- function (strat, stratRange, filterRange, betaRange, values, AUM){
  betaExp <- betaRange*values/AUM;
  bool <- stratRange==strat;
  filtered <- filterRange[bool];
  items <- unique(filtered);
  net <- numeric(0);
  for(i in items){  
    net <- c(net,DblFltNetExp(strat, stratRange, i, filterRange, betaExp));
  }
  x <- cbind(items,net);
  x <- x[order(as.numeric(x[,2]), decreasing = TRUE),];
  x <- x[1:10,];
  x <- as.data.frame(x);
  x$net <- as.numeric(as.character(x$net));
  names(x) <- NULL;
  return( x );
}

Bottom10NettedBetaPos <- function (strat, stratRange, filterRange, betaRange, values, AUM){
  betaExp <- betaRange*values/AUM;
  bool <- stratRange==strat;
  filtered <- filterRange[bool];
  items <- unique(filtered);
  net <- numeric(0);
  for(i in items){  
    net <- c(net,DblFltNetExp(strat, stratRange, i, filterRange, betaExp));
  }
  x <- cbind(items,net);
  x <- x[order(as.numeric(x[,2]), decreasing = FALSE),];
  x <- x[1:10,];
  x <- as.data.frame(x);
  x$net <- as.numeric(as.character(x$net));
  names(x) <- NULL;
  return( x );
}

Top10NettedBetaFactorPos <- function (strat, stratRange, filterRange, factorRange, values, AUM){
  Exp <- values/AUM;
  factorExp <- factorRange*values/AUM;
  bool <- stratRange==strat;
  filtered <- filterRange[bool];
  items <- unique(filtered);
  net <- numeric(0);
  netFactor <- numeric(0);
  for(i in items){  
    net <- c(net,DblFltNetExp(strat, stratRange, i, filterRange, Exp));
    netFactor <- c(netFactor,DblFltNetExp(strat, stratRange, i, filterRange, factorExp));
  }
  blanks <- matrix(c(""),10,3);
  x <- cbind(items,net,netFactor);
  x <- x[order(as.numeric(x[,3]), decreasing = TRUE),];
  x <- rbind(x,blanks);
  x <- x[1:10,];
  x <- as.data.frame(x);
  x$net <- as.numeric(as.character(x$net));
  x$netFactor <- as.numeric(as.character(x$netFactor));
  names(x) <- NULL;
  return( x );
}

Bottom10NettedBetaFactorPos <- function (strat, stratRange, filterRange, factorRange, values, AUM){
  Exp <- values/AUM;
  factorExp <- factorRange*values/AUM;
  bool <- stratRange==strat;
  filtered <- filterRange[bool];
  items <- unique(filtered);
  net <- numeric(0);
  netFactor <- numeric(0);
  for(i in items){  
    net <- c(net,DblFltNetExp(strat, stratRange, i, filterRange, Exp));
    netFactor <- c(netFactor,DblFltNetExp(strat, stratRange, i, filterRange, factorExp));
  }
  blanks <- matrix(c(""),10,3);
  x <- cbind(items,net,netFactor);
  x <- x[order(as.numeric(x[,3]), decreasing = FALSE),];
  x <- rbind(x,blanks);
  x <- x[1:10,];
  x <- as.data.frame(x);
  x$net <- as.numeric(as.character(x$net));
  x$netFactor <- as.numeric(as.character(x$netFactor));
  names(x) <- NULL;
  return( x );
}


LiquidityBox <- function (positionRange, quantityRange, volumeRange, exposureRange, AUM){
  library(dplyr);
  exposureRange <- exposureRange/AUM;
  items <- unique(positionRange);
  liquid <- numeric(0);
  for(i in items){
    q <- (positionRange==i)*abs(quantityRange);
    q <- sum(q);
    v <- (positionRange==i)*(volumeRange);
    v <- mean(v[v!=0]);
    liquid <- c(liquid,q/(v*.2));
  }
  liquid[is.na(liquid)] <- 0;
  liquidTable <- cbind(items,liquid);
  positionTable <- cbind(liquidTable[match(positionRange, liquidTable[,1]),],exposureRange);
  OneDayLong <- numeric(0);
  OneDayShort <- numeric(0);
  OneWeekLong <- numeric(0);
  OneWeekShort <- numeric(0);
  OneMonthLong <- numeric(0);
  OneMonthShort <- numeric(0);
  MonthPlusLong <- numeric(0);
  MonthPlusShort <- numeric(0);
  UnknownLong <- numeric(0);
  UnknownShort <- numeric(0);
  for(i in 1:nrow(positionTable)){
    exp <- as.numeric(positionTable[i,3]);
    liq <- as.numeric(positionTable[i,2]);
    if (liq==0){
      UnknownLong <- c(UnknownLong,max(exp,0));
      UnknownShort <- c(UnknownShort,min(exp,0));
    } else {
      rate <- exp/liq;
      OneDayLong <- c(OneDayLong,max(rate*min(liq,1),0));
      OneDayShort <- c(OneDayShort,min(rate*min(liq,1),0));
      OneWeekLong <- c(OneWeekLong,max(rate*min(liq,5)-rate*min(liq,1),0));
      OneWeekShort <- c(OneWeekShort,min(rate*min(liq,5)-rate*min(liq,1),0));
      OneMonthLong <- c(OneMonthLong,max(rate*min(liq,21)-rate*min(liq,5),0));
      OneMonthShort <- c(OneMonthShort,min(rate*min(liq,21)-rate*min(liq,5),0));
      MonthPlusLong <- c(MonthPlusLong,max(rate*liq-rate*min(liq,21),0));
      MonthPlusShort <- c(MonthPlusShort,min(rate*liq-rate*min(liq,21),0));    
    }
  }
  OneDayGross <- sum(OneDayLong)-sum(OneDayShort);
  OneWeekGross <- sum(OneWeekLong)-sum(OneWeekShort);
  OneMonthGross <- sum(OneMonthLong)-sum(OneMonthShort);
  MonthPlusGross <- sum(MonthPlusLong)-sum(MonthPlusShort);
  UnknownGross <- sum(UnknownLong)-sum(UnknownShort);
  x <- t(matrix(c('Liquidity','Long','Short','Gross','OneDay',sum(OneDayLong),sum(OneDayShort),OneDayGross,'OneWeek',sum(OneWeekLong),sum(OneWeekShort),OneWeekGross,'OneMonth',sum(OneMonthLong),sum(OneMonthShort),OneMonthGross,'>OneMonth',sum(MonthPlusLong),sum(MonthPlusShort),MonthPlusGross,'Unknown',sum(UnknownLong),sum(UnknownShort),UnknownGross),nrow=4,ncol=6));
  total <- cumsum(x[2:6,4]);
  totalCol <- total/total[5];
  x <- cbind(x,c('Total',totalCol));
  return( x );  
}

StratLiquidityBox <- function (strat, stratRange, positionRange, quantityRange, volumeRange, exposureRange, AUM){
  library(dplyr);
  bool <- stratRange==strat;
  positionRange <- positionRange[bool];
  quantityRange <- quantityRange[bool];
  volumeRange <- volumeRange[bool];
  exposureRange <- exposureRange[bool];
  exposureRange <- exposureRange/AUM;
  items <- unique(positionRange);
  liquid <- numeric(0);
  for(i in items){
    q <- (positionRange==i)*abs(quantityRange);
    q <- sum(q);
    v <- (positionRange==i)*(volumeRange);
    v <- mean(v[v!=0]);
    liquid <- c(liquid,q/(v*.2));
  }
  liquid[is.na(liquid)] <- 0;
  liquidTable <- cbind(items,liquid);
  positionTable <- cbind(liquidTable[match(positionRange, liquidTable[,1]),],exposureRange);
  OneDayLong <- numeric(0);
  OneDayShort <- numeric(0);
  OneWeekLong <- numeric(0);
  OneWeekShort <- numeric(0);
  OneMonthLong <- numeric(0);
  OneMonthShort <- numeric(0);
  MonthPlusLong <- numeric(0);
  MonthPlusShort <- numeric(0);
  UnknownLong <- numeric(0);
  UnknownShort <- numeric(0);
  for(i in 1:nrow(positionTable)){
    exp <- as.numeric(positionTable[i,3]);
    liq <- as.numeric(positionTable[i,2]);
    if (liq==0){
      UnknownLong <- c(UnknownLong,max(exp,0));
      UnknownShort <- c(UnknownShort,min(exp,0));
    } else {
      rate <- exp/liq;
      OneDayLong <- c(OneDayLong,max(rate*min(liq,1),0));
      OneDayShort <- c(OneDayShort,min(rate*min(liq,1),0));
      OneWeekLong <- c(OneWeekLong,max(rate*min(liq,5)-rate*min(liq,1),0));
      OneWeekShort <- c(OneWeekShort,min(rate*min(liq,5)-rate*min(liq,1),0));
      OneMonthLong <- c(OneMonthLong,max(rate*min(liq,21)-rate*min(liq,5),0));
      OneMonthShort <- c(OneMonthShort,min(rate*min(liq,21)-rate*min(liq,5),0));
      MonthPlusLong <- c(MonthPlusLong,max(rate*liq-rate*min(liq,21),0));
      MonthPlusShort <- c(MonthPlusShort,min(rate*liq-rate*min(liq,21),0));    
    }
  }
  OneDayGross <- sum(OneDayLong)-sum(OneDayShort);
  OneWeekGross <- sum(OneWeekLong)-sum(OneWeekShort);
  OneMonthGross <- sum(OneMonthLong)-sum(OneMonthShort);
  MonthPlusGross <- sum(MonthPlusLong)-sum(MonthPlusShort);
  UnknownGross <- sum(UnknownLong)-sum(UnknownShort);
  x <- t(matrix(c('Liquidity','Long','Short','Gross','OneDay',sum(OneDayLong),sum(OneDayShort),OneDayGross,'OneWeek',sum(OneWeekLong),sum(OneWeekShort),OneWeekGross,'OneMonth',sum(OneMonthLong),sum(OneMonthShort),OneMonthGross,'>OneMonth',sum(MonthPlusLong),sum(MonthPlusShort),MonthPlusGross,'Unknown',sum(UnknownLong),sum(UnknownShort),UnknownGross),nrow=4,ncol=6));
  total <- cumsum(x[2:6,4]);
  totalCol <- total/total[5];
  x <- cbind(x,c('Total',totalCol));
  return( x );  
}



FundNettedExposureBoxPct <- function (strat, stratRange, filterRange, values, AUM){
  Exp <- values/AUM
  bool <- stratRange==strat;
  filtered <- filterRange[bool];
  items <- unique(filtered);
  net <- numeric(0);
  for(i in items){  
    net <- c(net,DblFltNetExp(strat, stratRange, i, filterRange, Exp));
  }
  m <- cbind(items,net);
  x <- m[order(unlist(m[,2]), decreasing = TRUE ),];
  return( x );
}

FundBetaNettedExposureBoxPct <- function (strat, stratRange, filterRange, betaRange, values, AUM){
  betaExp <- betaRange*values/AUM
  bool <- stratRange==strat;
  filtered <- filterRange[bool];
  items <- unique(filtered);
  net <- numeric(0);
  for(i in items){  
    net <- c(net,DblFltNetExp(strat, stratRange, i, filterRange, betaExp));
  }
  m <- cbind(items,net);
  x <- m[order(unlist(m[,2]), decreasing = TRUE ),];
  return( x );
}

DblFltNettedExpBox <- function (strat, stratRange, filter, filterRange, undlRange, values, AUM){
  values <- values/AUM;
  bool <- stratRange==strat;
  filterRange <- filterRange[bool];
  undlRange <- undlRange[bool];
  values <- values[bool];
  stratRange <- stratRange[bool];
  filters <- unique(filterRange);
  filterlong <-  numeric(0);
  filtershort <- numeric(0);
  filtergross <- numeric(0);
  filternet <- numeric(0);
  for(f in filters){
    bool2 <- filterRange==f
    filteredUndl <- undlRange[bool2];
    items <- unique(filteredUndl);
    net <- numeric(0);
    for(i in items){  
      net <- c(net,DblFltNetExp(f, filterRange, i, undlRange, values));
    }
    filterlong <- c(filterlong,sum((net>0)*net));
    filtershort <- c(filtershort,sum((net<0)*net));
    filtergross <- c(filtergross,sum(abs(net)));
    filternet <- c(filternet,sum(net))
  }
  x <- cbind(filters, filterlong, filtershort, filtergross, filternet); 
  x <- as.matrix(x);
  x <- matrix(x, ncol = ncol(x), dimnames = NULL);
  x <- x[order(unlist(x[,5]), decreasing = TRUE),];
    if(is.vector(x)){
    x<-t(x);
    }
  x <- rbind(c(paste(filter, "Exposure", sep=" "),'Long','Short','Gross','Net'),x,c('Total',sum(filterlong),sum(filtershort),sum(filtergross),sum(filternet))); 
  return( x );
}

FltNettedExpBox <- function (filter, filterRange, undlRange, values, AUM){
  values <- values/AUM;
  filters <- unique(filterRange);
  filterlong <-  numeric(0);
  filtershort <- numeric(0);
  filtergross <- numeric(0);
  filternet <- numeric(0);
  for(f in filters){
    bool2 <- filterRange==f
    filteredUndl <- undlRange[bool2];
    items <- unique(filteredUndl);
    net <- numeric(0);
    for(i in items){  
      net <- c(net,DblFltNetExp(f, filterRange, i, undlRange, values));
    }
    filterlong <- c(filterlong,sum((net>0)*net));
    filtershort <- c(filtershort,sum((net<0)*net));
    filtergross <- c(filtergross,sum(abs(net)));
    filternet <- c(filternet,sum(net))
  }
  x <- cbind(filters, filterlong, filtershort, filtergross, filternet); 
  x <- as.matrix(x);
  x <- matrix(x, ncol = ncol(x), dimnames = NULL);
  x <- x[order(unlist(x[,5]), decreasing = TRUE),];
    if(is.vector(x)){
    x<-t(x);
    }
  x <- rbind(c(paste(filter, "Exposure", sep=" "),'Long','Short','Gross','Net'),x,c('Total',sum(filterlong),sum(filtershort),sum(filtergross),sum(filternet))); 
  return( x );
}


Top10VaRBoxPctComp <- function (strat, attributeType, varData, AUM){
  varData <- cbind(varData[,1:5],unlist(varData[,6])/AUM);
  m <- varData;
  m <- m[m[,1]==strat,];
  m <- m[m[,2]=='95VaR',];
  m <- m[m[,3]=='Component',];
  m <- m[m[,4]=='Positions',];
    if(is.vector(m)){
    m <- m[5:6];
    } else {
    m <- m[order(unlist(m[,6]), decreasing = TRUE ),];
    m <- m[,5:6];
    }
  n <- varData;
  n <- n[n[,1]==strat,];
  n <- n[n[,2]=='99VaR',];
  n <- n[n[,3]=='Component',];
  n <- n[n[,4]=='Positions',];
    if(is.vector(n)){
    n <- n[5:6];
    x <- c(m,n[2]);
    x<-t(x);
    x <- x[x[,2]>=0,];
    x<-rbind(x,c(' ',' ',' '));
    } else {
    n <- n[order(unlist(n[,6]), decreasing = TRUE ),];
    n <- n[,5:6];
    x <- cbind(m,n[,2]);
    x <- x[x[,2]>=0,];
    } 
  if(is.vector(x)){
    x<-t(x);
  }
  if (nrow(x)<10){
    Blanks <- matrix(rep(' ',3*(10-nrow(x))),ncol=3);
    x <- rbind(c('Top10 VaR Contributors','95VaR','99VaR'),x,Blanks);
  } else {
    x <- rbind(c('Top10 VaR Contributors','95VaR','99VaR'),x);
  }
  return( x );
}

Bottom10VaRBoxPctComp <- function (strat, attributeType, varData, AUM){
  varData <- cbind(varData[,1:5],unlist(varData[,6])/AUM);
  m <- varData;
  m <- m[m[,1]==strat,];
  m <- m[m[,2]=='95VaR',];
  m <- m[m[,3]=='Component',];
  m <- m[m[,4]=='Positions',];
    if(is.vector(m)){
    m <- m[5:6];
    } else {
    m <- m[order(unlist(m[,6])),];
    m <- m[,5:6];
    }
  n <- varData;
  n <- n[n[,1]==strat,];
  n <- n[n[,2]=='99VaR',];
  n <- n[n[,3]=='Component',];
  n <- n[n[,4]=='Positions',];
    if(is.vector(n)){
    n <- n[5:6];
    x <- c(m,n[2]);
    x<-t(x);
    x <- x[x[,2]<0,];
    x<-rbind(x,c(' ',' ',' '));
    } else {
    n <- n[order(unlist(n[,6])),];
    n <- n[,5:6];
    x <- cbind(m,n[,2]);
    x <- x[x[,2]<0,];
    } 
  if(is.vector(x)){
    x<-t(x);
  }
  if (nrow(x)<10){
    Blanks <- matrix(rep(' ',3*(10-nrow(x))),ncol=3);
    x <- rbind(c('Top10 VaR Diversifiers','95VaR','99VaR'),x,Blanks);
  } else {
    x <- rbind(c('Top10 VaR Diversifiers','95VaR','99VaR'),x);
  }
  return( x );
}

FactorExposureTable <- function (paraFund,fundCol,underlierName,exposures,factorBetas,factorNames,AUM){
  factorExposures <- as.vector(exposures) * as.matrix(factorBetas) / AUM;
  exposuresPct <- as.vector(exposures) / AUM;
  factorExposures <- as.data.frame(factorExposures);
  factorExposures <- cbind(exposuresPct,factorExposures);
  names(factorExposures) <- c('Exposure',factorNames);
  filterPositions <- as.data.frame(cbind(fundCol,underlierName));
  names(filterPositions) <- c('Fund','Underlier');
  x <- cbind(filterPositions,factorExposures);
  x <- x[x[,1]==paraFund,];
  x <- aggregate(.~Fund+Underlier, x, sum);
  x <- x[order(x$Exposure, decreasing = TRUE),];
  length <- ncol(x);
  x <- x[,c(2:length)];
  return( x );
}


FilterStressTable <- function (paraFund,fundCol,filterName,filterCol,stresses,stressNames,AUM){
  stressDol <- as.matrix(stresses);
  stressPct <- as.matrix(stresses) / AUM;
  stressTable <- as.data.frame(cbind(stressDol,stressPct));
  names(stressTable) <- c(paste("$ ",stressNames),paste("% ",stressNames));
  length <- ncol(stressTable);
  halflength <- length / 2;
  sequence <- seq(1,halflength)
  orderCol <- numeric(0) 
  for(i in sequence){
    orderCol <- c(orderCol,seq(i,length, by = halflength));
  }
  stressTable <- stressTable[,c(orderCol)];
  filterPositions <- as.data.frame(cbind(fundCol,filterCol));
  names(filterPositions) <- c('Fund','Filter');
  x <- cbind(filterPositions,stressTable);
  x <- x[x[,1]==paraFund,];
  x <- aggregate(.~Fund+Filter, x, sum);
  x <- x[order(x$Filter, decreasing = FALSE),];
  length <- ncol(x);
  x <- x[,c(2:length)];
  names(x)[names(x)=='Filter'] <- filterName;
  return( x );
}

PositionTable1 <- function (paraFund,fundCol,underlierCol,betaCol,correlCol,volCol,exposures,stresses,stressNames,AUM){
  exposuresPct <- as.vector(exposures) / AUM;
  exposuresPct <- as.data.frame(exposuresPct);
  names(exposuresPct) <-c('Exposure');
  stressDol <- as.matrix(stresses);
  stressPct <- as.matrix(stresses) / AUM;
  stressTable <- as.data.frame(cbind(stressDol,stressPct));
  names(stressTable) <- c(paste("$ ",stressNames),paste("% ",stressNames));
  length <- ncol(stressTable);
  halflength <- length / 2;
  sequence <- seq(1,halflength)
  orderCol <- numeric(0) 
  for(i in sequence){
    orderCol <- c(orderCol,seq(i,length, by = halflength));
  }
  stressTable <- stressTable[,c(orderCol)];
  stressTable <- stressTable[,c(1,2,7,8)];
  filterPositions <- as.data.frame(cbind(fundCol,underlierCol,betaCol,correlCol,volCol));
  names(filterPositions) <- c('Fund','Position','Beta','Correl','Volatility');
  x <- cbind(filterPositions,exposuresPct,stressTable);
  x <- x[x[,1]==paraFund,];
  x <- aggregate(.~Fund+Position+Beta+Correl+Volatility, x, sum);
  x <- x[order(x$Exposure, decreasing = TRUE),];
  length <- ncol(x);
  x <- x[,c(2:length)];
  x <- x[,c(1,5,2,3,4,6,7,8,9)]
  return( x );
}

PositionTable2 <- function (paraFund,fundCol,strategy,undlTicker,underlierCol,betaCol,correlCol,volCol,exposures,stresses,stressNames,AUM){
  exposuresPct <- as.vector(exposures) / AUM;
  exposuresPct <- as.data.frame(exposuresPct);
  names(exposuresPct) <-c('Exposure');
  stressDol <- as.matrix(stresses);
  stressPct <- as.matrix(stresses) / AUM;
  stressTable <- as.data.frame(cbind(stressDol,stressPct));
  names(stressTable) <- c(paste("$ ",stressNames),paste("% ",stressNames));
  length <- ncol(stressTable);
  halflength <- length / 2;
  sequence <- seq(1,halflength)
  orderCol <- numeric(0) 
  for(i in sequence){
    orderCol <- c(orderCol,seq(i,length, by = halflength));
  }
  stressTable <- stressTable[,c(orderCol)];
  stressTable <- stressTable[,c(1,2,7,8)];
  filterPositions <- as.data.frame(cbind(fundCol,underlierCol,undlTicker,strategy,betaCol,correlCol,volCol));
  names(filterPositions) <- c('Fund','Position','Identifier','Manager','Beta','Correl','Volatility');
  x <- cbind(filterPositions,exposuresPct,stressTable);
  x <- x[x[,1]==paraFund,];
  x <- aggregate(.~Fund+Position+Identifier+Manager+Beta+Correl+Volatility, x, sum);
  x <- x[order(x$Exposure, decreasing = TRUE),];
  length <- ncol(x);
  x <- x[,c(2:length)];
  x <- x[,c(1,2,3,7,4,5,6,8,9,10,11)];
  x$sum <- ave(x$Exposure, x$Manager, x$Position, FUN=sum);
  x <- x[order(x$sum, decreasing = TRUE),];
  x <- x[,c(1:11)]
  return( x );
}

FundHistStressTable <- function (paraFund,fundCol,stresses,stressNames,AUM){
  stressTable <- as.data.frame(stresses);
  names(stressTable) <- c(stressNames);
  filterPositions <- as.data.frame(fundCol);
  names(filterPositions) <- c('Fund');
  x <- cbind(filterPositions,stressTable);
  x <- x[x[,1]==paraFund,];
  x <- aggregate(.~Fund, x, sum);
  length <- ncol(x);
  x <- x[,c(2:length)];
  y <- x / AUM;
  x <- rbind(x,y);
  return( x );
}

FilterHistStressTable <- function (paraFund,fundCol,filterName,filterCol,stresses,stressNames,AUM){
  stressTable <- as.data.frame(stresses / AUM);
  names(stressTable) <- c(stressNames);
  filterPositions <- as.data.frame(cbind(fundCol,filterCol));
  names(filterPositions) <- c('Fund','Filter');
  x <- cbind(filterPositions,stressTable);
  x <- x[x[,1]==paraFund,];
  x <- aggregate(.~Fund+Filter, x, sum);
  x <- x[order(x$Filter, decreasing = FALSE),];
  length <- ncol(x);
  x <- x[,c(2:length)];
  names(x)[names(x)=='Filter'] <- filterName;
  return( x );
}