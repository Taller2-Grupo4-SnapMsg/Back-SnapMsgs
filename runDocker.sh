# This script is for seeing the endpoints connected to the data base without going through render
# Use with caution.
docker build -t postsback .
docker run -p 8000:8000 postsback