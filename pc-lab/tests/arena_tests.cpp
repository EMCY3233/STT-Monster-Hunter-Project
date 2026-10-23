#include "stt/arena.hpp"
#include <cstdlib>
#include <iostream>
#include <limits>

static void require(bool value, const char* message) {
    if (!value) { std::cerr << message << '\n'; std::exit(1); }
}
static stt::Input replay(std::uint64_t tick) {
    return {tick < 10 ? 1 : 0, 0,
            tick == 10 || tick == 40 || tick == 70 || tick == 100};
}
int main() {
    stt::FixedClock clock;
    int ticks = 0;
    for (int i = 0; i < 1000; ++i) ticks += clock.advance(1000000);
    require(ticks == 60, "one second must produce exactly 60 updates");
    require(clock.advance(-1) == 0, "negative elapsed time");
    require(clock.advance(std::numeric_limits<std::int64_t>::max()) == 15,
            "stall budget and overflow protection");
    clock.reset();
    require(clock.advance(16666666) == 0 && clock.advance(1) == 1,
            "fractional update carry");
    stt::Arena a;
    for (int i = 0; i < 20; ++i) a.step({-1, 0, false});
    for (int i = 0; i < 1000; ++i) a.step({0, 1, false});
    require(a.snapshot().x_mm == -1000 && a.snapshot().z_mm == 800,
            "obstacle contact must stop without penetration");
    for (int i = 0; i < 100; ++i) {
        a.step({1, 1, false});
        require(!stt::Arena::blocked(a.snapshot().x_mm, a.snapshot().z_mm),
                "diagonal sliding must remain outside obstacle");
    }
    require(a.snapshot().z_mm > 2200, "sliding must allow passing obstacle");
    const auto before = a.snapshot();
    require(!a.step({2, 0, true}) && a.snapshot().tick == before.tick,
            "invalid input is atomic");
    a.reset();
    stt::Arena b;
    for (int i = 0; i < 120; ++i) a.step(replay(a.snapshot().tick));
    stt::FixedClock schedule;
    for (int frame = 0; frame < 200; ++frame) {
        const int updates = schedule.advance(10000000);
        for (int i = 0; i < updates; ++i) b.step(replay(b.snapshot().tick));
    }
    require(a.snapshot().tick == 120 && b.snapshot().tick == 120 &&
            a.snapshot().x_mm == b.snapshot().x_mm &&
            a.snapshot().target_hp == 0 && b.snapshot().target_hp == 0 &&
            a.snapshot().hits == 4 && b.snapshot().hits == 4,
            "render schedule independent scripted combat replay");
    std::uint32_t seed = 42;
    for (int i = 0; i < 100000; ++i) {
        seed = seed * 1664525u + 1013904223u;
        a.step({static_cast<int>(seed % 3) - 1,
                static_cast<int>((seed / 7) % 3) - 1, false});
        const auto s = a.snapshot();
        require(!stt::Arena::blocked(s.x_mm, s.z_mm) &&
                s.x_mm >= -5000 && s.x_mm <= 5000 &&
                s.z_mm >= -5000 && s.z_mm <= 5000,
                "seeded walk must respect solid and arena bounds");
    }
    std::cout << "Arena, clock, replay and 100000-step collision checks passed\n";
}
