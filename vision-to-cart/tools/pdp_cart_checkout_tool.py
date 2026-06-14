from typing import Dict, Any, List

# Core router helper
from data_services.data_services_router import DataServicesRouter

def run_cart_action(payload: Dict[str, Any]) -> Dict[str, Any]:
    """
    Executes mock PDP lookup and Cart session actions:
    - view_pdp: Retrieve full PDP catalog properties.
    - add_to_cart: Append product to session cart stored in cache.
    - get_cart: Retrieve current cart items.
    """
    action = payload.get("action", "get_cart")
    session_id = payload.get("session_id", "default")
    router = DataServicesRouter()
    
    cart_cache_key = f"cart:{session_id}"
    
    if action == "view_pdp":
        product_id = payload.get("product_id")
        if not product_id:
            raise ValueError("Missing 'product_id' for view_pdp action.")
        product = router.get_product(product_id)
        if not product:
            return {"status": "error", "message": f"Product {product_id} not found."}
        return {"status": "success", "action": action, "product": product}
        
    elif action == "add_to_cart":
        product_id = payload.get("product_id")
        if not product_id:
            raise ValueError("Missing 'product_id' for add_to_cart action.")
            
        product = router.get_product(product_id)
        if not product:
            return {"status": "error", "message": f"Product {product_id} not found."}

        # Fetch current cart
        cart = router.get_cache(cart_cache_key) or []
        cart.append(product)
        router.set_cache(cart_cache_key, cart, ttl_seconds=3600) # Save for 1 hour
        
        return {
            "status": "success",
            "action": action,
            "message": f"Added '{product['name']}' to cart.",
            "cart_count": len(cart),
            "cart": cart
        }
        
    elif action == "get_cart":
        cart = router.get_cache(cart_cache_key) or []
        total_price = sum(item.get("price", 0) for item in cart)
        return {
            "status": "success",
            "action": action,
            "cart": cart,
            "cart_count": len(cart),
            "total_price": total_price
        }

    elif action == "remove_from_cart":
        product_id = payload.get("product_id")
        if not product_id:
            raise ValueError("Missing 'product_id' for remove_from_cart action.")
        cart = router.get_cache(cart_cache_key) or []
        cart = [item for item in cart if item.get("product_id") != product_id]
        router.set_cache(cart_cache_key, cart, ttl_seconds=3600)
        total_price = sum(item.get("price", 0) for item in cart)
        return {
            "status": "success",
            "action": action,
            "message": f"Removed '{product_id}' from cart.",
            "cart_count": len(cart),
            "cart": cart,
            "total_price": total_price
        }

    elif action == "clear_cart":
        router.set_cache(cart_cache_key, [], ttl_seconds=3600)
        return {
            "status": "success",
            "action": action,
            "message": "Cart cleared.",
            "cart_count": 0,
            "cart": [],
            "total_price": 0
        }

    return {"status": "error", "message": f"Unknown cart action: {action}"}
