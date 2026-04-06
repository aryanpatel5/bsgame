import random

import gradio as gr


def _to_int(v, name):
    """Coerce Gradio numeric inputs into an `int` (and reject non-integers)."""
    if v is None or isinstance(v, bool):
        # `bool` is a subclass of `int`; treat it as invalid user input here.
        raise gr.Error(f"{name} must be an integer.")
    if isinstance(v, int):
        return v
    if isinstance(v, float) and v.is_integer():
        return int(v)
    raise gr.Error(f"{name} must be an integer.")


def _is_prime(n):
    """Return True iff `n` is a prime number (trial division)."""
    if n < 2:
        return False
    if n % 2 == 0:
        return n == 2
    d = 3
    while d * d <= n:
        # Only need to test divisors up to sqrt(n); skip even candidates.
        if n % d == 0:
            return False
        d += 2
    return True


def _first_n_primes(n):
    """Generate the first `n` primes."""
    out, x = [], 2
    while len(out) < n:
        # Grow the list until we hit the requested count.
        if _is_prime(x):
            out.append(x)
        x += 1
    return out


def generate_list(kind, n, start, step):
    """Generate a deterministic list based on a preset."""
    if n <= 0:
        raise ValueError("List size must be > 0.")
    if kind == "evenly_spaced":
        if step <= 0:
            raise ValueError("Step must be > 0.")
        # List comprehension: fast + idiomatic for derived lists.
        return [start + i * step for i in range(n)]
    if kind == "primes":
        return _first_n_primes(n)
    if kind == "perfect_squares":
        return [i * i for i in range(1, n + 1)]
    raise ValueError("Unknown preset.")


def binary_search_trace(arr, target):
    """Binary search that records each step for the UI trace table."""
    rows = []
    low, high, step = 0, len(arr) - 1, 0
    while low <= high:
        step += 1
        # Integer midpoint to stay in array index space.
        mid = (low + high) // 2
        mid_value = arr[mid]
        if target == mid_value:
            rows.append([step, low, high, mid, mid_value, "found"])
            break
        if target < mid_value:
            rows.append([step, low, high, mid, mid_value, "left"])
            # Discard the right half (inclusive of `mid`).
            high = mid - 1
        else:
            rows.append([step, low, high, mid, mid_value, "right"])
            # Discard the left half (inclusive of `mid`).
            low = mid + 1
    return rows, len(rows)


def _state(arr=None, target=None, attempts=0, active=False, steps=0, trace=None, score=0):
    """Build the dict persisted inside `gr.State`."""
    return {
        "arr": arr,
        "target": target,
        "attempts": attempts,
        "active": active,
        "steps": steps,
        "trace": trace or [],
        "score": score,
    }


def _start_round(state, status):
    """Start a new round while preserving the current score."""
    arr = state.get("arr") if isinstance(state, dict) else None
    if not arr:
        raise gr.Error("Generate a set first.")
    score = int(state.get("score", 0)) if isinstance(state, dict) else 0

    # Choose a target and precompute its binary-search trace.
    target = random.choice(arr)
    trace, steps = binary_search_trace(arr, target)
    return (
        _state(arr=arr, target=target, attempts=0, active=True, steps=steps, trace=trace, score=score),
        str(target),
        status,
        str(score),
        gr.update(value=None, interactive=True),
        gr.update(interactive=True),
        gr.update(visible=False, value=[]),
        gr.update(visible=False),
    )


def on_preset_change(preset):
    # Only the evenly-spaced preset needs `start` and `step` controls.
    show = preset == "evenly_spaced"
    return gr.update(visible=show), gr.update(visible=show)


def on_generate_set(n, preset, start, step, state):
    """Validate inputs, generate the list, and reset round-specific UI."""
    # Gradio Number/Slider values can arrive as float; normalize up-front.
    n = _to_int(n, "List size")
    start = _to_int(start, "Start")
    step = _to_int(step, "Step")
    score = int(state.get("score", 0)) if isinstance(state, dict) else 0

    try:
        arr = generate_list(preset, n, start, step)
    except ValueError as e:
        raise gr.Error(str(e))

    # Dataframe expects rows; keep index alongside each value for clarity.
    list_rows = [[i, v] for i, v in enumerate(arr)]
    return (
        _state(arr=arr, score=score),
        list_rows,
        "-",
        "Set generated. Click Start Game.",
        str(score),
        gr.update(visible=False, value=[]),
        gr.update(value=None, interactive=False),
        gr.update(interactive=False),
        gr.update(visible=False),
    )


def on_start_game(state):
    # Simple wrapper to keep event wiring readable.
    return _start_round(state, "Game started. 3 tries.")


def on_restart_round(state):
    # Same logic as start, different status message.
    return _start_round(state, "New round. 3 tries.")


