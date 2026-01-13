"""Claude API integration for transcript analysis."""

import anthropic
import os
from typing import Dict, Optional
from .prompts import ANALYSIS_PROMPT


class ClaudeAnalyzer:
    """Handles transcript analysis using Claude API."""

    def __init__(self, api_key: Optional[str] = None, model: str = "claude-3-haiku-20240307"):
        """
        Initialize Claude analyzer.

        Args:
            api_key: Anthropic API key (reads from env if None)
            model: Claude model to use
        """
        self.api_key = api_key or os.getenv("ANTHROPIC_API_KEY")
        if not self.api_key:
            raise ValueError("ANTHROPIC_API_KEY not found in environment variables")

        self.model = model
        self.client = anthropic.Anthropic(api_key=self.api_key)
        print(f"✓ Claude API client initialized (model: {model})")

    def analyze_transcript(self, transcript: str, custom_prompt: Optional[str] = None) -> str:
        """
        Analyze a transcript using Claude.

        Args:
            transcript: The transcript text to analyze
            custom_prompt: Custom analysis prompt (uses default if None)

        Returns:
            Claude's analysis as a string
        """
        prompt = custom_prompt or ANALYSIS_PROMPT

        # Format the prompt with the transcript
        full_prompt = prompt.format(transcript=transcript)

        print("🤖 Sending transcript to Claude for analysis...")

        try:
            message = self.client.messages.create(
                model=self.model,
                max_tokens=4096,
                messages=[
                    {"role": "user", "content": full_prompt}
                ]
            )

            analysis = message.content[0].text
            print("✓ Analysis complete")
            return analysis

        except Exception as e:
            print(f"❌ Error calling Claude API: {e}")
            raise

    def analyze_with_context(self, transcript: str, context: Dict) -> str:
        """
        Analyze transcript with additional context.

        Args:
            transcript: The transcript text
            context: Dictionary with context info (meeting_type, participants, etc.)

        Returns:
            Claude's analysis
        """
        context_str = "\n".join([f"- {k}: {v}" for k, v in context.items()])

        custom_prompt = f"""
I have a transcript from a meeting/call with the following context:

{context_str}

Please analyze the transcript and provide:

1. **Meeting Summary** (2-3 sentences)
2. **Key Discussion Points**
3. **Action Items** (with responsible parties if mentioned)
4. **Context & Insights**
5. **Follow-up Recommendations**

Transcript:

{{transcript}}
"""
        return self.analyze_transcript(transcript, custom_prompt)

    def quick_summary(self, transcript: str) -> str:
        """
        Get a quick summary without detailed analysis.

        Args:
            transcript: The transcript text

        Returns:
            Brief summary
        """
        prompt = """
Please provide a brief 2-3 sentence summary of this conversation:

{transcript}
"""
        return self.analyze_transcript(transcript, prompt)


def test_claude():
    """Test Claude API connection."""
    try:
        analyzer = ClaudeAnalyzer()
        print("Claude API client initialized successfully")
    except Exception as e:
        print(f"Error initializing Claude: {e}")


if __name__ == "__main__":
    test_claude()
