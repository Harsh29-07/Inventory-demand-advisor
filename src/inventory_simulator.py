"""
inventory_simulator.py
----------------------
Reusable functions for reorder point calculation and inventory simulation.
"""

from scipy.stats import norm


def calculate_reorder_point(train, lead_time=7, service_level=0.95):
    """
    Calculate the reorder point and safety stock based on historical demand.

    Parameters
    ----------
    train : pd.DataFrame  — training data with a 'sales' column
    lead_time : int       — days between placing and receiving an order
    service_level : float — target fill rate (e.g. 0.95 = 95%)

    Returns
    -------
    reorder_point : float
    safety_stock  : float
    """
    z             = norm.ppf(service_level)
    demand_std    = train['sales'].std()
    avg_demand    = train['sales'].mean()
    safety_stock  = z * demand_std * (lead_time ** 0.5)
    reorder_point = avg_demand * lead_time + safety_stock
    return reorder_point, safety_stock


def simulate_inventory(test, reorder_point, order_quantity,
                       initial_inventory=200, lead_time=7,
                       holding_cost_per_unit=1, stockout_cost_per_unit=5):
    """
    Simulate day-by-day inventory under a continuous review (s, Q) policy.

    Parameters
    ----------
    test                  : pd.DataFrame — test period data with 'sales' column
    reorder_point         : float        — trigger level to place an order
    order_quantity        : int          — fixed quantity ordered each time
    initial_inventory     : int          — starting inventory on day 0
    lead_time             : int          — days until order arrives
    holding_cost_per_unit : float        — cost per unit held per day
    stockout_cost_per_unit: float        — cost per unit of unmet demand

    Returns
    -------
    dict with keys: stockouts, holding_cost, stockout_cost, total_cost,
                    inventory_history
    """
    inventory         = initial_inventory
    inventory_history = []
    stockouts         = 0
    holding_cost      = 0
    stockout_cost     = 0
    order_pending     = False
    order_arrival_day = None

    for i in range(len(test)):
        demand = test['sales'].iloc[i]

        # Receive pending order
        if order_pending and i == order_arrival_day:
            inventory    += order_quantity
            order_pending = False

        # Fulfill demand
        if demand <= inventory:
            inventory -= demand
        else:
            shortfall      = demand - inventory
            stockouts     += shortfall
            stockout_cost += shortfall * stockout_cost_per_unit
            inventory      = 0

        # Daily holding cost on end-of-day inventory
        holding_cost += inventory * holding_cost_per_unit

        # Trigger reorder if at or below ROP
        if inventory <= reorder_point and not order_pending:
            order_pending     = True
            order_arrival_day = i + lead_time

        inventory_history.append(inventory)

    return {
        "stockouts":         stockouts,
        "holding_cost":      round(holding_cost, 2),
        "stockout_cost":     round(stockout_cost, 2),
        "total_cost":        round(holding_cost + stockout_cost, 2),
        "inventory_history": inventory_history,
    }
