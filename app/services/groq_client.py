"""
Groq AI Client for MALABRO eShop AI Assistant
Provides OpenAI-compatible interface to Groq's LLM API
"""
from openai import OpenAI
from typing import List, Dict, Any, Optional
from app.core.config import settings
import json

class GroqClient:
    """Client for interacting with Groq's OpenAI-compatible API"""
    
    def __init__(self):
        self.client = OpenAI(
            api_key=settings.GROQ_API_KEY,
            base_url="https://api.groq.com/openai/v1"
        )
        self.default_model ="openai/gpt-oss-120b"
        
        
    async def chat_with_tools(
        self, 
        message: str, 
        tools: Optional[List[Dict[str, Any]]] = None,
        system_prompt: str = None
    ) -> Dict[str, Any]:
        """
        Chat with Groq using MCP tools for shop data access
        
        Args:
            message: User's question/request
            tools: Available MCP tools for function calling
            system_prompt: Custom system prompt (optional)
            
        Returns:
            Groq API response with tool calls if needed
        """
        if system_prompt is None:
            system_prompt = """You are MALABRO eShop AI Assistant. You help administrators manage their online grocery store.

You have access to real-time shop data through tools. Use these tools to:
- Check inventory status and stock levels
- Monitor pending orders and payments  
- Analyze sales performance and trends
- Provide business insights and recommendations

Always be helpful, professional, and provide actionable insights based on the current shop data."""

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": message}
        ]
        
        try:
            if tools:
                response = self.client.chat.completions.create(
                    model=self.default_model,
                    messages=messages,
                    tools=tools,
                    tool_choice="auto",
                    temperature=0.1  # Lower temperature for more consistent responses
                )
            else:
                response = self.client.chat.completions.create(
                    model=self.default_model,
                    messages=messages,
                    temperature=0.1
                )
                
            return {
                "success": True,
                "response": response,
                "message": response.choices[0].message.content if response.choices else None,
                "tool_calls": response.choices[0].message.tool_calls if response.choices and hasattr(response.choices[0].message, 'tool_calls') else None
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "message": f"Sorry, I encountered an error: {str(e)}"
            }
    
    def format_shop_context(self, context_data: Dict[str, Any]) -> str:
        """
        Format shop data context for AI understanding
        
        Args:
            context_data: Dictionary containing shop metrics and data
            
        Returns:
            Formatted string for AI context
        """
        context_parts = []
        
        if "inventory" in context_data:
            inv = context_data["inventory"]
            context_parts.append(f"Inventory: {inv.get('total_products', 0)} products, {len(inv.get('low_stock_items', []))} low stock")
            
        if "orders" in context_data:
            orders = context_data["orders"]
            context_parts.append(f"Orders: {orders.get('pending_count', 0)} pending, €{orders.get('pending_amount', 0):.2f} pending revenue")
            
        if "analytics" in context_data:
            analytics = context_data["analytics"]
            context_parts.append(f"Today: {analytics.get('orders_count', 0)} orders, €{analytics.get('revenue', 0):.2f} revenue")
            
        return " | ".join(context_parts) if context_parts else "No shop data available"

    def chat_completion(self, message: str, system_prompt: str = "", context: Dict[str, Any] = None) -> str:
        """
        Enhanced chat completion method with MCP tools for Mala-IA-Bro
        
        Args:
            message: User message
            system_prompt: System prompt with context
            context: Shop context data
            
        Returns:
            AI response text
        """
        try:
            messages = []
            
            if system_prompt:
                messages.append({"role": "system", "content": system_prompt})
                
            messages.append({"role": "user", "content": message})
            
            # Define available MCP tools for the AI
            tools = [
                {
                    "type": "function",
                    "function": {
                        "name": "search_products",
                        "description": "Search for specific products by name to get exact stock quantities, prices, and details",
                        "parameters": {
                            "type": "object",
                            "properties": {
                                "query": {
                                    "type": "string",
                                    "description": "Product name to search for (e.g., 'tomates', 'aubergines')"
                                },
                                "limit": {
                                    "type": "integer",
                                    "description": "Maximum number of results to return",
                                    "default": 10
                                }
                            },
                            "required": ["query"]
                        }
                    }
                },
                {
                    "type": "function",
                    "function": {
                        "name": "get_inventory_summary",
                        "description": "Get overall inventory statistics and low stock alerts",
                        "parameters": {
                            "type": "object",
                            "properties": {},
                            "required": []
                        }
                    }
                },
                {
                    "type": "function",
                    "function": {
                        "name": "get_recent_orders",
                        "description": "Get recent orders and sales data",
                        "parameters": {
                            "type": "object",
                            "properties": {
                                "limit": {
                                    "type": "integer",
                                    "description": "Number of recent orders to fetch",
                                    "default": 10
                                }
                            },
                            "required": []
                        }
                    }
                }
            ]
            
            response = self.client.chat.completions.create(
                model=self.default_model,
                messages=messages,
                tools=tools,
                tool_choice="auto",
                temperature=0.1,
                max_tokens=800
            )
            
            # Handle tool calls if present
            if response.choices[0].message.tool_calls:
                return self._handle_tool_calls(response.choices[0].message, messages)
            else:
                return response.choices[0].message.content if response.choices else "Désolé, je n'ai pas pu générer une réponse."
            
        except Exception as e:
            return f"Désolé, une erreur s'est produite: {str(e)}"
    
    def _handle_tool_calls(self, assistant_message, messages: List[Dict]) -> str:
        """Handle tool calls from the AI and execute MCP functions"""
        import requests
        
        messages.append({
            "role": "assistant", 
            "content": assistant_message.content,
            "tool_calls": [tc.model_dump() for tc in assistant_message.tool_calls]
        })
        
        for tool_call in assistant_message.tool_calls:
            function_name = tool_call.function.name
            function_args = json.loads(tool_call.function.arguments)
            
            try:
                # Call the appropriate MCP endpoint
                if function_name == "search_products":
                    url = "http://localhost:8000/api/v1/ai-tools/products/search"
                    params = {"query": function_args.get("query", ""), "limit": function_args.get("limit", 10)}
                    response = requests.get(url, params=params)
                    tool_result = response.json() if response.status_code == 200 else {"error": "Failed to search products"}
                    
                elif function_name == "get_inventory_summary":
                    url = "http://localhost:8000/api/v1/ai-tools/inventory/summary"
                    response = requests.get(url)
                    tool_result = response.json() if response.status_code == 200 else {"error": "Failed to get inventory"}
                    
                elif function_name == "get_recent_orders":
                    url = "http://localhost:8000/api/v1/ai-tools/orders/recent"
                    params = {"limit": function_args.get("limit", 10)}
                    response = requests.get(url, params=params)
                    tool_result = response.json() if response.status_code == 200 else {"error": "Failed to get orders"}
                    
                else:
                    tool_result = {"error": f"Unknown function: {function_name}"}
                
                # Add tool result to messages
                messages.append({
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "content": json.dumps(tool_result)
                })
                
            except Exception as e:
                messages.append({
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "content": json.dumps({"error": str(e)})
                })
        
        # Get final response from AI with tool results
        final_response = self.client.chat.completions.create(
            model=self.default_model,
            messages=messages,
            temperature=0.1,
            max_tokens=800,
            tool_choice="none"  # Prevent additional tool calls in final response
        )
        
        return final_response.choices[0].message.content if final_response.choices else "Désolé, je n'ai pas pu traiter votre demande."

# Global instance
groq_client = GroqClient()
