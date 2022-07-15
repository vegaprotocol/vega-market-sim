
/* properties of scmVars (example):
    - GIT_BRANCH:PR-40-head
    - GIT_COMMIT:05a1c6fbe7d1ff87cfc40a011a63db574edad7e6
    - GIT_PREVIOUS_COMMIT:5d02b46fdb653f789e799ff6ad304baccc32cbf9
    - GIT_PREVIOUS_SUCCESSFUL_COMMIT:5d02b46fdb653f789e799ff6ad304baccc32cbf9
    - GIT_URL:https://github.com/vegaprotocol/vega-market-sim.git
*/
def scmVars = null
def version = 'UNKNOWN'
def versionHash = 'UNKNOWN'
def commitHash = 'UNKNOWN'


pipeline {
    agent { label 'system-tests' }
    options {
        skipDefaultCheckout true
        timestamps()
        timeout(time: 45, unit: 'MINUTES')
    }
    parameters {
        string(name: 'VEGA_BRANCH', defaultValue: 'develop', description: 'Git branch name of the vegaprotocol/vega repository')
        string(name: 'DATA_NODE_BRANCH', defaultValue: 'develop', description: 'Git branch name of the vegaprotocol/data-node repository')
    }
    environment {
        CGO_ENABLED = 0
        GO111MODULE = 'on'
    }

    stages {
        stage('Git Clone') {
            parallel {
                stage('vega-market-sim') {
                    options { retry(3) }
                    steps {
                        dir('vega-market-sim') {
                            script {
                                scmVars = checkout(scm)
                                versionHash = sh (returnStdout: true, script: "echo \"${scmVars.GIT_COMMIT}\"|cut -b1-8").trim()
                                version = sh (returnStdout: true, script: "git describe --tags 2>/dev/null || echo ${versionHash}").trim()
                            }
                        }
                    }
                }
                stage('vega core') {
                    options { retry(3) }
                    steps {
                        dir('vega-market-sim') {
                            dir('extern/vega') {
                                git branch: "${params.VEGA_BRANCH}", credentialsId: 'vega-ci-bot', url: 'git@github.com:vegaprotocol/vega.git'
                            }
                        }
                    }
                }
                stage('data-node') {
                    options { retry(3) }
                    steps {
                        dir('vega-market-sim') {
                            dir('extern/data-node') {
                                git branch: "${params.DATA_NODE_BRANCH}", credentialsId: 'vega-ci-bot', url: 'git@github.com:vegaprotocol/data-node.git'
                            }
                        }
                    }
                }
            }
        }

        stage('Build Docker Image') {
            options { retry(3) }
            steps {
                dir('vega-market-sim') {
                    sh label: 'Build docker image', script: '''
                        scripts/build-docker-test.sh
                    '''
                }
            }
        }

        stage('Tests') {
            steps {
                dir('vega-market-sim') {
                    sh label: 'Run Integration Tests', script: '''
                        scripts/run-docker-integration-test.sh
                    '''
                }
                dir('vega-market-sim') {
                    sh label: 'Example Notebook Tests', script: '''
                        scripts/run-docker-example-notebook-test.sh
                    '''
                }
            }
            post {
                always {
                    archiveArtifacts artifacts: 'vega-market-sim/test_logs/**/*.out'
                    archiveArtifacts artifacts: 'vega-market-sim/test_logs/**/*.err'
                }
            }
        }
    }
    // post {
    //     // success {
    //     // }
    //     // unsuccessful {
    //     // }
    //     // cleanup {
    //     //     retry(3) {
    //     //     }
    //     // }
    // }
}