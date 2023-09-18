# this script will get sourced by docker-entrypoint.sh in the nginx image
# it will execute an infinite loop in the background
# this loop will reload the nginx configuration every 24 hours

echo "reload.sh: starting nginx reload loop"

while true
do
	echo "reload.sh: waiting"
	sleep 60
	echo "reload.sh: reloading nginx configuration"
	nginx -s reload
done &
