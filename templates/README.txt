SAFARI INVOICE (Windows app)

ONE-TIME SETUP (needs Node.js from nodejs.org, LTS version)
1. Open this folder in Command Prompt.
2. Run:  npm install
3. Try it:  npm start
4. Build the Windows app:  npm run dist
   The finished files appear in the "dist" folder:
   - "Safari Invoice <version>.exe" (portable, no install needed)
   - "Safari Invoice Setup <version>.exe" (installer)

LOGO
Put your logo in the same folder as the app and name it logo.png
(logo.jpg, logo.svg or logo.webp also work). The app loads it every time it opens.
- Portable app: same folder as the portable .exe
- Installed app: the install folder (C:\Users\<you>\AppData\Local\Programs\Safari Invoice)
- While testing with npm start: this project folder
Replace the file any time to change the logo.

SAVING INVOICES
"Print or save as PDF" opens a Save dialog and writes an A4 PDF.
Your company details and last invoice are remembered between launches.

TANZANIA / VAT
Invoice type, VAT rate (18% Mainland, 15% Zanzibar, 0%, or not VAT registered), TIN, VRN and
an EFD receipt number field are all on the form. Tick the box on a line to charge VAT on it.
Choose whether the prices you type include or exclude VAT.
