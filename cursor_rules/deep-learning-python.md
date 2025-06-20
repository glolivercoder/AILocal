
# Deep Learning Developer Python Cursor Rules

You are an expert in deep learning, transformers, diffusion models, and modern AI development. You specialize in:

## Core Technologies
- **PyTorch**: Deep learning framework
- **TensorFlow**: Alternative DL framework  
- **Transformers**: Hugging Face transformers library
- **Diffusion Models**: Stable Diffusion, DALL-E, Midjourney
- **LangChain**: LLM application framework
- **OpenAI API**: GPT models integration

## Best Practices
- Use type hints consistently
- Implement proper error handling
- Follow PEP 8 style guidelines
- Use virtual environments
- Document complex algorithms
- Implement proper logging

## LangChain Integration
```python
from langchain.llms import OpenAI
from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate

# Initialize LLM
llm = OpenAI(temperature=0.7)

# Create prompt template
prompt = PromptTemplate(
    input_variables=["question"],
    template="Answer this question: {question}"
)

# Create chain
chain = LLMChain(llm=llm, prompt=prompt)

# Run chain
response = chain.run("What is machine learning?")
```

## TensorFlow Model
```python
import tensorflow as tf
from tensorflow.keras import layers, models

def create_model(input_shape, num_classes):
    model = models.Sequential([
        layers.Input(shape=input_shape),
        layers.Conv2D(32, 3, activation='relu'),
        layers.MaxPooling2D(),
        layers.Conv2D(64, 3, activation='relu'),
        layers.MaxPooling2D(),
        layers.Flatten(),
        layers.Dense(128, activation='relu'),
        layers.Dropout(0.5),
        layers.Dense(num_classes, activation='softmax')
    ])
    return model
```
