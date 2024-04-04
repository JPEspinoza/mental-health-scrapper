FROM python:3.12-bookworm
ADD requirements.txt /requirements.txt
# Install GDAL dependencies and Python development headers
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        binutils \
        libproj-dev \
        libgdal-dev && \
    apt-get clean all
RUN pip install --no-cache-dir -r requirements.txt