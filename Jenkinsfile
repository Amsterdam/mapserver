#!groovy

def tryStep(String message, Closure block, Closure tearDown = null) {
    try {
        block();
    }
    catch (Throwable t) {
        slackSend message: "${env.JOB_NAME}: ${message} failure ${env.BUILD_URL}", channel: '#ci-channel', color: 'danger'

        throw t;
    }
    finally {
        if (tearDown) {
            tearDown();
        }
    }
}


node {

    stage("Checkout") {
        checkout scm
    }


    stage("Build develop image") {
        tryStep "build", {
            def image = docker.build("admin.datapunt.amsterdam.nl:5000/datapunt/mapserver:${env.BUILD_NUMBER}")
            image.push()
            image.push("develop")
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
                            [$class: 'StringParameterValue', name: 'BRANCH', value: 'master'],
                    ]
        }
    }
}


stage('Waiting for approval') {
    input "Deploy to Production?"
}



node {
    stage('Push production image') {
    tryStep "image tagging", {
        def image = docker.image("admin.datapunt.amsterdam.nl:5000/datapunt/mapserver:${env.BUILD_NUMBER}")
        image.pull()

            image.push("master")
            image.push("latest")
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
                            [$class: 'StringParameterValue', name: 'BRANCH', value: 'master'],
                    ]
        }
    }
}