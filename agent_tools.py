from dataclasses import dataclass, field # all the required inputs
from typing import Optional, Dict
import utils

@dataclass
class AppointmentAgent: # Appointment Agent Class
    data: Dict[str, Optional[str]] = field(default_factory=lambda: {"name": None, "phone": None, "email": None, "date": None}) # stores name, phone, email and date data
    state: str = "name"

    def handle_input(self, user_input: str) -> str: # Function to handel inputs of required data with proper validation
        if self.state == "name":
            self.data["name"] = (user_input or "").strip()
            if not self.data["name"]:
                return "Please tell me your name."
            self.state = "phone"
            return "Thanks! What's your phone number? (You csn include country code, e.g. +9779812345678)"

        if self.state == "phone": # Getting phone number detail with proper validation
            if utils.validate_phone(user_input or ""):
                self.data["phone"] = user_input.strip()
                self.state = "email"
                return "Great. Your email address?"
            return "The phone looks off. Try format like +9779812345678 (10-15 digits)."

        if self.state == "email": # Getting email data with validation
            if utils.validate_email(user_input or ""):
                self.data["email"] = user_input.strip()
                self.state = "date"
                return "Cool. When should we call you? (e.g., 2025-08-20 or 'next Monday')"
            return "That doesn't look like a valid email. Please try again."

        if self.state == "date": # Getting date of appointment with proper validation
            iso = utils.extract_date_from_text(user_input or "")
            if iso:
                self.data["date"] = iso
                self.state = "done"
                return f"✅ Appointment booked for {iso}!\nDetails: {self.data}"
            return "Couldn't parse that date. Try like 2025-08-20 or 'next Thursday'."

        if self.state == "done":
            return "All set already! If you want to change details, type 'book appointment' again."

        return "Not sure what to do—say 'book appointment' to start."
    
    
    # BY ASHIM NEPAL