```bash
# Start the server at http://127.0.0.1:8000
cd python
bash ./serve.sh 
# Run a quick test
python rag_lib.py 

# Dev client at http://localhost:5173/
cd client
bun dev         

# Build a distribution bundle in dist/
bun run build
```

http://127.0.0.1:8000/docs
