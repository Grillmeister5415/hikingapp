import { chromium } from '@playwright/test';

(async () => {
  const browser = await chromium.launch();
  const context = await browser.newContext({ viewport: { width: 1440, height: 900 } });
  const page = await context.newPage();

  // Login
  await page.goto('http://localhost:8082');
  await page.fill('input[type="email"]', 'test@example.com');
  await page.fill('input[type="password"]', 'test123');
  await page.click('button:has-text("Anmelden")');

  // Wait for navigation after login
  await page.waitForTimeout(2000);

  // Navigate to hiking trips
  await page.goto('http://localhost:8082/hiking');
  await page.waitForTimeout(1000);

  // Click on the first trip
  const firstTrip = await page.locator('.trip-card').first();
  await firstTrip.click();
  await page.waitForTimeout(2000);

  // Scroll to elevation profile if it exists
  await page.evaluate(() => {
    const profile = document.querySelector('.elevation-profile-container');
    if (profile) profile.scrollIntoView({ behavior: 'smooth', block: 'center' });
  });
  await page.waitForTimeout(1000);

  // Take desktop screenshot
  await page.screenshot({ path: '.playwright-mcp/elevation-profile-desktop.png', fullPage: true });
  console.log('Desktop screenshot saved');

  // Switch to mobile viewport
  await page.setViewportSize({ width: 393, height: 852 });
  await page.waitForTimeout(500);

  // Scroll to elevation profile again
  await page.evaluate(() => {
    const profile = document.querySelector('.elevation-profile-container');
    if (profile) profile.scrollIntoView({ behavior: 'smooth', block: 'center' });
  });
  await page.waitForTimeout(1000);

  // Take mobile screenshot
  await page.screenshot({ path: '.playwright-mcp/elevation-profile-mobile.png', fullPage: true });
  console.log('Mobile screenshot saved');

  await browser.close();
})();
