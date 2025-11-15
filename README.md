# 📘 PDFMathTranslate -- Local PDF Translator (Gemini-powered)

This tool allows you to **translate PDFs locally** using **Google
Gemini**.\
Math formulas, tables, formatting, and structure are preserved as much
as possible.

------------------------------------------------------------------------

## 🚀 Features

-   Translate **PDF → PDF** with preserved formatting\
-   Supports **Gemini 1.5 Flash / Pro** models\
-   Local **virtual environment** support\
-   Multi-language translation\
-   Output includes **mono** and **dual** translation PDFs

------------------------------------------------------------------------

## 📂 Project Setup

### 1️⃣ Clone the Repository

``` bash
git clone https://github.com/your-username/PDFMathTranslate.git
cd PDFMathTranslate
```

------------------------------------------------------------------------

## 🐍 2️⃣ Create and Activate Virtual Environment (Recommended)

``` bash
python -m venv venv
```

### Windows:

``` bash
venv\Scripts\activate
```

### Linux / macOS:

``` bash
source venv/bin/activate
```

------------------------------------------------------------------------

## 📦 3️⃣ Install Dependencies

``` bash
pip install -r requirements.txt
```

------------------------------------------------------------------------

## 🔑 4️⃣ Configure Environment Variables

Create a `.env` file in the project root:

    GEMINI_API_KEY=your_api_key_here
    GEMINI_MODEL=gemini-1.5-flash

------------------------------------------------------------------------

## ▶️ 5️⃣ Run the Translator

### Basic command:

``` bash
python -m pdf2zh input.pdf -s gemini -li en -lo hi -o out
```

### Explanation:

  Argument      Meaning
  ------------- -----------------------------
  `input.pdf`   The source PDF
  `-s gemini`   Use Gemini translator
  `-li en`      Input language (English)
  `-lo hi`      Output language (Hindi)
  `-o out`      Output folder name (`out/`)

After running, the tool will generate:

-   `out/input-mono.pdf`
-   `out/input-dual.pdf`

------------------------------------------------------------------------

## 🧠 Tips for Faster Translation

-   Use **Gemini Flash** instead of Pro\

-   Reduce number of pages using:

    ``` bash
    -p 1-5
    ```

-   Close unused apps while running

------------------------------------------------------------------------

## 📝 License

This project is for **personal/local use only**.
