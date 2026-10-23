#include <algorithm>
#include <array>
#include <cmath>
#include <cstdint>
#include <cstring>
#include <filesystem>
#include <fstream>
#include <iomanip>
#include <iostream>
#include <limits>
#include <set>
#include <sstream>
#include <stdexcept>
#include <string>
#include <vector>

namespace fs = std::filesystem;
using U = uint64_t;
using Bytes = std::vector<unsigned char>;
void require(bool good, const char* message) { if (!good) throw std::runtime_error(message); }
void span(U at, U size, U limit) { require(at <= limit && size <= limit - at, "range outside input"); }
U value(const Bytes& b, U at, unsigned width = 4) {
    span(at, width, b.size()); U result = 0;
    for (unsigned i = 0; i < width; ++i) result |= U(b[size_t(at) + i]) << (8 * i);
    return result;
}
Bytes read(const fs::path& path) {
    const auto size = fs::file_size(path);
    require(size <= 32 * 1024 * 1024, "input exceeds 32 MiB budget");
    std::ifstream f(path, std::ios::binary); require(bool(f), "cannot open input read-only");
    Bytes b(static_cast<size_t>(size));
    if (size) f.read(reinterpret_cast<char*>(b.data()), static_cast<std::streamsize>(size));
    require(bool(f), "input read failed"); return b;
}
struct Region { U at, size; };
void disjoint(std::vector<Region> regions) {
    regions.erase(std::remove_if(regions.begin(), regions.end(), [](const Region& r){return !r.size;}), regions.end());
    std::sort(regions.begin(), regions.end(), [](const Region& a, const Region& b){return a.at < b.at;});
    for (size_t i = 1; i < regions.size(); ++i)
        require(regions[i].at >= regions[i - 1].at + regions[i - 1].size, "overlapping structural regions");
}
std::string text(const Bytes& b, U at, U size) {
    span(at, size, b.size()); std::string s; bool terminated = false;
    for (U i = 0; i < size; ++i) {
        const auto c = b[size_t(at + i)];
        if (!c) { terminated = true; break; }
        require(c >= 32 && c < 127, "unsupported non-ASCII/control character"); s += char(c);
    }
    require(terminated && !s.empty(), "empty/unterminated name"); return s;
}
std::string json(const std::string& s) {
    std::string result = "\"";
    for (char c : s) { if (c == '\\' || c == '"') result += '\\'; result += c; }
    return result + "\"";
}
uint32_t material_hash(const std::string& s) {
    uint32_t c = 0xffffffff;
    for (unsigned char byte : s) {
        c ^= byte;
        for (unsigned bit = 0; bit < 8; ++bit) c = (c >> 1) ^ ((c & 1) ? 0xedb88320u : 0u);
    }
    return c; // Complement of the usual finalized CRC32; not a unique identity.
}
double floating(const Bytes& b, U at) {
    static_assert(sizeof(float) == 4 && std::numeric_limits<float>::is_iec559, "IEEE754 float required");
    const auto bits = static_cast<uint32_t>(value(b, at)); float f;
    std::memcpy(&f, &bits, 4); require(std::isfinite(f), "nonfinite vertex attribute"); return f;
}
struct Resource { U type; std::string path; };
struct Descriptor { U tag, index, hash; };
struct Material { U hash; std::vector<Descriptor> descriptors; };
struct Mrl { std::vector<Resource> resources; std::vector<Material> materials; };
Mrl parse_mrl(const Bytes& b) {
    require(value(b, 0) == 0x004c524d && value(b, 4) == 32, "only MRL32 supported");
    const U count = value(b, 8), nres = value(b, 12), res = value(b, 20), mat = value(b, 24);
    require(count <= 4096 && nres <= 4096, "MRL count budget exceeded");
    span(res, nres * 76, b.size()); span(mat, count * 60, b.size());
    require(res >= 28 && res + nres * 76 == mat, "unsupported MRL table layout");
    Mrl result;
    for (U i = 0; i < nres; ++i) {
        const U at = res + i * 76, type = value(b, at);
        result.resources.push_back({type, type ? text(b, at + 12, 64) : ""});
    }
    std::vector<Region> blocks;
    for (U i = 0; i < count; ++i) {
        const U at = mat + i * 60, size = value(b, at + 8), n = value(b, at + 24) & 4095;
        const U ptr = value(b, at + 52); span(ptr, size, b.size());
        require(ptr >= mat + count * 60 && n * 12 <= size, "invalid MRL descriptor block");
        blocks.push_back({ptr, size}); Material material{value(b, at + 4), {}};
        for (U j = 0; j < n; ++j)
            material.descriptors.push_back({value(b, ptr + j * 12), value(b, ptr + j * 12 + 4), value(b, ptr + j * 12 + 8)});
        result.materials.push_back(material);
    }
    disjoint(blocks); return result;
}
struct Vertex { std::array<double, 3> p, normal; std::array<double, 2> uv; };
struct Result { std::string obj, mtl, report; };
Result convert(const Bytes& b, const Mrl* mrl) {
    require(b.size() >= 128 && value(b, 0) == 0x00444f4d && value(b, 4, 2) == 230, "only MOD230 supported");
    require(value(b, 6, 2) == 0 && value(b, 36) == 0, "only unskinned static models supported");
    const U meshes = value(b, 8, 2), materials = value(b, 10, 2), nv = value(b, 12), ni = value(b, 16);
    const U vbsize = value(b, 24), groups = value(b, 32), gp = value(b, 44), mp = value(b, 48);
    const U meshp = value(b, 52), vb = value(b, 56), ib = value(b, 60);
    require(meshes > 0 && meshes <= 4096 && materials > 0 && materials <= 4096 &&
            nv <= 1000000 && ni <= 4000000 && groups <= 4096, "invalid MOD counts/budget");
    std::vector<Region> regions{{0, 128}, {gp, groups * 32}, {mp, materials * 128},
        {meshp, meshes * 48}, {vb, vbsize}};
    for (const auto& r : regions) span(r.at, r.size, b.size());
    std::set<U> group_ids;
    for (U i = 0; i < groups; ++i)
        require(group_ids.insert(value(b, gp + i * 32)).second, "duplicate group ID unsupported");
    require(ib <= b.size(), "index buffer outside input");
    const U index_available = b.size() - ib;
    // Some observed MOD230 files overdeclare the global count by one u16.
    // Mesh windows must still be fully present; no bytes or indices are invented.
    const U shortfall = ni * 2 > index_available ? ni * 2 - index_available : 0;
    require((shortfall == 0 || shortfall == 2) && ib % 2 == 0, "global index declaration exceeds supported shortfall/alignment");
    regions.push_back({ib, std::min(ni * 2, index_available)}); disjoint(regions);
    std::ostringstream obj, mtl, report; obj << std::setprecision(17);
    obj << "# Static MOD230; native coordinates/UVs; neutral materials, no textures\nmtllib materials.mtl\n";
    report << "{\"schema\":1,\"coordinate_system_verified\":false,\"textures_assigned\":false,"
           << "\"skeleton_converted\":false,\"global_index_shortfall_bytes\":" << shortfall << ",\"materials\":[";
    std::set<std::string> material_names;
    for (U i = 0; i < materials; ++i) {
        const auto name = text(b, mp + i * 128, 128); const auto hash = material_hash(name);
        require(material_names.insert(name).second, "duplicate MOD material name unsupported");
        std::vector<const Material*> matches;
        if (mrl) for (const auto& material : mrl->materials) if (material.hash == hash) matches.push_back(&material);
        if (i) report << ',';
        report << "{\"index\":" << i << ",\"name\":" << json(name) << ",\"complement_crc32\":" << hash
               << ",\"mrl_record_matches\":" << matches.size() << ",\"candidate_resource_slots\":[";
        bool first = true;
        if (matches.size() == 1) for (const auto& d : matches[0]->descriptors) if ((d.tag & 15) == 3) {
            if (!first) report << ',';
            first = false; const bool in_range = d.index > 0 && d.index <= mrl->resources.size();
            report << "{\"value\":" << d.index << ",\"parameter_hash\":" << d.hash
                   << ",\"one_based_index_in_range\":" << (in_range ? "true" : "false") << ",\"path\":";
            if (in_range && mrl->resources[size_t(d.index - 1)].type)
                report << json(mrl->resources[size_t(d.index - 1)].path);
            else report << "null";
            report << '}';
        }
        report << "]}";
        require(report.tellp() <= 16 * 1024 * 1024, "material report budget exceeded");
        mtl << "newmtl material_" << i << "\nKd 0.7 0.7 0.7\nd 1\n\n";
    }
    report << "],\"meshes\":["; U base = 1, vertex_total = 0, triangle_total = 0, index_total = 0;
    for (U mesh = 0; mesh < meshes; ++mesh) {
        const U at = meshp + mesh * 48, count = value(b, at + 2, 2), d0 = value(b, at + 4), d1 = value(b, at + 8);
        const U start = value(b, at + 12), stream = value(b, at + 16), format = value(b, at + 20);
        const U first_index = value(b, at + 24), index_count = value(b, at + 28), adjustment = value(b, at + 32);
        const U material = (d0 >> 12) & 4095, group = d0 & 4095;
        require(count > 0 && format == 0x59dc400b && ((d1 >> 16) & 255) == 28 &&
                ((d1 >> 24) & 63) == 4 && ((d1 >> 3) & 31) == 0, "unsupported vertex layout/skinning/primitive");
        require(material < materials, "mesh material index out of range");
        require(group_ids.count(group) != 0, "mesh references missing group ID");
        span(start, count, nv); span(first_index, index_count, ni);
        const U relative = (start + adjustment) * 28 + stream;
        span(relative, count * 28, vbsize); span(ib + first_index * 2, index_count * 2, b.size());
        require(vertex_total + count <= 250000, "export vertex budget exceeded"); vertex_total += count;
        require(index_count <= 1000000 - index_total, "export index budget exceeded"); index_total += index_count;
        std::vector<Vertex> vertices;
        obj << "o mesh_" << mesh << "\nusemtl material_" << material << '\n';
        for (U i = 0; i < count; ++i) {
            const U p = vb + relative + i * 28; Vertex v{};
            for (unsigned c = 0; c < 3; ++c) {
                v.p[c] = floating(b, p + c * 4);
                const int raw = b[size_t(p + 12 + c)];
                v.normal[c] = std::max(-1.0, (raw < 128 ? raw : raw - 256) / 127.0);
            }
            for (unsigned c = 0; c < 2; ++c) v.uv[c] = floating(b, p + 16 + c * 4);
            vertices.push_back(v); obj << "v " << v.p[0] << ' ' << v.p[1] << ' ' << v.p[2] << '\n';
        }
        for (const auto& v : vertices) obj << "vt " << v.uv[0] << ' ' << v.uv[1] << '\n';
        for (const auto& v : vertices) obj << "vn " << v.normal[0] << ' ' << v.normal[1] << ' ' << v.normal[2] << '\n';
        std::array<U, 2> previous{}; U run = 0, faces = 0, repeated = 0, zero = 0;
        for (U i = 0; i < index_count; ++i) {
            const U raw = value(b, ib + (first_index + i) * 2, 2);
            if (raw == 65535) { run = 0; continue; }
            require(raw >= start && raw - start < count, "index outside mesh vertices"); const U c = raw - start;
            if (run >= 2) {
                U a = previous[0], second = previous[1]; if (run & 1) std::swap(a, second);
                if (a == second || a == c || second == c) ++repeated;
                else {
                    const auto& p = vertices[size_t(a)].p; const auto& q = vertices[size_t(second)].p; const auto& r = vertices[size_t(c)].p;
                    std::array<double, 3> u{}, v{}, cross{};
                    for (unsigned j = 0; j < 3; ++j) { u[j] = q[j] - p[j]; v[j] = r[j] - p[j]; }
                    cross = {u[1]*v[2]-u[2]*v[1], u[2]*v[0]-u[0]*v[2], u[0]*v[1]-u[1]*v[0]};
                    if (cross[0] == 0 && cross[1] == 0 && cross[2] == 0) ++zero;
                    else {
                        obj << 'f'; for (U id : {a, second, c}) obj << ' ' << base + id << '/' << base + id << '/' << base + id;
                        obj << '\n'; ++faces;
                    }
                }
            }
            previous = {previous[1], c}; ++run;
        }
        triangle_total += faces;
        require(obj.tellp() <= 128 * 1024 * 1024, "OBJ report budget exceeded");
        if (mesh) report << ',';
        report << "{\"mesh\":" << mesh << ",\"group_id\":" << group
               << ",\"lod_mask_raw\":" << (d0 >> 24) << ",\"visible_bit_raw\":" << (d1 & 1)
               << ",\"material_index\":" << material << ",\"vertices\":" << count
               << ",\"triangles\":" << faces << ",\"repeated_index_triangles_removed\":" << repeated
               << ",\"zero_area_triangles_removed\":" << zero << '}'; base += count;
    }
    report << "],\"vertices\":" << vertex_total << ",\"triangles\":" << triangle_total
           << ",\"material_slot_semantics_verified\":false,\"mrl_match_method\":\"name complement CRC32; collisions possible\"}\n";
    return {obj.str(), mtl.str(), report.str()};
}
void write(const fs::path& p, const std::string& data) {
    std::ofstream f(p, std::ios::binary); f.write(data.data(), static_cast<std::streamsize>(data.size())); f.close();
    require(bool(f), "output write failed");
}
void private_destination(const fs::path& output) {
    auto current = fs::weakly_canonical(output);
    for (;;) {
        require(!fs::exists(current / ".git"), "asset output inside Git checkout is not allowed");
        const auto parent = current.parent_path();
        if (parent == current || parent.empty()) break;
        current = parent;
    }
}
int main(int argc, char** argv) {
    try {
        require(argc >= 2, "usage: stt-model INPUT.mod [--mrl INPUT.mrl] --out NEW_DIRECTORY");
        fs::path out, material; std::set<std::string> seen;
        for (int i = 2; i < argc; ++i) {
            const std::string option = argv[i]; require(seen.insert(option).second, "duplicate option");
            require(i + 1 < argc, "missing option value"); const std::string v = argv[++i];
            require(v.rfind("--", 0) != 0, "missing option value");
            if (option == "--out") out = v;
            else if (option == "--mrl") material = v;
            else throw std::runtime_error("unknown option");
        }
        require(!out.empty(), "--out required"); private_destination(out);
        const auto source = read(argv[1]); Mrl mrl;
        if (!material.empty()) mrl = parse_mrl(read(material));
        const auto result = convert(source, material.empty() ? nullptr : &mrl);
        require(fs::create_directory(out), "output directory must be new");
        write(out / "model.obj", result.obj); write(out / "materials.mtl", result.mtl); write(out / "report.json", result.report);
        std::cout << result.report; return 0;
    } catch (const std::exception& e) { std::cerr << "error: " << e.what() << '\n'; return 1; }
}
