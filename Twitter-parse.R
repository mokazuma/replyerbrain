require(tidyverse)

json_parse = function(username) {
  
  nullcheck <- function(inf) {
    if(is.null(inf))  inf = 0
    return(inf)
  }
  
  getsum <- function(dat) {
    sumdat = dat %>% lapply(str_count) %>% lapply(mean) %>% unlist() %>% 
      na.omit() %>% length()
    return(sumdat)
  }
  
  ##### read json data
  # JSON file is collected by python-twitter
  # https://github.com/bear/python-twitter
  user = jsonlite::fromJSON(paste0(username, 'user.json')) #from UserLookup function
  tweet = jsonlite::fromJSON(paste0(username, 'twits.json')) #from GetUserTimeline function
  
  ##### null check
  if(!is.null(user)) {
    user$statuses_count = nullcheck(user$statuses_count)
    user$friends_count = nullcheck(user$friends_count)
    user$followers_count = nullcheck(user$followers_count)
    user$favourites_count = nullcheck(user$favourites_count)
    tweet$hashtags = nullcheck(tweet$hashtags)
    tweet$urls = nullcheck(tweet$urls)
    tweet$media = nullcheck(tweet$media)
    
    ##### account information
    df <- data.frame(name = user$screen_name,
                     created = user$created_at,
                     tweet = user$statuses_count,
                     follow = user$friends_count,
                     follower = user$followers_count,
                     favourite = user$favourites_count,
                     api_tweet = tweet$text %>% length(),
                     api_retweet = tweet$text %>% str_detect('RT @|RT@') %>% 
                       which() %>% length(),
                     api_hashtag = getsum(tweet$hashtags),
                     api_link = getsum(tweet$urls),
                     api_media = getsum(tweet$media)
    )
    
    ##### usage time
    jsontime = file.mtime(paste0(username, 'twits.json')) %>% as.POSIXlt('GMT') %>% 
      str_remove(' GMT')
    timeinf = df$created %>%
      str_remove('Mon |Tue |Wed |Thu |Fri |Sat |Sun ') %>% 
      str_replace_all(c('Jan'='1', 'Feb'='2', 'Mar'='3', 'Apr'='4', 
                        'May'='5', 'Jun'='6', 'Jul'='7', 'Aug'='8', 
                        'Sep'='9', 'Oct'='10', 'Nov'='11', 'Dec'='12')) %>% 
      str_split_fixed(' ', 5)
    createdtime = paste(timeinf[5], timeinf[1], timeinf[2], sep='-') %>% paste(timeinf[3])
    accounttime = difftime(jsontime, createdtime) %>% as.numeric()
    
    ##### delete tweet < 100, null check
    if((df$api_tweet > 100) && (!is.null(tweet$created_at))) {
      
      ##### reply indexes
      if(!is.null(tweet$in_reply_to_screen_name)) {
        paddingdat = data.frame(replyname=tweet$in_reply_to_screen_name)
        paddingdat[is.na(paddingdat)] = "N"
        replyinf = paddingdat %>% filter(replyname!="N", replyname!=user$screen_name)
        reply_network = replyinf %>% distinct(replyname) %>% nrow()
        reply_number = replyinf %>% nrow()
        reply_freq = replyinf %>% group_by(replyname) %>% summarise(n()) %>% pull()
      } else {
        reply_network = 0
        reply_number = 0
        reply_freq = 0
      }
      
      if(sum(reply_freq) != 0) {
        reply_account = psych::describe(reply_freq) %>% select(mean, median, sd, max, min)
      } else {
        reply_account = data.frame(mean=0, median=0, sd=0, max=0, min=0)
      }
      names(reply_account) = paste0('reply_', names(reply_account))
      
      ##### normalization
      df = df %>% cbind(reply_network, reply_number, reply_account) %>% 
        mutate(across(tweet:favourite, ~ (.x / accounttime), .names = '{.col}.norm')) %>% 
        mutate(across(api_retweet:reply_number, ~ (.x / api_tweet)*100, .names = '{.col}.prop'))  
      
      return(df)
    }
  }
}

json_parse(username = xxx)
