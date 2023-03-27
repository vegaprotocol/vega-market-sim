@Library('vega-shared-library') _

def scmVars = null
def version = 'UNKNOWN'
def versionHash = 'UNKNOWN'
def commitHash = 'UNKNOWN'

pipeline {
    agent none
    options {
        skipDefaultCheckout true
        timestamps()
        timeout(time: 50, unit: 'MINUTES')
    }
    parameters {
        string( name: 'VEGA_VERSION', defaultValue: '42ec67c184dd92c86d8ab245f3a907daf0c08841',
                description: 'Git branch, tag or hash of the vegaprotocol/vega repository')
        string( name: 'JENKINS_SHARED_LIB_BRANCH', defaultValue: 'main',
                description: 'Git branch, tag or hash of the vegaprotocol/jenkins-shared-library repository')
    }
    environment {
        CGO_ENABLED = 0
        GO111MODULE = 'on'
    }

    stages {
        stage('Config') {
            agent any
            steps {
                sh 'printenv'
                echo "params=${params}"
                echo "isPRBuild=${isPRBuild()}"
                script {
                    params = pr.injectPRParams()
                }
                echo "params (after injection)=${params}"
            }
        }

        stage('Git clone') {
            agent any
            options { retry(3) }
            steps {
                dir('vega-market-sim') {
                    script {
                        scmVars = checkout(scm)
                        versionHash = sh (returnStdout: true, script: "echo \"${scmVars.GIT_COMMIT}\"|cut -b1-8").trim()
                        version = sh (returnStdout: true, script: "git describe --tags 2>/dev/null || echo ${versionHash}").trim()
                        commitHash = getCommitHash()
                    }
                    echo "scmVars=${scmVars}"
                    echo "commitHash=${commitHash}"
                }
            }
        }

        stage('Vega Market Sim Tests') {
            steps {
                script {
                    vegaMarketSim ignoreFailure: false,
                        timeout: 90,
                        vegaMarketSim: commitHash,
                        vegaVersion: params.VEGA_VERSION,
                        jenkinsSharedLib: params.JENKINS_SHARED_LIB_BRANCH
                }
            }
        }
    }
}