def on_submit_guess(guess, state):
    """Process a guess and return updated component values/props."""
    # Defensive checks: the UI can get out of sync with backend state.
    if not isinstance(state, dict) or not state.get("active") or not state.get("arr"):
        raise gr.Error("Start the game first.")

    guess = _to_int(guess, "Guess")
    # Compute next state explicitly so updates are predictable.
    attempts = int(state.get("attempts", 0)) + 1
    steps = int(state.get("steps", 0))
    trace = state.get("trace") or []
    target = state.get("target")
    arr = state.get("arr")
    score = int(state.get("score", 0))

    if guess == steps:
        score += 1
        # Correct: end the round, reveal trace, lock inputs.
        return (
            _state(arr=arr, target=target, attempts=attempts, active=False, steps=steps, trace=trace, score=score),
            str(target),
            f"Correct. Steps: {steps}.",
            gr.update(visible=True, value=trace),
            str(score),
            gr.update(interactive=False),
            gr.update(interactive=False),
            gr.update(visible=True),
        )

    if attempts >= 3:
        score -= 1
        # Out of tries: end the round, reveal trace, lock inputs.
        return (
            _state(arr=arr, target=target, attempts=attempts, active=False, steps=steps, trace=trace, score=score),
            str(target),
            f"No tries left. Steps: {steps}.",
            gr.update(visible=True, value=trace),
            str(score),
            gr.update(interactive=False),
            gr.update(interactive=False),
            gr.update(visible=True),
        )

    left = 3 - attempts
    # Still playing: keep inputs active and keep trace hidden.
    return (
        _state(arr=arr, target=target, attempts=attempts, active=True, steps=steps, trace=trace, score=score),
        str(target),
        f"Incorrect. Tries left: {left}.",
        gr.update(visible=False, value=[]),
        str(score),
        gr.update(interactive=True),
        gr.update(interactive=True),
        gr.update(visible=False),
    )


def on_reset():
    """Reset the UI back to defaults (including score)."""
    # Outputs must match the `outputs=[...]` order in the event binding.
    return (
        _state(score=0),
        [],
        "-",
        "",
        gr.update(value=20),
        gr.update(value="evenly_spaced"),
        gr.update(value=0, visible=True),
        gr.update(value=1, visible=True),
        gr.update(visible=False, value=[]),
        gr.update(value=None, interactive=False),
        gr.update(interactive=False),
        gr.update(value="0"),
        gr.update(visible=False),
    )


CSS = "#restart_btn button{font-size:20px;padding:18px 20px;width:100%}"


with gr.Blocks(title="Binary Search Steps Game") as demo:
    # UI layout + event wiring.
    gr.Markdown("# Binary Search Steps Game")

    state = gr.State(_state(score=0))

    with gr.Row():
        n = gr.Slider(5, 50, value=20, step=1, label="List size")
        preset = gr.Radio(["evenly_spaced", "primes", "perfect_squares"], value="evenly_spaced", label="Preset")

    with gr.Row():
        start = gr.Number(value=0, precision=0, label="Start", visible=True)
        step = gr.Number(value=1, precision=0, label="Step", visible=True)

    with gr.Row():
        generate_btn = gr.Button("Generate Set", variant="primary")
        start_btn = gr.Button("Start Game")
        restart_btn = gr.Button("Restart Game", variant="primary", visible=False, elem_id="restart_btn")
        reset_btn = gr.Button("Reset")

    list_df = gr.Dataframe(headers=["index", "value"], datatype=["number", "number"], value=[], label="List", interactive=False, wrap=True)

    with gr.Row():
        target_text = gr.Textbox(value="-", label="Target", interactive=False)
        status_text = gr.Textbox(value="", label="Status", interactive=False)
        score_text = gr.Textbox(value="0", label="Score", interactive=False)

    with gr.Row():
        guess = gr.Number(value=None, precision=0, label="Guess (steps)", interactive=False)
        submit_btn = gr.Button("Submit Guess", interactive=False)

    trace_df = gr.Dataframe(
        headers=["step", "low", "high", "mid", "mid_value", "decision"],
        datatype=["number", "number", "number", "number", "number", "str"],
        value=[],
        label="Trace",
        interactive=False,
        visible=False,
        wrap=True,
    )

    preset.change(on_preset_change, inputs=[preset], outputs=[start, step])

    generate_btn.click(on_generate_set, inputs=[n, preset, start, step, state], outputs=[state, list_df, target_text, status_text, score_text, trace_df, guess, submit_btn, restart_btn])
    start_btn.click(on_start_game, inputs=[state], outputs=[state, target_text, status_text, score_text, guess, submit_btn, trace_df, restart_btn])
    submit_btn.click(on_submit_guess, inputs=[guess, state], outputs=[state, target_text, status_text, trace_df, score_text, guess, submit_btn, restart_btn])
    restart_btn.click(on_restart_round, inputs=[state], outputs=[state, target_text, status_text, score_text, guess, submit_btn, trace_df, restart_btn])
    reset_btn.click(on_reset, inputs=[], outputs=[state, list_df, target_text, status_text, n, preset, start, step, trace_df, guess, submit_btn, score_text, restart_btn])


if __name__ == "__main__":
    demo.launch(css=CSS)
