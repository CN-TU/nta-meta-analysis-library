FROM python:alpine
LABEL maintainer="dcferreira"

RUN apk --update add git openssh bash && \
    rm -rf /var/lib/apt/lists/* /var/cache/apk/*
RUN pip install simplejson six requests jsonschema

RUN git clone https://github.com/CN-TU/nta-meta-analysis-specification /ntarc-spec
RUN git clone https://github.com/CN-TU/nta-meta-analysis-library /ntarc-library && \
    cd /ntarc-library && ./configure.sh
RUN git clone https://github.com/CN-TU/nta-meta-analysis /nta-meta-analysis

RUN echo "#!/bin/sh" > entrypoint.sh && \
    echo "(cd /ntarc-spec && git pull > /dev/null 2>&1)" >> entrypoint.sh && \
    echo "(cd /ntarc-library && git pull > /dev/null 2>&1)" >> entrypoint.sh && \
    echo "cd /ntarc-library && export PYTHONPATH=\`pwd\` && python \$@" >> entrypoint.sh && \ 
    chmod +x entrypoint.sh

ENTRYPOINT ["/bin/bash", "./entrypoint.sh"]

