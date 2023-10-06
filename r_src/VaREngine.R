VaREngine <- function(positionTable,riskfactors,data.in.columns=TRUE){
  Pos <- range.to.data.frame(positionTable, TRUE);
  Sector <- as.vector(Pos$Sector);
  count <- nrow(riskfactors);
  ln <- log(riskfactors[2:count,]/riskfactors[1:count-1,]);
  count <- nrow(ln);
  nn <- seq(count,1);
  df <- ((1-.94)*.94^(nn-1))^.5;
  df_ln <- ln*df;
  covmat <- t(df_ln)%*%df_ln;
  x <- covmat[1:10,1:10];
  return( x );
}