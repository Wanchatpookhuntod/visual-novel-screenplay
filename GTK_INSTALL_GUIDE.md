# PDF Generation Information

## Current PDF Engine: ReportLab Only

The Visual Novel Node Editor now uses **ReportLab exclusively** for PDF generation. WeasyPrint has been completely removed to simplify dependencies and improve Windows compatibility.

## Benefits of ReportLab
- ✅ No external dependencies (pure Python)
- ✅ Excellent Windows compatibility  
- ✅ Great Thai font support with THSarabunNew
- ✅ Stable and reliable PDF generation
- ✅ No GTK runtime requirements

## Installation
```bash
pip install reportlab
```

## Font Support
The application uses THSarabunNew fonts from the `font/` folder for optimal Thai text rendering in PDFs.

---

## Legacy WeasyPrint Information (No Longer Used)

*The following information is kept for reference only. WeasyPrint is no longer used in this application.*
