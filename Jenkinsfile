pipeline {
    agent any

    environment {
        // We define a default here, but it will be overwritten by the build number
        IMAGE_NAME = "contract-life-cycle-flask-app"
        IMAGE_TAG = "latest"
    }

    stages {
        stage('Build Docker Image') {
            steps {
                script {
                    // Set the IMAGE_TAG to the current build number BEFORE building the image
                    env.IMAGE_TAG = bat(returnStdout: true, script: 'echo %BUILD_NUMBER%').trim()
                }
                bat "docker build -t ${IMAGE_NAME}:${IMAGE_TAG} ."
            }
        }

        // Remove or comment out this stage if you have no tests
        // stage('Run Unit Tests') {
        //     steps {
        //         bat "docker run --rm ${IMAGE_NAME}:${IMAGE_TAG} python -m pytest tests/"
        //     }
        // }

        stage('Deploy to Server') {
            steps {
                script {
                    try {
                        bat 'docker stop clmp-container'
                    } catch (Exception e) {
                        echo "Container 'clmp-container' was not running, proceeding anyway."
                    }
                    try {
                        bat 'docker rm clmp-container'
                    } catch (Exception e) {
                        echo "Container 'clmp-container' did not exist, proceeding anyway."
                    }
                }
                // This command will now use the correct tag (the build number)
                bat "docker run -d --name clmp-container -p 5000:5000 ${IMAGE_NAME}:${IMAGE_TAG}"
            }
        }

        // Optional: Push to Docker Hub (requires credentials setup in Jenkins)
        stage('Push to Docker Hub') {
            steps {
                withDockerRegistry([ credentialsId: 'dockerhub-credentials', url: 'https://index.docker.io/v1/' ]) {
                    // This command will now use the correct tag (the build number)
                    bat "docker tag ${IMAGE_NAME}:${IMAGE_TAG} bhargav1518/${IMAGE_NAME}:${IMAGE_TAG}"
                    bat "docker push bhargav1518/${IMAGE_NAME}:${IMAGE_TAG}"
                }
            }
        }
    }
    post {
        always {
            echo 'Pipeline finished.'
        }
    }
}