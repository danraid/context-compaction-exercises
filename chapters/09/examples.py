# Listing 1
from dataclasses import dataclass

@dataclass(frozen=True)
class Call:
    input_tokens: int
    cached_tokens: int
    output_tokens: int

    def validate(self):
        assert self.input_tokens >= 0 and self.output_tokens >= 0
        assert 0 <= self.cached_tokens <= self.input_tokens

RATES = {
    "uncached_per_million": 4.0,
    "cached_per_million": 0.40,
    "output_per_million": 12.0,
}
SPEEDS = {
    "uncached_per_second": 20_000,
    "cached_per_second": 100_000,
    "output_per_second": 2_000,
}
TOOL_SECONDS_PER_FOREGROUND = 0.5

plans = {
    "A no compaction": {
        "foreground": [
            Call(100_000, 80_000, 2_000),
            Call(110_000, 80_000, 2_000),
            Call(120_000, 80_000, 2_000),
        ],
        "extra_calls": [], "tool_cost": 0.0, "extra_seconds": 0.0,
    },
    "B synchronous rewrite": {
        "foreground": [
            Call(60_000, 0, 2_000),
            Call(70_000, 50_000, 2_000),
            Call(80_000, 60_000, 2_000),
        ],
        "extra_calls": [Call(100_000, 80_000, 5_000)],
        "tool_cost": 0.0, "extra_seconds": 0.0,
    },
    "C stable-prefix fold": {
        "foreground": [
            Call(90_000, 80_000, 2_000),
            Call(100_000, 80_000, 2_000),
            Call(110_000, 80_000, 2_000),
        ],
        "extra_calls": [], "tool_cost": 0.03, "extra_seconds": 0.4,
    },
}

def cost_and_seconds(call):
    call.validate()
    uncached = call.input_tokens - call.cached_tokens
    cost = (
        uncached * RATES["uncached_per_million"]
        + call.cached_tokens * RATES["cached_per_million"]
        + call.output_tokens * RATES["output_per_million"]
    ) / 1_000_000
    seconds = (
        uncached / SPEEDS["uncached_per_second"]
        + call.cached_tokens / SPEEDS["cached_per_second"]
        + call.output_tokens / SPEEDS["output_per_second"]
    )
    return cost, seconds

print("Rates:", RATES)
print("Speeds:", SPEEDS)
print("Tool latency per foreground call:", TOOL_SECONDS_PER_FOREGROUND)
print("Recovery charges: $0; recovery calls: 0")
for name, plan in plans.items():
    calls = plan["foreground"] + plan["extra_calls"]
    totals = [cost_and_seconds(c) for c in calls]
    cost = sum(c for c, _ in totals) + plan["tool_cost"]
    seconds = (
        sum(s for _, s in totals)
        + len(plan["foreground"]) * TOOL_SECONDS_PER_FOREGROUND
        + plan["extra_seconds"]
    )
    fg_input = sum(c.input_tokens for c in plan["foreground"])
    fg_cached = sum(c.cached_tokens for c in plan["foreground"])
    print(f"{name}: cost=${cost:.3f}, seconds={seconds:.1f}, "
          f"foreground hit rate={fg_cached / fg_input:.1%}")