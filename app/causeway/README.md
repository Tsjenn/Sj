# Causeway — shipping the same app to the App Store and Google Play

The app is the folder `site/causeway/`. It is a Progressive Web App and it
is already live at https://tsjenn.github.io/Sj/causeway/ — on iPhone use
Share → Add to Home Screen, on Android Chrome offers Install. No accounts,
no cost, works offline. That is the version to send people today.

This folder wraps the same files as a native app when the owner decides
to pay for store listings. Nothing here has been run yet; it is the
scaffold, and the steps below are what remain.

## Accounts and costs (checked September 2026)

| Store | Cost | Gate |
|---|---|---|
| Apple App Store | US$99 a year, Apple Developer Program | Review; guideline 4.1 rejects copycats (this app is not one) |
| Google Play | US$25 once | A personal account created after Nov 2023 must run a closed test with **12 testers opted in continuously for 14 days** before production access. Budget 3–4 weeks. Organisation accounts (a registered business) are exempt. |

## Building without a Mac (the owner has an iPad)

1. `npm install` in this folder, then `npx cap add ios` and `npx cap add android`
   (any Linux/Windows machine or a cloud shell can do this part).
2. Commit the generated `ios/` and `android/` folders.
3. Sign up for **Codemagic** (free tier: 500 macOS build minutes a month) or
   **Capawesome Cloud**. Point it at this repo, workflow type Capacitor.
   It builds and signs the `.ipa` on its own Mac and can upload straight to
   TestFlight / App Store Connect; submission is then finished in a browser.
4. Android builds do not need a Mac; the same service produces the `.aab`.

## Before submitting

- Change `appId` in `capacitor.config.json` if the bundle id should differ.
- Privacy labels: the app collects nothing. The only network request is
  the exchange-rate fetch to api.frankfurter.app; declare it as "not
  linked to the user". No analytics, no accounts.
- Store listing copy must not use "accountant", "tax consultant" or
  "auditor" (Accountants Act 1967 s.22), and must not claim user numbers
  or outcomes that have not happened.
- Screenshots: take them from the live PWA at 390×844 in both themes.
