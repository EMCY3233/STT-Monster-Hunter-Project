// Original procedural PC study. No commercial assets or game-format inputs.
#include <GLFW/glfw3.h>
#include "stt/arena.hpp"
#include <array>
#include <chrono>
#include <cmath>
#include <cstddef>
#include <filesystem>
#include <fstream>
#include <iostream>
#include <stdexcept>
#include <string>
#include <vector>

namespace {
constexpr GLenum vertex_shader = 0x8B31, fragment_shader = 0x8B30;
constexpr GLenum compile_status = 0x8B81, link_status = 0x8B82;
constexpr GLenum array_buffer = 0x8892, dynamic_draw = 0x88E8;
// Only the OpenGL entry points used here; resolved after a 3.3 core context.
template<class T> T load(const char* name) {
    const auto pointer = glfwGetProcAddress(name);
    if (!pointer) throw std::runtime_error(std::string("Missing OpenGL entry: ") + name);
    return reinterpret_cast<T>(pointer);
}
#define GL_ENTRY(ret, name, ...) using name##Type = ret (APIENTRY*)(__VA_ARGS__); name##Type name = load<name##Type>("gl" #name)
struct GL {
    GL_ENTRY(GLuint, CreateShader, GLenum);
    GL_ENTRY(void, ShaderSource, GLuint, GLsizei, const char* const*, const GLint*);
    GL_ENTRY(void, CompileShader, GLuint);
    GL_ENTRY(void, GetShaderiv, GLuint, GLenum, GLint*);
    GL_ENTRY(void, GetShaderInfoLog, GLuint, GLsizei, GLsizei*, char*);
    GL_ENTRY(void, DeleteShader, GLuint);
    GL_ENTRY(GLuint, CreateProgram, void);
    GL_ENTRY(void, AttachShader, GLuint, GLuint);
    GL_ENTRY(void, LinkProgram, GLuint);
    GL_ENTRY(void, GetProgramiv, GLuint, GLenum, GLint*);
    GL_ENTRY(void, GetProgramInfoLog, GLuint, GLsizei, GLsizei*, char*);
    GL_ENTRY(void, UseProgram, GLuint);
    GL_ENTRY(void, DeleteProgram, GLuint);
    GL_ENTRY(void, GenVertexArrays, GLsizei, GLuint*);
    GL_ENTRY(void, BindVertexArray, GLuint);
    GL_ENTRY(void, DeleteVertexArrays, GLsizei, const GLuint*);
    GL_ENTRY(void, GenBuffers, GLsizei, GLuint*);
    GL_ENTRY(void, BindBuffer, GLenum, GLuint);
    GL_ENTRY(void, BufferData, GLenum, std::ptrdiff_t, const void*, GLenum);
    GL_ENTRY(void, DeleteBuffers, GLsizei, const GLuint*);
    GL_ENTRY(void, EnableVertexAttribArray, GLuint);
    GL_ENTRY(void, VertexAttribPointer, GLuint, GLint, GLenum, GLboolean, GLsizei, const void*);
    GL_ENTRY(GLint, GetUniformLocation, GLuint, const char*);
    GL_ENTRY(void, UniformMatrix4fv, GLint, GLsizei, GLboolean, const GLfloat*);
};
#undef GL_ENTRY
struct V { float x, y, z; };
V sub(V a, V b) { return {a.x-b.x,a.y-b.y,a.z-b.z}; }
float dot(V a, V b) { return a.x*b.x+a.y*b.y+a.z*b.z; }
V cross(V a, V b) { return {a.y*b.z-a.z*b.y,a.z*b.x-a.x*b.z,a.x*b.y-a.y*b.x}; }
V normalized(V a) { const float d=std::sqrt(dot(a,a)); return {a.x/d,a.y/d,a.z/d}; }
using Matrix = std::array<float,16>;
Matrix multiply(const Matrix& a, const Matrix& b) {
    Matrix c{};
    for (int j=0;j<4;++j) for (int i=0;i<4;++i)
        for (int k=0;k<4;++k) c[j*4+i] += a[k*4+i]*b[j*4+k];
    return c;
}
Matrix camera(V eye, V target, float aspect) {
    const V f=normalized(sub(target,eye)), s=normalized(cross(f,{0,1,0})), u=cross(s,f);
    const Matrix view{s.x,u.x,-f.x,0,s.y,u.y,-f.y,0,s.z,u.z,-f.z,0,
                      -dot(s,eye),-dot(u,eye),dot(f,eye),1};
    const float q=1.0f/std::tan(0.9f/2), n=0.1f, far=80;
    const Matrix projection{q/aspect,0,0,0,0,q,0,0,0,0,(far+n)/(n-far),-1,
                            0,0,2*far*n/(n-far),0};
    return multiply(projection,view);
}
struct Vertex { V p, color; };
void box(std::vector<Vertex>& out, V lo, V hi, V color) {
    const V p[]={{lo.x,lo.y,lo.z},{hi.x,lo.y,lo.z},{hi.x,hi.y,lo.z},{lo.x,hi.y,lo.z},
                 {lo.x,lo.y,hi.z},{hi.x,lo.y,hi.z},{hi.x,hi.y,hi.z},{lo.x,hi.y,hi.z}};
    const int faces[][4]={{0,1,2,3},{5,4,7,6},{4,0,3,7},{1,5,6,2},{3,2,6,7},{4,5,1,0}};
    for (int face=0;face<6;++face) {
        const float shade=0.65f+0.06f*static_cast<float>(face);
        const V c{color.x*shade,color.y*shade,color.z*shade};
        for (const int k : {0,1,2,0,2,3}) out.push_back({p[faces[face][k]],c});
    }
}
class Renderer {
    GL gl;
    GLuint program=0, vao=0, vbo=0;
    GLint matrix=-1;
    GLuint shader(GLenum type, const char* source) {
        const GLuint id=gl.CreateShader(type);
        gl.ShaderSource(id,1,&source,nullptr); gl.CompileShader(id);
        GLint ok=0; gl.GetShaderiv(id,compile_status,&ok);
        if (!ok) {
            char log[2048]{}; gl.GetShaderInfoLog(id,2048,nullptr,log);
            gl.DeleteShader(id); throw std::runtime_error(log);
        }
        return id;
    }
public:
    Renderer() {
        const char* vs="#version 330 core\nlayout(location=0) in vec3 p; layout(location=1) in vec3 c; uniform mat4 m; out vec3 color; void main(){color=c;gl_Position=m*vec4(p,1);}";
        const char* fs="#version 330 core\nin vec3 color; out vec4 pixel; void main(){pixel=vec4(color,1);}";
        const GLuint a=shader(vertex_shader,vs);
        GLuint b=0;
        try { b=shader(fragment_shader,fs); }
        catch (...) { gl.DeleteShader(a); throw; }
        program=gl.CreateProgram(); gl.AttachShader(program,a); gl.AttachShader(program,b);
        gl.LinkProgram(program); gl.DeleteShader(a); gl.DeleteShader(b);
        GLint ok=0; gl.GetProgramiv(program,link_status,&ok);
        if (!ok) {
            char log[2048]{}; gl.GetProgramInfoLog(program,2048,nullptr,log);
            gl.DeleteProgram(program); throw std::runtime_error(log);
        }
        matrix=gl.GetUniformLocation(program,"m");
        gl.GenVertexArrays(1,&vao); gl.BindVertexArray(vao);
        gl.GenBuffers(1,&vbo); gl.BindBuffer(array_buffer,vbo);
        gl.EnableVertexAttribArray(0); gl.EnableVertexAttribArray(1);
        gl.VertexAttribPointer(0,3,GL_FLOAT,GL_FALSE,sizeof(Vertex),nullptr);
        gl.VertexAttribPointer(1,3,GL_FLOAT,GL_FALSE,sizeof(Vertex),
                               reinterpret_cast<void*>(offsetof(Vertex,color)));
        glEnable(GL_DEPTH_TEST);
    }
    ~Renderer() { gl.DeleteBuffers(1,&vbo); gl.DeleteVertexArrays(1,&vao); gl.DeleteProgram(program); }
    void draw(stt::Snapshot state, int width, int height, float yaw, float elevation) {
        glViewport(0,0,width,height); glClearColor(0.055f,0.075f,0.11f,1);
        glClear(GL_COLOR_BUFFER_BIT|GL_DEPTH_BUFFER_BIT);
        std::vector<Vertex> vertices;
        vertices.reserve(10000);
        box(vertices,{-5.2f,-0.2f,-5.2f},{5.2f,0,5.2f},{0.22f,0.3f,0.36f});
        for (int i=-5;i<=5;++i) {
            const float v=static_cast<float>(i);
            box(vertices,{v-0.01f,0,-5},{v+0.01f,0.004f,5},{0.4f,0.5f,0.55f});
            box(vertices,{-5,0,v-0.01f},{5,0.004f,v+0.01f},{0.4f,0.5f,0.55f});
        }
        box(vertices,{-1.5f,0,1},{-0.5f,1,2},{0.85f,0.45f,0.18f});
        box(vertices,{-5.25f,0,-5.25f},{5.25f,0.2f,-5.2f},{0.3f,0.5f,0.6f});
        box(vertices,{-5.25f,0,5.2f},{5.25f,0.2f,5.25f},{0.3f,0.5f,0.6f});
        box(vertices,{-5.25f,0,-5.2f},{-5.2f,0.2f,5.2f},{0.3f,0.5f,0.6f});
        box(vertices,{5.2f,0,-5.2f},{5.25f,0.2f,5.2f},{0.3f,0.5f,0.6f});
        const float x=static_cast<float>(state.x_mm)/1000, z=static_cast<float>(state.z_mm)/1000;
        box(vertices,{x-0.2f,0,z-0.2f},{x+0.2f,0.85f,z+0.2f},{0.2f,0.9f,0.75f});
        box(vertices,{x-0.14f,0.85f,z-0.14f},{x+0.14f,1.12f,z+0.14f},{0.85f,0.95f,0.92f});
        if (state.target_hp>0) {
            box(vertices,{0.8f,0,-0.2f},{1.2f,1.1f,0.2f},{0.9f,0.25f,0.25f});
            box(vertices,{0.6f,1.3f,-0.04f},{0.6f+0.008f*state.target_hp,1.38f,0.04f},{0.4f,1,0.3f});
        }
        const float horizontal=8*std::cos(elevation);
        const V target{x,0.5f,z};
        const Matrix m=camera({x+horizontal*std::sin(yaw),0.5f+8*std::sin(elevation),z+horizontal*std::cos(yaw)},target,
                              static_cast<float>(width)/static_cast<float>(height));
        gl.UseProgram(program); gl.UniformMatrix4fv(matrix,1,GL_FALSE,m.data());
        gl.BindVertexArray(vao); gl.BindBuffer(array_buffer,vbo);
        gl.BufferData(array_buffer,static_cast<std::ptrdiff_t>(vertices.size()*sizeof(Vertex)),vertices.data(),dynamic_draw);
        glDrawArrays(GL_TRIANGLES,0,static_cast<GLsizei>(vertices.size()));
        if (glGetError()!=GL_NO_ERROR) throw std::runtime_error("OpenGL draw error");
    }
};
struct Window {
    GLFWwindow* pointer=nullptr;
    Window(bool hidden) {
        glfwSetErrorCallback([](int code,const char* message){std::cerr<<"GLFW "<<code<<": "<<message<<'\n';});
        if (!glfwInit()) throw std::runtime_error("GLFW initialization failed");
        glfwWindowHint(GLFW_CONTEXT_VERSION_MAJOR,3); glfwWindowHint(GLFW_CONTEXT_VERSION_MINOR,3);
        glfwWindowHint(GLFW_OPENGL_PROFILE,GLFW_OPENGL_CORE_PROFILE);
        glfwWindowHint(GLFW_VISIBLE,hidden ? GLFW_FALSE : GLFW_TRUE);
        pointer=glfwCreateWindow(hidden ? 640 : 1280,hidden ? 360 : 720,"STT - original native arena",nullptr,nullptr);
        if (!pointer) { glfwTerminate(); throw std::runtime_error("OpenGL 3.3 context unavailable"); }
        glfwMakeContextCurrent(pointer); glfwSwapInterval(hidden ? 0 : 1);
    }
    ~Window() { glfwDestroyWindow(pointer); glfwTerminate(); }
};
void check_pixels(int width,int height,const std::filesystem::path& capture) {
    std::vector<unsigned char> rgb(static_cast<std::size_t>(width)*height*3);
    glPixelStorei(GL_PACK_ALIGNMENT,1); glReadBuffer(GL_BACK);
    glReadPixels(0,0,width,height,GL_RGB,GL_UNSIGNED_BYTE,rgb.data());
    if (glGetError()!=GL_NO_ERROR) throw std::runtime_error("Pixel read failed");
    int colorful=0;
    for (std::size_t i=0;i<rgb.size();i+=3)
        if (rgb[i+1]>rgb[i]+25 && rgb[i+1]>rgb[i+2]) ++colorful;
    if (colorful<50) throw std::runtime_error("Rendered player color absent");
    if (!capture.empty()) {
        if (std::filesystem::exists(capture)) throw std::runtime_error("Capture path already exists");
        std::ofstream out(capture,std::ios::binary);
        out<<"P6\n"<<width<<' '<<height<<"\n255\n";
        for (int y=height-1;y>=0;--y)
            out.write(reinterpret_cast<const char*>(rgb.data()+static_cast<std::size_t>(y)*width*3),width*3);
        if (!out) throw std::runtime_error("Capture write failed");
    }
    std::cout<<"rendered_player_pixels="<<colorful<<'\n';
}
}
int main(int argc,char** argv) {
    try {
        bool smoke=false;
        std::filesystem::path capture;
        for (int i=1;i<argc;++i) {
            const std::string arg=argv[i];
            if (arg=="--smoke") smoke=true;
            else if (arg=="--capture" && i+1<argc) capture=argv[++i];
            else throw std::runtime_error("Usage: stt_native_arena [--smoke] [--capture NEW.ppm]");
        }
        if (!capture.empty() && !smoke) throw std::runtime_error("Capture requires --smoke");
        Window window(smoke);
        std::cout<<"GL_VENDOR="<<glGetString(GL_VENDOR)<<"\nGL_RENDERER="<<glGetString(GL_RENDERER)
                 <<"\nGL_VERSION="<<glGetString(GL_VERSION)<<'\n';
        Renderer renderer;
        stt::Arena arena;
        stt::FixedClock clock;
        auto previous=std::chrono::steady_clock::now();
        float yaw=0.5f, elevation=0.65f;
        bool reset_held=false;
        for (int frame=0;!glfwWindowShouldClose(window.pointer);++frame) {
            glfwPollEvents();
            auto key=[&](int k){return glfwGetKey(window.pointer,k)==GLFW_PRESS;};
            if (key(GLFW_KEY_ESCAPE)) break;
            const auto now=std::chrono::steady_clock::now();
            const auto elapsed=std::chrono::duration_cast<std::chrono::nanoseconds>(now-previous).count();
            previous=now;
            const bool focused=glfwGetWindowAttrib(window.pointer,GLFW_FOCUSED)!=0;
            const bool reset=focused && key(GLFW_KEY_R);
            if (reset && !reset_held) { arena.reset(); clock.reset(); }
            reset_held=reset;
            const int updates=smoke ? 1 : (focused ? clock.advance(elapsed) : 0);
            if (!focused && !smoke) clock.reset();
            for (int tick=0;tick<updates;++tick) {
                const auto s=arena.snapshot();
                const stt::Input input=smoke ? stt::Input{s.tick<10 ? 1 : 0,0,s.tick==10||s.tick==40||s.tick==70||s.tick==100}
                    : stt::Input{int(key(GLFW_KEY_D))-int(key(GLFW_KEY_A)),int(key(GLFW_KEY_S))-int(key(GLFW_KEY_W)),key(GLFW_KEY_SPACE)};
                if (!arena.step(input)) throw std::runtime_error("Simulation input rejected");
                if (!smoke) {
                    yaw+=0.025f*(int(key(GLFW_KEY_RIGHT))-int(key(GLFW_KEY_LEFT)));
                    elevation=std::clamp(elevation+0.02f*(int(key(GLFW_KEY_UP))-int(key(GLFW_KEY_DOWN))),0.2f,1.3f);
                    yaw=std::remainder(yaw,6.283185307f);
                }
            }
            int width=0,height=0; glfwGetFramebufferSize(window.pointer,&width,&height);
            if (width>0 && height>0) renderer.draw(arena.snapshot(),width,height,yaw,elevation);
            const auto s=arena.snapshot();
            if (!smoke && frame%15==0) {
                const std::string title="STT original | WASD move | arrows camera | Space attack | R reset | HP "+std::to_string(s.target_hp)+" | hits "+std::to_string(s.hits);
                glfwSetWindowTitle(window.pointer,title.c_str());
            }
            if (smoke && frame==119) {
                if (width<=0 || height<=0) throw std::runtime_error("Empty framebuffer");
                check_pixels(width,height,capture);
                std::cout<<"tick="<<s.tick<<" hp="<<s.target_hp<<" hits="<<s.hits<<'\n';
                return s.tick==120 && s.x_mm==500 && s.z_mm==0 && s.target_hp==0 && s.hits==4 ? 0 : 1;
            }
            glfwSwapBuffers(window.pointer);
            if (!focused && !smoke) glfwWaitEventsTimeout(0.05);
        }
        if (smoke) throw std::runtime_error("Smoke interrupted before completion");
        return 0;
    } catch (const std::exception& e) { std::cerr<<e.what()<<'\n'; return 1; }
}
