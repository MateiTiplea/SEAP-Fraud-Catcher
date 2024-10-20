# SEAP-Fraud-Catcher Chrome Extension

## Features
- Automatically extracts auction details (bidder, contracting authority, and purchase value) from e-licitatie.ro.
- Stores data using Chrome's local storage for persistence.
- Displays extracted data in a popup interface.
- Runs in the background and listens for page changes to trigger data extraction.
- Simple and easy-to-use UI with cleanly formatted data.

## Installation

### Steps to Load the Extension in Chrome:
1. Download the extension source code from this repository.
2. Open Chrome and navigate to `chrome://extensions/`.
3. Enable **Developer mode** by toggling the switch in the top-right corner.
4. Click on **Load unpacked** and select the folder where you saved the extension code.
5. The extension will now appear in your list of extensions, and the SEAP-Fraud-Catcher icon will be visible in the toolbar.

## How it Works

### Manifest (`manifest.json`)
The extension uses **Manifest V3** to specify its behavior and required permissions:
- `popup.html` is defined as the default popup for the extension, displaying auction data.
- Background scripts (`background.js`) handle communication between the content script and the popup.
- Content scripts (`content.js`) are injected into the auction pages and extract the required data (bidder, authority, purchase details).

### Content Script (`content.js`)
The content script scrapes auction details from the e-licitatie.ro direct acquisition page. It retrieves:
- **Bidder name and CIF**
- **Contracting authority name and CIF**
- **Purchase name, description, and estimated value**

Once collected, these details are saved in Chrome’s local storage and passed to the popup via messaging.

### Background Script (`background.js`)
The background script listens for messages from the content script and forwards them to the popup when it's opened. If the popup is closed, it logs that information cannot be displayed.

### Popup (`popup.js` and `popup.html`)
The popup displays the auction details collected by the content script. Data from local storage is retrieved and shown in a formatted way. The UI is automatically updated when new data is received.

## Running the Extension
1. After loading the extension, visit a direct acquisition page on [e-licitatie.ro](https://www.e-licitatie.ro/pub).
2. The content script will automatically extract the relevant data.
3. Click the SEAP-Fraud-Catcher icon in the toolbar to view the auction details in the popup.

## Permissions
The extension requires the following permissions:
- Access to `https://www.e-licitatie.ro/pub/direct-acquisition/view/*` to extract auction details.
- `activeTab` and `scripting` to interact with the page and collect data.
- `storage` to save the extracted data locally.

