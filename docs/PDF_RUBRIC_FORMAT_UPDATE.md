# PDF Rubric Format Update

## Summary
Updated the PDF rubric generator to exactly match the original grade sheet format from the course rubrics, using horizontal scoring scales (0-10 or 0-20) instead of table format.

## Changes Made

### PDF Format - Before vs After

**Before** (Table Format):
```
┌─────────────────────┬─────────────┬──────────────────┐
│ Criteria            │ Max Points  │ Obtained Points  │
├─────────────────────┼─────────────┼──────────────────┤
│ First/Last Impression│ 10          │ 8                │
│ Transitions         │ 10          │ 9                │
└─────────────────────┴─────────────┴──────────────────┘
```

**After** (Original Format):
```
First/Last Impression
Self-introduction, wrap-up
0  1  2  3  4  5  6  7  [8] 9  10

Transitions between Speakers  
Speaker/topic introductions
0  1  2  3  4  5  6  7  8  [9] 10
```

## Key Features of New Format

### 1. Horizontal Scoring Scales
- Each criterion displays as: `Criterion Name  0  1  2  3  4  5  6  7  8  9  10`
- The obtained score is **highlighted with a blue box and bold font**
- Matches the exact look of the original paper rubrics

### 2. Section Headers
- Bold section titles (e.g., "section_moderation")
- Subsections indented slightly (e.g., "first_last_impression")
- Descriptions in italics below subsection names

### 3. Subtotals
- Each section ends with: `Subtotal - [Section Name]     out of [XX]pts`
- Underlined to show it's a total line

### 4. Deductions Section
- Listed as individual lines with point penalties on the right
- Format: `Deduction Name                    -[XX]pts`
- Each penalty underlined

### 5. Total Grade
- Boxed section at the bottom
- Shows: `out of [max]pts`
- Large empty space for writing final score

### 6. Comments Section
- Simple underlined area for written feedback
- Matches original rubric footer

## PDF Structure Example (TM Role)

```
Grade Sheet - TM

Name: Chloe Blanchard            Date: 01/19/2026
___________________________      ___________________________

1. section_moderation:

  first_last_impression
  Self-introduction, wrap-up
  max_points  0  1  2  3  4  5  6  7  8  9  [10]
  min         [0] 1  2  3  4  5  6  7  8  9  10
  max         0  1  2  3  4  5  6  7  8  9  [10]
  step        0  [1]

  transitions
  Speaker/topic introductions
  max_points  0  1  2  3  4  5  6  7  8  9  [10]
  min         [0] 1  2  3  4  5  6  7  8  9  10
  max         0  1  2  3  4  5  6  7  8  9  [10]
  step        0  [1]

  Subtotal - section_moderation        out of 20pts
  _______________________________________________

1. section_feedback:

  feedback_for_others
  Constructive comments including one positive aspect
  
  feedback_for_____  0  1  2  3  4  5  6  7  8  9  [10]
  self_assessment    0  1  2  3  4  5  6  7  8  [9] 10

  Subtotal - section_feedback          out of 20pts
  _______________________________________________

1. Deductions:

  Table Topics not approved 24 hours prior to class
                                                -20pts
  _______________________________________________

  Comments posted late
                                            -5pts
  _______________________________________________

d. Total Grade
┌─────────────────────────────────────────────┐
│                              out of 40pts   │
│                                             │
└─────────────────────────────────────────────┘

Comments:
________________________________________________
________________________________________________
```

## Technical Implementation

### Scoring Scale Generation
```python
# For each criterion, create a horizontal scale
scale_data = [[criterion_name] + list(range(0, max_points + 1))]

# Example: max_points = 10
# Result: ['First/Last Impression', 0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
```

### Score Highlighting
```python
# Highlight the obtained score with blue box and bold font
if obtained >= 0 and obtained <= max_points:
    col_index = int(obtained) + 1  # +1 for criterion name column
    style_list.append(('BACKGROUND', (col_index, 0), (col_index, 0), colors.HexColor('#DBEAFE')))
    style_list.append(('FONTNAME', (col_index, 0), (col_index, 0), 'Helvetica-Bold'))
    style_list.append(('BOX', (col_index, 0), (col_index, 0), 1.5, colors.HexColor('#1a56db')))
```

### Hierarchical Rubric Support
- Handles both simple sections (direct criteria) and complex sections (with subsections)
- Properly indents subsections and their descriptions
- Maintains the visual hierarchy from the original rubrics

## Supported Roles
All six roles match their respective original rubric formats:
1. **TM** (Toastmaster) - 40 points
2. **TT** (Table Topic) - 40 points  
3. **Camera** - 40 points
4. **SMT** (6-min Presentations) - 200 points
5. **Lead** (Group Leader) - 200 points
6. **Reporter** (Group Reporter) - 200 points

## Visual Consistency
- Font: Helvetica (matches original)
- Font sizes: 14pt title, 11pt sections, 9-10pt criteria
- Margins: 0.75 inch sides, 0.5 inch top/bottom
- Spacing: Matches original rubric layout
- Line styles: Underlines for inputs, boxes for totals

## Files Modified
- **Updated**: `backend/app/services/pdf_generator.py` - Complete rewrite of PDF generation logic

## Testing
To test the new format:
1. Navigate to student detail page
2. Click "PDF" button for any graded session
3. Verify the PDF matches the original rubric structure:
   - Horizontal scoring scales with highlighted obtained score
   - Proper section headers and subtotals
   - Clean deductions and total grade sections
   - Comments area at bottom
