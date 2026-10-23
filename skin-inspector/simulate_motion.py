"""Original synthetic motion experiment; no game assets or LMT decoding.
Matrix LBS is compared with an independently expressed nested-rotation oracle.
"""
import argparse
import json
import math
import pathlib


def require(ok, message):
    if not ok:
        raise ValueError(message)


def identity():
    return [[float(i == j) for j in range(4)] for i in range(4)]


def multiply(a, b):
    return [[sum(a[i][k]*b[k][j] for k in range(4)) for j in range(4)] for i in range(4)]


def translation(x, y):
    result = identity()
    result[3][:2] = [x, y]
    return result


def rotation(angle):
    c, s = math.cos(angle), math.sin(angle)
    result = identity()
    result[0][:2], result[1][:2] = [c, s], [-s, c]
    return result


def rotate_point(point, angle):
    # Direct 2D analytic oracle, without matrix multiplication or hierarchy code.
    x, y = point
    return (math.cos(angle)*x-math.sin(angle)*y,
            math.sin(angle)*x+math.cos(angle)*y)


def oracle(position, joint, angles, offset):
    point = (position[0]-joint, position[1])
    for level in range(joint, -1, -1):
        point = rotate_point(point, angles[level])
        if level:
            point = (point[0]+1, point[1])
    return (point[0]+offset[0], point[1]+offset[1])


def run():
    vertices = []
    for segment in range(41):
        x = segment/20
        joint = min(1, int(x))
        weight = round((x-joint)*255)
        for y in (-.12, .12):
            vertices.append({'position': [x, y], 'joints': [joint, joint+1], 'weights': [255-weight, weight]})
    frames = []
    maximum = {'oracle_error': 0., 'palette_swap_error': 0., 'hierarchy_order_error': 0., 'unchecked_bad_weight_error': 0.}
    invalid_vertices = sum(0 < v['weights'][1] < 255 for v in vertices)
    for step in range(241):
        phase = step/240
        angles = [.25*math.sin(2*math.pi*phase), .7*math.sin(2*math.pi*phase), .6*math.sin(4*math.pi*phase)]
        offset = [.2*math.sin(2*math.pi*phase), .15*(math.cos(2*math.pi*phase)-1)]
        local = [multiply(rotation(angles[0]), translation(*offset))]
        local.extend(multiply(rotation(angle), translation(1, 0)) for angle in angles[1:])
        correct_global, wrong_global = [local[0]], [local[0]]
        for index in (1, 2):
            correct_global.append(multiply(local[index], correct_global[index-1]))
            wrong_global.append(multiply(wrong_global[index-1], local[index]))
        effective = [multiply(translation(-j, 0), correct_global[j]) for j in range(3)]
        wrong_effective = [multiply(translation(-j, 0), wrong_global[j]) for j in range(3)]
        states = {name: [] for name in ('correct', 'palette_swap', 'hierarchy_order', 'unchecked_bad_weights')}
        for vertex in vertices:
            p, joints, weights = vertex['position'], vertex['joints'], vertex['weights']
            expected = [0., 0.]
            for joint, weight in zip(joints, weights):
                q = oracle(p, joint, angles, offset)
                for axis in (0, 1):
                    expected[axis] += weight/255*q[axis]
            for name in states:
                blended = [0., 0.]
                trial_weights = weights[:]
                if name == 'unchecked_bad_weights' and 0 < weights[1] < 255:
                    trial_weights[0] -= min(20, trial_weights[0])
                for joint, weight in zip(joints, trial_weights):
                    mapped = [0, 2, 1][joint] if name == 'palette_swap' else joint
                    matrix = (wrong_effective if name == 'hierarchy_order' else effective)[mapped]
                    v = [*p, 0., 1.]
                    for axis in (0, 1):
                        blended[axis] += weight/255*sum(v[k]*matrix[k][axis] for k in range(4))
                states[name].append(blended)
                error = max(abs(blended[axis]-expected[axis]) for axis in (0, 1))
                key = {'correct': 'oracle_error', 'palette_swap': 'palette_swap_error',
                       'hierarchy_order': 'hierarchy_order_error', 'unchecked_bad_weights': 'unchecked_bad_weight_error'}[name]
                maximum[key] = max(maximum[key], error)
        frames.append({'time': step/60, 'states': states})
    rest_swap_error = max(abs(a[axis]-b[axis]) for a, b in zip(frames[0]['states']['correct'], frames[0]['states']['palette_swap']) for axis in (0, 1))
    require(maximum['oracle_error'] < 1e-12, 'matrix implementation disagrees with analytic oracle')
    require(rest_swap_error < 1e-12, 'rest ambiguity experiment invalid')
    require(maximum['palette_swap_error'] > .1, 'dynamic palette error not exposed')
    require(maximum['hierarchy_order_error'] > .1, 'noncommuting hierarchy error not exposed')
    require(maximum['unchecked_bad_weight_error'] > .01 and invalid_vertices > 0, 'bad-weight control invalid')
    return {'schema': 1, 'synthetic_only': True, 'game_animation_decoded': False,
            'seconds': 4, 'frames': len(frames), 'vertex_records': len(vertices),
            'rest_palette_swap_error': rest_swap_error, 'invalid_weight_vertex_records': invalid_vertices,
            'bad_weights_shown_unchecked_for_diagnosis': True,
            'summary': maximum, 'frames_data': frames}


def export(result, directory):
    directory = pathlib.Path(directory).resolve()
    require(not directory.exists(), 'destination exists')
    require(not any((p/'.git').exists() for p in (directory, *directory.parents)), 'destination inside Git')
    payload = json.dumps(result, separators=(',', ':'), allow_nan=False)
    template = pathlib.Path(__file__).with_name('simulation.html').read_text(encoding='utf-8')
    html = template.replace('/*SIMULATION*/null', payload)
    directory.mkdir(parents=True)
    (directory/'index.html').write_text(html, encoding='utf-8')
    (directory/'results.json').write_text(json.dumps({k: v for k, v in result.items() if k != 'frames_data'}, indent=2), encoding='utf-8')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--out', type=pathlib.Path)
    args = parser.parse_args()
    result = run()
    if args.out:
        export(result, args.out)
    print(json.dumps({k: v for k, v in result.items() if k != 'frames_data'}, indent=2))
