# prova-final-a2-devops

## Texto Explicativo

### MySQL e Redis

#### docker-compose.yml

No YAML, temos:

```yaml
  mysql:
    image: mysql:8
    container_name: db
    environment:
      MYSQL_ROOT_PASSWORD: example
      MYSQL_DATABASE: ecommerce
    ports:
      - "3306:3306"
    networks:
      - minha_rede

  redis:
    image: redis:latest
    container_name: redis
    ports:
      - "6379:6379"
    command: ["redis-server"]
    networks:
      - minha_rede
```

- Em `image`, setamos que vamos usar o mysql e o redis como imagem base dos serviços.
- Em `container_name`, definimos o nome do container. Vamos usar esse nome para se conectar depois.
- Especificamente no mysql, usamos o `environment` para definir a senha e o nome do banco de dados.
- Em `ports`, definimos as portas que cada serviço vai utilizar. As outras apis vão se comunicar por elas.
- Especificamente no redis, usamos o `command` para iniciar o redis. Esse comando é necessário para iniciar o cache dentro do container.
- Em `networks`, definimos quais as redes que os containers estão. Precisamos deixar todos na mesma rede para se comunicarem.

### product-service

#### Dockerfile

Para esse serviço, temos uma Dockerfile bem simples:

```dockerfile
FROM node:20

WORKDIR /app

COPY . .
RUN npm ci

EXPOSE 3001

CMD ["npm", "run", "start"]
```

- `FROM node:20` define a imagem que vamos usar. Escolhi uma imagem pronta do node, na versão 20 (que utilizo hoje).
- `WORKDIR /app` configura o container para usar a pasta `/app` como diretório base. Os arquivos do
nosso projeto ficarão aqui.
- `COPY . .` copia todos os arquivos do projeto para dentro do container, exceto pela `node_modules` (especificada
no .dockerignore).
- `RUN npm ci` instala as dependências do projeto. O `ci` normalmente é usado nas pipelines, e por isso escolhi ele.
- `EXPOSE 3001` configura a porta de saída do container. Vou conseguir acessar o app somente pela porta 3001.
- `CMD ["npm", "run", "start"]` define o comando que inicia o container. Nesse caso, rodo o script `start`, definido no package.json (que
nada mais é do que o `node index.js`)

#### docker-compose.yaml

No YAML, temos:


```yaml
  products:
    build:
      context: ./product-service
      dockerfile: Dockerfile
    container_name: products
    ports:
      - "3001:3001"
    networks:
      - minha_rede
```

- Em `build, context e dockerfile`, configuro a dockerfile e pasta para utilizar nesse serviço. Como o repositório é compartilhado,
especificamos aqui a pasta onde está o serviço.
- Em `container_name`, definimos o nome do container desse serviço. Usamos esse nome para nos comunicarmos com o container depois.
- Em `ports`, definimos quais portas estarão disponíveis para o host e outros containers na mesma rede.
- Em `networks`, definimos quais as redes que o container está. Precisamos deixar todos na mesma rede para se comunicarem.

### order-service

#### Dockerfile

Para esse serviço, temos uma Dockerfile mais robusta:

```dockerfile
FROM python:3.13-slim

RUN apt-get update && apt-get install -y curl libpq-dev
RUN curl -sSL https://install.python-poetry.org | python3

ENV PATH="/root/.local/bin:/app/.venv/bin:$PATH"
ENV POETRY_VIRTUALENVS_IN_PROJECT=true

WORKDIR /app

COPY .env.docker .env
COPY . .

RUN poetry install --no-root

EXPOSE 3002

CMD ["poetry", "run", "start"]
```

