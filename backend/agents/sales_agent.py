def handle_sales(stage):
    if stage == "start":
        return "Sure 👍 I can help you with a personal loan. How much amount are you looking for?"
    elif stage == "amount":
        return "Got it. What is your monthly salary?"
    return None
