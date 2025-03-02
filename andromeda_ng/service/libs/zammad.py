from zammad_py import ZammadAPI
import httpx
import json
from loguru import logger
from andromeda_ng.service.settings import config
from andromeda_ng.service.schema import ZammadCompany

url = config.ZAMMAD_URL
oath_token = config.ZAMMAD_TOKEN
headers = {
    "Authorization": f"Bearer {oath_token}",
    "Content-Type": "application/json"}
client = ZammadAPI(url, oath_token)


async def create_organization(company: ZammadCompany) -> dict:
    """Create a new customer in Zammad"""
    try:
        logger.info(f"Creating customer {company.name}")
        # Convert Pydantic model to dict for Zammad API
        company_data = company.model_dump()
        # Use ZammadAPI client to create organization
        result = client.organization.create(
            params=company_data
        )
        if result:
            logger.info(f"Customer {company.name} created successfully")
            return result
        return None
    except Exception as e:  # pragma: no cover
        logger.error(f"Error creating customer: {e}")
        return None


async def get_company_tickets(company_id: int) -> dict:
    """Get all tickets for a company using Zammad API"""
    try:
        logger.info(f"Getting tickets for company {company_id}")
        # Get all tickets
        tickets = client.ticket.search({
            "organization_id": company_id
        })

        # Get open tickets (state not 'closed' or 'resolved')
        open_tickets = client.ticket.search({
            "organization_id": company_id,
            "state_id": [1, 2, 3]  # Typically open, pending states
        })

        if tickets:
            logger.info(
                f"Found {len(tickets)} tickets for company {company_id}")
            return {
                "all_tickets": tickets,
                "open_count": len(open_tickets) if open_tickets else 0,
                "total_count": len(tickets),
                "ticket_url": f"{url}/api/v1/tickets?expand=true&organization_id={company_id}"
            }
        else:
            logger.error("No tickets found")
            return None
    except Exception as e:
        logger.error(f"Error getting tickets: {e}")
        return None


async def create_user(user: dict, zammad_id: int) -> dict:
    """Create a new user in Zammad
    Parameters for user creation:
    - login: str(email address)
    - firstname: str
    - lastname: str
    - email: str
    - password: str(optional)
    - phone: str(optional)
    - organization_id: int(optional)
    - roles: List[str](optional, defaults to["Customer"])
    - active: bool(optional, defaults to true)
"""
    try:
        logger.info(f"Creating user {user['email']}")
        # Use ZammadAPI client to create user

        result = client.user.create(
            params=user
        )
        if result:
            logger.info(f"User {user['email']} created successfully")
            return result
        return None
    except Exception as e:  # pragma: no cover
        logger.error(f"Error creating user: {e}")
        return None
