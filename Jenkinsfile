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
        string( name: 'VEGA_VERSION', defaultValue: '9ea03e445250aa1321f04953aff175e1bc0e5b4a',
                description: 'Git branch, tag or hash of the vegaprotocol/vega repository')
        string( name: 'JENKINS_SHARED_LIB_BRANCH', defaultValue: 'main',
                description: 'Git branch, tag or hash of the vegaprotocol/jenkins-shared-library repository')
        string( name: 'NODE_LABEL', defaultValue: 's-8vcpu-16gb',
                description: 'Node to run market sims' )
    }
    environment {
        CGO_ENABLED = 0
        GO111MODULE = 'on'
    }

    stages {
        stage('Config') {
            agent {
                label 's-2vcpu-4gb'
            }
            steps {
                sh 'printenv'
                echo "params=${params}"
                echo "isPRBuild=${isPRBuild()}"
                script {
                    params = pr.injectPRParams()
                }
                echo "params (after injection)=${params}"
                retry (3) {
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
        }

        stage('Vega Market Sim Tests') {
            steps {
                script {
                    vegaMarketSim (
                        ignoreFailure: false,
                        timeout: 90,
                        vegaMarketSim: commitHash,
                        vegaVersion: params.VEGA_VERSION,
                        jenkinsSharedLib: params.JENKINS_SHARED_LIB_BRANCH,
                        nodeLabel: params.NODE_LABEL,
                    )
                }
            }
        }
    }
}
