from services.config.workout_config import PROMPT



class LLMCoach:
    def __init__(self,groq_client):
        self.client = groq_client
        self.history = [] #add feedback message for better feedback
        self.system_prompt = PROMPT


    def give_feedback(self,event,issue):
        prompt = f"Event:{event}"


        if issue:
            prompt += f"Form Issue: {issue}"

        messages = [
            {"role": "system","content": self.system_prompt},
            *self.history[-self.MAX_HISTORY:],
            {"role":"user","content":prompt}
        ]


        try:
            response = self.client.chat.completions.create(   #response from api
                model = "llama-3.3-70b-versatile",
                messages=messages,
                temperature=0.4
            )
            text = response.choices[0].message.content.strip()  #feedback

        except Exception as e:
            print("LLM error:", e)   # API down / rate limit / no internet
            return None

        if not text:
            return None
            
        self.history.append({"role": "user", "content": prompt})
        self.history.append({"role":"assistant","content":text})
        self.history = self.history[-self.MAX_HISTORY * 2:]

        return text
