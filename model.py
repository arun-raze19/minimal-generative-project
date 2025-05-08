import markovify
import os
import random
import re
import json

class SimpleLLM:
    def __init__(self, corpus_path=None, state_size=2):
        """
        Initialize the simple LLM with a corpus file.

        Args:
            corpus_path (str): Path to the text file to use as corpus
            state_size (int): Size of the state for the Markov chain
        """
        self.model = None
        self.state_size = state_size
        self.json_data = None
        self.knowledge_base = {
            "greeting": [
                "Hello! How can I help you today?",
                "Hi there! What would you like to know?",
                "Greetings! I'm here to assist you.",
                "Hello! I'm a simple AI assistant. What's on your mind?"
            ],
            "farewell": [
                "Goodbye! Have a great day!",
                "Farewell! Come back if you have more questions.",
                "See you later! Take care!",
                "Bye for now! It was nice chatting with you."
            ],
            "unknown": [
                "I'm not sure I understand. Could you rephrase that?",
                "That's an interesting question, but I'm not sure how to answer it.",
                "I don't have enough information to provide a good answer to that.",
                "I'm still learning and don't have a good response for that yet."
            ],
            "identity": [
                "I'm a simple text-based AI assistant created with Python and Flask.",
                "I'm a minimal AI assistant that uses structured knowledge and Markov chains to generate responses.",
                "I'm a basic language model designed to simulate conversation and answer questions about AI concepts.",
                "I'm a text generator that tries to provide helpful responses based on my knowledge base."
            ],
            "capabilities": [
                "I can answer questions about AI concepts like machine learning, neural networks, and more.",
                "I can generate text responses based on patterns I've learned and my structured knowledge base.",
                "I'm designed to provide information about AI topics and engage in simple dialogue.",
                "I can respond to questions about artificial intelligence and related fields."
            ]
        }

        if corpus_path and os.path.exists(corpus_path):
            self.load_corpus(corpus_path)

    def load_corpus(self, corpus_path):
        """
        Load a corpus from a text file and build the model.

        Args:
            corpus_path (str): Path to the text file
        """
        try:
            with open(corpus_path, 'r', encoding='utf-8') as f:
                content = f.read()

            # Try to parse as JSON
            try:
                self.json_data = json.loads(content)
                print("Successfully loaded JSON data")

                # Create a text corpus from the JSON data for the Markov model
                text_corpus = ""

                # Process college info
                if "college_info" in self.json_data:
                    college = self.json_data["college_info"]
                    text_corpus += f"{college.get('name', '')} is {college.get('description', '')}\n\n"
                    text_corpus += f"Vision: {college.get('vision', '')}\n\n"

                    # Add mission statements
                    if "mission" in college and isinstance(college["mission"], list):
                        text_corpus += "Mission:\n"
                        for item in college["mission"]:
                            text_corpus += f"- {item}\n"
                        text_corpus += "\n"

                    # Add achievements
                    if "achievements" in college and isinstance(college["achievements"], list):
                        text_corpus += "Achievements:\n"
                        for item in college["achievements"]:
                            text_corpus += f"- {item}\n"
                        text_corpus += "\n"

                # Process academic programs
                if "academic_programs" in self.json_data:
                    programs = self.json_data["academic_programs"]

                    # Undergraduate programs
                    if "undergraduate" in programs and isinstance(programs["undergraduate"], list):
                        text_corpus += "Undergraduate Programs:\n"
                        for program in programs["undergraduate"]:
                            text_corpus += f"- {program.get('name', '')} ({program.get('abbreviation', '')}): {program.get('duration', '')}\n"
                            if "description" in program:
                                text_corpus += f"  {program.get('description', '')}\n"
                        text_corpus += "\n"

                    # Postgraduate programs
                    if "postgraduate" in programs and isinstance(programs["postgraduate"], list):
                        text_corpus += "Postgraduate Programs:\n"
                        for program in programs["postgraduate"]:
                            text_corpus += f"- {program.get('name', '')} ({program.get('abbreviation', '')}): {program.get('duration', '')}\n"
                        text_corpus += "\n"

                # Process departments
                if "departments" in self.json_data and isinstance(self.json_data["departments"], list):
                    for dept in self.json_data["departments"]:
                        text_corpus += f"The {dept.get('name', '')} ({dept.get('abbreviation', '')}) "
                        if "established" in dept:
                            text_corpus += f"was established in {dept.get('established', '')}. "
                        if "head" in dept:
                            text_corpus += f"It is headed by {dept.get('head', '')}. "
                        text_corpus += "\n"

                        # Add department vision and mission
                        if "vision" in dept:
                            text_corpus += f"Vision: {dept.get('vision', '')}\n"

                        if "mission" in dept and isinstance(dept["mission"], list):
                            text_corpus += "Mission:\n"
                            for item in dept["mission"]:
                                text_corpus += f"- {item}\n"
                            text_corpus += "\n"

                        # Add department events
                        if "events" in dept and isinstance(dept["events"], list):
                            text_corpus += f"Events organized by {dept.get('abbreviation', '')}:\n"
                            for event in dept["events"]:
                                text_corpus += f"- {event}\n"
                            text_corpus += "\n"

                # Process placements
                if "placements" in self.json_data:
                    placements = self.json_data["placements"]
                    text_corpus += f"The placement record is {placements.get('placement_record', '')}. "
                    text_corpus += f"The placement officer is {placements.get('placement_officer', '')}.\n"

                    if "placement_partners" in placements and isinstance(placements["placement_partners"], list):
                        text_corpus += "Placement partners include: "
                        text_corpus += f"{', '.join(placements['placement_partners'])}.\n\n"

                # Process events
                if "events" in self.json_data and isinstance(self.json_data["events"], list):
                    text_corpus += "College Events:\n"
                    for event in self.json_data["events"]:
                        text_corpus += f"- {event.get('name', '')}: {event.get('description', '')}\n"
                    text_corpus += "\n"

                # Process admissions
                if "admissions" in self.json_data:
                    admissions = self.json_data["admissions"]

                    if "undergraduate" in admissions:
                        text_corpus += "Undergraduate Admissions:\n"
                        text_corpus += f"Eligibility: {admissions['undergraduate'].get('eligibility', '')}\n"
                        text_corpus += f"Process: {admissions['undergraduate'].get('admission_process', '')}\n\n"

                    if "postgraduate" in admissions:
                        text_corpus += "Postgraduate Admissions:\n"
                        text_corpus += f"Eligibility: {admissions['postgraduate'].get('eligibility', '')}\n"
                        text_corpus += f"Process: {admissions['postgraduate'].get('admission_process', '')}\n\n"

                # Build the Markov model from the extracted text
                self.model = markovify.Text(text_corpus, state_size=self.state_size)

            except json.JSONDecodeError:
                # Not JSON, treat as plain text
                self.json_data = None
                self.model = markovify.Text(content, state_size=self.state_size)

            return True
        except Exception as e:
            print(f"Error loading corpus: {e}")
            return False

    def _search_json_knowledge(self, query):
        """
        Search the JSON knowledge base for relevant information.

        Args:
            query (str): The search query

        Returns:
            str: Information found or None if nothing relevant
        """
        if not self.json_data:
            return None

        query_lower = query.lower()
        query_words = set(re.findall(r'\b\w+\b', query_lower))

        # Check for college information
        if any(word in query_lower for word in ["college", "institution", "mec", "mailam"]):
            if "college_info" in self.json_data:
                college = self.json_data["college_info"]

                # Check for specific college information
                if any(word in query_lower for word in ["about", "description", "overview"]):
                    return f"{college.get('name', '')} is {college.get('description', '')}"

                if any(word in query_lower for word in ["vision"]):
                    return f"Vision of {college.get('name', '')}: {college.get('vision', '')}"

                if any(word in query_lower for word in ["mission"]):
                    mission = college.get("mission", [])
                    if mission:
                        return f"Mission of {college.get('name', '')}:\n" + "\n".join([f"- {item}" for item in mission])

                if any(word in query_lower for word in ["achievement", "accomplishment", "ranking"]):
                    achievements = college.get("achievements", [])
                    if achievements:
                        return f"Achievements of {college.get('name', '')}:\n" + "\n".join([f"- {item}" for item in achievements])

                if any(word in query_lower for word in ["contact", "address", "location", "phone", "email"]):
                    location = college.get("location", {})
                    contact = location.get("contact", {})
                    return f"Contact Information:\nAddress: {location.get('address', '')}\nPhone: {contact.get('phone', '')}\nMobile: {contact.get('mobile', '')}\nEmail: {contact.get('email', '')}"

                if any(word in query_lower for word in ["director", "principal", "management", "head"]):
                    key_people = college.get("key_people", [])
                    if key_people:
                        return "Key People:\n" + "\n".join([f"- {person.get('name', '')} ({person.get('position', '')})" for person in key_people])

                # General college information
                return f"{college.get('name', '')} is {college.get('description', '')}\n\nVision: {college.get('vision', '')}"

        # Check for courses/programs
        if any(word in query_lower for word in ["course", "program", "degree", "btech", "be", "me", "mba", "mca"]):
            if "academic_programs" in self.json_data:
                programs = self.json_data["academic_programs"]

                # Check for undergraduate programs
                if any(word in query_lower for word in ["undergraduate", "ug", "be", "btech", "bachelor"]):
                    ug_programs = programs.get("undergraduate", [])
                    if ug_programs:
                        return "Undergraduate Programs:\n" + "\n".join([f"- {program.get('name', '')} ({program.get('abbreviation', '')}): {program.get('duration', '')}" for program in ug_programs])

                # Check for postgraduate programs
                if any(word in query_lower for word in ["postgraduate", "pg", "me", "mtech", "mba", "mca", "master"]):
                    pg_programs = programs.get("postgraduate", [])
                    if pg_programs:
                        return "Postgraduate Programs:\n" + "\n".join([f"- {program.get('name', '')} ({program.get('abbreviation', '')}): {program.get('duration', '')}" for program in pg_programs])

                # Check for specific program
                for program_type in ["undergraduate", "postgraduate"]:
                    if program_type in programs:
                        for program in programs[program_type]:
                            program_name = program.get("name", "").lower()
                            program_abbr = program.get("abbreviation", "").lower()

                            if program_name in query_lower or (program_abbr and program_abbr in query_lower):
                                result = f"{program.get('name', '')} ({program.get('abbreviation', '')}) is a {program.get('duration', '')} program."
                                if "description" in program:
                                    result += f"\n\n{program.get('description', '')}"
                                return result

                # General programs information
                ug_count = len(programs.get("undergraduate", []))
                pg_count = len(programs.get("postgraduate", []))
                return f"Mailam Engineering College offers {ug_count} undergraduate programs and {pg_count} postgraduate programs."

        # Check for departments
        if any(word in query_lower for word in ["department", "dept"]):
            if "departments" in self.json_data:
                departments = self.json_data["departments"]

                # Check for specific department
                for dept in departments:
                    dept_name = dept.get("name", "").lower()
                    dept_abbr = dept.get("abbreviation", "").lower()

                    if dept_name in query_lower or (dept_abbr and dept_abbr in query_lower):
                        result = f"The {dept.get('name', '')} ({dept.get('abbreviation', '')}) "
                        if "established" in dept:
                            result += f"was established in {dept.get('established', '')}. "
                        if "head" in dept:
                            result += f"It is headed by {dept.get('head', '')}."

                        if "vision" in dept:
                            result += f"\n\nVision: {dept.get('vision', '')}"

                        if "mission" in dept and isinstance(dept["mission"], list):
                            result += "\n\nMission:\n" + "\n".join([f"- {item}" for item in dept["mission"]])

                        if "events" in dept and isinstance(dept["events"], list):
                            result += f"\n\nEvents organized by {dept.get('abbreviation', '')}:\n" + "\n".join([f"- {event}" for event in dept["events"]])

                        return result

                # General departments information
                return f"Mailam Engineering College has {len(departments)} departments including " + ", ".join([dept.get("abbreviation", "") for dept in departments])

        # Check for AI and Data Science specific queries
        if any(word in query_lower for word in ["ai", "artificial intelligence", "data science", "machine learning"]):
            for dept in self.json_data.get("departments", []):
                if "AI" in dept.get("abbreviation", "") or "Artificial Intelligence" in dept.get("name", ""):
                    result = f"The {dept.get('name', '')} ({dept.get('abbreviation', '')}) "
                    if "established" in dept:
                        result += f"was established in {dept.get('established', '')}. "
                    if "head" in dept:
                        result += f"It is headed by {dept.get('head', '')}."

                    if "program_objectives" in dept and isinstance(dept["program_objectives"], list):
                        result += "\n\nProgram Objectives:\n" + "\n".join([f"- {item}" for item in dept["program_objectives"]])

                    if "job_opportunities" in dept and isinstance(dept["job_opportunities"], list):
                        result += "\n\nJob Opportunities:"
                        for job in dept["job_opportunities"]:
                            result += f"\n- {job.get('field', '')}: " + ", ".join(job.get("roles", []))

                    return result

        # Check for placement information
        if any(word in query_lower for word in ["placement", "job", "career", "recruitment", "company"]):
            if "placements" in self.json_data:
                placements = self.json_data["placements"]
                result = f"The placement record is {placements.get('placement_record', '')}. "
                result += f"The placement officer is {placements.get('placement_officer', '')}."

                if "placement_partners" in placements and isinstance(placements["placement_partners"], list):
                    result += "\n\nPlacement partners include: " + ", ".join(placements["placement_partners"]) + "."

                if "contact" in placements:
                    contact = placements["contact"]
                    result += f"\n\nContact the Placement Officer:\nMobile: {contact.get('mobile', '')}\nEmail: {contact.get('email', '')}"

                return result

        # Check for admission information
        if any(word in query_lower for word in ["admission", "apply", "application", "eligibility", "entrance"]):
            if "admissions" in self.json_data:
                admissions = self.json_data["admissions"]
                result = "Admission Information:\n\n"

                if "undergraduate" in admissions:
                    ug = admissions["undergraduate"]
                    result += "Undergraduate Admissions:\n"
                    result += f"Eligibility: {ug.get('eligibility', '')}\n"
                    result += f"Process: {ug.get('admission_process', '')}\n\n"

                    if "documents_required" in ug and isinstance(ug["documents_required"], list):
                        result += "Documents Required:\n" + "\n".join([f"- {doc}" for doc in ug["documents_required"]]) + "\n\n"

                if "postgraduate" in admissions:
                    pg = admissions["postgraduate"]
                    result += "Postgraduate Admissions:\n"
                    result += f"Eligibility: {pg.get('eligibility', '')}\n"
                    result += f"Process: {pg.get('admission_process', '')}\n\n"

                    if "documents_required" in pg and isinstance(pg["documents_required"], list):
                        result += "Documents Required:\n" + "\n".join([f"- {doc}" for doc in pg["documents_required"]]) + "\n\n"

                if "contact" in admissions:
                    contact = admissions["contact"]
                    result += f"Contact for Admissions:\nPhone: {contact.get('phone', '')}\nMobile: {contact.get('mobile', '')}\nEmail: {contact.get('email', '')}"

                return result

        # Check for events
        if any(word in query_lower for word in ["event", "celebration", "function", "ceremony"]):
            if "events" in self.json_data and isinstance(self.json_data["events"], list):
                events = self.json_data["events"]
                return "College Events:\n" + "\n".join([f"- {event.get('name', '')}: {event.get('description', '')}" for event in events])

        # If no direct match, look for partial matches in all sections
        query_terms = set(query_lower.split())

        # Search in college info
        if "college_info" in self.json_data:
            college = self.json_data["college_info"]
            college_text = json.dumps(college).lower()
            if any(term in college_text for term in query_terms):
                return f"{college.get('name', '')} is {college.get('description', '')}"

        # Search in departments
        for dept in self.json_data.get("departments", []):
            dept_text = json.dumps(dept).lower()
            if any(term in dept_text for term in query_terms):
                return f"The {dept.get('name', '')} ({dept.get('abbreviation', '')}) is one of the departments at Mailam Engineering College."

        # Search in programs
        if "academic_programs" in self.json_data:
            programs = self.json_data["academic_programs"]
            for program_type in ["undergraduate", "postgraduate"]:
                if program_type in programs:
                    for program in programs[program_type]:
                        program_text = json.dumps(program).lower()
                        if any(term in program_text for term in query_terms):
                            return f"{program.get('name', '')} ({program.get('abbreviation', '')}) is a {program.get('duration', '')} program offered at Mailam Engineering College."

        return None

    # This method is no longer used but kept for reference
    def _format_concept_info(self, concept, query_words=None):
        """
        Format concept information into a readable response.

        Args:
            concept (dict): The concept dictionary
            query_words (set): Set of words from the query for highlighting relevant parts

        Returns:
            str: Formatted information
        """
        return "Information not available."

    def generate_response(self, question):
        """
        Generate a response to the user's question.

        Args:
            question (str): The user's question or input

        Returns:
            str: Generated response
        """
        if not self.model:
            return "I'm not fully initialized yet. Please wait a moment."

        # Convert question to lowercase for easier matching
        question_lower = question.lower()

        # Check for greetings
        if re.search(r'\b(hi|hello|hey|greetings)\b', question_lower):
            return random.choice(self.knowledge_base["greeting"])

        # Check for farewells
        if re.search(r'\b(bye|goodbye|farewell|see you)\b', question_lower):
            return random.choice(self.knowledge_base["farewell"])

        # Check for identity questions
        if re.search(r'\b(who are you|what are you|your name|your identity)\b', question_lower):
            return random.choice(self.knowledge_base["identity"])

        # Check for capability questions
        if re.search(r'\b(what can you do|your capabilities|your functions|your abilities)\b', question_lower):
            return random.choice(self.knowledge_base["capabilities"])

        try:
            # First, try to find relevant information in the JSON knowledge base
            json_response = self._search_json_knowledge(question)
            if json_response:
                return json_response

            # If no structured knowledge is found, fall back to Markov generation
            # Try to make a sentence that starts with a word from the question
            words = re.findall(r'\b\w+\b', question_lower)
            words = [w for w in words if len(w) > 3]  # Filter out short words

            if words:
                for _ in range(3):  # Try a few times
                    seed_word = random.choice(words)
                    sentence = self.model.make_sentence_with_start(seed_word, strict=False)
                    if sentence:
                        return sentence

            # If that fails, generate a few random sentences
            sentences = []
            for _ in range(2):
                sentence = self.model.make_sentence()
                if sentence:
                    sentences.append(sentence)

            if sentences:
                return " ".join(sentences)
            else:
                return random.choice(self.knowledge_base["unknown"])

        except Exception as e:
            print(f"Error generating response: {e}")
            return f"I'm having trouble processing that. {random.choice(self.knowledge_base['unknown'])}"

# Example usage
if __name__ == "__main__":
    llm = SimpleLLM("data/sample_text.txt")
    print(llm.generate_response("Tell me something interesting."))
