from fastapi import Depends
from langchain_core.tools import tool
from sqlalchemy.ext.asyncio import AsyncSession

import agent.service as service
from database.connection import get_db
import employees.service as employee_service


@tool
def search_in_policy_documents(query: str) -> dict[str, str]:
    """Search in the company's policy documents for relevant information.
    Always format the response in a clear and concise manner. If you cannot find the information, respond with "I could not find the information in the policy documents."

    Args:
        query: A question or search string from the user.
    Returns:
        A dictionary 'result' containing the relevant information from the policy documents.
    """

    return {"result": service.search_in_documents(query)}
    # return {"result": "Searching in policy documents for query: {query}... (This is a placeholder response. Implement the actual search logic.)"}


def make_search_employee_by_id(db: AsyncSession = Depends(get_db)):
    @tool
    async def search_employee_by_id(employee_id: int) -> str:
        """Search for an employee by their ID.

        Args:
            employee_id: int -> The unique identifier of the employee.
        Returns:
            A string containing the employee's details or a message if not found.
        """

        print(f"Searching for employee with ID: {employee_id}")
        employee = await employee_service.get_employee(db, employee_id)
        print(
            f"Found employee: {employee}"
            if employee
            else f"Employee with ID {employee_id} not found."
        )
        return (
            f"Employee Details: {employee}"
            if employee
            else f"Employee with ID {employee_id} not found."
        )

    return search_employee_by_id


def make_search_address_by_employee_id(db: AsyncSession = Depends(get_db)):
    @tool
    async def search_address_by_employee_id(employee_id: int) -> str:
        """Search for an employee's address by their ID.

        Args:
            employee_id: int -> The unique identifier of the employee.
        Returns:
            A string containing the employee's addresses details or a message if not found.
        """

        print(f"Searching for address of employee with ID: {employee_id}")
        address = await employee_service.get_addresses(db, employee_id)
        print(
            f"Found address: {address}"
            if address
            else f"Address for Employee ID {employee_id} not found."
        )
        return (
            f"Address Details: {address}"
            if address
            else f"Address for Employee ID {employee_id} not found."
        )

    return search_address_by_employee_id
