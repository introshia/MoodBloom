# How to Test MoodBloom on a Mobile Device

To view the local Flask development server on a mobile phone (or any other device), both the host computer (Mac) and the mobile device must be connected to the **same Wi-Fi network**.

## Step 1: Find the Host Mac's Local IP Address
Open a new terminal window in VS Code and run the following command:
\`\`\`bash
ipconfig getifaddr en0
\`\`\`
*(Note: If this returns blank, try `ipconfig getifaddr en1`. Note down the IP address it outputs, e.g., `192.168.0.25`).*

## Step 2: Start the Flask Server
By default, macOS uses Port 5000 for its AirPlay Receiver, which causes a conflict with Flask. To bypass this, we run the server on Port 5001 and expose it to the local network using `--host=0.0.0.0`.

Run this command in the project terminal:
\`\`\`bash
flask run --host=0.0.0.0 --port=5001
\`\`\`

## Step 3: View on Mobile
1. Open the web browser (Chrome, Safari, etc.) on your mobile device.
2. In the address bar, type `http://` followed by your Mac's IP address, a colon `:`, and the port `5001`.

**Example URL:**
\`\`\`text
http://192.168.0.25:5001
\`\`\`

## Troubleshooting
* **Site cannot be reached:** Double-check that both devices are on the exact same Wi-Fi network (not cellular data).
* **Port 5000 in use error:** If you prefer to use port 5000, you must turn off the AirPlay Receiver on the Mac (`System Settings > General > AirDrop & Handoff > AirPlay Receiver > Off`).