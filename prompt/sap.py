import google.generativeai as genai
import streamlit as st
import os

class TravelPlannerAssistant:
    def __init__(self, api_key):
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel('gemini-pro')
        self.previous_context = {}
    
    def refine_user_input(self, current_input):
        # Prepare prompt with previous context
        context_str = str(self.previous_context) if self.previous_context else "No previous context"
        
        prompt = f"""
        You are an advanced travel assistant analyzing a travel request.

        Current Input: {current_input}
        Previous Context: {context_str}

        Tasks:
        1. Analyze the current input 
        2. Identify any missing travel planning information
        3. If destination or duration is missing, use previous context
        4. Generate follow-up questions for incomplete details

        Critical Information Checklist:
        - Destination (MANDATORY)
        - Trip Duration (MANDATORY)
        - Budget Range
        - Travel Purpose
        - Personal Interests
        - Accommodation Preferences
        - Dietary Requirements

        If any MANDATORY information is missing, provide:
        - Summary of known details
        - Use Previous context to fill in missing details but give preference to current input compare to previous context
        """
        
        # Generate response
        response = self.model.generate_content(prompt)
        
        # Update context
        self._update_context(current_input)
        
        return response.text
    
    def _update_context(self, input_text):
        """
        Extract and store key details from input
        """
        context_prompt = """
        Extract structured key details from the input:
        - Destination
        - Duration
        - Budget
        - Interests
        - Dietary Preferences
        - Accommodation Type

        Provide response as a Python dictionary with these keys
        """
        
        context_response = self.model.generate_content(
            f"{context_prompt}\n\nInput: {input_text}"
        )
        
        # Parse context 
        try:
            # Use safe_eval or ast.literal_eval in production
            context_dict = eval(context_response.text)
            self.previous_context.update(context_dict)
        except:
            self.previous_context['raw_input'] = input_text
    
    def generate_activity_suggestions(self, refined_preferences):
        """Generate personalized activity suggestions"""
        prompt = f"""
        Act as an expert travel curator. Given the user's refined travel preferences:
        - Top 5 must-visit attractions
        - 3 hidden gem locations
        - Recommended daily activity mix
        - Estimated time for each activity
        - Alignment with traveler's interests

        Refined Preferences: {refined_preferences}
        """
        
        response = self.model.generate_content(prompt)
        return response.text
    
    def create_detailed_itinerary(self, activity_suggestions):
        """Create comprehensive day-by-day travel itinerary"""
        prompt = f"""
        Design a comprehensive travel itinerary:
        - Day-by-day breakdown
        - Precise activity timings
        - Transportation recommendations
        - Meal suggestions
        - Budget tracking
        - Flexibility for spontaneity

        Activity Suggestions: {activity_suggestions}
        """
        
        response = self.model.generate_content(prompt)
        return response.text

def main():
    st.title("🌍 AI Travel Planner (Gemini)")
    
    # API Key input (replace with secure method in production)
    api_key = st.text_input("Enter Gemini API Key", type="password")
    
    # Initialize session state for previous input
    if 'previous_input' not in st.session_state:
        st.session_state.previous_input = None
    
    # User input area
    user_input = st.text_area("Describe your dream trip...")
    
    if st.button("Generate Itinerary") and api_key:
        try:
            # Initialize planner
            planner = TravelPlannerAssistant(api_key = "AIzaSyAdhPbN-3u9m281xxkbpnjdEcphXWWzXJg")
            
            # Use previous input if current input is vague
            if not user_input.strip() and st.session_state.previous_input:
                user_input = st.session_state.previous_input
            
            # Refine input
            refined_input = planner.refine_user_input(user_input)
            st.write("📝 Refined Preferences:", refined_input)
            
            # Generate activity suggestions
            activity_suggestions = planner.generate_activity_suggestions(refined_input)
            st.write("🗺️ Activity Suggestions:", activity_suggestions)
            
            # Create detailed itinerary
            final_itinerary = planner.create_detailed_itinerary(activity_suggestions)
            st.write("✈️ Your Personalized Itinerary:", final_itinerary)
            
            # Update previous input
            st.session_state.previous_input = user_input
        
        except Exception as e:
            st.error(f"An error occurred: {e}")

if __name__ == "__main__":
    main()