# IDP System Deployment Guide

Because the backend relies heavily on system-level libraries for AI and data extraction (such as Tesseract OCR, Java for Tabula, and Poppler for PDFs), the easiest and most robust way to deploy the backend is using Docker on **Render**. The frontend is a standard Next.js application, which deploys seamlessly on **Vercel**.

## 1. Deploy the Backend (FastAPI) on Render

1. Go to [Render.com](https://render.com) and create a free account / log in.
2. Click **New +** in the top right corner and select **Web Service**.
3. Choose **Build and deploy from a Git repository** and connect your GitHub repository (`YashuGowda08/IDP-System`).
4. Apply the following settings:
   - **Name:** `idp-backend` (or any name you prefer)
   - **Root Directory:** Type `backend` *(This is extremely important as it tells Render to look for our Dockerfile inside the backend folder)*.
   - **Environment:** Select **Docker** (Render should detect the `Dockerfile` automatically because of the root directory setting).
   - **Region:** Choose the region closest to you.
   - **Instance Type:** Select the Free (or Starter) tier. 
5. Click **Create Web Service** at the bottom.
6. Render will now build the Docker image, install Java, Tesseract, Poppler, and the spaCy NLP model. This will take a few minutes.
7. Once deployed, Render will provide you with a live URL (e.g., `https://idp-backend-xyz.onrender.com`). **Copy this URL**.

---

## 2. Deploy the Frontend (Next.js) on Vercel

1. Go to [Vercel.com](https://vercel.com) and create a free account / log in.
2. Click **Add New...** and select **Project**.
3. Import your `YashuGowda08/IDP-System` GitHub repository.
4. In the **Configure Project** section:
   - **Root Directory:** Click Edit and select the `frontend` folder.
   - **Framework Preset:** Vercel should automatically detect **Next.js**.
5. Open the **Environment Variables** dropdown and add the following:
   - **Name:** `NEXT_PUBLIC_API_URL`
   - **Value:** Paste your Render backend URL from Step 1 (e.g., `https://idp-backend-xyz.onrender.com`). 
     > *Note: Make sure there is no trailing slash `/` at the very end of your URL.*
6. Click **Deploy**.
7. Vercel will install the Node dependencies, build the frontend, and deploy it.

---

## 3. Test the Deployed Application

1. Once Vercel finishes, click on the **Domain** they provide to open your live application.
2. You can upload a document. The frontend will now communicate directly with your live Render backend container instead of your local machine.

*Note: If you are using the Free tier on Render, the backend server might "go to sleep" after 15 minutes of inactivity. When you upload your first document after a period of inactivity, it may take an extra 30-60 seconds for the backend to wake up before processing starts.*
