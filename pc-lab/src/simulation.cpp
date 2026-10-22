#include "stt/simulation.hpp"
#include <algorithm>
#include <limits>

namespace stt {
bool Simulation::step(Input input) noexcept {
    if (input.x < -1 || input.x > 1 || input.z < -1 || input.z > 1 ||
        state_.tick == std::numeric_limits<std::uint64_t>::max()) return false;
    ++state_.tick;
    if (state_.cooldown_ticks > 0) --state_.cooldown_ticks;
    // Diagonals use 35 mm per axis (49.497 mm total), never faster than axial.
    const int distance = (input.x != 0 && input.z != 0) ? 35 : step_mm;
    state_.x_mm = std::clamp(state_.x_mm + input.x * distance,
                           -arena_limit_mm, arena_limit_mm);
    state_.z_mm = std::clamp(state_.z_mm + input.z * distance,
                           -arena_limit_mm, arena_limit_mm);
    if (input.attack && !attack_held_ && state_.cooldown_ticks == 0) {
        state_.cooldown_ticks = attack_cooldown_ticks;
        const std::int64_t dx = state_.x_mm - 1000;
        const std::int64_t dz = state_.z_mm;
        if (state_.target_hp > 0 && dx * dx + dz * dz <=
            std::int64_t{attack_range_mm} * attack_range_mm) {
            state_.target_hp = std::max(0, state_.target_hp - damage);
            ++state_.hits;
        }
    }
    attack_held_ = input.attack;
    return true;
}
}
