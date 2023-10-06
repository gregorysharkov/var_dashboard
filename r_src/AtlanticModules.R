FilterAtlanticBoxPct <- function (filter, filterRange, betaFactor, betaRange, values, AUM){
  items <- unique(filterRange);
  bvalues <- values*betaRange;
  bvalues <- bvalues/AUM;
  values <- values/AUM;
  bnet <- numeric(0);
  net <- numeric(0);
  for(i in items){
    bnet <- c(bnet,FltNetExp(i, filterRange, bvalues));
    net <- c(net,FltNetExp(i, filterRange, values));
  }
  x <- cbind(items, net, bnet);
  x <- as.matrix(x);
  x <- matrix(x, ncol = ncol(x), dimnames = NULL);
  x <- x[order(as.numeric(x[,2]), decreasing = TRUE),];
  x <- rbind(c(paste(filter, "Exposure", sep=" "),'Exposure','Beta Exposure'),x,c('Total',sum(net),sum(bnet)));
  return( x );
}