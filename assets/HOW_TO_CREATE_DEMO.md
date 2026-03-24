# How to Create Demo Assets

This guide shows you how to create professional demo screenshots and GIFs for OpenClaw Research Analyst.

## ✅ Already Created

### 1. Hero Screenshot (1200x630px)
📍 Location: `assets/hero-screenshot.png`
✅ Ready for GitHub README, social media, and documentation

## 🎬 Creating Demo GIF (Option 1: Recommended)

### Using asciinema + agg

1. **Install tools**:
```bash
pip3 install --user asciinema
cargo install agg  # Requires Rust, or use: brew install agg
```

2. **Record terminal session**:
```bash
cd /home/justin/openclaw-research-analyst

# Start recording
asciinema rec demo.cast

# In the recording, type these commands slowly:
clear
echo "🦞 OpenClaw Research Analyst v1.3.0"
echo ""
python3 scripts/stock_analyzer.py AAPL
echo ""
echo "✨ Try it: github.com/ZhenRobotics/openclaw-research-analyst"

# Press Ctrl+D to stop recording
```

3. **Convert to GIF**:
```bash
agg demo.cast assets/demo.gif --speed 1.5
```

4. **Optimize GIF size** (if > 5MB):
```bash
gifsicle -O3 --colors 256 assets/demo.gif -o assets/demo-optimized.gif
```

## 🎬 Creating Demo GIF (Option 2: terminalizer)

### Using terminalizer

1. **Install**:
```bash
npm install -g terminalizer
```

2. **Record**:
```bash
terminalizer record demo -c terminalizer.yml
```

3. **Render to GIF**:
```bash
terminalizer render demo -o assets/demo.gif
```

## 🎬 Creating Demo GIF (Option 3: Simple Screenshot Animation)

### Using Python (already working)

We've created a simple asciicast file at `/tmp/demo.cast`. You can:

1. **View in browser**:
```bash
# Upload to asciinema.org
asciinema upload /tmp/demo.cast
```

2. **Convert with alternative tool**:
```bash
# Using asciicast2gif (requires Docker)
docker run --rm -v $PWD:/data asciinema/asciicast2gif /tmp/demo.cast assets/demo.gif
```

## 📹 Creating Demo Video (YouTube/Twitter)

### Using OBS Studio

1. **Install OBS Studio**:
```bash
sudo apt install obs-studio  # Ubuntu/Debian
brew install obs-studio      # macOS
```

2. **Setup**:
   - Source: Window Capture (terminal)
   - Resolution: 1920x1080
   - FPS: 30

3. **Recording script**:
```bash
# Full demo (2-3 minutes)
cd openclaw-research-analyst

# 1. Introduction (15s)
clear
cat << 'EOF'
╔═══════════════════════════════════════════════════════════════╗
║   OpenClaw Research Analyst v1.3.0                           ║
║   AI-Powered Stock Analysis for US/China/HK Markets          ║
╚═══════════════════════════════════════════════════════════════╝
EOF

# 2. Installation (20s)
echo "$ npm install -g openclaw-research-analyst"
sleep 2

# 3. US Stock Analysis (45s)
echo "$ python3 scripts/stock_analyzer.py AAPL"
python3 scripts/stock_analyzer.py AAPL
sleep 5

# 4. Chinese Stock Analysis (45s)
echo "$ python3 scripts/stock_analyzer.py 002168.SZ"
python3 scripts/stock_analyzer.py 002168.SZ
sleep 5

# 5. China Market Report (30s)
echo "$ python3 scripts/cn_market_brief.py"
python3 scripts/cn_market_brief.py
sleep 3

# 6. Portfolio Management (20s)
echo "$ python3 scripts/portfolio_manager.py"
python3 scripts/portfolio_manager.py
sleep 3

# 7. Closing (10s)
echo "✨ Learn more at github.com/ZhenRobotics/openclaw-research-analyst"
```

4. **Edit** in video editor:
   - Add title cards
   - Add background music (royalty-free)
   - Add captions/subtitles
   - Export as MP4 (1080p, H.264)

## 📱 Creating Social Media Assets

### For Twitter/X (1200x675px)
```bash
# Crop hero screenshot
convert assets/hero-screenshot.png -gravity center -extent 1200x675 assets/hero-twitter.png
```

### For LinkedIn (1200x627px)
```bash
# Already perfect size!
cp assets/hero-screenshot.png assets/hero-linkedin.png
```

### For Instagram/Stories (1080x1920px)
```bash
# Create vertical version
python3 << 'EOF'
from PIL import Image, ImageDraw, ImageFont

# Create vertical image
WIDTH, HEIGHT = 1080, 1920
bg_color = "#0d1117"
img = Image.new('RGB', (WIDTH, HEIGHT), bg_color)

# Add title at top
draw = ImageDraw.Draw(img)
# ... (custom vertical layout)

img.save("assets/hero-instagram.png")
EOF
```

## 🎨 Tips for Great Demo Content

### Terminal Settings
```bash
# Use a clean, professional theme
# Recommended: Dracula, Nord, One Dark

# Large, readable font
# Size: 16-18pt
# Font: JetBrains Mono, Fira Code, Source Code Pro

# Clean prompt
export PS1='\[\033[01;32m\]$\[\033[00m\] '

# Remove clutter
clear
unset HISTFILE  # Don't save this demo session
```

### Timing
- Type slowly (0.5-1 character per 0.1s)
- Pause after commands (2-3 seconds)
- Let output finish before next command
- Keep total demo < 60 seconds for GIF
- Keep video demo < 3 minutes

### Content
- Show the "wow" feature first (8D analysis)
- Demonstrate real value (AAPL analysis)
- Show unique feature (Chinese market)
- End with clear CTA

## 📊 Current Assets

```
assets/
├── hero-screenshot.png     ✅ (1200x630px, 67KB)
├── demo.gif                ⏳ (pending - see instructions above)
├── demo.mp4                ⏳ (optional - YouTube upload)
└── HOW_TO_CREATE_DEMO.md   ✅ (this file)
```

## 🚀 Quick Start for Tomorrow's Launch

**Minimum Required:**
1. ✅ `hero-screenshot.png` (already created)
2. ⏳ `demo.gif` (follow Option 1 above, 30 minutes)

**Recommended:**
3. ⏳ `demo.mp4` (YouTube video, 1-2 hours)
4. ⏳ Social media variants (15 minutes)

**Priority:** Focus on the GIF - it's the most important for launch day engagement!

---

**Need help?** Ask in the discussion: github.com/ZhenRobotics/openclaw-research-analyst/discussions
