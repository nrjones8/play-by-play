game <- read.csv('oneSeries.csv', skip = 1, head = T)

maxDiff <- max(abs(game$diff))
# Looks like BM! Maybe it is, when teams are evenly matched?
qplot(time, diff, data = game, ylim = c(-maxDiff, maxDiff), geom = 'line')