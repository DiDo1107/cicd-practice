// Кейс 5: многоэтапный пайплайн lint -> test -> build -> deploy
pipeline {
    agent any

    triggers {
        pollSCM('* * * * *')
    }

    environment {
        IMAGE = "cicd-practice:${env.BUILD_NUMBER}"
        CONTAINER = 'cicd-practice-app'
        APP_PORT = '8000'
    }

    stages {
        stage('Setup') {
            steps {
                sh '''
                    python3 -m venv .venv
                    . .venv/bin/activate
                    pip install -q -r requirements-dev.txt
                '''
            }
        }

        stage('Lint') {
            steps {
                sh '. .venv/bin/activate && flake8 .'
            }
        }

        stage('Unit tests') {
            steps {
                sh '. .venv/bin/activate && pytest -v --junitxml=test-results.xml'
            }
            post {
                always {
                    junit 'test-results.xml'
                }
            }
        }

        stage('Build') {
            steps {
                sh 'docker build -t $IMAGE .'
            }
        }

        stage('Deploy') {
            steps {
                sh '''
                    docker rm -f $CONTAINER || true
                    docker run -d --name $CONTAINER -p $APP_PORT:5000 -e APP_VERSION=$BUILD_NUMBER $IMAGE
                    sleep 5
                    docker exec $CONTAINER python -c "import urllib.request; print(urllib.request.urlopen('http://localhost:5000/health').read())"
                '''
            }
        }
    }

    post {
        success {
            echo "Приложение развернуто: http://localhost:${APP_PORT}"
        }
        failure {
            echo 'Пайплайн упал, смотрите лог этапа'
        }
    }
}
