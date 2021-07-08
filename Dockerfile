# Below are the dependencies required for installing the common combination of numpy, scipy, pandas and matplotlib # in an Alpine based Docker image.
FROM fedora:34

RUN dnf -y update 
RUN dnf -y install python3-pip proj-devel gcc gcc-c++ python3-devel  git

RUN pip3 install pymongo call_to_dxcc  websocket-client maidenhead  



COPY openwebrx_cli.py /data/openwebrx_cli.py
COPY data.ini /data/data.ini
COPY band_slots.py /data/band_slots.py

CMD ["python3","/data/openwebrx_cli.py"]

