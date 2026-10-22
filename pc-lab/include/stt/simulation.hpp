#pragma once
#include <cstdint>

namespace stt {
// All values and mechanics are original study parameters, not MH4U data.
struct Input { int x = 0; int z = 0; bool attack = false; };
struct Snapshot {
    std::uint64_t tick = 0;
    int x_mm = 0;
    int z_mm = 0;
    int target_hp = 100;
    int cooldown_ticks = 0;
    std::uint32_t hits = 0;
};
class Simulation {
public:
    static constexpr int tick_hz = 60;
    static constexpr int arena_limit_mm = 5000;
    static constexpr int step_mm = 50;
    static constexpr int attack_range_mm = 750;
    static constexpr int attack_cooldown_ticks = 30;
    static constexpr int damage = 25;
    // Target is fixed at (1000, 0) mm. Inputs must be -1, 0 or +1.
    // Invalid input or tick exhaustion rejects the entire step unchanged.
    bool step(Input input) noexcept;
    Snapshot snapshot() const noexcept { return state_; }
    void reset() noexcept { state_ = {}; attack_held_ = false; }
private:
    Snapshot state_{};
    bool attack_held_ = false;
};
}
