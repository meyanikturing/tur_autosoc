FROM lerwys/iverilog

ENV LITEX_VERSION=8b4949edcdc1503056f3616f944905b1601d6cd9

ARG DEBIAN_FRONTEND=noninteractive

RUN sed -i '/stretch-updates/d' /etc/apt/sources.list && \
    sed -i 's|http://deb.debian.org/debian|http://archive.debian.org/debian|g' /etc/apt/sources.list && \
    sed -i 's|http://security.debian.org/debian-security|http://archive.debian.org/debian-security|g' /etc/apt/sources.list && \
    apt-get -y update && \
    apt-get install -y \
        git \
        wget \
        tar \
        automake \
        autoconf \
        make \
        build-essential \
        libssl-dev \
        zlib1g-dev \
        libbz2-dev \
        libreadline-dev \
        libsqlite3-dev \
        libffi-dev \
        gzip && \
    rm -rf /var/lib/apt/lists/*

# Install Python 3.7 from source
RUN wget https://www.python.org/ftp/python/3.7.12/Python-3.7.12.tgz && \
    tar xzf Python-3.7.12.tgz && \
    cd Python-3.7.12 && \
    ./configure --enable-optimizations && \
    make altinstall && \
    cd .. && \
    rm -rf Python-3.7.12 Python-3.7.12.tgz

# Set Python 3.7 as the default python3
RUN update-alternatives --install /usr/bin/python3 python3 /usr/local/bin/python3.7 1

# Install pip for Python 3.7
RUN wget https://bootstrap.pypa.io/pip/3.7/get-pip.py && python3 get-pip.py && \
    pip3 install setuptools


# Install LiteX HDL environment
RUN cd && mkdir litex && cd litex && \
    git clone --recursive --depth=1 https://github.com/enjoy-digital/litex && \
    cd litex && \
    python3 litex_setup.py --init --install --user --config=full && \
    cd ../..

WORKDIR /workspaces
CMD ["bash"]
