# 🧱 M.O.L.D.

**Micro-model Object Language Decoder**

> Dynamic JSON extraction on the fly. Your schema changes, M.O.L.D. adapts.

## 📖 Overview

**M.O.L.D.** is a lightweight Python solution designed to tame the chaos of unstructured text using Small Language Models (SLMs). It allows you to extract information into JSON format, guaranteeing that the output fits your real-time needs, even when the data schema is completely dynamic or unknown beforehand.

## ✨ Key Features

* **Zero Fine-Tuning:** Skip the expensive and time-consuming training pipelines. M.O.L.D. works out of the box with capable SLMs.
* **Dynamic Schema Resolution:** Handle unknown or user-defined schemas at runtime without breaking your application logic.
* **Type-Safe Outputs:** Native integration with Python data validation tools ensures that what you extract is  what you expect.

<!-- ## 🚀 Installation

Install M.O.L.D. via pip:

```bash
pip install mold-ai

```

## 💻 Quick Start

*(This section should contain a minimal, self-contained Python script showing how easy it is to use the library. Example below:)*

```python
from mold import MoldExtractor
from pydantic import BaseModel, Field

# 1. Initialize M.O.L.D. with your preferred SLM
extractor = MoldExtractor(model="mistral-nemo-12b")

# 2. Define a dynamic or runtime-specific schema
class UserProfile(BaseModel):
    name: str = Field(description="The full name of the person")
    skills: list[str] = Field(description="List of technical skills mentioned")

text_input = "Hey, I'm Alex. I've been coding in Python for 5 years and recently started exploring Streamlit and MongoDB."

# 3. Extract! M.O.L.D. forces the text into your schema
result = extractor.parse(text=text_input, schema=UserProfile)

print(result.json(indent=2))

``` -->

## 🧩 Integrations & Ecosystem

M.O.L.D. is designed to play nicely with your existing data science and web stacks. Whether you are building background data-cleaning pipelines, feeding a MongoDB database, or creating rapid interactive web apps with Streamlit, M.O.L.D. provides the structured data backbone you need.

## 📄 License

This project is licensed under the MIT License - see the `LICENSE` file for details.
