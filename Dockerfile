FROM dragoncrafted87/alpine:latest

ARG BUILD_DATE
ARG VCS_REF
ARG VERSION
LABEL org.label-schema.build-date=$BUILD_DATE \
      org.label-schema.name="DragonCrafted87 Alpine Greyhole Cron" \
      org.label-schema.description="Alpine Supervisord Image with Greyhole cron interface so we can use k8s cron controller." \
      org.label-schema.vcs-ref=$VCS_REF \
      org.label-schema.vcs-url="https://github.com/DragonCrafted87/docker-alpine-greyhole" \
      org.label-schema.version=$VERSION \
      org.label-schema.schema-version="1.0"

COPY root/. /

# Install all the things!
RUN pip3 --no-cache-dir install kubernetes  && \
    rm -rf /var/cache/apk/* && \
    chmod +x -R /scripts/*
