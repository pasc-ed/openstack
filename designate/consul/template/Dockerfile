FROM debian

#ENV http_proxy http://bluelagoon:22222
#ENV https_proxy http://bluelagoon:22222
ENV CT_URL https://releases.hashicorp.com/consul-template/0.14.0/consul-template_0.14.0_linux_amd64.zip

RUN apt-get update -qq && apt-get -y install curl unzip screen && \
    mkdir -p /etc/consul.d/template && \
    curl -O $CT_URL && unzip ${CT_URL##*/} -d /usr/local/bin/ && \
    apt-get remove -y curl unzip

#Setup Consul Template Files
VOLUME /etc/consul.d/template

#Default Variables

CMD consul-template -config /etc/consul.d/template/config.json
