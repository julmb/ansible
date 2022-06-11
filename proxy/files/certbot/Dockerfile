from certbot/certbot:arm64v8-latest
COPY certbot-renew /etc/periodic/15min/certbot-renew
RUN chmod +x /etc/periodic/15min/certbot-renew
ENTRYPOINT []
CMD ["crond", "-f", "-d", "8"]
