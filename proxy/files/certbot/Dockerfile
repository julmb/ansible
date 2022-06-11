from certbot/certbot:arm64v8-latest
COPY certbot-renew /etc/periodic/daily/certbot-renew
RUN chmod +x /etc/periodic/daily/certbot-renew
ENTRYPOINT []
CMD ["crond", "-f", "-d", "8"]
