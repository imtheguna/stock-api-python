FROM python:3.9-slim

ENV PYTHONUNBUFFERED=1

WORKDIR /app

COPY . /app

RUN apt-get update && apt-get install -y net-tools psmisc

RUN pip install --no-cache-dir -r requirements.txt

RUN echo '#!/bin/sh' > /check_and_kill_port.sh && \
    echo 'if netstat -tuln | grep ":4444 "' >> /check_and_kill_port.sh && \
    echo 'then echo "Port 4444 is in use. Killing the process using port 4444." && fuser -k 4444/tcp' >> /check_and_kill_port.sh && \
    echo 'fi' >> /check_and_kill_port.sh && \
    chmod +x /check_and_kill_port.sh

CMD ["/bin/sh", "-c", "/check_and_kill_port.sh && gunicorn run:app --log-level debug"]
