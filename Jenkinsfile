#!groovy

node {

    String BRANCH = "${env.BRANCH_NAME}"
    String INVENTORY = (BRANCH == "master" ? "production" : "acceptance")

    try {

    stage "Checkout"
        checkout scm

    stage "Build"

        def image = docker.build("admin.datapunt.amsterdam.nl:5000/datapunt/mapserver:${BRANCH}")
        image.push()

        if (BRANCH == "master") {
            image.push("latest")
        }

    stage "Deploy"

        build job: 'Subtask_Openstack_Playbook',
                parameters: [
                        [$class: 'StringParameterValue', name: 'INVENTORY', value: INVENTORY],
                        [$class: 'StringParameterValue', name: 'PLAYBOOK', value: 'deploy-mapserver.yml'],
                        [$class: 'StringParameterValue', name: 'BRANCH', value: BRANCH],
                ]
}
    catch (err) {
        slackSend message: "Problem while building Mapserver service: ${err}",
                channel: '#ci-channel'

        throw err
    }
}
