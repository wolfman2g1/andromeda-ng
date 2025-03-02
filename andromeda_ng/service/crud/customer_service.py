from loguru import logger
from andromeda_ng.service.models import Contact, Customer
from andromeda_ng.service.database import get_db
from sqlalchemy.orm import Session
from andromeda_ng.service.schema import CustomerSchema, CustomerOutput
from andromeda_ng.service.libs import zammad
import uuid


async def create_customer(db: Session, customer_data: CustomerSchema):
    check_customer = db.query(Customer).filter(
        Customer.customer_name == customer_data.customer_name).first()
    if check_customer:
        logger.error("Customer already exists")
        return {"error": "Customer already exists"}
    try:
        new_customer = Customer(**customer_data.dict())
        db.add(new_customer)
        db.commit()
        db.refresh(new_customer)
        return new_customer
    except Exception as e:
        logger.error(f"Error creating customer: {e}")
        db.rollback()
        return {"error": "Error creating customer"}


async def read_customers(db: Session):
    try:
        customers = db.query(Customer).all()
        return customers
    except Exception as e:
        logger.error(f"Error reading customers: {e}")
        return {"error": "Error reading customers"}


async def read_customer_by_id(db: Session, customer_id: uuid.UUID):
    try:
        customer = db.query(Customer).filter(
            Customer.id == customer_id).first()
        if not customer:
            return {"error": "Customer not found"}

        # Get tickets if customer exists
        ticket_info = await zammad.get_company_tickets(customer.zammad_id)

        # Prepare customer output with ticket information
        customer_data = customer.__dict__
        if ticket_info and ticket_info["all_tickets"]:
            tickets_list = []
            for ticket in ticket_info["all_tickets"]:
                tickets_list.append({
                    "id": ticket.get("id"),
                    "title": ticket.get("title"),
                    "number": ticket.get("number"),
                    "state": ticket.get("state"),
                    "priority": ticket.get("priority"),
                    "created_at": ticket.get("created_at"),
                    "updated_at": ticket.get("updated_at")
                })

            customer_data.update({
                "customer_tickets": tickets_list,
                "ticket_count": ticket_info["total_count"],
                "open_tickets": ticket_info["open_count"],
                "ticket_url": ticket_info["ticket_url"]
            })
        else:
            customer_data.update({
                "customer_tickets": [],  # Empty list instead of empty dict
                "ticket_count": 0,
                "open_tickets": 0,
                "ticket_url": f"{zammad.url}/api/v1/tickets?expand=true&organization_id={customer.zammad_id}"
            })

        return CustomerOutput(**customer_data)

    except Exception as e:
        logger.error(f"Error reading customer: {e}")
        return {"error": f"Error reading customer: {str(e)}"}


async def update_customer(db: Session, customer_id: uuid.UUID, customer_data: CustomerSchema):
    try:
        customer = db.query(Customer).filter(
            Customer.id == customer_id).first()
        if not customer:
            logger.error(f"Customer not found with id: {customer_id}")
            return {"error": "Customer not found"}
        customer.update(customer_data.dict(exclude_unset=True))
        db.commit()
        logger.info(f"Customer updated: {customer_id}")
        return customer
    except Exception as e:
        logger.error(f"Error updating customer: {e}")
        db.rollback()
        return {"error": "Error updating customer"}


async def delete_customer(db: Session, customer_id: uuid.UUID):
    try:
        customer = db.query(Customer).filter(
            Customer.id == customer_id).first()
        if not customer:
            logger.error(f"Customer not found with id: {customer_id}")
            return {"error": "Customer not found"}
        db.delete(customer)
        db.commit()
        logger.info(f"Customer deleted: {customer_id}")
        return customer
    except Exception as e:
        logger.error(f"Error deleting customer: {e}")
        db.rollback()
        return {"error": "Error deleting customer"}


async def read_customer_by_name(db: Session, customer_name: str):
    try:
        customer = db.query(Customer).filter(
            Customer.customer_name == customer_name).first()
        return customer
    except Exception as e:
        logger.error(f"Error reading customer: {e}")
        return {"error": "Error reading customer"}


async def get_customer_stats(db: Session):
    try:
        total_customers = db.query(Customer).count()
        active_customers = db.query(Customer).filter(
            Customer.is_active == True).count()
        inactive_customers = db.query(Customer).filter(
            Customer.is_active == False).count()
        return {
            "total_customers": total_customers,
            "active_customers": active_customers,
            "inactive_customers": inactive_customers
        }
    except Exception as e:
        logger.error(f"Error getting customer stats: {e}")
        return {"error": "Error getting customer stats"}
