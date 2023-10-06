
DAR_FactorPrices <- function(factors, factorWeights, positionPrices, dateCol){
  ones <- matrix(c(100),1,ncol(factors));
  count <- nrow(positionPrices);
  positionReturns <- positionPrices[2:count,]/positionPrices[1:count-1,]-1;
  factorReturns <- positionReturns%*%factorWeights + 1;
  factorPrices <- numeric(0);
  for(i in 1:ncol(factorReturns)){
    factorPrices <- c(factorPrices,cumprod(factorReturns[,i]));
  }
  factorPrices <- matrix(factorPrices,ncol=ncol(factors))*100;
  header <- rbind(factors,ones);
  x <- rbind(header,factorPrices);
  x <- cbind(c("Date",dateCol),x);
  return( x );
}

