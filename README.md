# Практика CI/CD

Простое Flask-приложение (`app/`) с юнит-тестами (`tests/`) и конфигурациями для всех 10 кейсов.

```bash
pip install -r requirements-dev.txt
flake8 .          # lint
pytest -v         # тесты
python -m app.main  # http://localhost:5000
```

| Кейс | Инструмент | Файлы |
|---|---|---|
| 1. CI-сборка | GitHub Actions | `.github/workflows/ci.yml` |
| 2. Юнит-тесты | GitLab CI | `.gitlab-ci.yml` (job `unit-tests`) |
| 3. Деплой на Heroku | CircleCI | `.circleci/config.yml`, `Procfile` |
| 4. Docker → Docker Hub | Jenkins | `Dockerfile`, `jenkins/Jenkinsfile.docker` |
| 5. Многоэтапный пайплайн | Jenkins | `Jenkinsfile` |
| 6. Уведомления | GitHub Actions | `.github/workflows/ci.yml` (job `notify`) |
| 7. Релизы по тегам | GitHub Actions | `.github/workflows/release.yml` |
| 8. Kubernetes + Helm | GitLab CI | `.gitlab-ci.yml`, `helm/cicd-app/` |
| 9. Анализ безопасности | SonarCloud, Bandit, pip-audit | `.github/workflows/security.yml`, `sonar-project.properties` |
| 10. Миграции БД | Flyway | `.github/workflows/deploy-db.yml`, `db/migrations/` |

---

## Подготовка

1. Установить [Git](https://git-scm.com/download/win) и [Docker Desktop](https://www.docker.com/products/docker-desktop/).
2. В папке проекта:
   ```bash
   git init -b main
   git add .
   git commit -m "Initial commit"
   ```

## Кейс 1 — GitHub Actions

1. На github.com → **New repository** → `cicd-practice` (без README).
2. ```bash
   git remote add origin https://github.com/<USER>/cicd-practice.git
   git push -u origin main
   ```
3. Вкладка **Actions** → workflow **CI** зелёный. Любой следующий коммит запускает его снова.

## Кейс 2 — GitLab CI

1. На gitlab.com → **New project → Create blank project** → `cicd-practice`.
2. ```bash
   git remote add gitlab https://gitlab.com/<USER>/cicd-practice.git
   git push -u gitlab main
   ```
3. **Build → Pipelines**: job `unit-tests` выполняется на каждый коммит, отчёт тестов — во вкладке **Tests**.

> GitLab может попросить подтвердить аккаунт (телефон/карта), чтобы пользоваться бесплатными shared runners.

## Кейс 3 — CircleCI + Heroku

1. Heroku: создать приложение (`heroku create <имя>` или через сайт), скопировать **API Key** (Account settings).
2. circleci.com → войти через GitHub → **Projects → Set Up Project** `cicd-practice` → использовать существующий `.circleci/config.yml`.
3. **Project Settings → Environment Variables**: `HEROKU_API_KEY`, `HEROKU_APP_NAME`.
4. Пуш в `main` → тесты → деплой. Приложение: `https://<имя>.herokuapp.com/`.

> У Heroku нет бесплатного тарифа (минимум Eco ~5$/мес).

## Кейсы 4 и 5 — Jenkins

1. Запустить Jenkins:
   ```bash
   docker compose -f jenkins/docker-compose.yml up -d --build
   docker exec jenkins cat /var/jenkins_home/secrets/initialAdminPassword
   ```
   Открыть http://localhost:8080, ввести пароль, установить рекомендуемые плагины.
2. **Manage Jenkins → Credentials → Global → Add**: тип *Username with password*, ID `dockerhub`, логин Docker Hub и *Access Token* (hub.docker.com → Account settings → Personal access tokens).
3. **Кейс 4**: New Item → *Pipeline* `docker-build` → Pipeline script from SCM → Git → URL GitHub-репозитория, ветка `*/main`, Script Path `jenkins/Jenkinsfile.docker`. После сборки образ появится в Docker Hub: `<USER>/cicd-practice`.
4. **Кейс 5**: New Item → *Pipeline* `multistage` → то же, Script Path `Jenkinsfile`. В **Stage View** видны этапы Setup → Lint → Unit tests → Build → Deploy. Приложение: http://localhost:8000.

Оба пайплайна опрашивают репозиторий раз в минуту (`pollSCM`), поэтому запускаются на каждый коммит.

## Кейс 6 — Уведомления

**Slack:** api.slack.com/apps → Create App → Incoming Webhooks → включить → Add New Webhook → скопировать URL.
GitHub → **Settings → Secrets and variables → Actions → New repository secret**: `SLACK_WEBHOOK_URL`.

**Email (Gmail):** включить двухфакторку, создать [пароль приложения](https://myaccount.google.com/apppasswords). Секреты: `MAIL_USERNAME` (адрес), `MAIL_PASSWORD` (пароль приложения), `MAIL_TO` (кому).

После любого коммита job `notify` отправит статус (успешно/неудачно).

## Кейс 7 — Релизы

```bash
git tag v1.0.0
git push origin v1.0.0
```
В **Releases** появится релиз с changelog (коммиты с прошлого тега) и архивом `cicd-practice-v1.0.0.tar.gz` + `SHA256SUMS.txt`.

## Кейс 8 — Kubernetes + Helm

1. Локальный кластер: в Docker Desktop **Settings → Kubernetes → Enable**, или `minikube start`.
2. Чтобы GitLab достучался до локального кластера, зарегистрировать **свой runner** (Settings → CI/CD → Runners → New project runner) и запустить его на этой машине; либо использовать облачный кластер.
3. **Settings → CI/CD → Variables**: переменная `KUBECONFIG`, тип **File**, значение — содержимое `~/.kube/config`.
4. Проект сделать публичным (или настроить `imagePullSecrets` в `helm/cicd-app/values.yaml`).
5. Пуш в `main` → `unit-tests` → `docker-build` (образ в GitLab Container Registry) → `helm-deploy`.
6. Проверка: `kubectl get pods -n cicd-app`, `helm list -n cicd-app`.

## Кейс 9 — Безопасность и качество

Bandit и pip-audit работают сразу. Для SonarCloud:
1. sonarcloud.io → войти через GitHub → **Analyze new project** → `cicd-practice`.
2. Отключить *Automatic Analysis* (Administration → Analysis Method).
3. В `sonar-project.properties` вписать свои `sonar.organization` и `sonar.projectKey`.
4. Секрет GitHub `SONAR_TOKEN` (My Account → Security → Generate token).

## Кейс 10 — Миграции БД

Миграции в `db/migrations/` (`V1__...sql`, `V2__...sql`, ...). При каждом пуше в `main` workflow **Deploy with DB migrations** поднимает PostgreSQL, выполняет `flyway migrate` и разворачивает приложение. В логе видно, какие миграции применены.
Новая миграция = новый файл `V4__описание.sql`.

Для реальной БД задайте секреты `DB_URL` (`jdbc:postgresql://host:5432/db`), `DB_USER`, `DB_PASSWORD`.
