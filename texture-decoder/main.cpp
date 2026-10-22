#include <algorithm>
#include <cstdint>
#include <filesystem>
#include <fstream>
#include <iostream>
#include <stdexcept>
#include <string>
#include <vector>

namespace fs = std::filesystem;
using Bytes = std::vector<uint8_t>;
static void require(bool condition, const char* message) {
    if (!condition) throw std::runtime_error(message);
}
static uint32_t word(const Bytes& b, size_t p) {
    require(p <= b.size() && b.size() - p >= 4, "truncated header/table");
    uint32_t value = 0;
    for (unsigned i = 0; i < 4; ++i) value |= uint32_t(b[p + i]) << (8 * i);
    return value;
}
static uint64_t number(const std::string& text) {
    require(!text.empty() && text.find_first_not_of("0123456789") == std::string::npos,
            "expected unsigned decimal integer");
    size_t end = 0;
    const auto value = std::stoull(text, &end);
    require(end == text.size(), "invalid integer");
    return value;
}
struct Image { uint32_t width, height; Bytes rgba; };
static Image decode(const Bytes& b, uint64_t mip) {
    require(word(b, 0) == 0x00584554, "not TEX");
    const auto flags = word(b, 4), dimensions = word(b, 8), format = word(b, 12);
    require((flags & 0xfff) == 0xa5, "only TEX A5 supported");
    require((flags >> 28) == 2 && ((flags >> 24) & 15) == 0,
            "only normal 2D textures with size_shift zero supported");
    require((format & 255) == 1, "only one texture supported");
    require((format >> 16) == 1, "unsupported texture layout flags");
    const uint32_t type = (format >> 8) & 255;
    require(type == 3 || type == 17, "only ABGR8888 and BGR888 supported");
    const uint32_t width = (dimensions >> 6) & 8191, height = dimensions >> 19;
    const uint32_t levels = dimensions & 63;
    require(width >= 8 && height >= 8 && width <= 4096 && height <= 4096 &&
            (width & (width - 1)) == 0 && (height & (height - 1)) == 0,
            "dimensions must be powers of two from 8 to 4096");
    require(levels >= 1 && levels <= 13 && mip < levels, "invalid mip selection/count");
    const size_t base = 16 + size_t(levels) * 4;
    require(base <= b.size(), "truncated offset table");
    const size_t channels = type == 3 ? 4 : 3;
    size_t expected = 0, selected = 0;
    uint32_t w = width, h = height, sw = 0, sh = 0;
    for (uint32_t i = 0; i < levels; ++i) {
        // Sub-8 mip padding is deliberately unsupported until independently verified.
        require(w >= 8 && h >= 8, "sub-8 mip layout unsupported");
        require(word(b, 16 + size_t(i) * 4) == expected,
                "mip offsets must be contiguous, relative to pixel data, and start at zero");
        if (i == mip) { selected = expected; sw = w; sh = h; }
        expected += size_t(w) * h * channels;
        w /= 2; h /= 2;
    }
    require(expected == b.size() - base, "payload length does not match all mip levels");
    Image image{sw, sh, Bytes(size_t(sw) * sh * 4)};
    for (uint32_t y = 0; y < sh; ++y) {
        for (uint32_t x = 0; x < sw; ++x) {
            size_t morton = 0;
            for (unsigned bit = 0; bit < 3; ++bit) {
                morton |= size_t((x >> bit) & 1) << (bit * 2);
                morton |= size_t((y >> bit) & 1) << (bit * 2 + 1);
            }
            const size_t tile = size_t(y / 8) * (sw / 8) + x / 8;
            const size_t src = base + selected + (tile * 64 + morton) * channels;
            const size_t dst = (size_t(y) * sw + x) * 4;
            const size_t a = channels == 4 ? 1 : 0;
            image.rgba[dst] = b[src + a + 2];
            image.rgba[dst + 1] = b[src + a + 1];
            image.rgba[dst + 2] = b[src + a];
            image.rgba[dst + 3] = channels == 4 ? b[src] : 255;
        }
    }
    return image;
}
int main(int argc, char** argv) {
    try {
        require(argc >= 2, "usage: stt-tex INPUT --out NEW_DIRECTORY [--offset N --size N --mip N]");
        fs::path input = argv[1], output;
        uint64_t offset = 0, length = 0, mip = 0;
        bool has_size = false;
        std::vector<std::string> seen;
        for (int i = 2; i < argc; i += 2) {
            require(i + 1 < argc, "missing option value");
            const std::string option = argv[i];
            require(std::find(seen.begin(), seen.end(), option) == seen.end(), "duplicate option");
            seen.push_back(option);
            if (option == "--out") output = argv[i + 1];
            else if (option == "--offset") offset = number(argv[i + 1]);
            else if (option == "--size") { length = number(argv[i + 1]); has_size = true; }
            else if (option == "--mip") mip = number(argv[i + 1]);
            else throw std::runtime_error("unknown option");
        }
        require(!output.empty(), "--out required");
        const auto total = fs::file_size(input);
        require(offset <= total, "input offset outside file");
        if (!has_size) length = total - offset;
        require(length >= 20 && length <= 128 * 1024 * 1024 && length <= total - offset,
                "invalid input range (limit 128 MiB)");
        std::ifstream source(input, std::ios::binary);
        require(bool(source), "cannot open input read-only");
        source.seekg(static_cast<std::streamoff>(offset));
        Bytes bytes(static_cast<size_t>(length));
        source.read(reinterpret_cast<char*>(bytes.data()), static_cast<std::streamsize>(length));
        require(bool(source), "input read failed");
        const auto image = decode(bytes, mip);
        require(fs::create_directory(output), "output directory must be new");
        std::ofstream target(output / "image.pam", std::ios::binary);
        target << "P7\nWIDTH " << image.width << "\nHEIGHT " << image.height
               << "\nDEPTH 4\nMAXVAL 255\nTUPLTYPE RGB_ALPHA\nENDHDR\n";
        target.write(reinterpret_cast<const char*>(image.rgba.data()),
                     static_cast<std::streamsize>(image.rgba.size()));
        target.close();
        require(bool(target), "output write failed");
        std::cout << "TEX A5 mip=" << mip << " width=" << image.width
                  << " height=" << image.height << " RGBA_bytes=" << image.rgba.size() << '\n';
        return 0;
    } catch (const std::exception& e) {
        std::cerr << "error: " << e.what() << '\n';
        return 1;
    }
}
