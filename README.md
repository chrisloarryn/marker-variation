### bash command for deploy to cloud
```bash
gcloud functions deploy marker-variation \
    --runtime python312 \
    --trigger-http \
    --allow-unauthenticated
```