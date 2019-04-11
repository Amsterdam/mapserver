#!groovy

def tryStep(String message, Closure block, Closure tearDown = null) {
    try {
        block()
    }
    catch (Throwable t) {
        slackSend message: "${env.JOB_NAME}: ${message} failure ${env.BUILD_URL}", channel: '#ci-channel', color: 'danger'

        throw t
    }
    finally {
        if (tearDown) {
            tearDown()
        }
    }
}


node {
    stage("Checkout") {
        checkout scm
    }


    stage("Build image") {
        tryStep "build", {
            docker.withRegistry('https://repo.data.amsterdam.nl','docker-registry') {
                def image = docker.build("datapunt/mapserver-public:${env.BUILD_NUMBER}", "--build-arg http_proxy=${JENKINS_HTTP_PROXY_STRING} --build-arg https_proxy=${JENKINS_HTTP_PROXY_STRING} .")
                image.push()
            }
        }
        tryStep "build private", {
            docker.withRegistry('https://repo.data.amsterdam.nl','docker-registry') {
                def image = docker.build("datapunt/mapserver-private:${env.BUILD_NUMBER}", "--build-arg http_proxy=${JENKINS_HTTP_PROXY_STRING} --build-arg https_proxy=${JENKINS_HTTP_PROXY_STRING} .")
                image.push()
            }
        }
    }
}


String BRANCH = "${env.BRANCH_NAME}"

if (BRANCH == "develop") {

    node {
        stage('Push acceptance image') {
            tryStep "image tagging", {
                docker.withRegistry('https://repo.data.amsterdam.nl','docker-registry') {
                    def image = docker.image("datapunt/mapserver-public:${env.BUILD_NUMBER}")
                    image.pull()
                    image.push("acceptance")
                }
            }
        }

        stage('Push acceptance image') {
            tryStep "image tagging", {
                docker.withRegistry('https://repo.data.amsterdam.nl','docker-registry') {
                    def image = docker.image("datapunt/mapserver-private:${env.BUILD_NUMBER}")
                    image.pull()
                    image.push("acceptance")
                }
            }
        }
    }

    node {
        stage("Deploy to ACC") {
            tryStep "deployment", {
                build job: 'Subtask_Openstack_Playbook',
                parameters: [
                    [$class: 'StringParameterValue', name: 'INVENTORY', value: 'acceptance'],
                    [$class: 'StringParameterValue', name: 'PLAYBOOK', value: 'deploy-mapserver.yml'],
                ]
            }
        }
    }

    stage('Waiting for approval') {
        slackSend channel: '#ci-channel', color: 'warning', message: 'Mapserver is waiting for Production Release - please confirm'
        input "Deploy to Production?"
    }

    node {
        stage('Push production image') {
            tryStep "image tagging", {
                docker.withRegistry('https://repo.data.amsterdam.nl','docker-registry') {
                def image = docker.image("datapunt/mapserver-public:${env.BUILD_NUMBER}")
                    image.pull()
                    image.push("production")
                    image.push("latest")
                }
            }

            tryStep "image tagging private", {
                docker.withRegistry('https://repo.data.amsterdam.nl','docker-registry') {
                    def image = docker.image("datapunt/mapserver-private:${env.BUILD_NUMBER}")
                    image.pull()
                    image.push("production")
                    image.push("latest")
                    }
            }
        }
    }

    node {
        stage("Deploy") {
            tryStep "deployment", {
                build job: 'Subtask_Openstack_Playbook',
                parameters: [
                    [$class: 'StringParameterValue', name: 'INVENTORY', value: 'production'],
                    [$class: 'StringParameterValue', name: 'PLAYBOOK', value: 'deploy-mapserver.yml'],
                ]
            }
        }
    }
}