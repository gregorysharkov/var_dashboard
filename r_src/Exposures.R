DblFilter <- function (strat, stratRange, filterRange){
  bool <- stratRange==strat;
  filter <- filterRange[bool];
  x <- unique(filter)
  return( x );
}

Filter <- function (filterRange){
  x <- unique(filterRange);
  return( x );
}

FltLongExp <- function (filter, filterRange, values){
  agg <- (filterRange==filter)*(values>=0)*values;
  x <- sum(agg);
  return( x );
}

FltShortExp <- function (filter, filterRange, values){
  agg <- (filterRange==filter)*(values<=0)*values;
  x <- sum(agg);
  return( x );
}

FltGrossExp <- function (filter, filterRange, values){
  agg <- (filterRange==filter)*abs(values);
  x <- sum(agg);
  return( x );
}

FltNetExp <- function (filter, filterRange, values){
  agg <- (filterRange==filter)*values;
  x <- sum(agg);
  return( x );
}

DblFltLongExp <- function (strat, stratRange, filter, filterRange, values){
  stratValues <- (stratRange==strat)*(values>=0)*values;
  agg <- (filterRange==filter)*stratValues;
  x <- sum(agg);
  return( x );
}

DblFltShortExp <- function (strat, stratRange, filter, filterRange, values){
  stratValues <- (stratRange==strat)*(values<=0)*values;
  agg <- (filterRange==filter)*stratValues;
  x <- sum(agg);
  return( x );
}

DblFltGrossExp <- function (strat, stratRange, filter, filterRange, values){
  stratValues <- (stratRange==strat)*abs(values);
  agg <- (filterRange==filter)*stratValues;
  x <- sum(agg);
  return( x );
}

DblFltNetExp <- function (strat, stratRange, filter, filterRange, values){
  stratValues <- (stratRange==strat)*values;
  agg <- (filterRange==filter)*stratValues;
  x <- sum(agg);
  return( x );
}


Top10VaR <- function (strat, attributeType, varData){
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
  return( x );
}

Bottom10VaR <- function (strat, attributeType, varData){
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
  return( x );
}
