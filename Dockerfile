FROM python:3.6-alpine3.7

# bash is installed for debugging
RUN apk add --no-cache bash

# Install python package requirements
COPY ./radiator-push /app
WORKDIR /app
RUN pip install --upgrade -r requirements.txt

CMD ["python", "radiator-push.py"]

# https://stackoverflow.com/questions/23810845/
# docker build -t radiator-push .
# docker run --net=host -v /Users/dean/code/radiator/radiator-push:/app radiator
