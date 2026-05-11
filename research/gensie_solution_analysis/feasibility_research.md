# Feasibility Research Report: Proposed GenSIE Solution

Based on the analysis of the proposed pipeline and the GenSIE shared task constraints (including the Hosted Inference architecture detailed in Section 6.2 of the task description), here are the findings regarding the feasibility of the proposed solution:

## 1. Compliance of `llguidance` in Docker with "Hosted Inference" Architecture
**Finding:** Not Compliant / Infeasible

**Analysis:** 
The GenSIE shared task utilizes a **"Hosted Inference"** architecture (Section 6.2). In this setup, the organizers provide an external inference server (typically exposing an OpenAI-compatible API), and the participant's Docker container connects to this server to generate responses. 
Libraries like `llguidance` perform constrained decoding by directly manipulating the token logits during the model's generation loop. Because the model weights and the generation process reside on the remote hosted server rather than inside the participant's Docker container, participants do not have access to the model's logits. Consequently, it is technically impossible to use `llguidance` client-side within the Docker container to constrain the remotely hosted LLM. 

## 2. Permissibility of MiniLM and FAISS inside the Offline Docker Container
**Finding:** Allowed (with conditions)

**Analysis:**
The use of custom libraries (e.g., FAISS) and small localized embedding models (e.g., MiniLM) is generally permissible within the offline Docker container. 
However, because the Docker container operates in an **offline** environment during evaluation (meaning no internet access is available at runtime except for the connection to the hosted inference API), all dependencies, libraries, and model weights (like the MiniLM weights) **must be pre-downloaded and baked into the Docker image** during the build phase. As long as these assets are self-contained within the image and comply with any overall container size limits set by the organizers, their inclusion is allowed and functional.

## 3. Viability of Multiple ReAct Loops and Ensembling against Resource Constraints
**Finding:** Highly Risky / Likely Infeasible

**Analysis:**
The proposed architecture relies heavily on multiple ReAct (Reasoning and Acting) loops and ensembling. These techniques require numerous sequential and parallel calls to the LLM per document to iterate through reasoning steps and aggregate multiple predictions.
In a shared task environment with hosted inference, there are typically strict **time limits per instance**, **API rate limits**, and **token consumption boundaries**. 
- **Time Constraints:** Multiple round-trips to an external API introduce significant network latency and sequential generation delays, likely exceeding the maximum allowed processing time per document.
- **Token Constraints:** ReAct loops inherently consume a large portion of the context window with intermediate reasoning steps, which might surpass the SLM's token limits (e.g., 8k context) or the allowed budget.
Therefore, a pipeline relying on heavy ensembling and multiple ReAct loops will struggle to respect the task's time and token resource constraints. A more streamlined, single-pass or optimized two-pass approach is strongly recommended.
