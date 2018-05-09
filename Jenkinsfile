pipeline {
  agent any
  stages {
    stage('Build') {
      steps {
        sh 'sudo kill -9  uwsgi'
        sh 'pip3 install -r requirements.txt'
        sh 'python3 manage.py makemigrations'
        sh 'python3 manage.py migrate'
        sh '/usr/local/python3/bin/uwsgi --ini /etc/script/uwsgi.ini'
      }
      post {
        always {
          sh 'pip3 install -r requirements.txt'
          sh 'python3 manage.py makemigrations'
          sh 'python3 manage.py migrate'
          sh '/usr/local/python3/bin/uwsgi --ini /etc/script/uwsgi.ini'
        }
      }
    }
  }
}
