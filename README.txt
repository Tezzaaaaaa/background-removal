PERSONAL BACKGROUND REMOVAL TOOL
=================================
Status: installed and working. Right-click Quick Action confirmed working.

WHAT IT DOES
------------
Right-click any image (or multiple selected images) in Finder -> Quick
Actions -> Remove Background. A few seconds later you'll get a notification
and a new "<originalname>-nobg.png" file appears right next to each
original, with the background made transparent. Runs 100% locally, no
internet needed after the one-time model download, no account, no cost.

STEP 1 - Install (already done)
--------------------------------
1. Unzipped into ~/bg-removal-tool
2. From Terminal:
     cd ~/bg-removal-tool
     bash install.sh
   This creates a private Python environment at
   ~/.background-removal-tool/venv (doesn't touch anything else on the
   Mac) and downloads the AI model (~176MB, one-time). Only installs
   onnxruntime, pillow, numpy, and certifi -- lightweight, no compiler
   needed.

STEP 2 - Manual test (already confirmed working)
--------------------------------------------------
   ~/.background-removal-tool/venv/bin/python3 ~/.background-removal-tool/remove_bg.py /path/to/a/photo.jpg
Creates "photo-nobg.png" next to the original and pops a notification.

STEP 3 - Right-click Quick Action (already set up and working)
------------------------------------------------------------------
Set up in Shortcuts.app as a Quick Action named "Remove Background":

1. Shortcuts.app -> New Shortcut -> name it "Remove Background"
2. Info icon -> enable "Use as Quick Action" -> Show in: Finder only
   -> Workflow receives: Image files
3. Add a "Run Shell Script" action:
     Shell: /bin/zsh
     Pass Input: as arguments
     Run as Administrator: UNCHECKED (must stay off -- as admin, $HOME
     points to root's home folder instead of yours, breaking the paths)
4. Script contents (note the semicolon before "done" -- required, or it's
   a parse error):
     for f in "$@"; do "$HOME/.background-removal-tool/venv/bin/python3" "$HOME/.background-removal-tool/remove_bg.py" "$f"; done
5. Save (Cmd+S)

USAGE
-----
Right-click one or more image files in Finder -> Quick Actions -> Remove
Background.

TROUBLESHOOTING NOTES (for future reference)
----------------------------------------------
- If install.sh ever fails again with a Python version error, it's
  because Homebrew's default python3 outpaced onnxruntime's support --
  install.sh auto-detects and prefers python3.12/3.13/3.11/3.10.
- If it's an SSL "CERTIFICATE_VERIFY_FAILED" error during model download,
  remove_bg.py already uses certifi's CA bundle explicitly to avoid this.
- If a fresh install.sh run ever seems to use the wrong Python version,
  delete ~/.background-removal-tool and re-run -- install.sh uses
  `venv --clear` and verifies the interpreter version automatically.
