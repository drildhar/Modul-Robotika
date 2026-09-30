const { chromium } = require('playwright-core');
const OUT = process.argv[2];
(async () => {
  const b = await chromium.launch({ executablePath: 'C:/Program Files/Google/Chrome/Application/chrome.exe', headless: true });
  const p = await b.newPage({ viewport: { width: 1280, height: 900 } });
  await p.goto('https://code.pybricks.com', { waitUntil: 'networkidle', timeout: 90000 });
  await p.waitForTimeout(3000);
  await p.click('button[aria-label=Close]');
  // draw red boxes + numbered badges around locators, screenshot, remove
  const shot = async (name, marks) => {
    await p.mouse.move(1275, 5); await p.waitForTimeout(1200);
    for (const [i, loc] of marks.entries()) {
      const r = await loc.boundingBox();
      await p.evaluate(({ r, n }) => {
        const d = document.createElement('div'); d.className = 'cc-mark';
        Object.assign(d.style, { position: 'fixed', left: r.x - 5 + 'px', top: r.y - 5 + 'px', width: r.width + 10 + 'px', height: r.height + 10 + 'px', border: '4px solid #e3120b', borderRadius: '8px', zIndex: 99999, pointerEvents: 'none', boxSizing: 'border-box' });
        const s = document.createElement('div'); s.textContent = n;
        Object.assign(s.style, { position: 'absolute', right: '-16px', top: '-16px', width: '28px', height: '28px', borderRadius: '50%', background: '#e3120b', color: '#fff', font: 'bold 16px/28px sans-serif', textAlign: 'center' });
        d.appendChild(s); document.body.appendChild(d);
      }, { r, n: String(i + 1) });
    }
    await p.screenshot({ path: `${OUT}/${name}.png` });
    await p.evaluate(() => document.querySelectorAll('.cc-mark').forEach(e => e.remove()));
  };
  const btn = (l) => p.locator(`button[aria-label="${l}"]`);
  const dlg = p.getByRole('dialog');
  const next = () => p.getByRole('button', { name: 'Next', exact: true });

  // close settings drawer if open so step 1 shows the gear clearly
  const drawerOpen = await p.locator('text=Install Pybricks Firmware').isVisible();
  if (drawerOpen) { await btn('Settings').click(); await p.waitForTimeout(800); }
  await shot('01-tombol-settings', [btn('Settings')]);
  await btn('Settings').click();
  await shot('02-menu-install-firmware', [p.getByText('Install Pybricks Firmware')]);
  await p.getByText('Install Pybricks Firmware').click();
  await p.check('input[value=inventorhub]', { force: true });
  await shot('03-pilih-inventor-hub', [p.locator('label:has(input[value=inventorhub])'), next()]);
  await next().click();
  await shot('04-setujui-lisensi', [dlg.locator('label:has(input[type=checkbox])'), next()]);
  await p.check('[role=dialog] input[type=checkbox]', { force: true });
  await next().click();
  await dlg.locator('input[type=text]').fill('Kancil');
  await shot('05-beri-nama-hub', [dlg.locator('input[type=text]'), next()]);
  await next().click();
  await p.setViewportSize({ width: 1280, height: 1000 });
  await shot('06-mode-update-dan-install', [p.getByRole('button', { name: 'Install', exact: true })]);
  await p.setViewportSize({ width: 1280, height: 900 });
  await p.keyboard.press('Escape'); await p.waitForTimeout(800);
  if (await dlg.count()) await dlg.locator('button[aria-label=Close]').first().click().catch(() => {});

  await p.getByText('Restore Official LEGO').click();
  await p.check('input[value=inventorhub]', { force: true }).catch(() => {});
  await shot('07-restore-firmware-lego', [p.getByText('Restore Official LEGO').first(), next()]);
  await b.close();
})();