- `FROM python:3.13-slim` define a imagem que vamos usar. Essa possui o python pré-instalado, na versão que preciso.
- `RUN apt-get update && apt-get install -y curl libpq-dev` atualiza os pacotes do sistema, dentro do container. Além disso, instala o pacote libpq-dev, que vamos usar no poetry mais pra frente.
- `RUN curl -sSL https://install.python-poetry.org | python3` instala o Poetry. Ele é o gerenciador de pacotes desse projeto (parecido com o maven, gradle, npm, etc).
- `ENV PATH="/root/.local/bin:/app/.venv/bin:$PATH"` e `ENV POETRY_VIRTUALENVS_IN_PROJECT=true` definem variaveis de ambiente. A primeira adiciona um caminho no PATH do container, permitindo executar os arquivos da pasta /root/.local/bin:/app/.venv/bin. O poetry está nesta pasta.
Já a segunda, configura uma variável para instalar o projeto dentro do container, sem precisar criar um virtualenv separado.
- `WORKDIR /app` configura o container para usar a pasta `/app` como diretório base. Os arquivos do
nosso projeto ficarão aqui.
- `COPY .env.docker .env` copia o arquivo .env.docker para dentro do container, renomeando-o para .env. Esse arquivo contém as variáveis
de ambiente usadas pelo app, como o mysql, redis, e a api de produtos.
- `COPY , ,` copia os demais arquivos para dentro do container.
- `RUN poetry install --no-root` instala as dependencias do projeto. 
- `EXPOSE 3002` configura a porta de saída do container. Vou conseguir acessar o app somente pela porta 3002.
- `CMD ["poetry", "run", "start"]` inicia o script start, definido no pyproject.toml. Esse script executa a aplicação.

#### docker-compose.yaml

No YAML, temos:

```yaml
  orders:
    build:
      context: ./order-service
      dockerfile: Dockerfile
    container_name: orders
    depends_on:
      - mysql
      - redis
      - products
    environment:
      PATH: "/root/.local/bin:/app/.venv/bin:$PATH"
      POETRY_VIRTUALENVS_IN_PROJECT: "true"
    ports:
      - "3002:3002"
    networks:
      - minha_rede
```

- Em `build, context e dockerfile`, configuro a dockerfile e pasta para utilizar nesse serviço. Como o repositório é compartilhado,
especificamos aqui a pasta onde está o serviço.
- Em `depends_on`, defino quais outros serviços essa api depende pra funcionar. Se não especificar aqui, a api pode quebrar (por
suas dependencias nao estarem ok).
- Em `environment`, reforço as variaveis de ambiente definidas na dockerfile e explicadas acima.
- Em `container_name`, definimos o nome do container desse serviço. Usamos esse nome para nos comunicarmos com o container depois.
- Em `ports`, definimos quais portas estarão disponíveis para o host e outros containers na mesma rede.
- Em `networks`, definimos quais as redes que o container está. Precisamos deixar todos na mesma rede para se comunicarem.

### payment-service

#### Dockerfile

Para esse serviço, temos uma dockerfile simples:

```dockerfile
FROM php:latest

WORKDIR /var/www/html

COPY . .

EXPOSE 3000

CMD ["php", "-S", "0.0.0.0:3000"]
```

- Em `FROM php:latest` define a imagem que vamos usar. Essa possui o PHP pré-configurado, e é o que eu preciso.
- Em `WORKDIR /var/www/html` configura o container para usar a pasta `/var/www/html` como diretório base. Os arquivos do
nosso projeto ficarão aqui. Nessa imagem, os arquivos PHP rodam especificamente nesse diretorio.
- Em `COPY , ,` copia os demais arquivos para dentro do container.
- Em `CMD ["php", "-S", "0.0.0.0:3000"]`, inicio a execução do app. O comando php vai "servir" todos os arquivos do diretório
/var/www/html, incluindo o index.php.

#### docker-compose.yml

No YAML, temos:

```yaml
  payments:
    build:
      context: ./payment-service
      dockerfile: Dockerfile
    container_name: payments
    depends_on:
      - orders
    environment:
      ORDER_API_URL: "http://orders:3002"
    ports:
      - "3000:3000"
    networks:
      - minha_rede
```

- Em `build, context e dockerfile`, configuro a dockerfile e pasta para utilizar nesse serviço. Como o repositório é compartilhado,
especificamos aqui a pasta onde está o serviço.
- Em `depends_on`, defino quais outros serviços essa api depende pra funcionar. Se não especificar aqui, a api pode quebrar (por
suas dependencias nao estarem ok).
- Em `environment`, reforço as variaveis de ambiente. Nesse caso, temos que definir o endereço da api orders.
- Em `container_name`, definimos o nome do container desse serviço. Usamos esse nome para nos comunicarmos com o container depois.
- Em `ports`, definimos quais portas estarão disponíveis para o host e outros containers na mesma rede.
- Em `networks`, definimos quais as redes que o container está. Precisamos deixar todos na mesma rede para se comunicarem.