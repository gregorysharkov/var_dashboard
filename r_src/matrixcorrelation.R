
#
# return a 2-dimensional correlation matrix for the given data.
# unless full.matrix is set, the upper-triangular will be omitted
# (or the lower triangular, if data is in rows).
#

MatrixCorrelation <- function( m, data.in.columns=TRUE){
  x <- cor(t(m)); 
  return( x );
}

MatrixCovariance <- function( m, data.in.columns=TRUE){
  x <- cov(t(m)); 
  return( x );
}

PortStDev <- function ( rtns, wgt, data.in.columns=TRUE){ 
  mat <- cov(rtns); 
  x <- sqrt(t(wgt)%*%(mat%*%wgt));
  return( x );
}

VaR95 <- function ( rtns, wgt, data.in.columns=TRUE){ 
  mat <- cov(rtns); 
  x <- sqrt(t(wgt)%*%(mat%*%wgt))*1.644854;
  return( x );
}

VaR99 <- function ( rtns, wgt, data.in.columns=TRUE){ 
  mat <- cov(rtns); 
  x <- sqrt(t(wgt)%*%(mat%*%wgt))*2.326348;
  return( x );
}