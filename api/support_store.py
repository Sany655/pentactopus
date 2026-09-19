"""Support Tickets Store for Pentactopus.

Provides persistence for user support requests, bug reports, and inquiries.
Uses PostgreSQL if configured, otherwise falls back to local JSON files.
"""

import os
import json
import time
import uuid
import logging
from typing import Dict, Any, List, Optional
from api.db_adapter import DatabaseAdapter

logger = logging.getLogger("pentactopus.support")

if os.getenv("VERCEL") or os.name != "nt":
    DATA_DIR = "/tmp/penta_data"
else:
    DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data")

os.makedirs(DATA_DIR, exist_ok=True)
TICKETS_FILE = os.path.join(DATA_DIR, "support_tickets.json")

class SupportStore:
    """Manages creation, listing, and resolution of support tickets."""
    _mem_tickets: Dict[str, Dict[str, Any]] = {}
    _loaded = False

    @classmethod
    def _load_tickets(cls) -> Dict[str, Dict[str, Any]]:
        if cls._loaded:
            return cls._mem_tickets

        db_tickets = DatabaseAdapter.load_support_tickets()
        if db_tickets is not None:
            cls._mem_tickets = db_tickets
            cls._loaded = True
            return cls._mem_tickets

        if os.path.isfile(TICKETS_FILE):
            try:
                with open(TICKETS_FILE, "r", encoding="utf-8") as f:
                    cls._mem_tickets = json.load(f)
            except Exception as e:
                logger.error(f"Failed to load tickets from JSON: {e}")
        
        cls._loaded = True
        return cls._mem_tickets

    @classmethod
    def _save_tickets(cls, tickets: Dict[str, Dict[str, Any]]) -> None:
        cls._mem_tickets = tickets
        try:
            with open(TICKETS_FILE, "w", encoding="utf-8") as f:
                json.dump(tickets, f, indent=2)
        except Exception as e:
            logger.error(f"Failed to save tickets to JSON: {e}")

        if DatabaseAdapter.is_postgres_configured():
            for t in tickets.values():
                DatabaseAdapter.save_support_ticket(t)

    @classmethod
    def create_ticket(cls, name: str, email: str, message: str) -> Dict[str, Any]:
        """Create a new support ticket."""
        tickets = cls._load_tickets()
        ticket_id = f"ticket_{uuid.uuid4().hex[:10]}"
        
        ticket = {
            "id": ticket_id,
            "name": name.strip(),
            "email": email.lower().strip(),
            "message": message.strip(),
            "status": "open",
            "created_at": time.time(),
            "resolved_at": None
        }
        
        tickets[ticket_id] = ticket
        cls._save_tickets(tickets)
        return ticket

    @classmethod
    def list_tickets(cls) -> List[Dict[str, Any]]:
        """Return a list of all tickets sorted by creation time (newest first)."""
        tickets = cls._load_tickets()
        return sorted(list(tickets.values()), key=lambda x: x.get("created_at", 0), reverse=True)

    @classmethod
    def get_ticket(cls, ticket_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve a single ticket by its ID."""
        tickets = cls._load_tickets()
        return tickets.get(ticket_id)

    @classmethod
    def resolve_ticket(cls, ticket_id: str) -> Optional[Dict[str, Any]]:
        """Mark a ticket as resolved."""
        tickets = cls._load_tickets()
        ticket = tickets.get(ticket_id)
        if not ticket:
            return None
            
        ticket["status"] = "resolved"
        ticket["resolved_at"] = time.time()
        
        cls._save_tickets(tickets)
        
        # Optimize PG update if configured
        DatabaseAdapter.update_support_ticket_status(ticket_id, "resolved", ticket["resolved_at"])
        
        return ticket
