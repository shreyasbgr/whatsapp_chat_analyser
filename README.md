# 📱 WhatsApp Chat Analyzer

A powerful Streamlit-based web application for analyzing WhatsApp chat exports with advanced media detection, group notification filtering, and comprehensive data processing capabilities.

## 🌟 Features

### 📊 **Core Functionality**
- **File Upload**: Easy drag-and-drop interface for WhatsApp chat `.txt` files
- **User Selection**: Dropdown to analyze overall chat or specific users
- **Media Detection**: Automatic detection and classification of images, GIFs, stickers, videos, documents, and more
- **Group Notifications**: Intelligent filtering of system messages (pinned messages, user joins, etc.)
- **Data Integrity**: Maintains master DataFrame with all messages while providing clean filtered copies

### 🎯 **Data Structure**
- **Master DataFrame**: Complete dataset including all messages and system notifications
- **User Messages**: Filtered copy excluding group notifications
- **Smart Media Handling**: 
  - Text messages: `message` column filled, `media` and `media_file_name` columns empty
  - Media without captions: `message` and `media_file_name` columns empty, `media` column filled
  - Media with user captions: `message` (caption) and `media` columns filled, `media_file_name` empty
  - Media with file names: `media` and `media_file_name` columns filled, `message` empty
- **Comprehensive Metadata**: Timestamps, user info, message modifiers, and more

### 📈 **Analytics Ready**
- Clean data structure perfect for building advanced analytics
- Separate tracking of text vs. media messages
- Proper timezone handling (IST with UTC conversion)
- Extensible architecture for adding new analysis types

## 🚀 Quick Start

### Prerequisites
- Python 3.8 or higher
- pip package manager

### Installation

1. **Clone or download the repository**
   ```bash
   git clone <repository-url>
   cd whatsapp_chat_analysis
   ```

2. **Create virtual environment**
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

### Running the Application

#### **Option 1: Using the launch script (Recommended)**
```bash
chmod +x run_app.sh
./run_app.sh
```

#### **Option 2: Manual launch**
```bash
source venv/bin/activate
streamlit run app.py
```

The app will open in your browser at `http://localhost:8501`

## 📁 File Structure

```
whatsapp_chat_analysis/
├── app.py                           # Main Streamlit application
├── parser.py                        # WhatsApp chat parsing logic
├── utils.py                         # Utility functions
├── requirements.txt                 # Python dependencies
├── run_app.sh                       # Launch script
├── README.md                        # This file
├── test_app.py                      # Basic functionality tests
├── test_group_notifications.py     # Group notification tests
├── test_media_detection.py         # Media detection tests
├── test_complete_functionality.py  # Comprehensive test suite
└── venv/                           # Virtual environment (created after setup)
```

## 🧪 Testing

### **Run All Tests**
```bash
source venv/bin/activate

# Basic functionality test
python test_app.py

# Media detection test
python test_media_detection.py

# Group notification classification test
python test_group_notifications.py

# Comprehensive test suite
python test_complete_functionality.py
```

### **Expected Test Results**
- ✅ **Parser functionality**: File parsing, DataFrame creation
- ✅ **Media detection**: 134 media messages detected (images, GIFs, stickers, etc.)
- ✅ **File name handling**: 1 media with file names, 133 media without file names
- ✅ **Caption separation**: Message column contains only user-typed content
- ✅ **Group notifications**: 70 system messages properly classified
- ✅ **Data integrity**: All counts match, no data loss
- ✅ **User filtering**: 103 unique users identified

## 📱 How to Export WhatsApp Chat

### **On iPhone:**
1. Open WhatsApp and go to the chat you want to analyze
2. Tap the contact/group name at the top
3. Scroll down and tap "Export Chat"
4. Choose "Without Media" for faster processing
5. Select "Save to Files" or "Mail" to save the `.txt` file

### **On Android:**
1. Open WhatsApp and go to the chat you want to analyze
2. Tap the three dots (⋮) in the top-right corner
3. Select "More" → "Export Chat"
4. Choose "Without Media"
5. Select your preferred method to save the `.txt` file

## 🔧 Technical Details

### **Parser Features**
- **Message Pattern Recognition**: Handles standard WhatsApp export format
- **Media Type Detection**: Identifies images, videos, GIFs, stickers, documents, contacts, locations, polls
- **System Message Filtering**: Recognizes 20+ types of group notifications
- **Timezone Handling**: Converts IST to UTC with proper timezone support
- **Error Handling**: Robust parsing with graceful error recovery

