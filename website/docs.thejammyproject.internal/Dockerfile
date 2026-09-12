FROM python:3.13-alpine AS build

WORKDIR /docs
COPY website/docs.thejammyproject.internal/requirements.txt .
RUN pip install --no-cache-dir --requirement requirements.txt
COPY website/docs.thejammyproject.internal/ .
RUN mkdocs build --strict --site-dir /site

FROM nginxinc/nginx-unprivileged:1.28-alpine
COPY website/docs.thejammyproject.internal/nginx.conf /etc/nginx/conf.d/default.conf
COPY --from=build /site/ /usr/share/nginx/html/

EXPOSE 8080
