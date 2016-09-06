FROM debian

#ENV http_proxy http://bluelagoon:22222
#ENV https_proxy http://bluelagoon:22222

ENV CT_URL https://releases.hashicorp.com/consul/0.6.4/consul_0.6.4_linux_amd64.zip

RUN apt-get update -qq && apt-get -y install curl unzip && curl -O $CT_URL && unzip ${CT_URL##*/} -d /usr/local/bin/ && apt-get remove -y curl unzip

EXPOSE 8500

CMD consul agent -server -bootstrap -data-dir /tmp/consul -advertise 172.17.0.2
