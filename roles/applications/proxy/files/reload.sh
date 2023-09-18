# this script should be mounted under /docker-entrypoint in the nginx container
# it will then get sourced by docker-entrypoint.sh
# it executes a loop in the background that reloads the nginx configuration every 24 hours
# docker-entrypoint.sh hands off control to nginx, orphaning the loop which will reparent

# TODO: this currently does not exit cleanly when the container is stopped
#       this is due to sleep not being interrupted by SIGTERM
#       this can be avoided by using `sleep 24h & wait $!`
#       this does not help, presumably because it does not break the loop

while true
do
	sleep 24h
	nginx -s reload
done &
