# this script should be mounted under /docker-entrypoint in the nginx container
# it will then get sourced by docker-entrypoint.sh
# it executes a loop in the background that reloads the nginx configuration every 24 hours
# docker-entrypoint.sh hands off control to nginx, orphaning the loop which will reparent

while true
do
	sleep 24h
	nginx -s reload
done &
