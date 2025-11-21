const fs = require('fs');
const path = require('path');

const PROJECT_ROOT = process.cwd();
const APP_NAME = 'store';

console.log("=== FIXING IMAGE LOADING (DEEP CLEAN) ===");

// --- 1. AGGRESSIVE SETTINGS REPAIR ---
const settingsPath = path.join(PROJECT_ROOT, 'zenstore', 'settings.py');
if (fs.existsSync(settingsPath)) {
    let settings = fs.readFileSync(settingsPath, 'utf8');

    // A. Remove ANY existing Media/Cloudinary configs to start fresh
    // This regex removes lines starting with these keywords
    settings = settings.replace(/^MEDIA_URL = .*$/gm, '');
    settings = settings.replace(/^MEDIA_ROOT = .*$/gm, '');
    settings = settings.replace(/^DEFAULT_FILE_STORAGE = .*$/gm, '');
    settings = settings.replace(/^CLOUDINARY_STORAGE = \{[\s\S]*?\}/gm, '');
    
    // B. Ensure INSTALLED_APPS has cloudinary (and remove duplicates)
    // We remove them first to ensure we can add them in the correct order
    settings = settings.replace(/'cloudinary_storage',/g, '');
    settings = settings.replace(/'cloudinary',/g, '');
    
    // Add them explicitly at the top of INSTALLED_APPS
    settings = settings.replace(
        "INSTALLED_APPS = [", 
        "INSTALLED_APPS = [\n    'cloudinary_storage',\n    'cloudinary',"
    );

    // C. Append the Clean, Correct Config
    const robustConfig = `
# ==============================================
# ROBUST MEDIA CONFIGURATION
# ==============================================
import os

# Force Cloudinary on Render
if 'RENDER' in os.environ:
    print("--- SETTINGS: CONFIGURING CLOUDINARY ---")
    
    CLOUDINARY_STORAGE = {
        'CLOUD_NAME': os.environ.get('CLOUDINARY_CLOUD_NAME'),
        'API_KEY': os.environ.get('CLOUDINARY_API_KEY'),
        'API_SECRET': os.environ.get('CLOUDINARY_API_SECRET'),
    }
    
    DEFAULT_FILE_STORAGE = 'cloudinary_storage.storage.MediaCloudinaryStorage'
    
    # Ensure we don't use local URLs
    MEDIA_URL = 'https://res.cloudinary.com/' + os.environ.get('CLOUDINARY_CLOUD_NAME') + '/'
    
else:
    print("--- SETTINGS: CONFIGURING LOCAL STORAGE ---")
    MEDIA_URL = '/images/'
    MEDIA_ROOT = os.path.join(BASE_DIR, 'static/images')
`;

    fs.writeFileSync(settingsPath, settings + "\n" + robustConfig);
    console.log("✅ settings.py scrubbed and updated.");
}

// --- 2. ADD DEBUGGING TO VIEWS.PY ---
const viewsPath = path.join(APP_NAME, 'views.py');
if (fs.existsSync(viewsPath)) {
    let views = fs.readFileSync(viewsPath, 'utf8');
    
    // We inject a print statement into the 'home' view to see what the server sees
    const debugCode = `
def home(request):
    data = get_cart_data(request)
    categories = Category.objects.all()
    
    # --- DEBUG PRINT ---
    products = Product.objects.all()[:3]
    for p in products:
        print(f"[DEBUG] Product: {p.name} | Image URL: {p.imageURL}")
    # -------------------
    
    return render(request, 'store/home.html', {'categories': categories, 'cartItems': data['cartItems']})
`;
    
    // Replace the existing home view with the debug one
    // (Using a simple replacement strategy for the function definition)
    // First, remove the old home function
    views = views.replace(/def home\(request\):[\s\S]*?return render\(request, 'store\/home\.html', \{'categories': categories, 'cartItems': data\['cartItems'\]\}\)/, "");
    
    // Add the new one at the top of views (after imports)
    views = views.replace("from django.contrib import messages", "from django.contrib import messages\n" + debugCode);

    fs.writeFileSync(viewsPath, views);
    console.log("✅ Debug logging added to home view.");
}

console.log("\n=======================================");
console.log("       READY FOR DEPLOYMENT 🚀");
console.log("=======================================");
console.log("1. Push to GitHub.");
console.log("2. Wait for Render deploy.");
console.log("3. CRITICAL: Go to Admin Panel and RE-UPLOAD the image one last time.");
console.log("4. Check Render Logs. You should see '[DEBUG] Product: ... | Image URL: https://res.cloudinary...'");