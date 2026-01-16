from typing import Optional
from twuaqirag.rag.rag_types import ReviewSentiment

class user_review_agent:
     
     """
    Evaluates what the USER says or writes as a review.
    This runs inside the RAG flow when intent == REVIEW.
    """
     def evaluate(self,text: Optional[str])-> ReviewSentiment:
          
       if text == None:
           return ReviewSentiment.NEUTRAL
       
       clean_text = text.strip().lower()

       if not clean_text:
           return ReviewSentiment.NEUTRAL
       

       negative_keywords=[
           "bad",
            "dirty",
            "broken",
            "not working",
            "terrible",
            "problem",
            "issue",
            "worst",
            "noisy",
            "smelly",
            # Arabic
            "سيئ",
            "وسخ",
            "خربان",
            "ما يشتغل",
            "مشكلة",
            "أسوأ",
            "ما عجبني"

       ]

       if any(word in clean_text for word in negative_keywords):
          return ReviewSentiment.NEGATIVE
    

       return ReviewSentiment.POSITIVE



          
    
 




