from typing import TypedDict, Literal
from langgraph.graph import StateGraph, START, END
import random

class AgentState(TypedDict):
    player_name: str
    guesses: list[int]
    attempts: int
    lbound: int
    ubound: int
    target_number: int
    hint: str
    

def setup(state: AgentState) -> AgentState:
    """Greet the player and ask for his name."""
    print(f"Hello, {state['player_name']}! Let's play a game.")
    state['player_name'] = f"Hii, {state['player_name']}"
    state['guesses'] = []
    state['attempts'] = 0
    state['target_number'] = random.randint(1, 20)
    state['hint'] = "Game started guess the number"
    state['lbound'] = 1
    state['ubound'] = 20
    print(f"{state['player_name']} The game has begun. I'm thinking of a number between 1 and 20.")
    return state

def guess_node(state: AgentState) -> AgentState:
    """Ask the player to guess a number."""
    possible_guesses = [i for i in range(state['lbound'], state['ubound']) if i not in state['guesses']]
    if possible_guesses: 
        guess = random.choice(possible_guesses)
    else:
        guess = random.randint(state['lbound'], state['ubound'])
        
    state['guesses'].append(guess)
    state['attempts'] += 1
    print(f"Attempt {state['attempts']}: Guessing {guess} (Current range: {state['lbound']}-{state['ubound']})")
    return state


def hint_node(state: AgentState) -> AgentState:
    """Here we provide the hint based on the latest guess and update the bounds"""
    latest_guess = state['guesses'][-1]
    if latest_guess < state['target_number']:
        state['hint'] = f"The number {latest_guess} is too low. Try higher!"
        state['lbound'] = max(state['lbound'], latest_guess + 1)
        
        print(f"Hint: {state['hint']}")
    elif latest_guess > state['target_number']:
        state['hint'] = f"The number {latest_guess} is too high. Try lower!"
        state['ubound'] = min(state['ubound'], latest_guess - 1)
        
        print(f"Hint: {state['hint']}")
    else:
        state['hint'] = f"Correct! You found the number {state['target_number']} in {state['attempts']} attempts!"
        print(f"Hint: {state['hint']}")
        
        
    return state

def should_continue(state: AgentState) -> Literal["end", "continue"]:
    """Determine whether the game should continue."""
    if state['attempts'] > 7:
        print(f"You have exceeded the maximum number of attempts. Game over. The number was {state['target_number']}")
        return "end"
    elif state['target_number'] == state['guesses'][-1]:
        print(f"Congratulations! You guessed the number {state['target_number']} in {state['attempts']} attempts!")
        return "end"  
    else: 
        print(f"{state['attempts']}/7 is used")
        return "continue"
    


graph = StateGraph(AgentState)
graph.add_node("setup_node", setup)
graph.add_node("guess_node", guess_node)
graph.add_node("hint_node", hint_node)

graph.add_edge(START, "setup_node")
graph.add_edge("setup_node", "guess_node")
graph.add_edge("guess_node", "hint_node")
graph.add_conditional_edges(
    "hint_node",
    should_continue,
    {
        "end": END,
        "continue": "guess_node"
    }
    )

graph.set_entry_point("setup_node")

app = graph.compile()

result = app.invoke({"player_name": "Student", "guesses": [], "attempts": 0, "lower_bound": 1, "upper_bound": 20})

