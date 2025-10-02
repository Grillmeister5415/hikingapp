import { chromium } from '@playwright/test';

(async () => {
  const browser = await chromium.launch({ headless: true });

  // Desktop screenshot
  console.log('Taking desktop screenshot...');
  const desktopContext = await browser.newContext({
    viewport: { width: 1440, height: 900 }
  });
  const desktopPage = await desktopContext.newPage();

  // Login
  await desktopPage.goto('http://localhost:8082');
  await desktopPage.fill('input[type="email"]', 'test@example.com');
  await desktopPage.fill('input[type="password"]', 'test123');
  await desktopPage.click('button:has-text("Anmelden")');
  await desktopPage.waitForTimeout(2000);

  // Navigate to trip 10
  await desktopPage.goto('http://localhost:8082/trip/10');
  await desktopPage.waitForTimeout(3000);

  // Take full page screenshot
  await desktopPage.screenshot({
    path: '/Users/fabian/WanderProject/wanderapp_backend/.playwright-mcp/elevation-desktop-full.png',
    fullPage: true
  });
  console.log('Desktop screenshot saved');

  await desktopContext.close();

  // Mobile screenshot
  console.log('Taking mobile screenshot...');
  const mobileContext = await browser.newContext({
    viewport: { width: 393, height: 852 }
  });
  const mobilePage = await mobileContext.newPage();

  // Login
  await mobilePage.goto('http://localhost:8082');
  await mobilePage.fill('input[type="email"]', 'test@example.com');
  await mobilePage.fill('input[type="password"]', 'test123');
  await mobilePage.click('button:has-text("Anmelden")');
  await mobilePage.waitForTimeout(2000);

  // Navigate to trip 10
  await mobilePage.goto('http://localhost:8082/trip/10');
  await mobilePage.waitForTimeout(3000);

  // Take full page screenshot
  await mobilePage.screenshot({
    path: '/Users/fabian/WanderProject/wanderapp_backend/.playwright-mcp/elevation-mobile-full.png',
    fullPage: true
  });
  console.log('Mobile screenshot saved');

  await mobileContext.close();
  await browser.close();
})();
