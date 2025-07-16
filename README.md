# GPS-tracker

## Running with Docker

Чтобы запустить сервер в контейнере Docker, выполните следующие действия в корневом каталоге:
```bash
cd docker
docker-compose up --build
```

Далее необходимо открыть браузер по ссылке `http://localhost:8080/docs/` чтобы увидеть документацию OpenAPI

Чтобы посмотреть логи приложения, необходимо запустить сервер по команде выше, а далее
```bash
docker exec -it gps-track-service tail -f /usr/src/app/logs/api.log
```

Чтобы запустить тесты, необходимо запустить команду

```bash
 ./run_test.sh 
```