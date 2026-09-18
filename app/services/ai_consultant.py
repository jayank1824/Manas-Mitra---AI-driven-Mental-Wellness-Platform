import json
from typing import List, Dict, Optional
from app.config import settings

SYSTEM_PROMPT = """
You are Dr. Manas, an AI mental wellness consultant on the Manas Mitra platform. You are warm, empathetic, and highly knowledgeable about mental health.

Your expertise includes:
- Clinical psychology (CBT, DBT, ACT, mindfulness-based approaches)
- Anxiety disorders (GAD, social anxiety, panic disorder)
- Depression and mood disorders
- Stress management and burnout prevention
- Sleep hygiene and insomnia management
- Migraine and cluster headache management (relaxation techniques, trigger identification)
- Loneliness and social isolation
- Overthinking and rumination patterns
- Self-esteem and confidence building
- Grief and loss counseling
- Anger management
- PTSD awareness

Guidelines:
1. Always be empathetic, warm, and non-judgmental
2. Use active listening techniques - acknowledge feelings before offering advice
3. Provide practical, evidence-based techniques and exercises
4. For breathing exercises, guide them to the Breathing Bubble game on the platform
5. For social connection needs, suggest the Community feature and offline meetups
6. For activity-based therapy, reference their personalized activity section
7. NEVER diagnose - say "it sounds like you might be experiencing..." instead
8. For crisis situations (suicidal thoughts, self-harm), IMMEDIATELY provide:
   - National helpline: 988 Suicide & Crisis Lifeline (call or text 988)
   - Crisis Text Line: Text HOME to 741741
   - India: iCall 9152987821, Vandrevala Foundation 1860-2662-345
   - Emphasize: "Please reach out to a professional counselor or call a crisis helpline"
9. Keep responses concise but thorough (150-300 words)
10. End responses with a follow-up question or actionable next step
11. Reference platform features when appropriate (Mind Games, Activities, Community)
12. Use calming language and avoid clinical jargon when possible

IMPORTANT DISCLAIMER: Always remind users that you are an AI assistant and not a replacement for professional medical advice. Encourage them to consult with licensed mental health professionals for diagnosis and treatment.
"""

async def get_ai_response(user_message: str, chat_history: List[Dict], user_context: Optional[Dict] = None) -> str:
    """
    Get response from Gemini API for the AI consultant.
    Falls back to rule-based responses if API key is not configured.
    """
    if settings.GEMINI_API_KEY:
        try:
            from google import genai
            client = genai.Client(api_key=settings.GEMINI_API_KEY)
            
            # Build conversation history
            contents = []
            
            # Add user context if available
            context_msg = SYSTEM_PROMPT
            if user_context:
                context_msg += f"\n\nUser Context:\n- Name: {user_context.get('name', 'User')}\n"
                context_msg += f"- Wellness Score: {user_context.get('wellness_score', 'N/A')}/100\n"
                context_msg += f"- Risk Level: {user_context.get('risk_level', 'unknown')}\n"
                context_msg += f"- Interests: {', '.join(user_context.get('interests', []))}\n"
            
            # Add chat history (last 10 messages for context)
            for msg in chat_history[-10:]:
                contents.append({
                    "role": "user" if msg["role"] == "user" else "model",
                    "parts": [{"text": msg["content"]}]
                })
            
            # Add current message
            contents.append({"role": "user", "parts": [{"text": user_message}]})
            
            response = client.models.generate_content(
                model="gemini-2.5-flash",
                contents=contents,
                config={
                    "system_instruction": context_msg,
                    "temperature": 0.7,
                    "max_output_tokens": 1024
                }
            )
            return response.text
        except Exception as e:
            print(f"Gemini API error: {e}")
            return get_fallback_response(user_message)
    else:
        return get_fallback_response(user_message)


