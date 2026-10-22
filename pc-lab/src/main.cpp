#include "stt/simulation.hpp"
#include <iostream>

int main() {
    stt::Simulation simulation;
    // Finite, reproducible script: approach dummy, attack four times, idle.
    for (int tick = 0; tick < 600; ++tick) {
        stt::Input input;
        input.x = tick < 10 ? 1 : 0;
        input.attack = tick == 10 || tick == 40 || tick == 70 || tick == 100;
        if (!simulation.step(input)) return 2;
    }
    const auto s = simulation.snapshot();
    std::cout << "STT original synthetic PC lab; not MH4U execution\n"
              << "tick=" << s.tick << " x_mm=" << s.x_mm
              << " z_mm=" << s.z_mm << " hp=" << s.target_hp
              << " hits=" << s.hits << '\n';
    return s.tick == 600 && s.x_mm == 500 && s.z_mm == 0 &&
           s.target_hp == 0 && s.hits == 4 ? 0 : 1;
}
