#include "stt/simulation.hpp"
#include <cstdlib>
#include <iostream>
#include <limits>

static int checks = 0;
static void check(bool ok, const char* label) {
    ++checks;
    if (!ok) { std::cerr << "FAIL: " << label << '\n'; std::exit(1); }
}
static bool same(stt::Snapshot a, stt::Snapshot b) {
    return a.tick == b.tick && a.x_mm == b.x_mm && a.z_mm == b.z_mm &&
           a.target_hp == b.target_hp && a.cooldown_ticks == b.cooldown_ticks &&
           a.hits == b.hits;
}
int main() {
    stt::Simulation s;
    check(same(s.snapshot(), {}), "initial state");
    check(!s.step({std::numeric_limits<int>::max(), 0, true}) &&
          same(s.snapshot(), {}), "invalid x is atomic");
    check(!s.step({0, std::numeric_limits<int>::min(), true}) &&
          same(s.snapshot(), {}), "invalid z is atomic");
    s.step({0, 0, true});
    check(s.snapshot().target_hp == 100, "outside range misses");
    s.reset();
    for (int i = 0; i < 4; ++i) s.step({1, 0, false});
    s.step({0, 0, true});
    check(s.snapshot().target_hp == 100, "800 mm misses");
    s.reset();
    for (int i = 0; i < 5; ++i) s.step({1, 0, false});
    s.step({0, 0, true});
    check(s.snapshot().target_hp == 75, "750 mm inclusive hit");
    for (int i = 0; i < 60; ++i) s.step({0, 0, true});
    check(s.snapshot().hits == 1, "held input cannot repeat attack");
    s.step({}); s.step({0, 0, true});
    check(s.snapshot().hits == 2, "release rearms attack");
    s.step({}); s.step({0, 0, true});
    check(s.snapshot().hits == 2, "cooldown rejects fresh edge");
    for (int i = 0; i < 60; ++i) s.step({0, 0, true});
    check(s.snapshot().hits == 2, "rejected edge not queued");
    stt::Simulation timing;
    for (int i = 0; i < 10; ++i) timing.step({1, 0, false});
    timing.step({0, 0, true});
    for (int i = 0; i < 28; ++i) timing.step({});
    timing.step({0, 0, true});
    check(timing.snapshot().hits == 1 && timing.snapshot().cooldown_ticks == 1,
          "attack before 30 ticks rejected");
    timing.step({}); timing.step({0, 0, true});
    check(timing.snapshot().hits == 2, "attack after cooldown accepted");
    for (int attack = 0; attack < 5; ++attack) {
        for (int i = 0; i < 30; ++i) s.step({});
        s.step({0, 0, true});
    }
    check(s.snapshot().hits == 4 && s.snapshot().target_hp == 0,
          "dead target cannot receive repeated rewards or damage");
    s.reset();
    for (int i = 0; i < 1000; ++i) s.step({1, 1, false});
    check(s.snapshot().x_mm == 5000 && s.snapshot().z_mm == 5000, "positive bounds");
    for (int i = 0; i < 1000; ++i) s.step({-1, -1, false});
    check(s.snapshot().x_mm == -5000 && s.snapshot().z_mm == -5000, "negative bounds");
    s.reset(); s.step({1, 1, false});
    check(s.snapshot().x_mm == 35 && s.snapshot().z_mm == 35, "bounded diagonal");
    s.reset();
    check(same(s.snapshot(), {}), "reset clears state");
    stt::Simulation a, b;
    bool replay_ok = true;
    for (int i = 0; i < 100000; ++i) {
        const stt::Input input{i % 3 - 1, (i / 7) % 3 - 1, i % 31 == 0};
        replay_ok = a.step(input) && b.step(input) &&
                    same(a.snapshot(), b.snapshot()) && replay_ok;
    }
    check(replay_ok && a.snapshot().tick == 100000, "100000 tick deterministic replay");
    std::cout << checks << " checks passed\n";
}
