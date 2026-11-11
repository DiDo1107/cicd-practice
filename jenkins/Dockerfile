# Jenkins с Python и Docker CLI внутри — для кейсов 4 и 5
FROM jenkins/jenkins:lts-jdk17

USER root
RUN apt-get update \
    && apt-get install -y --no-install-recommends python3 python3-venv python3-pip docker.io \
    && rm -rf /var/lib/apt/lists/*

RUN jenkins-plugin-cli --plugins workflow-aggregator git junit credentials-binding
