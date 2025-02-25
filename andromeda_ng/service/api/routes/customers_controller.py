from fastapi import status, APIRouter, Depends, HTTPException
from typing import List, Optional
from loguru import logger
import uuid
from andromeda_ng.service.schema import CustomerSchema, CustomerOutput
from andromeda_ng.service.crud import customer_service
from andromeda_ng.service.database import get_db

router = APIRouter(prefix="/api/v1/customers", tags=["customers"])


@router.post("/", response_model=CustomerSchema, status_code=status.HTTP_201_CREATED)
async def create_customer(customer_data: CustomerSchema, db=Depends(get_db)):
    customer_name = customer_data.customer_name.lower()
    # Check if customer already exists
    check_customer = await customer_service.read_customer_by_name(db, customer_name)
    if check_customer:
        logger.error(f"Customer already exists with name: {customer_name}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Customer already exists")
    customer = await customer_service.create_customer(db, customer_data)
    if not customer:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail="Please check your input data")
    logger.info(f"Customer created: {customer.id}")
    return customer


@router.get("/", response_model=List[CustomerOutput],  status_code=status.HTTP_200_OK)
async def read_customers(db=Depends(get_db)):
    try:
        logger.info("Reading customers")
        customers = await customer_service.read_customers(db)
        return customers
    except HTTPException as e:
        logger.error(f"Error reading customers: {e}")
        raise e
    except Exception as e:
        logger.error(f"Unexpected error reading customers: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail="An unexpected error occurred")


@router.get("/{customer_id}", response_model=CustomerOutput, status_code=status.HTTP_200_OK)
async def read_customer_by_id(customer_id: uuid.UUID, db=Depends(get_db)):
    try:
        customer = await customer_service.read_customer_by_id(db, customer_id)
        if not customer:
            logger.error(f"Customer not found with id: {customer_id}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Customer not found")
        logger.info(f"Found Customer id: {customer_id}")
        return customer
    except HTTPException as e:
        logger.error(f"Error reading customer: {e}")
        raise e
    except Exception as e:
        logger.error(f"Unexpected error reading customer: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail="An unexpected error occurred")


@router.put("/{customer_id}", response_model=CustomerOutput, status_code=status.HTTP_200_OK)
async def update_customer(customer_id: uuid.UUID, customer_data: CustomerSchema, db=Depends(get_db)):
    try:
        customer = await customer_service.update_customer(db, customer_id, customer_data)
        if not customer:
            logger.error(f"Customer not found with id: {customer_id}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Customer not found")
        logger.info(f"Customer updated: {customer_id}")
        return customer
    except HTTPException as e:
        logger.error(f"Error updating customer: {e}")
        raise e
    except Exception as e:
        logger.error(f"Unexpected error updating customer: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail="An unexpected error occurred")


@router.delete("/{customer_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_customer(customer_id: uuid.UUID, db=Depends(get_db)):
    try:
        await customer_service.delete_customer(db, customer_id)
        logger.info(f"Customer deleted: {customer_id}")
    except HTTPException as e:
        logger.error(f"Error deleting customer: {e}")
        raise e
    except Exception as e:
        logger.error(f"Unexpected error deleting customer: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail="An unexpected error occurred")


# Additional routes for customer-related operations
@router.get("/name/{customer_name}", response_model=CustomerOutput, status_code=status.HTTP_200_OK)
async def read_customer_by_name(customer_name: str, db=Depends(get_db)):
    try:
        customer = await customer_service.read_customer_by_name(db, customer_name)
        if not customer:
            logger.error(f"Customer not found with name: {customer_name}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Customer not found")
        logger.info(f"Found Customer name: {customer_name}")
        return customer
    except HTTPException as e:
        logger.error(f"Error reading customer: {e}")
        raise e
    except Exception as e:
        logger.error(f"Unexpected error reading customer: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail="An unexpected error occurred")
