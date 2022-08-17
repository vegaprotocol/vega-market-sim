pipeline {
    agent { label 'system-tests' }
    options {
        timestamps()
        timeout(time: 45, unit: 'MINUTES')
    }
    parameters {
        string(name: 'VEGA_BRANCH', defaultValue: '9330de0991d0c818a1b08ea623ad807370fbc212', description: 'Git branch name of the vegaprotocol/vega repository')
   }
    environment {
        CGO_ENABLED = 0
        GO111MODULE = 'on'
        DOCKER_IMAGE_NAME_LOCAL = 'vega_sim_test:latest'
    }

    stages {
        stage('Config') {
            steps {
                sh 'printenv'
                echo "params=${params}"
            }
        }

        stage('Git Clone') {
            parallel {
                stage('vega core') {
                    options { retry(3) }
                    steps {
                        dir('extern/vega') {
                            checkout(
                                [$class: 'GitSCM', branches: [[name: "${params.VEGA_BRANCH}" ]], 
                                userRemoteConfigs: [[credentialsId: 'vega-ci-bot', url: 'git@github.com:vegaprotocol/vega.git']]]
                            )
                        }
                    }
                }
            }
        }

        stage('Build Docker Image') {
            options { retry(3) }
            steps {
                sh label: 'Build docker image', script: '''
                    docker build --tag="${DOCKER_IMAGE_NAME_LOCAL}" -t vegasim_test .
                '''
            }
        }

        stage('Tests') {
            steps {
                sh label: 'Run Integration Tests', script: '''
                    scripts/run-docker-integration-test.sh ${BUILD_NUMBER}
                '''
                sh label: 'Example Notebook Tests', script: '''
                    scripts/run-docker-example-notebook-test.sh
                '''
            }
            post {
                always {
                    archiveArtifacts artifacts: 'test_logs/**/*.out'
                }
            }
        }
    }
    post {
        always {
            retry(3) {
                cleanWs()
                sh label: 'Clean docker images', script: '''#!/bin/bash -e
                    [ -z "$(docker images -q "${DOCKER_IMAGE_NAME_LOCAL}")" ] || docker rmi "${DOCKER_IMAGE_NAME_LOCAL}"
                '''
            }
        }
    }
}