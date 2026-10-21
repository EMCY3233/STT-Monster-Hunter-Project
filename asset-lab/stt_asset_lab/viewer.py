"""Stdlib Tk canvas mesh inspector; no game format decoder or network access."""
import time
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from .model import export, load, pose, AssetError
from .projection import project as project_point

def run(data):
    root = tk.Tk()
    root.title('STT Asset Lab — original project samples')
    root.geometry('1040x720')
    bar = ttk.Frame(root); bar.pack(fill='x')
    playing = tk.BooleanVar(value=True)
    bones_visible = tk.BooleanVar(value=True)
    selected = tk.StringVar(value=data['clips'][0]['name'])
    ttk.Checkbutton(bar, text='Play / pause', variable=playing).pack(side='left')
    selector = ttk.Combobox(bar, textvariable=selected, state='readonly', width=24)
    selector.pack(side='left')
    ttk.Checkbutton(bar, text='Bones', variable=bones_visible).pack(side='left')
    body = ttk.Frame(root); body.pack(fill='both', expand=True)
    hierarchy = ttk.Treeview(body, columns=('index',), show='tree')
    hierarchy.column('#0', width=230)
    hierarchy.pack(side='left', fill='y')
    canvas = tk.Canvas(body, background='#111c2b', highlightthickness=0)
    canvas.pack(side='left', fill='both', expand=True)
    status = tk.StringVar()
    ttk.Label(root, textvariable=status).pack(fill='x')
    state = {'data':data, 'time':0.0, 'last':time.monotonic(), 'yaw':0.5, 'zoom':120, 'drag':None}
    def refresh():
        d = state['data']; selector['values'] = [c['name'] for c in d['clips']]
        selected.set(d['clips'][0]['name']); state['time'] = 0
        hierarchy.delete(*hierarchy.get_children())
        for i, b in enumerate(d['bones']):
            hierarchy.insert('' if b['parent'] < 0 else str(b['parent']), 'end', iid=str(i), text=b['name'], open=True)
    def open_asset():
        path = filedialog.askopenfilename(filetypes=[('STT JSON','*.json')])
        if path:
            try:
                state['data'] = load(path); refresh()
            except (AssetError, OSError) as exc:
                messagebox.showerror('Rejected asset', str(exc))
    def save_asset():
        path = filedialog.asksaveasfilename(defaultextension='.json', filetypes=[('STT JSON','*.json')])
        if path:
            try: export(state['data'], path)
            except (AssetError, OSError) as exc: messagebox.showerror('Export failed', str(exc))
    ttk.Button(bar, text='Open STT JSON', command=open_asset).pack(side='left')
    ttk.Button(bar, text='Export STT JSON', command=save_asset).pack(side='left')
    ttk.Button(bar, text='Reset time', command=lambda:state.update(time=0.0)).pack(side='left')
    def drag(event):
        if state['drag'] is not None: state['yaw'] += (event.x-state['drag'])*0.01
        state['drag'] = event.x
    canvas.bind('<ButtonPress-1>', lambda e:state.update(drag=e.x))
    canvas.bind('<B1-Motion>', drag)
    canvas.bind('<ButtonRelease-1>', lambda e:state.update(drag=None))
    def zoom(delta): state['zoom'] = min(350,max(30,state['zoom']+delta))
    canvas.bind('<MouseWheel>', lambda e:zoom(10 if e.delta > 0 else -10))
    canvas.bind('<Button-4>', lambda e:zoom(10)); canvas.bind('<Button-5>', lambda e:zoom(-10))
    def draw():
        now = time.monotonic(); dt = min(0.1, now-state['last']); state['last'] = now
        if playing.get(): state['time'] += dt
        d = state['data']; index = [c['name'] for c in d['clips']].index(selected.get())
        joints, vertices = pose(d,index,state['time'])
        w,h = canvas.winfo_width(),canvas.winfo_height(); canvas.delete('all')
        def project(v):
            return project_point(v, state['yaw'], state['zoom'], w, h)
        points = [project(v) for v in vertices]
        for tri in sorted(d['triangles'],key=lambda t:sum(points[i][2] for i in t)):
            canvas.create_polygon(*[n for i in tri for n in points[i][:2]],fill='#326d95',outline='#83bed7')
        if bones_visible.get():
            for i,b in enumerate(d['bones']):
                x,y,_ = project(joints[i])
                if b['parent'] >= 0:
                    px,py,_ = project(joints[b['parent']]); canvas.create_line(px,py,x,y,fill='#ffce65',width=3)
                canvas.create_oval(x-4,y-4,x+4,y+4,fill='#fff0b2',outline='')
                canvas.create_text(x+8,y,text=b['name'],fill='#fff0b2',anchor='w')
        status.set(f"{d['name']} | STT Asset/1 | {len(vertices)} vertices | {len(joints)} bones | {selected.get()} {state['time']%d['clips'][index]['duration']:.2f}s | metres | drag: orbit · wheel: zoom")
        root.after(33,draw)
    selector.bind('<<ComboboxSelected>>',lambda e:state.update(time=0.0))
    refresh(); draw(); root.mainloop()
