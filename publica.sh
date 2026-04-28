gcloud auth configure-docker us-central1-docker.pkg.dev
docker build -t us-central1-docker.pkg.dev/jkdemo001/ardemosintia/viviendapi:v1 .
docker push us-central1-docker.pkg.dev/jkdemo001/ardemosintia/viviendapi:v1
