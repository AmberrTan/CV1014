## Running This Project with pip, venv, and Python

Follow these steps to set up and run the project using Python's built-in venv and pip (no uv required):

### 1. Create a Virtual Environment

```
python3 -m venv .venv
```

### 2. Activate the Virtual Environment

- On macOS/Linux:
	```
	source .venv/bin/activate
	```
- On Windows:
	```
	.venv\Scripts\activate
	```

### 3. Install Dependencies

```
pip install -r requirements.txt
```


### 4. Run the API Server

Use [uvicorn](https://www.uvicorn.org/) to start the FastAPI app:

```
uvicorn src.main:app --reload
```

This will start the server at http://127.0.0.1:8000

You can then open your browser and visit [http://127.0.0.1:8000](http://127.0.0.1:8000) to access the API or static frontend.

---
For more details, see the source files in the `src/` directory.
