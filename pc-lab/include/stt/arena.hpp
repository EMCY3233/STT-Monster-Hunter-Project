#pragma once
#include "simulation.hpp"
#include <algorithm>
#include <cstdint>

namespace stt {
// Original study obstacle, expanded by a 200 mm square actor footprint.
// Ground is a fixed horizontal plane; this is not a general physics engine.
class Arena {
public:
    static bool blocked(int x, int z) noexcept {
        return x > -1700 && x < -300 && z > 800 && z < 2200;
    }
    bool step(Input input) noexcept {
        if (input.x < -1 || input.x > 1 || input.z < -1 || input.z > 1)
            return false;
        const auto s = simulation_.snapshot();
        const int distance = input.x && input.z ? 35 : Simulation::step_mm;
        // X then Z sliding, each bounded step is shorter than the solid width.
        // Use original distance on both axes even when one axis is blocked.
        int x = std::clamp(s.x_mm + input.x * distance, -5000, 5000);
        if (blocked(x, s.z_mm)) input.x = 0;
        x = input.x ? x : s.x_mm;
        const int z = std::clamp(s.z_mm + input.z * distance, -5000, 5000);
        if (blocked(x, z)) input.z = 0;
        // Core changes diagonal distance if an axis is removed. Test that actual
        // final position too, otherwise a slide could enter the expanded solid.
        auto trial = simulation_;
        if (!trial.step(input)) return false;
        const auto next = trial.snapshot();
        if (blocked(next.x_mm, next.z_mm)) {
            input.x = 0; input.z = 0;
        }
        return simulation_.step(input);
    }
    Snapshot snapshot() const noexcept { return simulation_.snapshot(); }
    void reset() noexcept { simulation_.reset(); }
private:
    Simulation simulation_;
};

class FixedClock {
public:
    // Discard time beyond 250 ms after a stall; at most 15 updates per draw.
    int advance(std::int64_t nanoseconds) noexcept {
        if (nanoseconds <= 0) return 0;
        phase_ += std::min<std::int64_t>(nanoseconds, 250000000) * 60;
        const int ticks = static_cast<int>(phase_ / 1000000000);
        phase_ %= 1000000000;
        return ticks;
    }
    void reset() noexcept { phase_ = 0; }
private:
    std::int64_t phase_ = 0;
};
}
