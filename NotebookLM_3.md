**Objective:**
Phase 3: Final Prompt Generation. Your task is to take the **Podcast Blueprint** you just created and convert it into a single, perfect prompt for Google's NotebookLM.

**Core Directive:**
Your entire output must be a single block of text, starting with "Hello NotebookLM,". This output is not for you to execute; it is designed to be copied and pasted directly into NotebookLM. Do not include any extra conversational text, explanations, or formatting like code blocks around your response.

---

### **Requirements for the NotebookLM Prompt:**

Your generated prompt must incorporate the best practices for creating a high-quality audio overview in NotebookLM. It must include:

1.  **Clear Identity and Audience:** Start by telling NotebookLM what it is and for whom it is creating the content.
2.  **Language Specification:** Explicitly define the language of the podcast (German or English), matching the blueprint. Use a clear and direct phrase.
3.  **Strict Time Constraint:** Reiterate the hard 8-minute time limit for the entire audio overview.
4.  **Dialogue Format Instruction:** Instruct NotebookLM to adopt a conversational format between two distinct personas: an **Expert** and a **Curious Student**.
5.  **Inclusion of the Blueprint:** The core of your prompt will be the dialogue outline from the blueprint you created. You must embed the key talking points and the flow of the conversation directly into the prompt.
6.  **Source Referencing Instruction:** Instruct NotebookLM to base its explanations *strictly* on the provided source materials (slides and transcript) and to use them to flesh out the talking points you provide. This is crucial for accuracy.
7.  **Tone and Style:** Specify a tone that is clear, engaging, and educational, avoiding overly complex jargon.

---

### **Example of a Perfect Output (Based on the Previous Blueprint Example):**

Hello NotebookLM,

Please generate an audio overview based on my uploaded sources. Your primary task is to create a study podcast with the following strict parameters:

**1. Language and Audience:** The podcast is for a German-speaking university student. The entire dialogue must be in German.

**2. Format:** The format must be a conversation between two speakers:
    *   **Speaker 1 (The Expert):** Explains concepts clearly and accurately based on the provided sources.
    *   **Speaker 2 (The Curious Student):** Asks clarifying questions to guide the conversation and make it easier to follow.

**3. Strict Time Limit:** The total duration of the podcast must not exceed 8 minutes. You must be concise and focus only on the most critical information outlined below.

**4. Podcast Script and Structure:**
You must follow this conversational structure. Use my uploaded slides and transcript to provide the actual content for the expert's talking points.

*   **Introduction (~45 seconds):**
    *   The student asks what the main goal of the first lecture is.
    *   The expert explains that the goal is to build a foundation and defines what an information system is, referencing slides 3-4.

*   **Main Topic 1: The Three Core Perspectives (~3 minutes):**
    *   The expert introduces the three-level model (Technology, Organization, Management) from slide 8.
    *   The student asks for a breakdown of each level.
    *   The expert defines the Technology perspective based on slide 9.
    *   The expert defines the Organization perspective based on slide 10.
    *   The expert defines the Management perspective and emphasizes that all three must work together for success, based on slide 11.

*   **Main Topic 2: Data, Information, and Knowledge (~2.5 minutes):**
    *   The student asks for the practical difference between these terms.
    *   The expert clearly defines "Data" and "Information" using the examples from slide 6.
    *   The student then asks about "Knowledge".
    *   The expert explains knowledge as the ability to use information for decisions, using the concepts from slide 7.

*   **Conclusion (~1 minute):**
    *   The student asks for the single most important takeaway from the lecture.
    *   The expert concludes by stating that an information system is a socio-technical system and that the integration of all three perspectives is key to creating value, as mentioned on slide 12.

**Final Instruction:** Please begin generating the audio overview now. Adhere strictly to the structure, roles, language, and time limit.

---

**Your Command:**

Now, generate the final NotebookLM prompt based on the blueprint you created. Ensure the output is a single block of text and follows all the requirements listed above.