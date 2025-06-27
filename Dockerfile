FROM python:3.11

WORKDIR /app

COPY requirements.txt .

#no-cache-dir: don't cache the instaled packages to save spaces
#upgrade: will upgarde libary versions for docker image
RUN pip install --no-cache-dir --upgrade -r requirements.txt

#copy everything from local Todo folder to app folder of docker image we created in earlier step
#COPY ./Todo /app
COPY . .

#"--host", "0.0.0.0" makes server acessible from outside the conatiner
#"--port", "80" : listen on port 80 inside the container

CMD ["uvicorn", "Todo.main:app", "--host", "0.0.0.0", "--port", "80"]