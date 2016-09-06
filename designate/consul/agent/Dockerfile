FROM debian

#ENV http_proxy http://bluelagoon:22222
#ENV https_proxy http://bluelagoon:22222
ENV CT_URL https://releases.hashicorp.com/consul/0.6.4/consul_0.6.4_linux_amd64.zip
ENV CT_WEBUI https://releases.hashicorp.com/consul/0.6.4/consul_0.6.4_web_ui.zip

RUN apt-get update -qq && apt-get -y install curl unzip screen && \
    curl -O $CT_URL && unzip ${CT_URL##*/} -d /usr/local/bin/ && \
    mkdir -p /opt/web_ui && \
    mkdir -p /var/consul && \
    mkdir -p /etc/consul.d/client && \
    curl -O $CT_WEBUI && unzip ${CT_WEBUI##*/} -d /opt/web_ui/ && \
    apt-get remove -y curl unzip

VOLUME /etc/consul.d/client
EXPOSE 8500

#CMD consul agent -data-dir /tmp/consul -client 172.17.0.2 -ui-dir /opt/opt_webui -join 10.20.0.3
CMD consul agent -config-dir /etc/consul.d/client
