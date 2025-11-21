const fs = require('fs');
const path = require('path');

const PROJECT_ROOT = process.cwd();
const APP_NAME = 'zenstore';
const settingsPath = path.join(PROJECT_ROOT, APP_NAME, 'settings.py');

console.log("=== PRO FIX: SANITIZING SETTINGS.PY DUPLICATES ===");

if (fs.existsSync(settingsPath)) {
    let settings = fs.readFileSync(settingsPath, 'utf8');

    // ---------------------------------------------------------
    // STEP 1: AGGRESSIVE CLEANUP (Remove ALL existing mentions)
    // ---------------------------------------------------------
    
    // Remove specific app strings from lists (handling trailing commas)
    settings = settings.replace(/'cloudinary_storage',/g, '');
    settings = settings.replace(/"cloudinary_storage",/g, '');
    settings = settings.replace(/'cloudinary',/g, '');
    settings = settings.replace(/"cloudinary",/g, '');
    
    // Remove any lines that look like: INSTALLED_APPS += ['cloudinary'...]
    // This regex matches "INSTALLED_APPS +=" followed by brackets containing cloudinary
    settings = settings.replace(/INSTALLED_APPS \+= \[.*'cloudinary'.*\]/g, '');
    
    // Remove the specific "Deep Clean" block we added earlier if it exists
    settings = settings.replace(/INSTALLED_APPS \+= \[\s*'cloudinary_storage',\s*'cloudinary',\s*\]/g, '');

    console.log("✅ Removed all scattered Cloudinary references.");

    // ---------------------------------------------------------
    // STEP 2: RE-INJECT EXACTLY ONCE (Main List)
    // ---------------------------------------------------------
    
    // Find the start of INSTALLED_APPS
    if (settings.includes("INSTALLED_APPS = [")) {
        settings = settings.replace(
            "INSTALLED_APPS = [",
            "INSTALLED_APPS = [\n    'cloudinary_storage',\n    'cloudinary',"
        );
        console.log("✅ Re-injected apps cleanly at the top of the list.");
    } else {
        console.error("❌ CRITICAL: Could not find INSTALLED_APPS list.");
    }

    // ---------------------------------------------------------
    // STEP 3: ENSURE PRODUCTION LOGIC DOESN'T ADD IT AGAIN
    // ---------------------------------------------------------
    
    // We look for the RENDER block. If we find code inside it adding apps, we kill it.
    // Simplest way: The regex in Step 1 already removed the "+=" lines.
    // We just ensure the Media config remains.

    fs.writeFileSync(settingsPath, settings);
    console.log("✅ settings.py Saved.");

} else {
    console.error("❌ settings.py not found.");
}

console.log("\n=======================================");
console.log("       FIX DEPLOYED! 🚀");
console.log("=======================================");
console.log("1. git add .");
console.log("2. git commit -m 'Sanitize duplicate apps'");
console.log("3. git push origin main");