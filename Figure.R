
require(tidyverse)
require(circlize)

#######################################################
# Figure 2
#######################################################
##### data from CONN
df = read_fwf('stat.txt', skip=2) %>% select(X2, X3, X6) %>% na.omit()

names(df) = c('from', 'to', 't')
namechange = function(name) {
  newname = name %>% str_remove_all('seed_|-|_vox200') %>% str_trim() %>%
    str_replace_all(c('temporalpole'='TP', 'frontalpole'='FP',  
                      'l'='L-', 'r'='R-', 'R-ACC'='rACC'))
  return(newname)
}
df$from = namechange(df$from)
df$to = namechange(df$to)

##### diagram
Cairo::CairoPNG("Figure2b.png", width = 1024, height = 768, dpi=175)
chordDiagram(df, 
             grid.col = c(`L-IFG`='red', `FP`='violet', `rACC`='orange'), 
             annotationTrack = c("name", "grid"), 
             link.sort = T, 
             link.decreasing = T)
dev.off()
