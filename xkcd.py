import numpy as np
from scipy.interpolate import interp1d
from matplotlib import cm, pyplot as plt
import jokerScript


# Automating XKCD-Style Narrative Charts:
# https://source.opennews.org/articles/automating-xkcd-style-narrative-charts/

# Create xkcd-Style Narrative Charts with numpy, scipy and matplotlib:
# https://codegolf.stackexchange.com/questions/39728/create-xkcd-style-narrative-charts

# Movie Narrative Charts Poster:
# https://store.xkcd.com/products/movie-narrative-charts-poster


def sorted_event(prev, event):
    """ Returns a new sorted event, where the order of the groups is
    similar to the order in the previous event. """
    similarity = lambda a, b: len(set(a) & set(b)) - len(set(a) ^ set(b))
    most_similar = lambda g: max(prev, key=lambda pg: similarity(g, pg))
    return sorted(event, key=lambda g: prev.index(most_similar(g)))


def parse_data(chars, events):
    """ Turns the input data into 3 "tables":
    - characters: {character_id: character_name}
    - timelines: {character_id: [y0, y1, y2, ...],
    - deaths: {character_id: (x, y)}
    where x and y are the coordinates of a point in the xkcd like plot.
    """
    characters = dict(enumerate(chars))
    deaths = {}
    timelines = {char: [] for char in characters}

    def coords(character, event):
        for gi, group in enumerate(event):
            if character in group:
                ci = group.index(character)
                return (gi + 0.5 * ci / len(group)) / len(event)
        return None

    t = 0
    previous = events[0]
    for event in events:
        if isinstance(event[0], list):
            previous = event = sorted_event(previous, event)
            for character in [c for c in characters if c not in deaths]:
                timelines[character] += [coords(character, event)] * 2
            t += 2
        else:
            for char in set(event) - set(deaths):
                deaths[char] = (t-1, timelines[char][-1])
    return characters, timelines, deaths


def find_max(timelines, scenes):
    """
    Find the y value of the main events in every period
    - timelines: {character_id: [y0, y1, y2, ...],
    - scenes: [[s0], [s1], [s2], ...]
    where s are a list of chad_id participates in that main scene.
    """
    # find the longest timeline:
    max_len = 0
    for timeline in timelines.values():
        if len(timeline) > max_len:
            max_len = len(timeline)

    # find the max y value that corresponding to an event:
    times = []
    for i in range(max_len):
        max_y = 0
        for char, timeline in timelines.items():
            if i < len(timeline) and timeline[i] is not None:
                if timeline[i] > max_y and char in scenes[i//2]:
                    max_y = timeline[i]
        times.append(max_y)
    return times


def plot_data(chars, timelines, deaths, scenes, annotations):
    """
    Draws a nice xkcd like movie timeline
     - chars: {character_id: character_name}
    - timelines: {character_id: [y0, y1, y2, ...],
    - deaths: {character_id: (x, y)}
    - scenes: [[s0], [s1], [s2], ...]
    - annotation: [a0, a1, a2, ...]
    when a is the location of the according scenes s0.
    """
    plt.xkcd()  # because python :)

    fig = plt.figure(figsize=(60, 20))
    ax = fig.add_subplot(111)
    ax.get_xaxis().set_visible(False)
    ax.get_yaxis().set_visible(False)
    ax.set_xlim([0, max(map(len, timelines.values()))])

    # find a different color to every characters:
    color_floats = np.linspace(0, 1, len(chars))
    color_of = lambda char_id: cm.tab20(color_floats[char_id])

    # draw the characters line using a linear interpolation between the according timelines:
    for char_id in sorted(chars):
        y = timelines[char_id]
        f = interp1d(np.linspace(0, len(y)-1, len(y)), y, kind='linear')
        x = np.linspace(0, len(y)-1, len(y))
        y_max = find_max(timelines, scenes)
        for i in range(0, len(x) - 1, 2):
            plt.annotate(annotations[i//2], (0.5 + x[i], y_max[i]), fontsize='medium',
                     fontweight='bold')
        ax.plot(x, f(x), c=color_of(char_id))

    # add the special notation the the location when some characters died:
    x, y = zip(*(deaths[char_id] for char_id in sorted(deaths)))
    ax.scatter(x, y, c=np.array(list(map(color_of, sorted(deaths)))), zorder=99, s=40)

    for char_id in deaths.keys():
        point = deaths.get(char_id)
        plt.annotate(chars[char_id] + " DEAD", (point[0] + 0.15, point[1]), fontsize='small',
                     fontstyle='italic')

    ax.legend(list(map(chars.get, sorted(chars))), loc='best', ncol=4)
    print ('testplot.png saved')
    fig.savefig('testplot.png')


def update_events(events, ind_tony, ind_natasha):
    """
    Add the death events to the events list according to the death location in the script
    - events: [[e0], [e1], [e2], ...]
    where e are a list of lists of all the chad_id participates in that scene according the script.
    - ind_tony: the index of the scene that TONY STARK dead there.
    - ind_natasha: the index of the scene that NATASHA ROMANOFF dead there.
    """
    new_ev = [None] * (len(events) + 2)
    new_ev[:ind_natasha + 1] = np.array(events[:ind_natasha + 1])
    new_ev[ind_natasha + 1] = [4]
    new_ev[ind_natasha + 2:ind_tony + 1] = events[ind_natasha + 1: ind_tony + 1]
    new_ev[ind_tony + 1] = [0]
    new_ev[ind_tony + 2:] = events[ind_tony + 1:]
    return new_ev


def important_events(events, places):
    """
    Create the important locations and descriptions of the scenes
    - events: [[e0], [e1], [e2], ...]
    - places: {char: [i0, i1, ...]}
    when i is the index of the corresponding scene.
    """
    annotations = [''] * len(events)
    for str, idx in places.items():
        for i in range(len(idx)):
            if i == 0:
                annotations[idx[i]] = str
            else:
                if idx[i] - idx[i - 1] > 2:
                    annotations[idx[i]] = str
    annotations[43] = "THE FINAL BATTLE"
    return annotations


if __name__ == '__main__':
    characters = jokerScript.get_characters("https://www.imdb.com/title/tt4154796/fullcredits")
    events, scenes, death_tony, death_natasha, bla = jokerScript.translate_char_to_num()
    places = jokerScript.interesting_scene()
    annotations = important_events(events, places)
    events = update_events(events, death_tony, death_natasha) # add the death events

    chars, timelines, deaths = parse_data(characters, events)
    plot_data(chars, timelines, deaths, scenes, annotations)


