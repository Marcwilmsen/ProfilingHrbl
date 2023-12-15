FROM python:3

WORKDIR /usr/src/app

COPY Herb_PyGAD/requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY Herb_PyGAD .

CMD [ "python", "./main.py" ]