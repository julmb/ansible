# this script should be mounted under /docker-entrypoint in the nginx container
# it will then get sourced by docker-entrypoint.sh
# it executes a loop in the background that reloads the nginx configuration every 24 hours
# docker-entrypoint.sh hands off control to nginx, orphaning the loop which will reparent

# TODO: this currently does not exit cleanly when the container is stopped
#       this is due to sleep not being interrupted by SIGTERM
#       this can be avoided by using `sleep 24h & wait $!`
#       this does not help, presumably because it does not break the loop
#       https://pentacent.medium.com/nginx-and-lets-encrypt-with-docker-in-less-than-5-minutes-b4b8a60d3a71
#       https://stackoverflow.com/questions/56981892/why-do-sleep-wait-in-bash
#       https://stackoverflow.com/questions/360201/how-do-i-kill-background-processes-jobs-when-my-shell-script-exits
#       http://mywiki.wooledge.org/SignalTrap#When_is_the_signal_handled.3F
#       https://stackoverflow.com/questions/27694818/interrupt-sleep-in-bash-with-a-signal-trap

while true
do
	sleep 24h
	nginx -s reload
done &
