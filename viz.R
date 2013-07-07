# IDEAS:
# - Look only at certain opponents
# - Color by opponents' record??
# - Look only at certain time intervals
# - "summarize" time series
# - BM?
# - variance/"balance" of league?


full_df <- data.frame(matrix(nrow = 0, ncol = 3))
colnames(full_df) <- c('date_opp', 'time', 'diff')


for(f in list.files()) {
  time_series <- read.csv(f, head = F)
  # Add opponent info in another column
  time_series <- cbind(f, time_series)
  names(time_series) <- c('date_opp', 'time', 'diff')
  full_df <- merge(full_df, time_series, all = T)
}
full_df$date_opp <- as.character(full_df$date_opp)
full_df$time <- as.numeric(full_df$time)
full_df$diff <- as.integer(full_df$diff)


plot_all <- function() {
  # Plot all games
  plot_tls <- ggplot(data = full_df, aes(time, diff, color = date_opp)) +
    geom_point(pch = '.') + geom_line(alpha = .5)
  plot_tls
}

plot_time <- function(all_data, start_time = 0, end_time = 48, ) {
  # NOTE careful with OT
  interval <- which(all_data$time < end_time & all_data$time > start_time)
  # Only plot times between <start> and <end>
  plot_time_int <- ggplot(data = all_data[interval, ], aes(time, diff, color = date_opp)) +
    geom_point(pch = '.') + geom_line(alpha = .5)
  plot_time_int
}


plot_by_record <- function(all_data) {
  
}

# diagnostics
blowouts <- unique(full_df[which(abs(full_df$diff) > 25), 'date_opp'])

# Looks like BM! Maybe it is, when teams are evenly matched?
qplot(time, diff, data = game, ylim = c(-maxDiff, maxDiff), geom = 'line')


parse_records <- function(standings_file <- '2011_2012_standings.csv') {
  entire_table <- read.csv(standings_file, head = T)
  # No better way...
  team_ids <- c('CHI', 'SAS', 'OKC', 'MIA', 'IND', 'LAL', 'MEM', 'ATL', 'LAC', 'BOS', 'DEN', 'ORL',
                'DAL', 'NYK', 'UTA', 'PHI', 'HOU', 'PHX', 'MIL', 'POR', 'MIN', 'DET', 'GSW', 'TOR', 
                'NJN', 'SAC', 'CLE', 'NOH', 'WAS', 'CHN')
  entire_table$team_id <- team_ids
  relevant_info <- ddply(entire_table, .(team_id), summarize,
                         win_pct = parse_pct_from_record(Overall))
  write.csv(relevant_info, 'team_win_pct.csv', row.names = F, quote = F)
}

parse_pct_from_record <- function(record_str) {
  # Given string of from WINS-LOSSES, return win pct
  split_rec <- strsplit(as.character(record_str), '-')[[1]]
  print(split_rec)
  wins <- as.integer(split_rec[1])
  losses <- as.integer(split_rec[2])
  return(wins / (wins + losses))
}
