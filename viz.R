
full_df <- data.frame(matrix(nrow = 0, ncol = 3))
colnames(full_df) <- c('date_opp', 'time', 'diff')

for(f in list.files()) {
  time_series <- read.csv(f, head = F)
  # Add opponent info in another column
  time_series <- cbind(f, time_series)
  names(time_series) <- c('date_opp', 'time', 'diff')
  print(head(time_series))
  full_df <- merge(full_df, time_series, all = T)
}
full_df$date_opp <- as.character(full_df$date_opp)
full_df$time <- as.numeric(full_df$time)
full_df$diff <- as.integer(full_df$diff)

plot_tls <- ggplot(data = full_df, aes(time, diff, color = date_opp)) +
  geom_point(pch = '.') + geom_line(alpha = .5)
plot_tls
plot_time_series <- function(ts) {
  maxDiff <- max(abs(ts$diff))
  
}

# Looks like BM! Maybe it is, when teams are evenly matched?
qplot(time, diff, data = game, ylim = c(-maxDiff, maxDiff), geom = 'line')