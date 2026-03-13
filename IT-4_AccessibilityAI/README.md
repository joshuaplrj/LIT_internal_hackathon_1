# IT-4: AccessibilityAI — Automated WCAG 2.2 Compliance Auditor

## Overview

Build an **AI-powered web accessibility auditing tool** that automatically scans websites for WCAG 2.2 Level AA compliance.

## Requirements

| Requirement | Target |
|---|---|
| Pages to scan | Up to 10,000 |
| WCAG criteria | All 50 Level AA |
| Processing time | < 60 min for 1000 pages |
| False positive rate | < 10% |
| Auto-fix rate | ≥ 30% of issues |

## WCAG 2.2 Level AA Categories

1. **Perceivable**: Text alternatives, captions, adaptable, distinguishable
2. **Operable**: Keyboard accessible, enough time, navigable, input modalities
3. **Understandable**: Readable, predictable, input assistance
4. **Robust**: Compatible, status messages

## Analysis Methods

### 1. Static Analysis (HTML/CSS)

```python
from bs4 import BeautifulSoup

def check_alt_text(html):
    soup = BeautifulSoup(html, 'html.parser')
    images = soup.find_all('img')
    
    issues = []
    for img in images:
        if not img.get('alt'):
            issues.append({
                'criterion': '1.1.1',
                'element': str(img),
                'severity': 'critical',
                'fix': 'Add descriptive alt text'
            })
        elif img.get('alt') == '':
            if not img.get('role') == 'presentation':
                issues.append({
                    'criterion': '1.1.1',
                    'element': str(img),
                    'severity': 'warning',
                    'fix': 'Add role="presentation" for decorative images'
                })
    
    return issues

def check_color_contrast(css, html):
    # Parse CSS for color definitions
    # Calculate contrast ratios
    # WCAG AA requires 4.5:1 for normal text, 3:1 for large text
    pass

def check_heading_structure(html):
    soup = BeautifulSoup(html, 'html.parser')
    headings = soup.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6'])
    
    issues = []
    prev_level = 0
    
    for heading in headings:
        level = int(heading.name[1])
        
        if level - prev_level > 1:
            issues.append({
                'criterion': '1.3.1',
                'element': str(heading),
                'severity': 'warning',
                'fix': f'Heading level skipped from h{prev_level} to h{level}'
            })
        
        prev_level = level
    
    return issues
```

### 2. Dynamic Analysis (Headless Browser)

```python
from playwright.sync_api import sync_playwright

def check_keyboard_navigation(url):
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()
        page.goto(url)
        
        # Check focus visibility
        focusable = page.query_selector_all('a, button, input, select, textarea, [tabindex]')
        
        issues = []
        for element in focusable:
            # Check if element is visible when focused
            element.focus()
            is_visible = page.evaluate('(el) => { const style = window.getComputedStyle(el); return style.outlineStyle !== "none" && style.outlineWidth !== "0px"; }', element)
            
            if not is_visible:
                issues.append({
                    'criterion': '2.4.7',
                    'element': element.evaluate('el => el.outerHTML'),
                    'severity': 'critical',
                    'fix': 'Add visible focus indicator'
                })
        
        browser.close()
    
    return issues

def check_aria_roles(url):
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()
        page.goto(url)
        
        # Check for ARIA roles
        elements_with_role = page.query_selector_all('[role]')
        
        issues = []
        valid_roles = ['alert', 'button', 'checkbox', 'dialog', 'link', 'menu', 'menuitem', 'navigation', 'radio', 'search', 'tab', 'tabpanel', 'textbox']
        
        for element in elements_with_role:
            role = element.get_attribute('role')
            if role not in valid_roles:
                issues.append({
                    'criterion': '4.1.2',
                    'element': element.evaluate('el => el.outerHTML'),
                    'severity': 'warning',
                    'fix': f'Invalid ARIA role: {role}'
                })
        
        browser.close()
    
    return issues
```

### 3. Visual Analysis (ML)

```python
import torch
from PIL import Image

class ContrastChecker(torch.nn.Module):
    def __init__(self):
        super().__init__()
        self.cnn = torch.nn.Sequential(
            torch.nn.Conv2d(3, 32, 3, padding=1),
            torch.nn.ReLU(),
            torch.nn.MaxPool2d(2),
            torch.nn.Conv2d(32, 64, 3, padding=1),
            torch.nn.ReLU(),
            torch.nn.MaxPool2d(2),
            torch.nn.Flatten(),
            torch.nn.Linear(64 * 56 * 56, 128),
            torch.nn.ReLU(),
            torch.nn.Linear(2, 1),
            torch.nn.Sigmoid()
        )
    
    def forward(self, x):
        return self.cnn(x)

def check_visual_contrast(screenshot_path):
    model = ContrastChecker()
    model.load_state_dict(torch.load('contrast_model.pth'))
    model.eval()
    
    image = Image.open(screenshot_path)
    # Process image regions
    # Return contrast issues
    pass
```

### 4. Screen Reader Simulation

```python
def simulate_screen_reader(html):
    soup = BeautifulSoup(html, 'html.parser')
    
    # Remove non-visible elements
    for element in soup.find_all(style=re.compile(r'display:\s*none|visibility:\s*hidden')):
        element.decompose()
    
    # Extract text in reading order
    reading_order = []
    
    # Main content
    main = soup.find('main') or soup.find(role='main')
    if main:
        reading_order.extend(extract_text(main))
    
    # Navigation
    nav = soup.find('nav') or soup.find(role='navigation')
    if nav:
        reading_order.insert(0, ('navigation', extract_text(nav)))
    
    # Check for meaningful sequence
    issues = []
    if not is_meaningful_sequence(reading_order):
        issues.append({
            'criterion': '1.3.2',
            'severity': 'warning',
            'fix': 'Content order may not be meaningful when read by screen reader'
        })
    
    return reading_order, issues
```

## Auto-Fix Generation

```python
def generate_fix(issue, html):
    if issue['criterion'] == '1.1.1':  # Missing alt text
        # Use ML to generate alt text
        alt_text = generate_alt_text_with_ml(issue['element'])
        return f'Add alt="{alt_text}" to image'
    
    elif issue['criterion'] == '1.4.3':  # Low contrast
        # Suggest color adjustments
        current_color = extract_color(issue['element'])
        suggested_color = adjust_for_contrast(current_color)
        return f'Change color from {current_color} to {suggested_color}'
    
    elif issue['criterion'] == '2.4.7':  # No focus indicator
        return 'Add CSS: :focus { outline: 2px solid #005fcc; }'
    
    # ... more fix generators
```

## Deliverables

1. **Tool Source Code**: Complete implementation
2. **Architecture Document**: Design and methodology
3. **Test Results**: On 5 provided websites
4. **Precision/Recall**: Per WCAG criterion

## Project Structure

```
IT-4_AccessibilityAI/
├── README.md
├── crawler/
│   ├── spider.py
│   └── sitemap.py
├── analyzers/
│   ├── static.py
│   ├── dynamic.py
│   ├── visual.py
│   └── screen_reader.py
├── models/
│   ├── contrast_checker.py
│   └── alt_text_generator.py
├── fixer/
│   ├── patch_generator.py
│   └── templates/
├── report/
│   ├── generator.py
│   └── templates/
├── audit.py
└── solution_template.py
```

## Tips

1. Start with static analysis - it's fast and catches many issues
2. Dynamic analysis catches issues that only appear after JavaScript execution
3. Visual analysis is needed for contrast and text-in-images
4. Screen reader simulation helps verify reading order
5. Auto-fix generation is challenging - start with simple fixes
