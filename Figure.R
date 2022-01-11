
require(tidyverse)
require(circlize)
setwd('/Users/kmori/Dropbox/Paper/CiNet/SNS_rsMRI/')

#######################################################
# Figure 2
#######################################################
##### read data from CONN
filename = 'result/Replycnt_rev/stat.txt'
# filename = 'result/Reply/stat_cnt_person.txt'
df = read_fwf(filename, skip=2) %>% select(X2, X3, X6) %>% na.omit()

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
Cairo::CairoPNG("figure/network_circlecnt_rev.png", width = 1024, height = 768, dpi=175)
chordDiagram(df, 
             grid.col = c(`L-IFG`='red', `FP`='violet', `rACC`='orange'), 
             annotationTrack = c("name", "grid"), 
             link.sort = T, 
             link.decreasing = T)
dev.off()
