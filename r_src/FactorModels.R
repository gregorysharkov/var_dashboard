ffFactors <- function(tsportfolio,tsfactor){

  ts <- cbind(tsportfolio,tsfactor);
  tsdata <- data.frame(ts);
  n <- dim(tsdata)[2];
  fit <- lm(paste0("cbind(", paste(names(tsdata)[1:(n-3)], collapse = ", "), ")", " ~ ."),data=tsdata);
  beta <- t(coef(fit));
  #beta;
  rse <- sigma(fit);
  fitsum<-summary(fit);
  m<-length(fitsum);
  r2<-matrix(1,nrow=m,ncol=1);
  for( i in 1:m){
    r2[i] <- fitsum[[i]]$r.squared;
  }
  output <- cbind(beta,rse,r2);
  return(output);
}

sortEigVec <- function (ss){
  n <- dim(ss)[2]
  for (i in 1:(n-1)) {
    v <- ss[i, i:n];
	j <- which.max(v); 
	ifelse(j>1, {mm <- ss[,i];ss[,i] <- ss[,i+j-1]; ss[,i+j-1]<-mm; },1);
  }
  return(ss);
}

posiEigVec <- function (ss){
  n <- dim(ss)[2];
  for (i in 1:n) {
                   ifelse( max(abs(ss[,i])) > max(ss[,i]), ss[,i]<- (-1)*ss[,i],1) ;
                  }
  return(ss);                
}

ffFactorsPCA <- function(tsportfolio,tsfactor){
  ts <- as.data.frame(tsfactor);
  pca <- prcomp(ts);
  ss <- pca$rotation;
  st <- sortEigVec(posiEigVec(ss));

  pcafactor <- tsfactor %*% st;
  coeff <- ffFactors(tsportfolio,pcafactor);
  fvar <- cov(pcafactor);
  pvar <- t(t(coeff[,2:4]^2) * diag(fvar));
  output <- cbind(coeff,pvar);
  return(output);
}

pcaRotation <- function(tsfactor){
  ts <- as.data.frame(tsfactor);
  pca <- prcomp(ts);
  ss <- pca$rotation;
  st <- sortEigVec(posiEigVec(ss));
  st;
}

mfpcaRotation <- function(tsfactor){
  ts <- as.data.frame(tsfactor);
  pca <- prcomp(ts);
  ss <- pca$rotation;
  #st <- sortEigVec(posiEigVec(ss));
  ss;
}

multiFactors <- function(tsportfolio,tsfactor){

  ts <- cbind(tsportfolio,tsfactor);
  tsdata <- data.frame(ts);
  n <- dim(tsdata)[2];
  m <- dim(tsfactor)[2];
  fit <- lm(paste0("cbind(", paste(names(tsdata)[1:(n-m)], collapse = ", "), ")", " ~ ."),data=tsdata);
  beta <- t(coef(fit));
  #beta;
  rse <- sigma(fit);
  fitsum<-summary(fit);
  m<-length(fitsum);
  r2<-matrix(1,nrow=m,ncol=1);
  for( i in 1:m){
    r2[i] <- fitsum[[i]]$r.squared;
  }
  output <- cbind(beta,rse,r2);
  return(output);
}

multiFactorsPCA <- function(tsportfolio,tsfactor){
  ts <- as.data.frame(tsfactor);
  pca <- prcomp(ts);
  ss <- pca$rotation;
  #i <- dim(tsfactor)[2];
  #psdev <-diag(1,i,i);
  #diag(psdev) <- 1/pca$sdev;

  #st <- sortEigVec(posiEigVec(ss));
  st <- ss;
  pcafactor <- tsfactor %*% st; # %*% psdev;
  coeff <- multiFactors(tsportfolio,pcafactor);
  tstats <- multiFactorsStats(tsportfolio,pcafactor);
  n <- dim(coeff)[2];
  fvar <- cov(pcafactor);
  pvar <- t(t(coeff[,2:(n-2)]^2) * diag(fvar));
  output <- cbind(coeff,pvar,tstats);
  return(output);
}

multiFactorsPCAsd <- function(tsportfolio,tsfactor){
  ts <- as.data.frame(tsfactor);
  pca <- prcomp(ts);
  ss <- pca$rotation;
  i <- dim(tsfactor)[2];
  psdev <-diag(1,i,i);
  diag(psdev) <- 1/pca$sdev;

  #st <- sortEigVec(posiEigVec(ss));
  st <- ss;
  pcafactor <- tsfactor %*% st %*% psdev;
  coeff <- multiFactors(tsportfolio,pcafactor);
  tstats <- multiFactorsStats(tsportfolio,pcafactor);
  n <- dim(coeff)[2];
  fvar <- cov(pcafactor);
  pvar <- t(t(coeff[,2:(n-2)]^2) * diag(fvar));
  output <- cbind(coeff,pvar,tstats);
  return(output);
}

multiFactorsPCA2 <- function(tsportfolio,tsfactor){
  ts <- as.data.frame(tsfactor);
  pca <- prcomp(ts);
  ss <- pca$rotation;
  #st <- sortEigVec(posiEigVec(ss));
  st <- ss;
  #standarize factor variance

  pcafactor <- tsfactor %*% st;

  coeff <- multiFactors(tsportfolio,pcafactor[,1:22]);
  tstats <- multiFactorsStats(tsportfolio,pcafactor[,1:22]);
  n <- dim(coeff)[2];
  fvar <- cov(pcafactor[,1:22]);
  pvar <- t(t(coeff[,2:(n-2)]^2) * diag(fvar));
  output <- cbind(coeff,pvar,tstats);
  return(output);
}

multiFactorsPCAsd2 <- function(tsportfolio,tsfactor){
  ts <- as.data.frame(tsfactor);
  pca <- prcomp(ts);
  ss <- pca$rotation;
  #st <- sortEigVec(posiEigVec(ss));
  st <- ss;
  #standarize factor variance
  i <- dim(tsfactor)[2];
  psdev <-diag(1,i,i);
  diag(psdev) <- 1/pca$sdev;

  pcafactor <- tsfactor %*% st %*% psdev;

  coeff <- multiFactors(tsportfolio,pcafactor[,1:22]);
  tstats <- multiFactorsStats(tsportfolio,pcafactor[,1:22]);
  n <- dim(coeff)[2];
  fvar <- cov(pcafactor[,1:22]);
  pvar <- t(t(coeff[,2:(n-2)]^2) * diag(fvar));
  output <- cbind(coeff,pvar,tstats);
  return(output);
}


multiFactorsStats <- function(tsportfolio,tsfactor){

  ts <- cbind(tsportfolio,tsfactor);
  tsdata <- data.frame(ts);
  n <- dim(tsdata)[2];
  m <- dim(tsfactor)[2];
  fit <- lm(paste0("cbind(", paste(names(tsdata)[1:(n-m)], collapse = ", "), ")", " ~ ."),data=tsdata);
 # beta <- t(coef(fit));
  #beta;
  #rse <- sigma(fit);
  fitsum<-summary(fit);
  j<-length(fitsum);
  tstats<-matrix(1,nrow=j,ncol=m+1);
  pvalue<-matrix(1,nrow=j,ncol=m+1);
  for( i in 1:j){
    tstats[i,] <- t(fitsum[[i]]$coefficients[,3]);
    pvalue[i,] <- t(fitsum[[i]]$coefficients[,4]);
  }
  output <- cbind(tstats,pvalue);
  return(output);
}
