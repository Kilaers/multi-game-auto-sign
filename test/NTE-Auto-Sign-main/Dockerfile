FROM ghcr.io/astral-sh/uv:python3.13-alpine


COPY requirements.txt .
RUN uv pip install --system -r requirements.txt
RUN uv pip install --system  requests
RUN uv pip install --system  cryptography
WORKDIR /app
COPY . .

ENV TOKEN token
ENV TZ=Asia/Shanghai
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone


CMD ["python", "nte.py" ]
