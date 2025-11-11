# TODO

- Add a docker-compose.yml to keep the mcp server running:

```docker-compose.yml
version: '3.8'
services:
  mcp-server:
    image: your-mcp-server-image
    ports:
      - "8000:8000"
    restart: unless-stopped  # Keeps container running
    command: python server.py  # Or whatever starts your server
    # Ensure the main process doesn't exit
    stdin_open: true
    tty: true
```

- Rebuild and add the docker container again to all relaited files
    - catalogs
    - registry.yaml

