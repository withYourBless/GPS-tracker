# GPS-tracker

## Running with Docker

Чтобы запустить сервер в контейнере Docker, выполните следующие действия в корневом каталоге:
```bash
cd docker
docker-compose up --build
```

Далее необходимо открыть браузер по ссылке `http://localhost:8080/docs/` чтобы увидеть документацию OpenAPI


Чтобы запустить тесты, необходимо запустить команду

```bash
 ./run_test.sh 
```