// Generic state-in/state-out harness; generated headers stay outside Git.
#include "translated.hpp"
#include <iostream>
#include <limits>
int main() {
    static_assert(std::numeric_limits<std::uint32_t>::digits == 32);
    ArmState s;
    while (std::cin >> s.cpsr) {
        for (auto& value : s.r) if (!(std::cin >> value)) return 1;
        const bool ok = translated_leaf(s);
        std::cout << (ok ? 1 : 0) << ' ' << s.cpsr;
        for (const auto value : s.r) std::cout << ' ' << value;
        std::cout << '\n';
    }
    return std::cin.eof() ? 0 : 1;
}
