### bash command for deploy to cloud
```bash
gcloud functions deploy marker-variation \
    --runtime python312 \
    --trigger-http \
    --allow-unauthenticated
```

### only update function with authentication required
```bash
gcloud functions deploy marker-variation \
    --runtime python312 \
    --trigger-http \
    --no-allow-unauthenticated \
    --update-labels=version=5
```