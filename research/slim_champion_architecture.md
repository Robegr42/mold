# SlimChampionAgent Architecture

The `SlimChampionAgent` is a streamlined, high-accuracy pipeline designed for Small Language Models (SLMs). It combines Retrieval-Augmented Generation (RAG), cognitive reasoning hints, and a Two-Pass execution strategy to maximize extraction quality while minimizing the latency and cost associated with larger ensembles.

## Workflow Diagram

```mermaid
graph TD
    %% Input Node
    Input[Input: Task & Target Schema] --> AugPhase

    %% Augmentation Phase
    subgraph AugPhase [1. Augmentation Phase]
        direction TB
        
        subgraph RAG [RAG Module Detail]
            RAG_Input[Task: Instruction + Text] --> RAG_Emb[SentenceTransformer Embedding]
            RAG_Emb --> RAG_FAISS[FAISS Vector Search L2]
            RAG_FAISS --> RAG_TopK[Top-K Retrieval]
            RAG_TopK --> RAG_Output[Semantic Few-Shot Examples]
        end

        subgraph Architect [Architect Module Detail]
            Arch_Input[Task + Target Schema] --> Arch_Analysis[Schema Analysis]
            Arch_Analysis --> Arch_Distill[Constraint Distillation]
            Arch_Distill --> Arch_Tips[Strategic Tip Generation]
            Arch_Tips --> Arch_Output[Reasoning Hints]
        end
    end

    %% Pass 1
    RAG_Output --> Pass1
    Arch_Output --> Pass1
    Input --> Pass1

    subgraph Pass1 [2. Pass 1: Cognitive Analysis]
        direction TB
        P1_Prompt[Construct Analysis Prompt]
        P1_Inv[Apply InvariantPromptMixin]
        P1_LLM[LLM: Step-by-Step Reasoning]
        
        P1_Prompt --> P1_Inv --> P1_LLM
    end

    %% Pass 2
    P1_LLM -- "Reasoning Output (Analysis)" --> Pass2
    Input --> Pass2

    subgraph Pass2 [3. Pass 2: Strict Extraction]
        direction TB
        P2_Prompt[Construct Extraction Prompt]
        P2_Inv[Apply InvariantPromptMixin]
        P2_LLM[LLM: JSON Extraction]
        
        P2_Prompt --> P2_Inv --> P2_LLM
    end

    %% Final Output
    P2_LLM --> FinalOutput[Final Structured JSON Output]

    %% Styling
    style AugPhase fill:#f9f,stroke:#333,stroke-width:2px
    style Pass1 fill:#bbf,stroke:#333,stroke-width:2px
    style Pass2 fill:#bfb,stroke:#333,stroke-width:2px
    style FinalOutput fill:#fff,stroke:#333,stroke-width:4px
```

## Deep Dive: Augmentation Mechanics

### Retrieval-Augmented Generation (RAG)
The RAG module utilizes a local vector database to provide the SLM with high-quality, relevant context:
*   **Vectorization**: The `SentenceTransformer` (specifically the `all-MiniLM-L6-v2` model) converts the input task instruction and text into a high-dimensional query vector. This model is chosen for its optimal balance of speed and semantic representation.
*   **Similarity Search**: `FAISS` (Facebook AI Similarity Search) performs a local L2 distance calculation between the query vector and pre-computed embeddings of the training dataset. This allows for near-instant retrieval of context without external API calls.
*   **Contextual Injection**: The `Top-K` results (most semantically similar examples) are formatted into the prompt as few-shot examples, demonstrating successful extraction patterns to the model.

### Architect Module
The `ArchitectModule` acts as a "Schema Expert" that generates strategic hints *before* the main extraction begins:
*   **Schema Analysis**: It performs a deep dive into the target JSON schema to identify complex structures, data types, and specific validation constraints.
*   **Constraint Distillation**: It translates technical schema requirements into natural language instructions that are more easily digestible for an SLM.
*   **Strategic Tip Generation**: It generates proactive reasoning hints (e.g., "Distinguish between physical addresses and mailing addresses") to steer the model's focus toward high-risk or ambiguous extraction areas, effectively pre-calculating a roadmap for the reasoning phase.

## Component Overview

### 1. Augmentation Phase
Before any reasoning occurs, the agent enriches the context with two types of external knowledge:
- **RAG Module**: Retrieves the most relevant `k` few-shot examples from the training set. This provides the model with "in-context learning" samples that demonstrate the desired extraction format and style.
- **Architect Module**: Generates high-level strategic "hints" (e.g., "Look for temporal markers", "Distinguish between location and organization"). These hints guide the model's focus during the reasoning phase.

### 2. Pass 1: Cognitive Analysis
The goal of this pass is **reasoning without constraints**.
- **Unconstrained Analysis**: The model is asked to perform a step-by-step analysis in a specific reasoning language (e.g., Spanish). This forces the model to use more "cognitive cycles" on the problem before attempting to format the output.
- **Invariant Injection**: The `InvariantPromptMixin` adds critical rules like the "Extract-or-Null" instruction, ensuring the model remains grounded in the text even during analysis.

### 3. Pass 2: Strict Extraction
The goal of this pass is **syntax-constrained formatting**.
- **Contextual Extraction**: The model receives the original input text AND the detailed analysis produced in Pass 1.
- **Strict Schema Enforcement**: Using the `json_schema` response format, the model maps its previously generated reasoning into the final structured format.
- **Final Invariants**: Re-applies the "Extract-or-Null" rule to ensure that if the reasoning identified a field as missing, it is correctly output as `null` in the JSON.

## Key Benefits
- **Lower Latency**: By avoiding multiple ensemble rounds or complex auditing loops, it remains fast enough for production SLM use.
- **Higher Grounding**: The "Null Rule" invariant significantly reduces hallucinations by giving the model a safe exit when data is missing.
- **Cross-Lingual Reasoning**: Reasoning in a different language than the target output can sometimes bypass linguistic biases in the model's training data.
