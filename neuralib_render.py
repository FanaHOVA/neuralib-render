import requests
import os
from dotenv import load_dotenv
from pydantic import BaseModel, Field
from typing import Literal

load_dotenv()

# It's important for classes to be in snake case to match their definition that goes in the LLM context
class list_all_services(BaseModel):
    """List all cloud services the user is hosting on Render.com"""
    limit: int = Field(default=20, description="The max number of services to return.")

class create_service(BaseModel):
    """Create a new cloud service for the user on Render.com"""
    name: str = Field(default="my-new-service", description="The name of the service to create.")
    service_type: Literal['cron_job', 'web_service', 'background_worker', 'private_service', 'static_site'] = Field(default="web", description="The type of service to create.")
    service_details: dict = Field(default={}, description="The service details to set for the service. For example for a cron job: { 'env': 'docker', 'schedule': '0 0 * * *' }")


class Render:
  @staticmethod
  def authorization_headers():
    return {
        'Accept': 'application/json',
        'Authorization': f'Bearer {os.getenv("RENDER_API_KEY")}'
      }
  
  def list_all_services():
      url = f'https://api.render.com/v1/services?limit=20'

      response = requests.get(url, headers=Render.authorization_headers())

      if response.status_code != 200:
        print(f"Error: {response.status_code}, {response.text}")
        
      print(response.json())
      
  def create_service(name='my-new-service', service_type='cron_job', service_details={ "env": "docker", "schedule": "0 0 * * *" }):
      url = 'https://api.render.com/v1/services'
      
      data = {
        "ownerId": os.getenv("RENDER_OWNER_ID"),
        "name": name,
        "type": service_type,
        "serviceDetails": service_details
      }

      response = requests.post(url, headers=Render.authorization_headers(), json=data)

      print(response.json())
      
  @staticmethod
  def custom_schema(model):
    schema = model.schema()
    # Ensure 'type' for parameters is set to 'object'
    parameters_schema = {
      "type": "object",
      "properties": schema.get('properties', {}),
      "required": schema.get('required', [])
    }
    # Remove 'title' and 'description' from each property in 'properties'
    for param in parameters_schema['properties'].values():
      param.pop('title', None)
      param.pop('description', None)

    return {
      "type": "function",  # Ensure this is set correctly for the API
      "function": {
        "name": model.__name__,
        "description": schema.get('description', ''),
        "parameters": parameters_schema  # Updated structure
      }
    }
    
  @staticmethod
  def functions():
    return [
      Render.format_for_function_calling(list_all_services),
      Render.format_for_function_calling(create_service)
    ]

