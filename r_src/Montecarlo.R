MonteCarlo <- function( rfs, n){
  count <- nrow(rfs);
  ln <- log(rfs[2:count,]/rfs[1:count-1,]);
  count <- nrow(ln);
  nn <- seq(count,1);
  df <- ((1-.94)*.94^(nn-1))^.5;
  df_ln <- ln*df;
  covmat <- t(df_ln)%*%df_ln;
  num <- ncol(rfs);
  library(MASS);
  x <- mvrnorm(n,rep(0,num),covmat);
  return( x );
}