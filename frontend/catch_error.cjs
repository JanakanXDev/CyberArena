const { chromium } = require('playwright');

(async () => {
  try {
    const browser = await chromium.launch();
    const page = await browser.newPage();
    
    page.on('console', msg => {
      if (msg.type() === 'error' || msg.type() === 'warning') {
        console.log(`[${msg.type().toUpperCase()}] ${msg.text()}`);
      }
    });
    
    page.on('pageerror', error => {
      console.log(`[UNCAUGHT EXCEPTION] ${error.message}`);
    });
    
    page.on('requestfailed', request => {
      console.log(`[REQUEST FAILED] ${request.url()} - ${request.failure().errorText}`);
    });

    console.log("Navigating to http://localhost:5173 ...");
    await page.goto('http://localhost:5173', { waitUntil: 'networkidle', timeout: 10000 });
    console.log("Waiting 3 seconds for React to mount...");
    await page.waitForTimeout(3000);
    
    await browser.close();
  } catch (err) {
    console.error("Script error:", err);
  }
})();
