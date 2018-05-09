pipeline {
  agent any
  stages {
    stage('Build') {
      steps {
        catchError() {
          sh 'sudo kill -9 uwsgi'
        }

      }
    }
  }
}