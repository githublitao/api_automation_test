pipeline {
  agent any
  stages {
    stage('Build') {
      steps {
        sh 'sudo kill -9  uwsgi'
        sh 'pip3 install -r requirements.txt'
        sh 'python3 manage.py makemigrations'
        sh 'python3 manage.py migrate'
        sh 'cp -r /usr/local/python3/bin/darklow-django-suit-52ecdad/suit/static/admin frontend/dist/static'
        sh 'cp -r /usr/local/python3/bin/darklow-django-suit-52ecdad/suit/static/suit frontend/dist/static'
        sh 'cp -rf /usr/local/python3/lib/python3.6/site-packages/django/contrib/admin/static/admin frontend/dist/static'
        sh 'cp -r /usr/local/python3/lib/python3.6/site-packages/rest_framework_swagger/static/rest_framework_swagger frontend/dist/static'
        sh 'cp -r /usr/local/python3/lib/python3.6/site-packages/rest_framework/static/rest_framework frontend/dist/static'
        sh '/usr/local/python3/bin/uwsgi --ini /etc/script/uwsgi.ini'
        sh '/usr/local/python3/bin/uwsgi --ini /etc/script/Ituwsgi.ini'
        sh '/usr/local/python3/bin/uwsgi --ini /etc/script/MItuwsgi.ini'
      }
      post {
        always {
          sh 'pip3 install -r requirements.txt'
          sh 'python3 manage.py makemigrations'
          sh 'python3 manage.py migrate'
          sh 'cp -r /usr/local/python3/bin/darklow-django-suit-52ecdad/suit/static/admin frontend/dist/static'
          sh 'cp -r /usr/local/python3/bin/darklow-django-suit-52ecdad/suit/static/suit frontend/dist/static'
          sh 'cp -rf /usr/local/python3/lib/python3.6/site-packages/django/contrib/admin/static/admin frontend/dist/static'
          sh 'cp -r /usr/local/python3/lib/python3.6/site-packages/rest_framework_swagger/static/rest_framework_swagger frontend/dist/static'
          sh 'cp -r /usr/local/python3/lib/python3.6/site-packages/rest_framework/static/rest_framework frontend/dist/static'
          sh '/usr/local/python3/bin/uwsgi --ini /etc/script/uwsgi.ini'
          sh '/usr/local/python3/bin/uwsgi --ini /etc/script/Ituwsgi.ini'
          sh '/usr/local/python3/bin/uwsgi --ini /etc/script/MItuwsgi.ini'
        }
      }
    }
  }
}