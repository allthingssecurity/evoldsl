#!/usr/bin/env python3
"""
Quick script to test the frontend and show what's actually happening
"""

import webbrowser
import time

print("🔍 Opening browser to debug the frontend...")
print("📱 Opening: http://localhost:3000")
print("🔧 Also opening test page: http://localhost:3000/test.html")
print("")
print("🔎 To debug:")
print("1. Open browser dev tools (F12)")
print("2. Check the Console tab for JavaScript errors")
print("3. Check the Network tab to see if files are loading")
print("4. Check the Elements tab to see if React is rendering")
print("")

# Open both pages
webbrowser.open('http://localhost:3000')
time.sleep(2)
webbrowser.open('http://localhost:3000/test.html')

print("✅ Browser opened! Check the pages and dev tools.")