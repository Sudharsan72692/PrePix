# PrePix (Image Processing)

This workspace contains a Flask backend that processes uploaded images (converts to grayscale) and a simple Svelte frontend that uses Firebase for authentication and storage.

Backend (Flask):

1. Create a Python virtual environment and install dependencies:

```powershell
python -m venv env
.\env\Scripts\activate
pip install -r backend/requirements.txt
```

2. Run the backend:

```powershell
python backend/app.py
```

Frontend (Svelte + Firebase):

1. Change to the frontend folder and install dependencies:

```bash
npm install
npm run dev
```

2. Open `http://localhost:5173` and use the Register / Login pages. After registering you'll receive a verification email (Firebase sends it). Verify your email before uploading files.

Notes:
- The frontend sends the image to the Flask backend at `http://localhost:5000/process` which returns a grayscale image and the frontend uploads the processed image to Firebase Storage.
- Ensure your Firebase project's auth and storage rules allow the client operations used here.
