pipeline {
    agent {
        docker {
            image 'docker:latest'
        }
    }

    environment {
        IMAGE_NAME = "contract-life-cycle-flask-app"
        IMAGE_TAG = "latest"
    }

    stages {
        stage('Build Docker Image') {
            steps {
                script {
                    env.IMAGE_TAG = sh(returnStdout: true, script: 'echo ${BUILD_NUMBER}').trim()
                }
                sh "docker build -t ${IMAGE_NAME}:${IMAGE_TAG} ."
            }
        }

        // Remove or comment out this stage if you have no tests
        // stage('Run Unit Tests') {
        //     steps {
        //         sh "docker run --rm ${IMAGE_NAME}:${IMAGE_TAG} python -m pytest tests/"
        //     }
        // }

        stage('Deploy to Server') {
            steps {
                sh "docker stop clmp-container || true"
                sh "docker rm clmp-container || true"
                sh "docker run -d --name clmp-container -p 5000:5000 ${IMAGE_NAME}:${IMAGE_TAG}"
            }
        }

        // Optional: Push to Docker Hub (requires credentials setup in Jenkins)
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