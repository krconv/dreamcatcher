FROM python:3
WORKDIR /app

# install dependencies
COPY requirements.txt ./
RUN pip install -r requirements.txt

# install the project
COPY . .
RUN pip install -e .

CMD ["dreamcatcher", "catch", "apartments"]
