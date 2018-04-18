#!/usr/bing/env groovy

//Declarative
pipeline {
	agent any    		//agent必需的,告诉Jenkins分配执行器和工作空间

    stages {			//stage必需的,
		stage('Build') {
			steps {		//step必需的
				echo 'Building....'
			}
		}
		stage('Test') {
			steps{
				echo 'Testing....'
			}
		}
		stage('Deploy') {
			steps{
				echo 'Deploying....'
			}
		}
    }
}