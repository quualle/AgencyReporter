import os
import json
from typing import Dict, List, Any, Optional
from openai import OpenAI
from dotenv import load_dotenv
from datetime import datetime

# Load environment variables
load_dotenv()

class OpenAIIntegration:
    """
    Integration with OpenAI API for text analysis
    """
    def __init__(self):
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OpenAI API key is not set. Set OPENAI_API_KEY environment variable.")
        
        self.client = OpenAI(api_key=api_key)
        self.model = os.getenv("OPENAI_MODEL", "gpt-4-turbo")
    
    def analyze_cancellations(self, texts: List[str], categories: Optional[List[Dict[str, str]]] = None) -> Dict[str, Any]:
        """
        Analyze cancellation reasons in a list of texts (emails, tickets, etc.)
        
        Args:
            texts: List of text content to analyze
            categories: Optional list of predefined categories. If not provided, default categories will be used.
            
        Returns:
            Dictionary with categorized cancellation reasons
        """
        if categories is None:
            # Default cancellation reason categories
            categories = [
                {"id": "caregiver_unavailable", "name": "Betreuungskraft verhindert", "description": "Die Betreuungskraft ist aus persönlichen Gründen nicht verfügbar."},
                {"id": "health_issues", "name": "Gesundheitliche Probleme", "description": "Gesundheitliche Probleme der Betreuungskraft oder im Umfeld."},
                {"id": "customer_dissatisfied", "name": "Kunde unzufrieden", "description": "Der Kunde ist mit dem Vorschlag/Profil nicht zufrieden."},
                {"id": "communication_problems", "name": "Kommunikationsprobleme", "description": "Probleme in der Kommunikation oder Sprachbarrieren."},
                {"id": "qualification_mismatch", "name": "Qualifikation passt nicht", "description": "Die Qualifikation entspricht nicht den Anforderungen."},
                {"id": "pricing_issues", "name": "Preisprobleme", "description": "Unstimmigkeiten bezüglich der Kosten oder Vergütung."},
                {"id": "scheduling_conflict", "name": "Terminkonflikt", "description": "Konflikte mit dem geplanten Einsatzzeitraum."},
                {"id": "administrative_issues", "name": "Administrative Probleme", "description": "Probleme mit Dokumenten, Visa, etc."},
                {"id": "changed_requirements", "name": "Geänderte Anforderungen", "description": "Die Anforderungen des Kunden haben sich geändert."},
                {"id": "family_issues", "name": "Familiäre Gründe", "description": "Familiäre Verpflichtungen oder Probleme der Betreuungskraft."},
                {"id": "transport_issues", "name": "Transportprobleme", "description": "Probleme mit Transport oder Anreise zum Einsatzort."},
                {"id": "personal_conflict", "name": "Persönlicher Konflikt", "description": "Persönliche Konflikte zwischen Beteiligten."},
                {"id": "better_offer", "name": "Besseres Angebot", "description": "Die Betreuungskraft hat ein besseres Angebot erhalten."},
                {"id": "accommodation_issues", "name": "Unterkunftsprobleme", "description": "Probleme mit der angebotenen Unterkunft."},
                {"id": "other", "name": "Sonstiges", "description": "Andere nicht kategorisierte Gründe."}
            ]
        
        # Prepare categories for prompt
        categories_str = "\n".join([f"- {cat['id']}: {cat['name']} - {cat['description']}" for cat in categories])
        
        # Process texts in batches if necessary (large volumes)
        results = {}
        batch_size = min(10, len(texts))  # Process up to 10 texts per API call
        
        for i in range(0, len(texts), batch_size):
            batch = texts[i:i+batch_size]
            
            # Join texts with identifiers
            texts_with_ids = [f"Text {j+1}: {text}" for j, text in enumerate(batch)]
            
            messages = [
                {"role": "system", "content": (
                    "Du bist ein Experte für die Analyse von Abbruchgründen in der Pflegevermittlung. "
                    "Deine Aufgabe ist es, Texte zu analysieren und den Grund für einen Abbruch einer der vordefinierten Kategorien zuzuordnen. "
                    "Verwende NUR die folgenden Kategorien:\n\n" + categories_str
                )},
                {"role": "user", "content": (
                    "Analysiere jeden der folgenden Texte und ordne ihn einer der vordefinierten Kategorien zu. "
                    "Gib für jeden Text die ID der am besten passenden Kategorie zurück. "
                    "Antworte im JSON-Format als Array mit Objekten, die jeweils eine 'text_id' und eine 'category_id' enthalten. "
                    "Hier sind die Texte:\n\n" + "\n\n".join(texts_with_ids)
                )}
            ]
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=0.2,  # Lower temperature for more consistent results
                response_format={"type": "json_object"}
            )
            
            try:
                analysis = json.loads(response.choices[0].message.content)
                
                # Count categories
                for item in analysis.get("results", []):
                    category_id = item.get("category_id")
                    if category_id:
                        results[category_id] = results.get(category_id, 0) + 1
            except (json.JSONDecodeError, AttributeError, KeyError):
                # Fallback for parsing errors
                print("Error parsing LLM response. Using fallback parsing.")
                content = response.choices[0].message.content
                # Simple fallback parsing (extract category IDs)
                for cat in categories:
                    cat_id = cat["id"]
                    if cat_id in content:
                        count = content.count(cat_id)
                        results[cat_id] = results.get(cat_id, 0) + count
        
        return {
            "reason_categories": results,
            "total_analyzed": len(texts)
        }
    
    def analyze_violations(self, texts: List[str], categories: Optional[List[Dict[str, str]]] = None) -> Dict[str, Any]:
        """
        Analyze profile violations in a list of texts (emails, tickets, etc.)
        
        Args:
            texts: List of text content to analyze
            categories: Optional list of predefined categories. If not provided, default categories will be used.
            
        Returns:
            Dictionary with categorized violations
        """
        if categories is None:
            # Default violation categories
            categories = [
                {"id": "experience_misrepresentation", "name": "Erfahrung falsch dargestellt", "description": "Die angegebene Berufserfahrung entspricht nicht der Realität."},
                {"id": "language_skill_exaggeration", "name": "Sprachkenntnisse übertrieben", "description": "Die Deutschkenntnisse wurden im Profil übertrieben dargestellt."},
                {"id": "smoking_status_incorrect", "name": "Raucherstatus inkorrekt", "description": "Der angegebene Raucherstatus stimmt nicht mit der Realität überein."},
                {"id": "age_discrepancy", "name": "Altersabweichung", "description": "Das angegebene Alter stimmt nicht mit dem tatsächlichen Alter überein."},
                {"id": "license_issues", "name": "Führerschein-Probleme", "description": "Probleme mit dem angegebenen Führerschein."},
                {"id": "qualification_misrepresentation", "name": "Qualifikation falsch dargestellt", "description": "Die angegebene Qualifikation entspricht nicht der Realität."},
                {"id": "false_availability", "name": "Falsche Verfügbarkeit", "description": "Die angegebene Verfügbarkeit entspricht nicht der Realität."},
                {"id": "document_issues", "name": "Dokumentenprobleme", "description": "Probleme mit Ausweisdokumenten oder Zertifikaten."},
                {"id": "personality_mismatch", "name": "Persönlichkeitsdiskrepanz", "description": "Die beschriebene Persönlichkeit weicht stark von der tatsächlichen ab."},
                {"id": "other", "name": "Sonstige Verstöße", "description": "Andere nicht kategorisierte Regelverstöße."}
            ]
        
        # Prepare categories for prompt
        categories_str = "\n".join([f"- {cat['id']}: {cat['name']} - {cat['description']}" for cat in categories])
        
        # Process texts in batches if necessary (large volumes)
        results = {}
        batch_size = min(10, len(texts))  # Process up to 10 texts per API call
        
        for i in range(0, len(texts), batch_size):
            batch = texts[i:i+batch_size]
            
            # Join texts with identifiers
            texts_with_ids = [f"Text {j+1}: {text}" for j, text in enumerate(batch)]
            
            messages = [
                {"role": "system", "content": (
                    "Du bist ein Experte für die Analyse von Regelverstößen bei Betreuungskräften in der Pflege. "
                    "Deine Aufgabe ist es, Texte zu analysieren und den Regelverstoß einer der vordefinierten Kategorien zuzuordnen. "
                    "Verwende NUR die folgenden Kategorien:\n\n" + categories_str
                )},
                {"role": "user", "content": (
                    "Analysiere jeden der folgenden Texte und ordne ihn einer der vordefinierten Kategorien zu. "
                    "Gib für jeden Text die ID der am besten passenden Kategorie zurück. "
                    "Antworte im JSON-Format als Array mit Objekten, die jeweils eine 'text_id' und eine 'category_id' enthalten. "
                    "Hier sind die Texte:\n\n" + "\n\n".join(texts_with_ids)
                )}
            ]
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=0.2,  # Lower temperature for more consistent results
                response_format={"type": "json_object"}
            )
            
            try:
                analysis = json.loads(response.choices[0].message.content)
                
                # Count categories
                for item in analysis.get("results", []):
                    category_id = item.get("category_id")
                    if category_id:
                        results[category_id] = results.get(category_id, 0) + 1
            except (json.JSONDecodeError, AttributeError, KeyError):
                # Fallback for parsing errors
                print("Error parsing LLM response. Using fallback parsing.")
                content = response.choices[0].message.content
                # Simple fallback parsing (extract category IDs)
                for cat in categories:
                    cat_id = cat["id"]
                    if cat_id in content:
                        count = content.count(cat_id)
                        results[cat_id] = results.get(cat_id, 0) + count
        
        return {
            "reason_categories": results,
            "total_analyzed": len(texts)
        }
    
    def summarize_agency_performance(self, agency_data: Dict[str, Any]) -> str:
        """
        Generate a summary of agency performance
        
        Args:
            agency_data: Dictionary containing agency metrics and performance data
            
        Returns:
            String with generated summary
        """
        try:
            # Prepare data string from dictionary
            data_str = json.dumps(agency_data, indent=2)
            
            messages = [
                {"role": "system", "content": (
                    "Du bist ein Experte für die Analyse von Leistungsdaten von Vermittlungsagenturen in der Pflege. "
                    "Deine Aufgabe ist es, einen kurzen, prägnanten Überblick über die Leistung einer Agentur zu verfassen. "
                    "Die Zusammenfassung sollte etwa 3-5 Sätze umfassen und die wichtigsten Stärken und Schwächen hervorheben."
                )},
                {"role": "user", "content": (
                    "Erstelle eine kurze Zusammenfassung der Leistung dieser Agentur basierend auf den folgenden Daten. "
                    "Hebe die wichtigsten Stärken und Schwächen hervor. "
                    "Halte die Zusammenfassung auf 3-5 Sätze und konzentriere dich auf die relevantesten Aspekte.\n\n" + data_str
                )}
            ]
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=0.7,  # Higher temperature for more creative text generation
                max_tokens=200  # Limit to keep it concise
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            print(f"Error generating performance summary: {str(e)}")
            return "Zusammenfassung konnte nicht generiert werden."
    
    async def analyze_cv_quality(
        self, 
        cv_content: str,
        communications: Dict[str, Any],
        care_stay_info: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Analyze CV quality by comparing claims with customer communications
        """
        
        # Prepare communications text
        comm_text = ""
        for email in communications.get("emails", []):
            comm_text += f"\n\nEmail from {email['sender']} on {email['date']}:\n"
            comm_text += f"Subject: {email['subject']}\n"
            comm_text += f"Body: {email['body'][:1000]}...\n" if len(email['body']) > 1000 else f"Body: {email['body']}\n"
        
        for ticket in communications.get("tickets", []):
            comm_text += f"\n\nTicket from {ticket['sender']} on {ticket['date']}:\n"
            comm_text += f"Subject: {ticket['subject']}\n"
            comm_text += f"Body: {ticket['body'][:1000]}...\n" if len(ticket['body']) > 1000 else f"Body: {ticket['body']}\n"
        
        # Create the analysis prompt
        prompt = f"""
You are analyzing the quality of a caregiver's CV by comparing their claims with actual customer feedback.

CARE STAY INFORMATION:
- Care Stay ID: {care_stay_info['care_stay_id']}
- Agency: {care_stay_info['agency_name']}
- Caregiver: {care_stay_info['caregiver_name']}
- Duration: {care_stay_info['start_date']} to {care_stay_info['end_date']}
- Status: {care_stay_info['status']}

CV CONTENT:
{cv_content}

CUSTOMER COMMUNICATIONS (Emails and Tickets):
{comm_text}

TASK:
Analyze the CV claims against the customer communications. For each category below, assess if the CV claims match the reality experienced by the customer.

Categories to analyze:
1. German Language Skills (Deutschkenntnisse)
2. Years of Experience / Professional Skills
3. Driver's License (if mentioned)
4. Smoking Status (if mentioned)
5. Age (if mentioned)
6. Personal Characteristics / Soft Skills

For each category:
- Extract the CV claim
- Look for evidence in communications that confirms or contradicts the claim
- Assign a fulfillment score (1-5, where 5 = fully matches, 1 = completely false)
- Provide confidence level (0-1) in your assessment
- List specific evidence quotes

IMPORTANT:
- Start with benefit of doubt (assume 5/5 unless evidence suggests otherwise)
- Only lower scores if there's clear evidence of disappointment or mismatch
- Consider if customer expectations were realistic
- Focus on factual discrepancies, not subjective preferences

Return a JSON object with this structure:
{{
    "categories": {{
        "german_skills": {{
            "category_name": "German Language Skills",
            "cv_claim": "...",
            "fulfillment_score": 5,
            "confidence": 0.9,
            "evidence": ["quote1", "quote2"],
            "discrepancy_detected": false
        }},
        // ... other categories
    }},
    "fulfillment_scores": {{
        "german_skills": 5,
        "experience": 5,
        "drivers_license": 5,
        "smoking": 5,
        "age": 5,
        "soft_skills": 5
    }},
    "discrepancies": [
        {{
            "category": "...",
            "cv_claim": "...",
            "reality": "...",
            "severity": "high/medium/low"
        }}
    ],
    "overall_score": 5.0,
    "details": {{
        "total_communications_analyzed": {len(communications.get('emails', [])) + len(communications.get('tickets', []))},
        "negative_mentions_found": 0,
        "positive_mentions_found": 0
    }},
    "recommendations": [
        "..."
    ]
}}
"""

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are an expert at analyzing CV quality and detecting discrepancies between claims and reality. Always be fair and objective."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                response_format={"type": "json_object"}
            )
            
            result = json.loads(response.choices[0].message.content)
            result['analysis_date'] = datetime.now().isoformat()
            result['care_stay_id'] = care_stay_info['care_stay_id']
            
            return result
            
        except Exception as e:
            # Return a default structure in case of error
            return {
                "care_stay_id": care_stay_info['care_stay_id'],
                "analysis_date": datetime.now().isoformat(),
                "categories": {},
                "fulfillment_scores": {
                    "german_skills": 5,
                    "experience": 5,
                    "drivers_license": 5,
                    "smoking": 5,
                    "age": 5,
                    "soft_skills": 5
                },
                "discrepancies": [],
                "overall_score": 5.0,
                "details": {
                    "error": str(e),
                    "total_communications_analyzed": 0
                },
                "recommendations": ["Analysis failed - manual review required"]
            } 