def get_fallback_response(message: str) -> str:
    """Rule-based fallback responses when Gemini API is not available."""
    message_lower = message.lower()
    
    # Crisis detection
    crisis_keywords = ["suicide", "kill myself", "end my life", "self-harm", "cutting", "don't want to live", "want to die"]
    if any(kw in message_lower for kw in crisis_keywords):
        return """🆘 I hear you, and I want you to know that you matter deeply. What you're feeling right now is temporary, even though it may not feel that way.

Please reach out to professional help immediately:
📞 **988 Suicide & Crisis Lifeline**: Call or text 988
💬 **Crisis Text Line**: Text HOME to 741741
🇮🇳 **India - iCall**: 9152987821
🇮🇳 **Vandrevala Foundation**: 1860-2662-345

You don't have to face this alone. A trained counselor is available 24/7 to listen and help. ❤️

*I am an AI assistant and not a substitute for professional mental health care. Please contact a licensed professional.*"""
    
    # Anxiety responses
    if any(kw in message_lower for kw in ["anxious", "anxiety", "worried", "panic", "nervous", "fear"]):
        return """I understand you're feeling anxious, and I want you to know that's completely valid. Anxiety is your body's natural response, but we can learn to manage it better. 💙

Here are some techniques that can help right now:

1. **4-7-8 Breathing**: Try our Breathing Bubble game! Inhale for 4 seconds, hold for 7, exhale for 8. This activates your parasympathetic nervous system.

2. **Grounding (5-4-3-2-1)**: Notice 5 things you see, 4 you hear, 3 you touch, 2 you smell, 1 you taste.

3. **Progressive Muscle Relaxation**: Tense each muscle group for 5 seconds, then release.

Would you like to tell me more about what's triggering your anxiety? Understanding the root cause can help us find the best approach for you. 🌿

*Remember: I'm an AI wellness companion. For persistent anxiety, please consult a licensed therapist.*"""
    
    # Depression responses
    if any(kw in message_lower for kw in ["depressed", "depression", "sad", "hopeless", "worthless", "empty"]):
        return """I hear you, and I want you to know that feeling this way doesn't define you. Depression can make everything feel heavy, but there are steps we can take together. 💜

Some gentle suggestions:

1. **Gratitude Practice**: Try our Gratitude Journal game - writing just 3 small things you're grateful for can shift perspective over time.

2. **Small Activities**: Even 10 minutes of your favorite hobby can help. Check your Activities section for personalized suggestions.

3. **Social Connection**: Consider joining a Community group here. Sometimes just knowing others understand helps.

4. **Movement**: A short walk, gentle stretching, or yoga can boost serotonin naturally.

What feels most manageable for you right now? We can start with the smallest step. 🌱

*I'm an AI companion. For clinical depression, please seek help from a mental health professional.*"""
    
    # Loneliness
    if any(kw in message_lower for kw in ["lonely", "alone", "isolated", "no friends", "nobody"]):
        return """Feeling lonely can be incredibly painful, and I'm glad you're reaching out. Connection is a fundamental human need. 🤗

Here's what might help:

1. **Join a Community**: Our platform has interest-based communities where you can connect with people who share your passions.

2. **Attend Meetups**: We organize offline meetups every 2 weeks - music jams, art workshops, and more. Real connections start here!

3. **Start Small**: Sometimes a simple "hello" in a community post can lead to meaningful conversations.

4. **Activity Groups**: Doing activities alongside others creates natural bonds.

Would you like me to suggest some communities based on your interests? 🌈

*I'm an AI assistant. If loneliness is severely affecting your life, consider speaking with a counselor.*"""
    
    # Sleep issues
    if any(kw in message_lower for kw in ["sleep", "insomnia", "can't sleep", "nightmares", "tired"]):
        return """Sleep issues can really affect your overall wellbeing. Let's work on improving your sleep quality. 🌙

**Sleep Hygiene Tips:**
1. Keep a consistent sleep schedule (same time every day)
2. Avoid screens 1 hour before bed
3. Try our Breathing Bubble game before bed - the 4-7-8 technique is excellent for sleep
4. Keep your room cool, dark, and quiet
5. Avoid caffeine after 2 PM
6. Try writing in the Gratitude Journal before bed - it calms racing thoughts

**Relaxation Technique:**
Body scan meditation: Starting from your toes, slowly focus on relaxing each body part upward.

How long have you been experiencing sleep difficulties? This can help me suggest more specific strategies. 😴

*For chronic insomnia, please consult a healthcare provider.*"""
    
    # Headache/Migraine
    if any(kw in message_lower for kw in ["headache", "migraine", "cluster headache", "head pain"]):
        return """I'm sorry you're dealing with headaches. They can be debilitating, but there are management strategies we can explore. 🧠

**Immediate Relief:**
1. Try our Breathing Bubble game - deep breathing can reduce headache intensity
2. Apply cold/warm compress to your forehead
3. Stay hydrated - dehydration is a common trigger
4. Rest in a dark, quiet room

**Prevention:**
1. Track your triggers (stress, food, sleep, weather)
2. Regular sleep schedule
3. Stress management through our Mind Games
4. Regular physical activity
5. Log your headaches in Daily Log to identify patterns

Do you notice any specific triggers for your headaches? Tracking them can reveal important patterns. 💊

*For chronic or severe headaches, please consult a neurologist or your primary care physician.*"""
    
    # Stress
    if any(kw in message_lower for kw in ["stress", "overwhelmed", "burned out", "burnout", "too much", "pressure"]):
        return """I can see you're under a lot of pressure. Stress can feel overwhelming, but let's break it down together. 🌊

**Quick Stress Relief:**
1. **Breathing**: Try the 4-7-8 technique in our Breathing Bubble game
2. **Move**: Even 5 minutes of stretching helps
3. **Write it out**: Brain dump everything stressing you in the Gratitude Journal

**Long-term Strategies:**
1. **Prioritize**: Make a list and tackle one thing at a time
2. **Boundaries**: It's okay to say no
3. **Activities**: Engage in your favorite hobbies daily - check your Activities section
4. **Community**: Share what you're going through - you're not alone

What's the biggest stressor in your life right now? Let's focus on that. 🎯

*If stress is significantly impacting your daily life, please consider professional counseling.*"""
    
    # Overthinking
    if any(kw in message_lower for kw in ["overthink", "overthinking", "racing thoughts", "can't stop thinking", "ruminating"]):
        return """Overthinking can feel like being trapped in a loop. Let's work on breaking that cycle. 🔄

**Techniques to Stop Overthinking:**
1. **5-4-3-2-1 Grounding**: Focus on your senses to come back to the present
2. **Set a 'Worry Window'**: Allow yourself 15 minutes to worry, then stop
3. **Focus Games**: Try our Focus Flow or Memory Match games - they redirect your attention
4. **Physical Activity**: Movement interrupts thought loops
5. **Write it down**: Journal your thoughts in the Gratitude Journal

**Cognitive Reframing:**
- Ask: "Will this matter in 5 years?"
- Challenge: "Is this thought a fact or an opinion?"
- Replace: Turn "What if it goes wrong?" into "What if it goes right?"

What thoughts tend to loop for you most? Understanding the pattern helps break it. 🧘

*For persistent rumination, cognitive behavioral therapy (CBT) with a professional is highly effective.*"""
    
    # Greeting
    if any(kw in message_lower for kw in ["hello", "hi", "hey", "good morning", "good evening", "namaste"]):
        return """Hello! Welcome to your wellness consultation. 🙏 I'm Dr. Manas, your AI mental wellness companion.

I'm here to:
- 💬 Listen to what's on your mind
- 🧠 Share evidence-based wellness techniques
- 🎯 Guide you to helpful platform features
- 📊 Discuss your wellness progress

How are you feeling today? Feel free to share anything - there's no judgment here. 🌿

*Remember: I'm an AI assistant. For professional diagnosis and treatment, please consult a licensed mental health professional.*"""
    
    # Default
    return f"""Thank you for sharing that with me. I want to make sure I understand you correctly. 💙

Could you tell me a bit more about what you're experiencing? For example:
- How long have you been feeling this way?
- What situations trigger these feelings?
- How is it affecting your daily life?

In the meantime, here are some things you can try on our platform:
- 🫁 **Breathing Bubble** game for immediate calm
- 📝 **Gratitude Journal** for perspective
- 👥 **Community** for connection
- 🎯 **Activities** for productive engagement

I'm here to listen and help however I can. 🌿

*I'm an AI wellness companion, not a substitute for professional medical advice.*"""
