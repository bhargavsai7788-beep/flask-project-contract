pipeline {
    agent any

    environment {
        IMAGE_NAME = "contract-life-cycle-flask-app"
        IMAGE_TAG = "${env.BUILD_ID}"
        CONTAINER_NAME = "clmp-container"
    }

    stages {
        stage('Checkout') {
            steps {
                checkout scm
            }
        }
        stage('Build Docker Image') {
            steps {
                sh "docker build -t ${IMAGE_NAME}:${IMAGE_TAG} ."
            }
        }
        stage('Run Unit Tests') {
            steps {
                sh "docker run --rm ${IMAGE_NAME}:${IMAGE_TAG} pytest"
            }
        }
        stage('Deploy to Server') {
            steps {
                // Stop and remove any existing container
                sh "docker stop ${CONTAINER_NAME} || true"
                sh "docker rm ${CONTAINER_NAME} || true"
                // Run the new container
                sh "docker run -d -p 5000:5000 --name ${CONTAINER_NAME} ${IMAGE_NAME}:${IMAGE_TAG}"
            }
        }
        //Optional: Push to Docker Hub (requires credentials setup in Jenkins)
        stage('Push to Docker Hub') {
            steps {
                withDockerRegistry([ credentialsId: 'dockerhub-credentials', url: 'https://index.docker.io/v1/' ]) {
                    sh "docker tag ${IMAGE_NAME}:${IMAGE_TAG} bhargav1518/${IMAGE_NAME}:${IMAGE_TAG}"
                    sh "docker push bhargav1518/${IMAGE_NAME}:${IMAGE_TAG}"
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