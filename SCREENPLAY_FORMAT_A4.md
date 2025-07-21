# A4 Screenplay Formatting Documentation

## Overview
The Visual Novel Node Editor now exports PDFs using **professional screenplay formatting standards** optimized for A4 paper size.

## Screenplay Format Specifications

### Page Setup (A4)
- **Page Size**: A4 (210 × 297 mm)
- **Top Margin**: 1 inch (25.4 mm)
- **Bottom Margin**: 1 inch (25.4 mm)  
- **Left Margin**: 1.5 inches (38.1 mm) - Standard screenplay
- **Right Margin**: 1 inch (25.4 mm)

### Element Formatting

#### 1. Scene Headings (SLUG LINES)
- **Font**: THSarabunNew, 12pt
- **Position**: Left-aligned, full width
- **Format**: `INT./EXT. LOCATION - TIME`
- **Spacing**: 24pt before, 12pt after
- **Style**: ALL UPPERCASE

**Example:**
```
INT. COFFEE SHOP - DAY
EXT. สวนสาธารณะ - บ่าย
```

#### 2. Action/Description Lines
- **Font**: THSarabunNew, 12pt
- **Position**: Full width (no indentation)
- **Spacing**: 12pt before and after
- **Style**: Normal case, descriptive
- **Note**: Background descriptions from scene settings are excluded from PDF format for cleaner screenplay appearance

**Example:**
```
เธอเดินเข้ามาในร้าน มองหาที่นั่ง
พวกเขานั่งลงที่โต๊ะข้างหน้าต่าง
```

#### 3. Character Names
- **Font**: THSarabunNew, 12pt
- **Position**: 2.2 inches from left margin
- **Spacing**: 12pt before, 0pt after
- **Style**: UPPERCASE

**Example:**
```
                    สมชาย
                    JOHN
```

#### 4. Parentheticals
- **Font**: THSarabunNew, 11pt
- **Position**: 1.8 inches from left, 2 inches from right
- **Spacing**: 0pt before and after
- **Style**: Lowercase in parentheses

**Example:**
```
                 (มองไปที่นาฬิกา)
                 (looking at watch)
```

#### 5. Dialog
- **Font**: THSarabunNew, 12pt
- **Position**: 1 inch from left, 1.5 inches from right
- **Spacing**: 0pt before, 12pt after
- **Line Height**: 16pt (enhanced for Thai text)

**Example:**
```
              วันนี้อากาศดีจัง ขอกาแฟร้อนหนึ่งแก้วครับ
              The weather is nice today. One hot coffee, please.
```

#### 6. Transitions

**IN Transitions (Before Scene Heading)**
- **Font**: THSarabunNew, 12pt
- **Position**: Left-aligned, full width
- **Spacing**: 12pt before and after
- **Style**: UPPERCASE with colon
- **Placement**: Before scene heading (SLUG LINE)

**OUT Transitions (After Scene Content)**
- **Font**: THSarabunNew, 12pt
- **Position**: Right-aligned
- **Spacing**: 12pt before, 24pt after
- **Style**: UPPERCASE with colon
- **Placement**: After scene content, before next scene

**Examples:**
```
FADE IN:
INT. LOCATION - TIME

[Scene content here]

                                                      CUT TO:

DISSOLVE IN:
EXT. NEW LOCATION - TIME
```

**Supported Transitions:**
- **IN**: FADE IN:, DISSOLVE IN:, CUT IN:, FADE FROM BLACK:
- **OUT**: CUT TO:, DISSOLVE TO:, FADE OUT:, FADE TO BLACK:

## Thai Language Support

### Font Features
- **Primary Font**: THSarabunNew (all variants)
- **Unicode Support**: Full Thai character set
- **Diacritic Support**: Proper vowel and tone mark rendering
- **Line Spacing**: Optimized for Thai text (16pt for dialog)

### Text Processing
- **Normalization**: Unicode NFC normalization
- **Character Handling**: Proper Thai vowel and tone positioning
- **Mixed Text**: Seamless Thai-English integration

## Export Features

### Automatic Formatting
- ✅ Scene headings converted to SLUG LINE format
- ✅ Character names automatically uppercase
- ✅ Proper indentation for all elements
- ✅ Standard screenplay spacing
- ✅ Professional page layout
- ✅ IN transitions before scene headings (left aligned)
- ✅ OUT transitions after scene content (right aligned)
- ✅ Proper transition sequencing

### Content Processing
- ✅ Node sequence processing
- ✅ Scene transitions included
- ✅ Background descriptions excluded (cleaner format)
- ✅ Dialog with parentheticals support
- ✅ Action lines from node content included
- ✅ Proper scene numbering

### Quality Assurance
- ✅ Industry-standard margins
- ✅ Consistent typography
- ✅ Professional appearance
- ✅ Print-ready output
- ✅ Thai text optimization

## Usage

### Export Process
1. Open Visual Novel Node Editor
2. Create or edit your node sequence
3. Go to File → Export → PDF Screenplay
4. Choose filename and location
5. PDF generates with professional formatting

### File Output
- **Format**: PDF (A4)
- **Quality**: Print-ready
- **Compatibility**: All PDF readers
- **Font Embedding**: Included for portability

## Benefits

### Professional Standard
- 📄 Follows industry screenplay formatting
- 🎬 Suitable for film/video production
- 📝 Print-ready for script reading
- 🌐 International A4 standard

### Thai Language Excellence
- 🇹🇭 Optimized for Thai script
- ✨ Perfect diacritic rendering
- 📖 Excellent readability
- 🔤 Mixed language support

### Technical Advantages
- ⚡ Fast ReportLab generation
- 💾 Compact file sizes
- 🔧 No external dependencies
- 🖨️ High-quality output

## Sample Output

The exported PDF will look like a professional screenplay with:
- Proper scene headings
- Correctly indented character names
- Well-formatted dialog blocks
- Action descriptions at full width
- Right-aligned transitions
- Professional Thai typography

This formatting standard ensures your visual novel screenplay looks professional and follows industry conventions while maintaining excellent Thai language support.
