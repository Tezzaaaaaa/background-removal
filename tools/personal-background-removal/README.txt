PERSONAL BACKGROUND REMOVAL TOOL
=================================

STEP 1 — Install
-----------------
1. Unzip this folder somewhere permanent, e.g. your home folder (~/bg-removal-tool).
2. Open Terminal.
3. Run:
     cd ~/bg-removal-tool   (or wherever you put it)
     bash install.sh
   This sets up its own private Python environment (won't touch anything
   else on your Mac) and downloads the AI model (~176MB, one-time).
   It only installs onnxruntime, pillow, and numpy — lightweight, no
   compiler/build tools required.

STEP 2 — Test it
----------------
   ~/.background-removal-tool/venv/bin/python3 ~/.background-removal-tool/remove_bg.py /path/to/a/photo.jpg
It will create "photo-nobg.png" next to the original, with the background
made transparent, and pop a notification.

STEP 3 — Hook it up to right-click
-----------------------------------
See the instructions the assistant gave you in chat for creating a
Shortcuts.app Quick Action. Once set up, right-click any image in Finder
→ Quick Actions → Remove Background.