### **Media Types Detected**
- `image` - Image files
- `gif` - GIF animations  
- `sticker` - WhatsApp stickers
- `video` - Video files
- `audio` - Audio files
- `voice` - Voice messages
- `document` - Document files
- `contact` - Contact cards
- `location` - Location shares
- `poll` - Polls
- `media` - General media (fallback)

### **Group Notification Types**
- Pinned/unpinned messages
- User joins via invite link
- User additions/removals
- Admin changes
- Group setting modifications
- Security notifications
- Disappearing message settings
- And more...

## 📊 Data Schema

### **DataFrame Columns**
| Column | Type | Description |
|--------|------|-------------|
| `datetime_ist` | string | ISO format timestamp in IST |
| `datetime_ist_human` | string | Human-readable timestamp |
| `datetime_utc` | string | ISO format timestamp in UTC |
| `sender` | string | Message sender name or 'group_notification' |
| `message` | string | User-typed message content or captions |
| `media` | string | Media type (empty for text messages) |
| `media_file_name` | string | File name for documents and attachments |
| `message_modifier` | string | Message edit/delete indicators |
| `group_system_message` | boolean | Whether it's a system message |
| `year` | int | Year extracted from timestamp |
| `month` | int | Month extracted from timestamp |
| `day` | int | Day extracted from timestamp |
| `hour` | int | Hour extracted from timestamp |
| `minute` | int | Minute extracted from timestamp |

### **Data Flow**
1. **Raw Chat File** → **Parser** → **Master DataFrame**
2. **Master DataFrame** → **Filter** → **User Messages DataFrame**
3. **User Messages** → **Filter** → **Filtered DataFrame** (by selected user)

## 🛠️ Customization

### **Adding New Media Types**
Edit `parser.py` and add patterns to the `media_patterns` dictionary:
```python
media_patterns = {
    # ... existing patterns ...
    r"your_pattern": "your_media_type",
}
```

### **Adding New Group Notifications**
Edit `parser.py` and add keywords to the `group_system_keywords` list:
```python
group_system_keywords = [
    # ... existing keywords ...
    "your_new_keyword",
]
```

### **Adding New Analysis Types**
The app structure is designed to be easily extensible. You can add new analysis features by:
1. Creating new analysis functions
2. Adding options to the dropdown
3. Implementing the analysis logic in `app.py`

## 🐛 Troubleshooting

### **Common Issues**

#### **"ModuleNotFoundError: No module named 'streamlit'"**
- Solution: Activate the virtual environment first
  ```bash
  source venv/bin/activate
  pip install -r requirements.txt
  ```

#### **"Error parsing file"**
- Ensure your chat export is in the correct format: `[DD/MM/YY, HH:MM:SS AM/PM] Contact Name: Message`
- Try exporting the chat again from WhatsApp
- Check if the file is corrupted or incomplete

#### **"No messages found"**
- Verify the chat file contains actual messages
- Check if the date format matches expected pattern
- Ensure the file encoding is UTF-8

### **Debug Information**
The app includes a comprehensive debug section that shows:
- Master DataFrame statistics
- Group notification counts
- Media message breakdowns
- User filtering results
- Sample data from each category

## 🔒 Privacy & Security

- **Local Processing**: All data processing happens locally on your machine
- **No Data Upload**: Chat data never leaves your computer
- **No Storage**: Messages are not stored permanently
- **Session-Based**: Data is cleared when you close the browser

## 📈 Performance

### **Typical Processing Times**
- **Small chats** (< 1,000 messages): < 1 second
- **Medium chats** (1,000-10,000 messages): 1-3 seconds
- **Large chats** (10,000+ messages): 3-10 seconds

### **Memory Usage**
- **Master DataFrame**: ~1MB per 10,000 messages
- **Filtered Views**: Minimal additional memory
- **Media Detection**: Negligible overhead

## 🤝 Contributing

We welcome contributions! Areas for improvement:
- Additional media type detection
- More group notification patterns
- Advanced analytics features
- Performance optimizations
- UI/UX enhancements

## 📄 License

This project is open source and available under the MIT License.

## 🙏 Acknowledgments

- Built with [Streamlit](https://streamlit.io/)
- Pandas for data processing
- Python's built-in `re` module for pattern matching
- WhatsApp for the standardized export format

---

**🚀 Ready to analyze your WhatsApp chats? Run `streamlit run app.py` and start exploring!**
