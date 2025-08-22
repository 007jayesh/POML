# 🚀 POML (Prompt Orchestration Markup Language): Microsoft new markup method for prompt engineering.

## Project Structure

```
POML/
├── app.py                 # Main Streamlit application
├── requirements.txt       # Python dependencies
├── venv/                 # Virtual environment
└── README.md             # This file
```

## Quick Start

### 1. Set up Virtual Environment
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Run the Streamlit App
```bash
streamlit run app.py
```

The application will open in your default browser at `http://localhost:8501`

## About POML

POML (Prompt Orchestration Markup Language) is Microsoft's innovative markup language for structured prompt engineering with Large Language Models. It provides:

- **Structured Components**: XML-like syntax for organized prompts
- **Rich Data Integration**: Support for images, tables, and complex data
- **Template Engine**: Variables, loops, and conditionals
- **Professional Tooling**: VS Code extension and SDK support

## 🎮 Enhanced AI-Powered Demo Features

The interactive demo includes revolutionary AI integration:

### 🤖 AI Playground
- **Live AI Execution**: Direct integration with Google Gemini 2.5 Pro
- **Real-time POML Processing**: Execute structured prompts and see immediate results
- **Template Library**: Quick-start templates for various domains
- **Conversation History**: Track interactions and AI responses
- **Response Analytics**: Analyze AI output quality metrics

### 🔄 POML vs Plain Text Comparison
- **Side-by-side Testing**: Compare structured vs unstructured prompts
- **Quality Metrics**: Structure, clarity, and specificity scoring
- **Performance Analysis**: Quantitative proof of POML's effectiveness
- **Visual Insights**: Charts and graphs showing improvement

### 🎨 Creative Examples Gallery
- **Creative Writing Assistant**: Story development and character creation
- **Data Storyteller**: Transform metrics into executive narratives  
- **Learning Companion**: Educational content with analogies
- **Business Strategy Advisor**: Strategic recommendations and analysis
- **Character Development**: Rich personality and background creation

### 📊 Analytics Dashboard
- **Usage Metrics**: Track your prompt engineering sessions
- **Response Trends**: Word count and quality over time
- **Word Clouds**: Visualize AI response themes
- **Execution Logs**: Detailed history of all interactions

### 🛠️ Advanced Features
- **Syntax Validation**: Real-time POML error checking
- **Live Preview**: See rendered output as you type
- **Template Management**: Save and load custom POML templates
- **Export Capabilities**: Download conversation logs and analytics

## 🔧 Technical Implementation

### 🏗️ Architecture
The enhanced Streamlit app features:
- **Google AI Integration**: Direct connection to Gemini 2.5 Pro model
- **Custom POML Renderer**: Advanced parser with AI execution capabilities
- **Real-time Analytics**: Plotly visualizations and metrics tracking
- **Interactive UI**: Modern interface with multiple specialized pages
- **Quality Analysis Engine**: Prompt effectiveness measurement tools

### 🤖 AI Integration
```python
# Google Gemini Configuration
import google.generativeai as genai
genai.configure(api_key=os.getenv('GOOGLE_API_KEY'))
model = genai.GenerativeModel('gemini-2.5-pro-preview-03-25')

# POML-to-AI Pipeline
renderer = POMLRenderer()
response = renderer.execute_with_ai(poml_content, user_input)
```

### 📊 Advanced Components
- **PromptAnalyzer**: Quality metrics calculation
- **CreativeExamples**: Domain-specific template library  
- **Analytics Engine**: Usage tracking and visualization
- **Comparison Engine**: Side-by-side prompt testing
- **Conversation Manager**: Session history and context

## 🎯 Usage Examples

### Basic AI-Powered POML
```xml
<poml>
  <role>Expert data scientist and storytelling specialist</role>
  <task>Transform metrics into compelling executive narratives</task>
  <example>
    Good narrative: "Our 40% user growth isn't just a number—it signals 
    product-market fit finally clicking."
  </example>
  <output-format>
    <h3>📈 Key Insight</h3>
    <p>Main finding with business impact</p>
    <h3>💡 Strategic Implication</h3>  
    <p>What this means for decision makers</p>
    <h3>🎯 Recommended Action</h3>
    <p>Specific next steps</p>
  </output-format>
</poml>
```

### Creative Template with Variables
```xml
<poml>
  <let name="genre" value="science fiction" />
  <let name="mood" value="mysterious" />
  
  <role>Bestselling {{genre}} author known for {{mood}} storylines</role>
  <task>Create an engaging opening paragraph for a short story</task>
  <example>
    Effective opening: "The coffee cup trembled in Sarah's hands, not from 
    fear, but from electricity that shouldn't exist."
  </example>
  <output-format>
    <h3>Opening Paragraph</h3>
    <p>Compelling first paragraph (100-150 words)</p>
    <h3>Character Notes</h3>
    <p>Brief character background and motivation</p>
  </output-format>
</poml>
```

### Advanced Analytics Template
```xml
<poml>
  <role>Senior strategy consultant with digital transformation expertise</role>
  <task>Analyze business scenario and provide strategic recommendations</task>
  <output-format>
    <h2>🎯 Strategic Priority</h2>
    <p>Primary recommendation with rationale</p>
    <h2>📋 Action Plan</h2>
    <list>
      <item>Phase 1: Immediate actions (0-3 months)</item>
      <item>Phase 2: Core implementation (3-9 months)</item>
      <item>Phase 3: Optimization (9-12 months)</item>
    </list>
  </output-format>
</poml>
```


### 🔑 Environment Configuration
```bash
# Required Environment Variables
GOOGLE_API_KEY=your_gemini_api_key_here
GEMINI_MODEL=gemini-2.5-pro-preview-03-25

```


## 🤝 Contributing & Enhancement Ideas

### 🎯 High-Impact Contributions
- **🤖 Additional AI Models**: Integration with Claude, GPT-4, or other LLMs
- **📊 Advanced Analytics**: More sophisticated quality metrics and insights
- **🎨 Template Gallery**: Domain-specific POML templates
- **🔧 Enhanced Rendering**: Better syntax validation and error handling
- **📱 Mobile Optimization**: Responsive design improvements
- **🔒 Security Features**: Enhanced API key management and validation

### 🛠️ Development Workflow
```bash
# Development setup
git clone [repository-url]
cd POML
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
pip install -r dev-requirements.txt  # Additional dev tools
streamlit run app.py --server.runOnSave true
```

## Resources

- [Official POML Documentation](https://microsoft.github.io/poml/latest/)
- [POML GitHub Repository](https://github.com/microsoft/poml)
- [VS Code Extension](https://marketplace.visualstudio.com/items?itemName=ms-toolsai.poml)
