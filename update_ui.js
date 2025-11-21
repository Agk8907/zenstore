const fs = require('fs');
const path = require('path');

const PROJECT_ROOT = process.cwd();
const APP_NAME = 'zenstore';
const settingsPath = path.join(PROJECT_ROOT, APP_NAME, 'settings.py');

console.log("=== APPLYING ABSOLUTE STATIC FILE FIX ===");

if (fs.existsSync(settingsPath)) {
    let settings = fs.readFileSync(settingsPath, 'utf8');

    // ---------------------------------------------------------
    // STEP 1: CLEANUP (Remove ANY existing static/media config)
    // ---------------------------------------------------------
    // We wipe the slate clean to ensure no conflicting lines exist.
    settings = settings.replace(/^STATIC_URL = .*$/gm, '');
    settings = settings.replace(/^STATIC_ROOT = .*$/gm, '');
    settings = settings.replace(/^STATICFILES_DIRS = .*$/gm, '');
    settings = settings.replace(/^STATICFILES_STORAGE = .*$/gm, '');
    settings = settings.replace(/^MEDIA_URL = .*$/gm, '');
    settings = settings.replace(/^MEDIA_ROOT = .*$/gm, '');
    settings = settings.replace(/^DEFAULT_FILE_STORAGE = .*$/gm, '');
    settings = settings.replace(/^CLOUDINARY_STORAGE = \{[\s\S]*?\}/gm, '');
    
    // Remove middleware if it was added messily before
    settings = settings.replace(/'whitenoise.middleware.WhiteNoiseMiddleware',/g, '');
    settings = settings.replace(/"whitenoise.middleware.WhiteNoiseMiddleware",/g, '');

    // ---------------------------------------------------------
    // STEP 2: RE-INJECT MIDDLEWARE (Crucial Position)
    // ---------------------------------------------------------
    // WhiteNoise MUST be directly after SecurityMiddleware
    if (settings.includes("SecurityMiddleware")) {
        settings = settings.replace(
            /('django\.middleware\.security\.SecurityMiddleware',)/,
            "$1\n    'whitenoise.middleware.WhiteNoiseMiddleware',"
        );
        console.log("✅ WhiteNoise Middleware injected correctly.");
    } else {
        console.error("⚠️ Could not find SecurityMiddleware to place WhiteNoise!");
    }

    // ---------------------------------------------------------
    // STEP 3: APPEND THE "GOLD STANDARD" CONFIG
    // ---------------------------------------------------------
    const finalConfig = `
# ==============================================
# FINAL STATIC & MEDIA CONFIGURATION
# ==============================================
import os

# 1. STATIC FILES (CSS/JS)
STATIC_URL = '/static/'
# Where Django looks for your CSS files locally
STATICFILES_DIRS = [
    os.path.join(BASE_DIR, 'static'),
]
# Where Django puts them for production (Render)
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')

# 2. STORAGE ENGINE (WhiteNoise for CSS, Cloudinary for Images)
if 'RENDER' in os.environ:
    # --- PRODUCTION ---
    # Use WhiteNoise to compress and serve CSS/JS
    STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'
    
    # Use Cloudinary for uploaded images
    DEFAULT_FILE_STORAGE = 'cloudinary_storage.storage.MediaCloudinaryStorage'
    CLOUDINARY_STORAGE = {
        'CLOUD_NAME': os.environ.get('CLOUDINARY_CLOUD_NAME'),
        'API_KEY': os.environ.get('CLOUDINARY_API_KEY'),
        'API_SECRET': os.environ.get('CLOUDINARY_API_SECRET'),
    }
else:
    # --- LOCALHOST ---
    MEDIA_URL = '/images/'
    MEDIA_ROOT = os.path.join(BASE_DIR, 'static/images')
`;

    fs.writeFileSync(settingsPath, settings + "\n" + finalConfig);
    console.log("✅ Settings completely rewritten for Static/Media stability.");

} else {
    console.error("❌ settings.py not found.");
}

// ---------------------------------------------------------
// STEP 4: VERIFY BUILD SCRIPT
// ---------------------------------------------------------
const buildPath = path.join(PROJECT_ROOT, 'build.sh');
const buildScript = `#!/usr/bin/env bash
# Exit on error
set -o errexit

# Install dependencies
pip install -r requirements.txt

# CRITICAL: Collect static files
echo "Running Collectstatic..."
python manage.py collectstatic --no-input --clear

# Apply migrations
python manage.py migrate
`;
fs.writeFileSync(buildPath, buildScript);
console.log("✅ build.sh updated to force clean collectstatic.");

console.log("\n=======================================");
console.log("       FIX DEPLOYED! 🚀");
console.log("=======================================");
console.log("1. git add .");
console.log("2. git commit -m 'Absolute Static File Fix'");
console.log("3. git push origin main");