# Render Native Runtime Build Setup (No Docker)

## Problem
Render's Python buildpack doesn't support `apt-get` system package installation via `Aptfile`. This means the old approach of listing system packages in an `Aptfile` won't work on Render's native Python runtime. We need to use a static Tesseract binary instead.

## Solution: Static Tesseract Binary

Instead of installing Tesseract via system packages, we download a pre-compiled static binary during the build process.

### Step 1: Configure Render Build Command

In your Render dashboard:

1. Go to **Settings > Build & Deploy**
2. Find **Build Command** field
3. Replace with:

```bash
pip install -r requirements.txt && \
mkdir -p bin tessdata && \
curl -L https://github.com/DanielMYT/tesseract-static/releases/download/v5.4.1/tesseract.x86_64 -o bin/tesseract && \
chmod +x bin/tesseract && \
curl -L https://github.com/tesseract-ocr/tessdata/raw/main/eng.traineddata -o tessdata/eng.traineddata
```

**What this does:**
- Creates `bin/` and `tessdata/` directories in your project root
- Downloads static Tesseract v5.4.1 binary (~20MB)
- Downloads English language training data (~8MB)
- Makes the binary executable

**Optional: Add More Languages**

If you need additional language support, add more lines to the build command:

```bash
# French
curl -L https://github.com/tesseract-ocr/tessdata/raw/main/fra.traineddata -o tessdata/fra.traineddata && \

# German  
curl -L https://github.com/tesseract-ocr/tessdata/raw/main/deu.traineddata -o tessdata/deu.traineddata && \

# Spanish
curl -L https://github.com/tesseract-ocr/tessdata/raw/main/spa.traineddata -o tessdata/spa.traineddata
```

Then use in Python:
```python
pytesseract.image_to_string(image, lang='fra')  # French
pytesseract.image_to_string(image, lang='deu')  # German
pytesseract.image_to_string(image, lang='spa')  # Spanish
pytesseract.image_to_string(image, lang='eng+fra')  # Multiple languages
```

### Step 2: Update requirements.txt

Ensure these packages are in your `requirements.txt`:

```
pytesseract==0.3.10
Pillow
opencv-python-headless==4.8.1.78
```

### Step 3: Code Configuration (Already Done)

The backend code already has the correct configuration in `backend/services/qwen_service.py`:

```python
# Configure pytesseract to use static binary from Render build
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TESSERACT_CMD = os.path.join(PROJECT_ROOT, 'bin', 'tesseract')
TESSDATA_DIR = os.path.join(PROJECT_ROOT, 'tessdata')

if os.path.exists(TESSERACT_CMD):
    pytesseract.pytesseract.tesseract_cmd = TESSERACT_CMD
    os.environ['TESSDATA_PREFIX'] = TESSDATA_DIR
```

This automatically finds and uses the static binary downloaded during the build.

### Step 4: Deploy

1. Commit your code:
   ```bash
   git add backend/services/qwen_service.py requirements.txt
   git commit -m "feat: Use static tesseract binary for Render native runtime"
   git push origin main
   ```

2. Render will automatically trigger a new build
3. Monitor the build logs to see:
   - "Installing tesseract..." 
   - Successful curl downloads
4. Once deployed, test by uploading a receipt

## Testing

### Local Testing
```bash
# Runs on system tesseract
python -m pytest test/test_receipt_api.py -v
```

### Production Testing on Render

1. **Via API:**
   ```bash
   curl -X POST https://sentinel-o0yb.onrender.com/api/transactions/receipt-upload \
     -H "Authorization: Bearer YOUR_JWT_TOKEN" \
     -F "file=@receipt.jpg"
   ```
   
   Expected response should include merchant name (not "Unknown Merchant")

2. **Via Telegram Bot:**
   - Send a receipt photo to your bot
   - Should process and recognize merchant
   - Should show: "✅ Merchant – ₦Amount (Category)"

3. **Check Render Logs:**
   ```
   ✅ Using static tesseract binary: /project/bin/tesseract
   ✅ OCR extracted 150 characters
   ✅ Successfully parsed receipt: {merchant: "...", amount: ..., category: "..."}
   ```

## Troubleshooting

### Error: "tesseract is not installed or it's not in your PATH"

**Cause:** Build command didn't run or binary download failed

**Fix:**
1. Check Render build logs - look for "curl" commands
2. Verify binary exists: Run in backend shell `ls -lh bin/tesseract`
3. Check file size - should be ~20MB
4. Redeploy by pushing a code change

### OCR Returns Empty Text

**Cause:** Binary exists but tessdata directory missing

**Fix:**
1. Verify `tessdata/eng.traineddata` exists (~4MB)
2. If missing, check build logs for curl errors
3. Manually re-run build or redeploy

### Slow Build Times

The static binary approach adds ~30 seconds to build time due to downloads. This is normal and can't be avoided with the native runtime. The upside is no need for Docker or custom buildpacks.

## Comparison: Aptfile vs Static Binary

| Approach | Aptfile | Static Binary |
|----------|---------|---|
| **Requires** | Custom buildpack or Docker | Standard Python buildpack |
| **Runtime** | System tesseract in PATH | Download during build |
| **Build Speed** | Faster | ~30s slower (downloads) |
| **Size** | ~50MB installed | ~20MB binary + ~8MB data |
| **Works on Render Free Tier** | ✅ (with buildpack) | ✅ Yes |
| **Maintenance** | Depends on system packages | Update binary URL if needed |

## Alternative: Docker Approach (If You Switch)

If you later want to use Docker instead of native runtime:

1. Uncomment the `Dockerfile` at project root (currently in `backend/`)
2. Set Render environment to Docker (not Python)
3. Add `Aptfile` to project root with system packages
4. Render will use `RUN apt-get` instead of curl

For now, the static binary approach is simplest and most reliable for free tier.

## File Structure After Build

After successful deployment, your Render instance will have:

```
project/
├── bin/
│   └── tesseract              (executable binary, ~20MB)
├── tessdata/
│   ├── eng.traineddata        (English data, ~4MB)
│   └── [other languages if added]
├── backend/
│   ├── services/
│   │   ├── qwen_service.py    (configured to use static binary)
│   │   └── ...
│   └── ...
└── ...
```

This structure allows OCR to work on production Render deployments without system package dependencies.
