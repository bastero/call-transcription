"""Prompt templates for Claude analysis."""

ANALYSIS_PROMPT = """
I have a transcript from a meeting/call. Please analyze it and provide:

1. **Meeting Summary** (2-3 sentences)
   - What was the overall purpose and outcome?

2. **Key Discussion Points**
   - List the main topics discussed
   - Include important decisions made

3. **Action Items**
   - Extract specific tasks mentioned
   - Identify who is responsible (if mentioned)
   - Note any deadlines

4. **Context & Insights**
   - Important context or background mentioned
   - Notable concerns or risks raised
   - Opportunities identified

5. **Follow-up Recommendations**
   - What should happen next?
   - Any unresolved questions?

Here's the transcript:

{transcript}

Please be specific and reference speakers or participants when relevant.
"""

SENTIMENT_PROMPT = """
Analyze the sentiment and tone of this conversation:
- Overall mood (positive, neutral, negative, mixed)
- Each speaker's engagement level
- Any tension or disagreement
- Collaborative vs. combative dynamics

Transcript:

{transcript}
"""

TECHNICAL_PROMPT = """
Extract technical details from this conversation:
- Technical decisions made
- Architecture or design choices discussed
- Technologies mentioned
- Technical challenges or blockers
- Implementation approach agreed upon

Transcript:

{transcript}
"""

BUSINESS_PROMPT = """
Analyze this call from a business perspective:
- Customer pain points mentioned
- Budget/pricing discussions
- Timeline and urgency
- Competitors mentioned
- Next steps in sales/business process
- Risks and opportunities

Transcript:

{transcript}
"""

QUICK_SUMMARY_PROMPT = """
Provide a concise 2-3 sentence summary of this conversation:

{transcript}
"""
