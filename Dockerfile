FROM nvidia/cuda:11.8.0-cudnn8-devel-ubuntu20.04

# metadata
LABEL maintainer = "Julio de Castro Vargas Fernandes"
LABEL lab = "Laboratorio de Metodos Computacionais em Engenharia"

# defining useful commands
ENV DEBIAN_FRONTEND noninteractive
ENV APT_INSTALL apt-get install -y --fix-missing
ENV PIP_INSTALL python -m pip install --retries 10 --timeout 60
ENV GIT_CLONE git clone --depth 10
ENV BUILD_LOCATION /packageinstallations

# defining workdir for all subsequent installs
WORKDIR $BUILD_LOCATION

# initial update
RUN apt-get update -y

# install apt-utils
RUN $APT_INSTALL apt-utils

# installing tools
RUN $APT_INSTALL \
    software-properties-common \
    build-essential \
    ca-certificates \
    wget \
    curl \
    vim \
    git \
    libssl-dev \
    unzip \
    unrar \
    yasm \
    portaudio19-dev \
    apt-utils \
    ffmpeg

# installing dependencies
RUN $APT_INSTALL \
    pkg-config \
    libsndfile1-dev \
    libavcodec-dev \
    libavformat-dev \
    libswscale-dev \
    libtbb2 \
    libtbb-dev \
    libjpeg-dev \
    libpng-dev \
    libtiff-dev \
    libdc1394-dev \
    libsm6 \
    libxext6 \
    libhdf5-dev

RUN $GIT_CLONE https://github.com/Kitware/CMake && cd CMake && \
    ./bootstrap && make -j"$(nproc)" install && \
    cd $WORKDIR

# installing python
RUN $APT_INSTALL \
    python3 \
    python3-dev \
    python3-distutils-extra \
    python3-pip

# binding python
RUN ln -s /usr/bin/python3 /usr/local/bin/python3
RUN ln -s /usr/bin/python3 /usr/local/bin/python
# binding pip
RUN ln -s /usr/bin/pip3 /usr/local/bin/pip

# upgrading pip
RUN pip install --upgrade pip

# installing python packages
RUN $PIP_INSTALL setuptools
RUN $PIP_INSTALL \
    numpy \
    numba \
    chainer \
    scipy \
    pandas \
    scikit-image \
    scikit-learn \
    matplotlib \
    seaborn \
    bokeh \
    tqdm \
    h5py \
    segyio \
    cloudpickle \
    audioread \
    librosa \
    sacred \
    statsmodels \
    resampy \
    jupyterlab \
    urllib3 \
    beautifulsoup4 \
    scrapy \
    nltk \
    gensim \
    protobuf \
    pyyaml \
    flask \
    flask_auth \
    typing \
    imageio \
    imageaug \
    joblib \
    wavefile \
    Cython \
    SoundFile \
    Pillow \
    PyAudio \
    PyWavelets \
    ipywidgets \
    pymongo \ 
    dask \
    bokeh \
    tensorflow-datasets \
    dash \
    loguru \
    altair \
    vega_datasets \
    xarray \
    netcdf4 \
    jedi \ 
    xgboost \
    opencv-python \
    streamlit \
    openpyxl \
    mlflow \
    tensorboard \
    tensorflow-probability \
    porespy \
    shapely

# installing tensorflow
RUN $PIP_INSTALL 'tensorflow>=2.11.0,<2.12.0'

# adding a user
RUN useradd -u 1000 -m julio

# cleaning
RUN ldconfig && apt-get clean && apt-get autoremove
WORKDIR /home/julio
RUN rm -rf $BUILD_LOCATION

USER julio
