# AI-Powered Intelligent Document Processing (IDP) System

A full-stack system that extracts **text, tables, and images** from documents (PDF, JPG, PNG) and converts them into structured **JSON/CSV/Excel** formats.

**Backend:** Python FastAPI | **Frontend:** Next.js + Tailwind CSS  
**AI/ML:** Tesseract OCR, EasyOCR, OpenCV, spaCy NLP, Tabula

---

## 📁 Project Structure

```
├── backend/
│   ├── main.py                  # FastAPI app & endpoints
│   ├── config.py                # Configuration settings
│   ├── requirements.txt         # Python dependencies
│   ├── modules/
│   │   ├── preprocessing.py     # OpenCV image preprocessing
│   │   ├── ocr_engine.py        # Tesseract + EasyOCR
│   │   ├── pdf_processor.py     # PDF → images, embedded images
│   │   ├── table_extractor.py   # Tabula table extraction
│   │   ├── nlp_processor.py     # spaCy named entity recognition
│   │   ├── output_generator.py  # JSON/CSV/Excel output
│   │   └── classifier.py        # Document classification
│   └── utils/
│       └── logger.py            # Structured logging
├── frontend/
│   └── src/
│       ├── app/                 # Next.js pages
│       ├── components/          # React UI components
│       └── lib/api.ts           # Backend API client
└── README.md
```

---

## 🚀 Setup Instructions

### Prerequisites

| Tool | Purpose | Install |
|------|---------|---------|
| **Python 3.9+** | Backend | [python.org](https://python.org) |
| **Node.js 18+** | Frontend | [nodejs.org](https://nodejs.org) |
| **Tesseract OCR** | Text extraction | See below |
| **Java 8+** | Tabula (table extraction) | [java.com](https://java.com) |
| **Poppler** | PDF to image conversion | See below |

#### Install Tesseract OCR (Windows)
1. Download from: https://github.com/UB-Mannheim/tesseract/wiki
2. Install to `C:\Program Files\Tesseract-OCR\`
3. Add to PATH (or set `TESSERACT_CMD` in `config.py`)

#### Install Poppler (Windows)
1. Download from: https://github.com/oschwartz10612/poppler-windows/releases
2. Extract and add `bin/` folder to PATH
3. Or set `POPPLER_PATH` environment variable

---

### Backend Setup

```bash
# Navigate to backend
cd backend

# Create virtual environment
python -m venv venv
venv\Scripts\activate        # Windows
# source venv/bin/activate   # macOS/Linux

# Install dependencies
pip install -r requirements.txt

# Download spaCy model
python -m spacy download en_core_web_sm

# Start server
uvicorn main:app --reload --port 8000
```

The API will be available at **http://localhost:8000**  
Swagger docs at **http://localhost:8000/docs**

---

### Frontend Setup

```bash
# Navigate to frontend
cd frontend

# Install dependencies
npm install

# Start dev server
npm run dev
```

The UI will be available at **http://localhost:3000**

---

## 📡 API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/upload` | Upload a document (PDF/JPG/PNG) |
| `POST` | `/process-document/{file_id}` | Start processing pipeline |
| `GET`  | `/status/{job_id}` | Check processing status |
| `GET`  | `/results/{job_id}` | Get structured results |
| `GET`  | `/download/{job_id}?format=json\|csv\|excel` | Download output file |

---

## 🔄 Processing Pipeline

```
Upload → PDF Conversion → OpenCV Preprocessing → OCR (Tesseract + EasyOCR)
                                                         ↓
              Excel/CSV/JSON ← Output Generation ← NLP (spaCy) ← Table Extraction
                                                         ↓
                                              Document Classification
```

**Stages:**
1. **Load/Convert** — PDF pages to images, extract embedded images
2. **Preprocess** — Grayscale, denoise, threshold, skew correction
3. **OCR** — Dual-engine: Tesseract (printed) + EasyOCR (handwritten)
4. **Table Extraction** — Tabula for PDFs, text parsing for images
5. **NLP** — spaCy NER: persons, dates, amounts, organizations
6. **Classification** — Keyword-based: invoice, resume, form, report, letter
7. **Output** — JSON, CSV, multi-sheet Excel

---

## 🎨 Frontend Features

- **Drag & drop** file upload with format validation
- **Real-time progress** tracking with animated status bar
- **Extracted text** viewer with expand/collapse and copy
- **Entity display** with color-coded NLP results
- **Dynamic tables** with tab navigation for multi-table documents
- **Image gallery** with lightbox for page and embedded images
- **One-click downloads** for JSON, CSV, and Excel formats
- **Dark theme** with glassmorphism design

---

## 🧪 Testing

Place sample documents in `backend/test_data/` and use either:
- The **frontend UI** at http://localhost:3000
- The **Swagger docs** at http://localhost:8000/docs
- **curl**:
  ```bash
  # Upload
  curl -X POST http://localhost:8000/upload -F "file=@test_data/sample_invoice.pdf"
  
  # Process (use file_id from upload response)
  curl -X POST http://localhost:8000/process-document/{file_id}
  
  # Check status
  curl http://localhost:8000/status/{job_id}
  
  # Download results
  curl http://localhost:8000/download/{job_id}?format=json -o results.json
  ```

---

## ⚙️ Configuration

Edit `backend/config.py` to customize:
- `TESSERACT_CMD` — Path to Tesseract binary
- `POPPLER_PATH` — Path to Poppler binaries
- `MAX_FILE_SIZE` — Maximum upload size (default: 50 MB)
- `DPI_FOR_PDF` — PDF rendering resolution (default: 300)
- `MAX_PAGES` — Maximum PDF pages to process (default: 50)
- `CORS_ORIGINS` — Allowed frontend origins

---

## 📦 Tech Stack

| Layer | Technology |
|-------|-----------|
| Backend | FastAPI, Python 3.9+ |
| Frontend | Next.js 15, React 19, TypeScript |
| Styling | Tailwind CSS 4 |
| OCR | Tesseract, EasyOCR |
| Computer Vision | OpenCV |
| NLP | spaCy |
| Table Extraction | Tabula-py |
| PDF Processing | pdf2image, PyMuPDF |
| Data Export | Pandas, openpyxl |
